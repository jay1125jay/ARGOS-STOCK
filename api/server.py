import json
from http.server import HTTPServer, BaseHTTPRequestHandler

from engines.stock.core.config import Config
from engines.stock.core.datahub import DataHub


class ArgosAPI(BaseHTTPRequestHandler):

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        hub = DataHub()
        path = self.path.split("?")[0]

        routes = {
            "/api/v1/health": hub.health,
            "/api/v1/decision": hub.decision,
            "/api/v1/report": hub.report,
            "/api/v1/account": hub.account,
            "/api/v1/positions": hub.positions,
            "/api/v1/history": hub.history,
            "/api/v1/execution": hub.execution,
            "/api/v1/runner": hub.runner,
            "/api/v1/system": hub.snapshot,
        }

        if path in routes:
            self.send_json(routes[path]())
            return

        self.send_json({
            "error": "NOT_FOUND",
            "path": path
        }, 404)


def main():
    Config.ensure_dirs()

    server = HTTPServer(
        (Config.API_HOST, Config.API_PORT),
        ArgosAPI
    )

    print("ARGOS_STOCK_API_READY")
    print(f"http://{Config.API_HOST}:{Config.API_PORT}/api/v1/health")
    print("PAPER_ONLY:", Config.PAPER_ONLY)
    print("REAL_ORDER:", Config.REAL_ORDER)

    server.serve_forever()


if __name__ == "__main__":
    main()