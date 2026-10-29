"""Local HTTP receiver: saves the POSTed CI test report as test-report.json.

Run:  python receiver/receiver.py
Env:  PORT (default 5001), REPORT_FILE (default test-report.json)
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "5001"))
REPORT_FILE = os.environ.get("REPORT_FILE", "test-report.json")


class Handler(BaseHTTPRequestHandler):
    def _reply(self, code, message):
        body = json.dumps({"message": message}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._reply(200, "receiver is running")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            report = json.loads(raw)
        except json.JSONDecodeError:
            self._reply(400, "body is not valid JSON")
            return
        with open(REPORT_FILE, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[receiver] saved {REPORT_FILE}: status={report.get('overall_status')} "
              f"commit={str(report.get('commit_sha'))[:7]}", flush=True)
        self._reply(200, f"saved to {REPORT_FILE}")

    def log_message(self, fmt, *args):
        print("[receiver]", fmt % args, flush=True)


if __name__ == "__main__":
    print(f"[receiver] listening on 0.0.0.0:{PORT}, writing {REPORT_FILE}", flush=True)
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
