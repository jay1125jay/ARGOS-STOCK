import json
import os
import urllib.request
from datetime import datetime

from engines.portfolio_engine import calculate_portfolio
from engines.position_manager import check_all_exits, load_positions
from engines.technical_engine import build_signal
from engines.report_engine import (
    ensure_report_files,
    save_trade,
    calculate_report,
    save_report,
)
from engines.news_engine import update_news_status
from engines.macro_engine import update_macro_status
from engines.decision_engine import build_decision
from engines.execution_engine import build_execution_plan
from engines.paper_router import route_paper_order
from engines.operation_logger import append_operation_log
from engines.auto_selector import select_auto_candidate
from engines.auto_start_engine import run_auto_start
from engines.paper_session_engine import update_paper_session
from engines.operation_report_engine import generate_operation_report
from engines.runtime_monitor import update_runtime_status


BASE_DIR = r"C:\ARGOS_AI"
MARKET_FILE = os.path.join(BASE_DIR, "data", "market", "market_status.json")

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT"]


def ensure_files():
    os.makedirs(os.path.dirname(MARKET_FILE), exist_ok=True)
    ensure_report_files()


def fetch_candles(symbol, interval, limit=120):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"

    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def analyze_symbol(symbol):
    candles_5m = fetch_candles(symbol, "5m", 120)
    candles_1m = fetch_candles(symbol, "1m", 120)

    return build_signal(symbol, candles_5m, candles_1m)


def signal_strength(item):
    signal_score = float(item.get("signal_score", 50) or 50)
    risk_score = float(item.get("risk_score", 100) or 100)
    action = item.get("action", "WAIT")

    direction_strength = abs(signal_score - 50)
    action_bonus = 100 if action in ["LONG", "SHORT"] else 0

    return action_bonus + direction_strength - risk_score


def select_best_signal(results):
    if not results:
        return {
            "symbol": "NONE",
            "price": 0,
            "signal_score": 0,
            "risk_score": 100,
            "action": "WAIT",
            "selection_reason": "NO_RESULTS"
        }

    actionable = [item for item in results if item.get("action") in ["LONG", "SHORT"]]

    if actionable:
        best = sorted(actionable, key=signal_strength, reverse=True)[0]
        best["selection_reason"] = "ACTIONABLE_SIGNAL"
        return best

    best = sorted(results, key=signal_strength, reverse=True)[0]
    best["selection_reason"] = "WATCHLIST_STRONGEST_SIGNAL"
    return best


def scan_market():
    results = []

    for symbol in SYMBOLS:
        try:
            results.append(analyze_symbol(symbol))
        except Exception as e:
            results.append({
                "symbol": symbol,
                "price": 0,
                "change_pct": 0,
                "rsi": 50,
                "ema9": 0,
                "ema21": 0,
                "trend": "ERROR",
                "volume_ratio": 0,
                "atr_pct": 0,
                "signal_score": 0,
                "risk_score": 100,
                "action": "WAIT",
                "error": str(e),
            })

    best = select_best_signal(results)

    with open(MARKET_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mode": "PAPER_ONLY",
            "results": results,
            "best": best,
        }, f, indent=2)

    return results, best


def print_market(results):
    for r in results:
        print(
            f"{r['symbol']} PRICE={r['price']} CHANGE={r['change_pct']}% "
            f"5M_TREND={r.get('trend_5m')} "
            f"1M_ENTRY={r.get('entry_signal_1m')} "
            f"FINAL={r.get('final_action')} "
            f"RSI1M={r.get('rsi_1m')} RSI5M={r.get('rsi_5m')} "
            f"VOL={r['volume_ratio']} ATR={r['atr_pct']} "
            f"SIGNAL={r['signal_score']} RISK={r['risk_score']} ACTION={r['action']}"
        )


def print_positions():
    data = load_positions()
    positions = data.get("positions", [])

    print("-" * 50)
    print(f"OPEN_POSITIONS={len(positions)}")

    for p in positions:
        print(
            f"HOLDING {p['symbol']} {p['action']} "
            f"ENTRY={p['entry']} TP={p['tp']} SL={p['sl']} "
            f"SIZE={p.get('position_size')}"
        )


def main():
    ensure_files()
    trade_changed = False

    print("ARGOS AI")
    print("MODE=PAPER_ONLY")
    print("REAL_ORDER=FALSE")
    print("API_ORDER=FALSE")
    print("AUTO_REAL_ORDER=FALSE")
    print("-" * 50)

    news = update_news_status()
    macro = update_macro_status()

    print("NEWS_ENGINE=OK")
    print("NEWS_SENTIMENT=" + str(news.get("market_sentiment")))
    print("NEWS_RISK=" + str(news.get("risk_level")))
    print("MACRO_ENGINE=OK")
    print("MACRO_REGIME=" + str(macro.get("market_regime")))
    print("MACRO_RATE_RISK=" + str(macro.get("rate_risk")))
    print("MACRO_EVENT_RISK=" + str(macro.get("event_risk")))
    print("-" * 50)

    results, best = scan_market()
    print_market(results)

    print("-" * 50)
    print(f"BEST_SYMBOL={best['symbol']}")
    print(f"BEST_ACTION={best['action']}")
    print(f"BEST_SIGNAL_SCORE={best['signal_score']}")
    print(f"BEST_RISK_SCORE={best['risk_score']}")
    print(f"BEST_SELECTION_REASON={best.get('selection_reason', '-')}")

    closed_trades = check_all_exits(results)

    for trade in closed_trades:
        save_trade(trade)
        trade_changed = True

        print("POSITION_EXIT=EXECUTED")
        print(f"EXIT_SYMBOL={trade['symbol']}")
        print(f"EXIT_REASON={trade.get('exit_reason')}")
        print(f"PNL={trade['pnl']}")
        print(f"RESULT={trade['result']}")

    decision = build_decision()

    print("-" * 50)
    print("DECISION_ENGINE=OK")
    print("DECISION_SYMBOL=" + str(decision.get("symbol")))
    print("DECISION=" + str(decision.get("decision")))
    print("DECISION_ACTION=" + str(decision.get("action")))
    print("DECISION_REASON=" + str(decision.get("reason")))
    print("AUTO_ALLOWED=" + str(decision.get("auto_allowed")))

    execution = build_execution_plan()

    print("-" * 50)
    print("EXECUTION_ENGINE=OK")
    print("EXECUTION_ACTION=" + str(execution.get("execution_action")))
    print("EXECUTION_SYMBOL=" + str(execution.get("symbol")))
    print("EXECUTION_DIRECTION=" + str(execution.get("direction")))
    print("PAPER_ORDER_READY=" + str(execution.get("paper_order_ready")))
    print("POSITION_SIZE=" + str(execution.get("position_size")))
    print("REAL_ORDER_ENABLED=" + str(execution.get("real_order_enabled")))
    print("API_ORDER_ENABLED=" + str(execution.get("api_order_enabled")))

    router = route_paper_order()

    print("-" * 50)
    print("PAPER_ROUTER=OK")
    print("ROUTER_STATUS=" + str(router.get("status")))
    print("ROUTER_REASON=" + str(router.get("reason")))
    print("ROUTER_REAL_ORDER_ENABLED=" + str(router.get("real_order_enabled")))
    print("ROUTER_API_ORDER_ENABLED=" + str(router.get("api_order_enabled")))
    print("ROUTER_AUTO_REAL_ORDER_ENABLED=" + str(router.get("auto_real_order_enabled")))

    if router.get("status") == "PAPER_POSITION_OPENED":
        trade_changed = True

    report = calculate_report()

    if trade_changed:
        save_report(report)

    portfolio = calculate_portfolio({
        "total_pnl": report["total_pnl"],
        "total_trades": report["total_trades"],
        "win_rate": report["win_rate"],
    })

    print_positions()

    print("-" * 50)
    print(f"TOTAL_TRADES={report['total_trades']}")
    print(f"WINS={report['wins']}")
    print(f"LOSSES={report['losses']}")
    print(f"WIN_RATE={report['win_rate']}%")
    print(f"TOTAL_PNL={report['total_pnl']}")
    print(f"CURRENT_BALANCE={portfolio['current_balance']}")

    select_auto_candidate()
    run_auto_start()
    update_paper_session(
        market={"best": best, "results": results},
        decision=decision,
        execution=execution,
        router=router
    )
    generate_operation_report()
    update_runtime_status(health="GOOD", last_error="")
    append_operation_log()

    update_runtime_status(
    loops=...,
    health="GOOD"
    )   


if __name__ == "__main__":
    main()