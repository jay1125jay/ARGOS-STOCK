from __future__ import annotations

import copy
import json
import os
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class OrderManager:
    """
    ARGOS_STOCK 주문 상태 관리 엔진.

    책임:
    - 주문 생성 및 고유 주문번호 발급
    - 주문 상태 전환 검증
    - 체결 수량 관리
    - orders.json 원자적 저장
    - 프로그램 재시작 시 주문 복원

    이 엔진은 PortfolioEngine을 직접 호출하지 않는다.
    실제 포트폴리오 반영은 ExecutionAI가 FILLED 상태를 확인한 뒤 수행한다.
    """

    ENGINE_NAME = "order_manager"
    MODE = "PAPER_ONLY"

    STATUS_NEW = "NEW"
    STATUS_ACCEPTED = "ACCEPTED"
    STATUS_PARTIAL = "PARTIAL"
    STATUS_FILLED = "FILLED"
    STATUS_CANCELED = "CANCELED"
    STATUS_REJECTED = "REJECTED"

    VALID_STATUSES = {
        STATUS_NEW,
        STATUS_ACCEPTED,
        STATUS_PARTIAL,
        STATUS_FILLED,
        STATUS_CANCELED,
        STATUS_REJECTED,
    }

    FINAL_STATUSES = {
        STATUS_FILLED,
        STATUS_CANCELED,
        STATUS_REJECTED,
    }

    VALID_SIDES = {"BUY", "SELL"}

    ALLOWED_TRANSITIONS = {
        STATUS_NEW: {
            STATUS_ACCEPTED,
            STATUS_CANCELED,
            STATUS_REJECTED,
        },
        STATUS_ACCEPTED: {
            STATUS_PARTIAL,
            STATUS_FILLED,
            STATUS_CANCELED,
            STATUS_REJECTED,
        },
        STATUS_PARTIAL: {
            STATUS_PARTIAL,
            STATUS_FILLED,
            STATUS_CANCELED,
        },
        STATUS_FILLED: set(),
        STATUS_CANCELED: set(),
        STATUS_REJECTED: set(),
    }

    def __init__(self, orders_path: Optional[str | Path] = None) -> None:
        project_root = Path(__file__).resolve().parents[2]

        self.orders_path = (
            Path(orders_path)
            if orders_path is not None
            else project_root / "data" / "orders" / "orders.json"
        )

        self._lock = threading.RLock()
        self._data = self._load_or_initialize()

    @staticmethod
    def _now() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _empty_data(self) -> Dict[str, Any]:
        return {
            "engine": self.ENGINE_NAME,
            "mode": self.MODE,
            "orders": [],
            "updated_at": self._now(),
        }

    def _load_or_initialize(self) -> Dict[str, Any]:
        self.orders_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.orders_path.exists():
            data = self._empty_data()
            self._atomic_write(data)
            return data

        with self.orders_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        self._validate_storage(data)
        return data

    def _validate_storage(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            raise ValueError(
                "orders.json 최상위 데이터는 객체여야 합니다."
            )

        orders = data.get("orders")

        if not isinstance(orders, list):
            raise ValueError(
                "orders.json의 orders는 배열이어야 합니다."
            )

        seen_order_ids = set()

        for order in orders:
            self._validate_loaded_order(order)

            order_id = order["order_id"]

            if order_id in seen_order_ids:
                raise ValueError(
                    f"중복 주문번호가 발견되었습니다: {order_id}"
                )

            seen_order_ids.add(order_id)

    def _validate_loaded_order(self, order: Dict[str, Any]) -> None:
        required_fields = {
            "order_id",
            "symbol",
            "side",
            "price",
            "qty",
            "filled_qty",
            "remaining_qty",
            "status",
            "reason",
            "created_at",
            "updated_at",
        }

        if not isinstance(order, dict):
            raise ValueError(
                "orders 배열의 각 주문은 객체여야 합니다."
            )

        missing_fields = required_fields - set(order.keys())

        if missing_fields:
            missing = ", ".join(sorted(missing_fields))
            raise ValueError(
                f"주문 필드가 누락되었습니다: {missing}"
            )

        if order["status"] not in self.VALID_STATUSES:
            raise ValueError(
                "유효하지 않은 주문 상태입니다: "
                f"{order['status']}"
            )

        if order["side"] not in self.VALID_SIDES:
            raise ValueError(
                "유효하지 않은 주문 방향입니다: "
                f"{order['side']}"
            )

        qty = int(order["qty"])
        filled_qty = int(order["filled_qty"])
        remaining_qty = int(order["remaining_qty"])

        if qty <= 0:
            raise ValueError(
                "주문 수량은 1 이상이어야 합니다."
            )

        if filled_qty < 0 or filled_qty > qty:
            raise ValueError(
                "체결 수량이 유효하지 않습니다."
            )

        if remaining_qty != qty - filled_qty:
            raise ValueError(
                "잔여 수량 계산이 일치하지 않습니다."
            )

    def _atomic_write(self, data: Dict[str, Any]) -> None:
        self.orders_path.parent.mkdir(parents=True, exist_ok=True)

        temporary_path: Optional[Path] = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=str(self.orders_path.parent),
                prefix="orders_",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)

                json.dump(
                    data,
                    temporary_file,
                    ensure_ascii=False,
                    indent=2,
                )

                temporary_file.flush()
                os.fsync(temporary_file.fileno())

            os.replace(
                temporary_path,
                self.orders_path,
            )

        finally:
            if (
                temporary_path is not None
                and temporary_path.exists()
            ):
                temporary_path.unlink()

    def _save(self) -> None:
        self._data["engine"] = self.ENGINE_NAME
        self._data["mode"] = self.MODE
        self._data["updated_at"] = self._now()

        self._atomic_write(self._data)

    def _next_order_id(self) -> str:
        today = datetime.now().strftime("%Y%m%d")
        prefix = f"PAPER-{today}-"

        maximum_sequence = 0

        for order in self._data["orders"]:
            order_id = str(
                order.get(
                    "order_id",
                    "",
                )
            )

            if not order_id.startswith(prefix):
                continue

            sequence_text = order_id[len(prefix):]

            if sequence_text.isdigit():
                maximum_sequence = max(
                    maximum_sequence,
                    int(sequence_text),
                )

        return f"{prefix}{maximum_sequence + 1:06d}"

    def _find_order_index(self, order_id: str) -> int:
        normalized_order_id = str(order_id).strip()

        if not normalized_order_id:
            raise ValueError(
                "order_id가 비어 있습니다."
            )

        for index, order in enumerate(
            self._data["orders"]
        ):
            if order["order_id"] == normalized_order_id:
                return index

        raise KeyError(
            "주문을 찾을 수 없습니다: "
            f"{normalized_order_id}"
        )

    def _transition(
        self,
        order: Dict[str, Any],
        new_status: str,
    ) -> None:
        current_status = order["status"]

        if new_status not in self.VALID_STATUSES:
            raise ValueError(
                "유효하지 않은 주문 상태입니다: "
                f"{new_status}"
            )

        allowed = self.ALLOWED_TRANSITIONS[
            current_status
        ]

        if new_status not in allowed:
            raise ValueError(
                "허용되지 않은 주문 상태 전환입니다: "
                f"{current_status} -> {new_status}"
            )

        order["status"] = new_status
        order["updated_at"] = self._now()

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        normalized = str(symbol).strip()

        if not normalized:
            raise ValueError(
                "symbol이 비어 있습니다."
            )

        return normalized

    @classmethod
    def _normalize_side(cls, side: str) -> str:
        normalized = str(side).strip().upper()

        if normalized not in cls.VALID_SIDES:
            raise ValueError(
                "side는 BUY 또는 SELL이어야 합니다."
            )

        return normalized

    @staticmethod
    def _normalize_price(price: float | int) -> float:
        normalized = float(price)

        if normalized <= 0:
            raise ValueError(
                "price는 0보다 커야 합니다."
            )

        return normalized

    @staticmethod
    def _normalize_qty(qty: float | int) -> int:
        numeric_qty = float(qty)

        if not numeric_qty.is_integer():
            raise ValueError(
                "국내주식 주문 수량은 정수여야 합니다."
            )

        normalized = int(numeric_qty)

        if normalized <= 0:
            raise ValueError(
                "qty는 1 이상이어야 합니다."
            )

        return normalized

    def create_order(
        self,
        symbol: str,
        side: str,
        price: float | int,
        qty: float | int,
        reason: str = "",
        strategy: str = "",
        client_order_key: str = "",
    ) -> Dict[str, Any]:
        """
        신규 주문을 NEW 상태로 생성한다.

        client_order_key:
        ExecutionAI가 동일 신호를 다시 전달하면
        동일 키를 기준으로 중복 생성을 차단한다.

        빈 문자열이면 중복 키 검사를 수행하지 않는다.
        """

        with self._lock:
            normalized_symbol = self._normalize_symbol(
                symbol
            )
            normalized_side = self._normalize_side(
                side
            )
            normalized_price = self._normalize_price(
                price
            )
            normalized_qty = self._normalize_qty(
                qty
            )
            normalized_client_key = str(
                client_order_key
            ).strip()

            if normalized_client_key:
                for existing_order in self._data["orders"]:
                    if (
                        existing_order.get(
                            "client_order_key"
                        )
                        == normalized_client_key
                    ):
                        raise ValueError(
                            "중복 client_order_key 주문입니다: "
                            f"{normalized_client_key}"
                        )

            timestamp = self._now()

            order = {
                "order_id": self._next_order_id(),
                "client_order_key": normalized_client_key,
                "symbol": normalized_symbol,
                "side": normalized_side,
                "price": normalized_price,
                "qty": normalized_qty,
                "filled_qty": 0,
                "remaining_qty": normalized_qty,
                "average_fill_price": 0.0,
                "status": self.STATUS_NEW,
                "reason": str(reason).strip(),
                "strategy": str(strategy).strip(),
                "reject_reason": "",
                "cancel_reason": "",
                "created_at": timestamp,
                "accepted_at": "",
                "filled_at": "",
                "canceled_at": "",
                "rejected_at": "",
                "updated_at": timestamp,
            }

            self._data["orders"].append(order)
            self._save()

            return copy.deepcopy(order)

    def accept_order(
        self,
        order_id: str,
    ) -> Dict[str, Any]:
        with self._lock:
            index = self._find_order_index(
                order_id
            )
            order = self._data["orders"][index]

            self._transition(
                order,
                self.STATUS_ACCEPTED,
            )
            order["accepted_at"] = self._now()

            self._save()

            return copy.deepcopy(order)

    def fill_order(
        self,
        order_id: str,
        fill_qty: float | int,
        fill_price: float | int,
    ) -> Dict[str, Any]:
        """
        주문에 신규 체결 수량을 누적한다.

        fill_qty는 이번 체결분이다.

        누적 체결 수량이 주문 수량과 같으면 FILLED,
        주문 수량보다 작으면 PARTIAL 상태가 된다.
        """

        with self._lock:
            index = self._find_order_index(
                order_id
            )
            order = self._data["orders"][index]

            current_status = order["status"]

            if current_status not in {
                self.STATUS_ACCEPTED,
                self.STATUS_PARTIAL,
            }:
                raise ValueError(
                    "ACCEPTED 또는 PARTIAL 주문만 "
                    "체결할 수 있습니다. "
                    f"현재 상태: {current_status}"
                )

            normalized_fill_qty = self._normalize_qty(
                fill_qty
            )
            normalized_fill_price = (
                self._normalize_price(
                    fill_price
                )
            )

            remaining_qty = int(
                order["remaining_qty"]
            )

            if normalized_fill_qty > remaining_qty:
                raise ValueError(
                    "체결 수량이 잔여 주문 수량을 "
                    "초과했습니다. "
                    f"fill_qty={normalized_fill_qty}, "
                    f"remaining_qty={remaining_qty}"
                )

            previous_filled_qty = int(
                order["filled_qty"]
            )
            previous_average_price = float(
                order.get(
                    "average_fill_price",
                    0.0,
                )
            )

            new_filled_qty = (
                previous_filled_qty
                + normalized_fill_qty
            )

            total_fill_amount = (
                previous_average_price
                * previous_filled_qty
                + normalized_fill_price
                * normalized_fill_qty
            )

            new_average_fill_price = (
                total_fill_amount
                / new_filled_qty
            )

            order["filled_qty"] = new_filled_qty
            order["remaining_qty"] = (
                int(order["qty"])
                - new_filled_qty
            )
            order["average_fill_price"] = round(
                new_average_fill_price,
                4,
            )

            if order["remaining_qty"] == 0:
                self._transition(
                    order,
                    self.STATUS_FILLED,
                )
                order["filled_at"] = self._now()

            else:
                self._transition(
                    order,
                    self.STATUS_PARTIAL,
                )

            self._save()

            return copy.deepcopy(order)

    def cancel_order(
        self,
        order_id: str,
        reason: str = "",
    ) -> Dict[str, Any]:
        with self._lock:
            index = self._find_order_index(
                order_id
            )
            order = self._data["orders"][index]

            self._transition(
                order,
                self.STATUS_CANCELED,
            )
            order["cancel_reason"] = str(
                reason
            ).strip()
            order["canceled_at"] = self._now()

            self._save()

            return copy.deepcopy(order)

    def reject_order(
        self,
        order_id: str,
        reason: str,
    ) -> Dict[str, Any]:
        with self._lock:
            normalized_reason = str(
                reason
            ).strip()

            if not normalized_reason:
                raise ValueError(
                    "주문 거절 사유가 필요합니다."
                )

            index = self._find_order_index(
                order_id
            )
            order = self._data["orders"][index]

            self._transition(
                order,
                self.STATUS_REJECTED,
            )
            order["reject_reason"] = (
                normalized_reason
            )
            order["rejected_at"] = self._now()

            self._save()

            return copy.deepcopy(order)

    def get_order(
        self,
        order_id: str,
    ) -> Dict[str, Any]:
        with self._lock:
            index = self._find_order_index(
                order_id
            )

            return copy.deepcopy(
                self._data["orders"][index]
            )

    def list_orders(
        self,
        status: Optional[str] = None,
        symbol: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            normalized_status = (
                str(status).strip().upper()
                if status is not None
                else None
            )

            normalized_symbol = (
                str(symbol).strip()
                if symbol is not None
                else None
            )

            if (
                normalized_status is not None
                and normalized_status
                not in self.VALID_STATUSES
            ):
                raise ValueError(
                    "유효하지 않은 주문 상태입니다: "
                    f"{normalized_status}"
                )

            result = []

            for order in self._data["orders"]:
                if (
                    normalized_status is not None
                    and order["status"]
                    != normalized_status
                ):
                    continue

                if (
                    normalized_symbol is not None
                    and order["symbol"]
                    != normalized_symbol
                ):
                    continue

                result.append(
                    copy.deepcopy(order)
                )

            return result

    def get_open_orders(
        self,
    ) -> List[Dict[str, Any]]:
        with self._lock:
            return [
                copy.deepcopy(order)
                for order in self._data["orders"]
                if order["status"]
                not in self.FINAL_STATUSES
            ]


def _run_self_test() -> None:
    """
    운영 orders.json을 변경하지 않는 임시 단위 테스트.
    """

    with tempfile.TemporaryDirectory() as temporary_directory:
        test_path = (
            Path(temporary_directory)
            / "orders.json"
        )

        manager = OrderManager(test_path)

        created = manager.create_order(
            symbol="005930",
            side="BUY",
            price=70000,
            qty=2,
            reason="SELF_TEST",
            strategy="ORDER_MANAGER_V1",
            client_order_key="SELF-TEST-001",
        )

        assert created["status"] == "NEW"
        assert created["filled_qty"] == 0
        assert created["remaining_qty"] == 2

        accepted = manager.accept_order(
            created["order_id"]
        )

        assert accepted["status"] == "ACCEPTED"

        partial = manager.fill_order(
            order_id=created["order_id"],
            fill_qty=1,
            fill_price=70000,
        )

        assert partial["status"] == "PARTIAL"
        assert partial["filled_qty"] == 1
        assert partial["remaining_qty"] == 1

        filled = manager.fill_order(
            order_id=created["order_id"],
            fill_qty=1,
            fill_price=70100,
        )

        assert filled["status"] == "FILLED"
        assert filled["filled_qty"] == 2
        assert filled["remaining_qty"] == 0
        assert (
            filled["average_fill_price"]
            == 70050.0
        )

        restored_manager = OrderManager(
            test_path
        )
        restored = restored_manager.get_order(
            created["order_id"]
        )

        assert restored["status"] == "FILLED"
        assert (
            restored["average_fill_price"]
            == 70050.0
        )
        assert (
            len(restored_manager.list_orders())
            == 1
        )
        assert (
            restored_manager.get_open_orders()
            == []
        )

        print("ORDER_MANAGER_SELF_TEST=PASS")
        print(
            f"ORDER_ID={restored['order_id']}"
        )
        print(
            f"STATUS={restored['status']}"
        )
        print(
            f"FILLED_QTY={restored['filled_qty']}"
        )
        print(
            "AVERAGE_FILL_PRICE="
            f"{restored['average_fill_price']}"
        )
        print("RESTART_RESTORE=PASS")


if __name__ == "__main__":
    _run_self_test()

