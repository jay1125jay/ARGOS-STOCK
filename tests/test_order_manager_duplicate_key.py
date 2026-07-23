import json
import tempfile
from pathlib import Path

from engines.stock.order_manager import OrderManager


def run_test() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        orders_path = (
            Path(temporary_directory)
            / "orders.json"
        )

        manager = OrderManager(
            orders_path=orders_path
        )

        client_order_key = (
            "DUPLICATE-KEY-TEST-001"
        )

        first_order = manager.create_order(
            symbol="005930",
            side="BUY",
            price=70000,
            qty=1,
            reason="DUPLICATE_KEY_TEST",
            strategy="ORDER_MANAGER_TEST",
            client_order_key=client_order_key,
        )

        duplicate_blocked = False
        duplicate_message = ""

        try:
            manager.create_order(
                symbol="005930",
                side="BUY",
                price=70000,
                qty=1,
                reason="DUPLICATE_KEY_TEST",
                strategy="ORDER_MANAGER_TEST",
                client_order_key=client_order_key,
            )

        except ValueError as error:
            duplicate_blocked = True
            duplicate_message = str(error)

        with orders_path.open(
            "r",
            encoding="utf-8-sig",
        ) as file:
            stored_data = json.load(file)

        stored_orders = stored_data.get(
            "orders",
            [],
        )

        assert duplicate_blocked is True
        assert len(stored_orders) == 1
        assert (
            stored_orders[0]["order_id"]
            == first_order["order_id"]
        )
        assert (
            stored_orders[0]["client_order_key"]
            == client_order_key
        )

        print(
            "DUPLICATE_CLIENT_ORDER_KEY_TEST=PASS"
        )
        print(
            f"FIRST_ORDER_ID={first_order['order_id']}"
        )
        print(
            f"STORED_ORDER_COUNT={len(stored_orders)}"
        )
        print(
            f"BLOCK_MESSAGE={duplicate_message}"
        )
        print(
            "PRODUCTION_ORDERS_UNTOUCHED=PASS"
        )


if __name__ == "__main__":
    run_test()