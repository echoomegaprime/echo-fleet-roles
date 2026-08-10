"""Small authenticated HTTP/JSON transport over the shared gateway."""
from __future__ import annotations

import argparse
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from connector_gateway import dispatch


class Handler(BaseHTTPRequestHandler):
    server_version = "InnovatorConnector/1.0"

    def log_message(self, *_args):
        return

    def _write(self, status: int, body: dict):
        encoded = json.dumps(body, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        if self.path != "/health":
            self._write(404, {"ok": False, "error": "not_found"})
            return
        self._write(200, dispatch({"id": "http-health", "op": "health"}))

    def do_POST(self):
        if self.path != "/v1/connector":
            self._write(404, {"ok": False, "error": "not_found"})
            return
        expected = os.environ.get("ECHO_CONNECTOR_HTTP_TOKEN")
        supplied = self.headers.get("Authorization", "")
        if expected and not hmac.compare_digest(supplied, "Bearer " + expected):
            self._write(401, {"ok": False, "error": "unauthorized"})
            return
        length = min(int(self.headers.get("Content-Length", "0")), 1_048_576)
        try:
            request = json.loads(self.rfile.read(length))
            result = dispatch(request)
        except (ValueError, TypeError, json.JSONDecodeError):
            result = {"ok": False, "error": "invalid_json"}
        self._write(200 if result.get("ok", False) else 400, result)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8791)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(json.dumps({"listening": f"http://{args.host}:{args.port}", "auth": bool(os.environ.get("ECHO_CONNECTOR_HTTP_TOKEN"))}))
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
