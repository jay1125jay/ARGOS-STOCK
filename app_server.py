import csv
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

from engines.portfolio_engine import calculate_portfolio
from engines.analytics_engine import analyze_trades
from engines.health_engine import get_health
from engines.home_summary_engine import build_home_summary

ROOT = r"C:\ARGOS_AI"
APP = os.path.join(ROOT, "app")

TRADES = os.path.join(ROOT, "data", "trades", "paper_trades.csv")
REPORT = os.path.join(ROOT, "data", "reports", "report.csv")
MARKET = os.path.join(ROOT, "data", "market", "market_status.json")
POSITIONS = os.path.join(ROOT, "data", "open_positions.json")
NEWS = os.path.join(ROOT, "data", "news", "news_status.json")
MACRO = os.path.join(ROOT, "data", "macro", "macro_status.json")
SYSTEM_LOG = os.path.join(ROOT, "data", "logs", "system_log.csv")
DECISION_LOG = os.path.join(ROOT, "data", "logs", "decision_log.csv")
AI = os.path.join(ROOT, "data", "ai", "ai_status.json")
BACKTEST = os.path.join(ROOT, "data", "backtest", "backtest_status.json")
CHART = os.path.join(ROOT, "data", "chart", "chart_state.json")
CHART_ANALYSIS = os.path.join(ROOT, "data", "chart", "chart_analysis.json")
BRAIN = os.path.join(ROOT, "data", "brain", "argos_brain_status.json")
DECISION = os.path.join(ROOT, "data", "decision", "decision_status.json")
EXECUTION = os.path.join(ROOT, "data", "execution", "execution_status.json")
PAPER_ROUTER = os.path.join(ROOT, "data", "execution", "paper_router_status.json")
AUTO = os.path.join(ROOT, "data", "auto", "auto_status.json")
SETTINGS = os.path.join(ROOT, "data", "config", "settings.json")
SESSION = os.path.join(ROOT, "data", "reports", "paper_session.json")
RUNTIME = os.path.join(ROOT, "data", "system", "runtime_status.json")

def read_csv(path):
    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def read_json(path):
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_unrealized_pnl(action, entry, price, position_size):
    if action == "LONG":
        pnl_pct = (price - entry) / entry
    elif action == "SHORT":
        pnl_pct = (entry - price) / entry
    else:
        pnl_pct = 0

    return round(position_size * pnl_pct, 6)


def enrich_positions(positions, market):
    results = market.get("results", [])
    position_list = positions.get("positions", [])

    for position in position_list:
        symbol = position.get("symbol")
        action = position.get("action")
        entry = float(position.get("entry", 0))
        tp = float(position.get("tp", 0))
        sl = float(position.get("sl", 0))
        position_size = float(position.get("position_size", 1000.0))

        current = None

        for item in results:
            if item.get("symbol") == symbol:
                current = item
                break

        if not current:
            position["current_price"] = "-"
            position["unrealized_pnl"] = "-"
            position["tp_distance_pct"] = "-"
            position["sl_distance_pct"] = "-"
            continue

        price = float(current.get("price", 0))

        if action == "LONG":
            tp_distance = ((tp - price) / price) * 100
            sl_distance = ((price - sl) / price) * 100
        elif action == "SHORT":
            tp_distance = ((price - tp) / price) * 100
            sl_distance = ((sl - price) / price) * 100
        else:
            tp_distance = 0
            sl_distance = 0

        position["current_price"] = round(price, 6)
        position["unrealized_pnl"] = calculate_unrealized_pnl(
            action,
            entry,
            price,
            position_size
        )
        position["tp_distance_pct"] = round(tp_distance, 4)
        position["sl_distance_pct"] = round(sl_distance, 4)

    return positions

class Handler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path.startswith("/api/status"):
            trades = read_csv(TRADES)
            reports = read_csv(REPORT)
            market = read_json(MARKET)
            positions = read_json(POSITIONS)
            news = read_json(NEWS)
            macro = read_json(MACRO)
            system_logs = read_csv(SYSTEM_LOG)
            decision_logs = read_csv(DECISION_LOG)
            ai = read_json(AI)
            backtest = read_json(BACKTEST)
            chart = read_json(CHART)
            chart_analysis = read_json(CHART_ANALYSIS)
            brain = read_json(BRAIN)
            decision = read_json(DECISION)
            execution = read_json(EXECUTION)
            paper_router = read_json(PAPER_ROUTER)
            auto = read_json(AUTO)
            session = read_json(SESSION) 
            settings = read_json(SETTINGS)
            runtime = read_json(RUNTIME)
                      
            latest_report = {
                "total_trades": 0,
                "wins": 0,
                "losses": 0,
                "win_rate": 0,
                "total_pnl": 0
            }

            if reports:
                r = reports[-1]
                latest_report = {
                    "total_trades": float(r.get("total_trades", 0)),
                    "wins": float(r.get("wins", 0)),
                    "losses": float(r.get("losses", 0)),
                    "win_rate": float(r.get("win_rate", 0)),
                    "total_pnl": float(r.get("total_pnl", 0))
                }

            portfolio = calculate_portfolio(latest_report)
            positions = enrich_positions(positions, market)
            analytics = analyze_trades()
            health = get_health()

            home_summary = build_home_summary(
                portfolio=portfolio,
                report=latest_report,
                positions=positions,
                decision=decision,
                execution=execution,
                auto_status=auto
            )

            body = json.dumps({
                "report": latest_report,
                "portfolio": portfolio,
                "trades": trades[-50:],
                "market": market,
                "positions": positions,
                "analytics": analytics,
                "health": health,
                "news": news,
                "macro": macro,
                "system_logs": system_logs[-20:],
                "decision_logs": decision_logs[-50:],
                "ai": ai,
                "backtest": backtest,
                "chart": chart,
                "chart_analysis": chart_analysis,
                "brain": brain,
                "decision": decision,
                "execution": execution,
                "paper_router": paper_router,
                "auto": auto,
                "home_summary": home_summary,
                "settings": settings,
                "runtime": runtime,
                "session": session,

            }).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        if self.path.startswith("/api/chart?"):
            from urllib.parse import urlparse, parse_qs
            from engines.chart_engine import build_chart_state

            query = parse_qs(urlparse(self.path).query)

            market = query.get("market", ["CRYPTO"])[0]
            symbol = query.get("symbol", ["BTCUSDT"])[0]

            chart = build_chart_state(market=market, symbol=symbol)
            body = json.dumps(chart).encode("utf-8")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
            return

        file_name = "index.html"

        if self.path.endswith(".css") or self.path.endswith(".js"):
            file_name = self.path[1:]

        file_path = os.path.join(APP, file_name)

        if not os.path.exists(file_path):
            self.send_response(404)
            self.end_headers()
            return

        with open(file_path, "rb") as f:
            data = f.read()

        content_type = "text/html"

        if file_name.endswith(".css"):
            content_type = "text/css"
        elif file_name.endswith(".js"):
            content_type = "application/javascript"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(data)


HTTPServer(("0.0.0.0", 8000), Handler).serve_forever()