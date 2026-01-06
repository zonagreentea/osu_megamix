#!/usr/bin/env python3
import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

LOG_PATH = "logs/freeze_frames.jsonl"

class Handler(BaseHTTPRequestHandler):
    def _send(self, code=200, body=b"OK"):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send()

    def do_POST(self):
        if urlparse(self.path).path != "/freeze":
            self._send(404, b"not found")
            return

        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)

        try:
            data = json.loads(raw.decode("utf-8", "replace"))
        except Exception:
            self._send(400, b"bad json")
            return

        data["_server_ts"] = time.time()

        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

        self._send()

def main():
    print("[freeze_logger] listening on http://127.0.0.1:8787/freeze")
    print("[freeze_logger] writing -> freeze_frames.jsonl")
    HTTPServer(("127.0.0.1", 8787), Handler).serve_forever()

if __name__ == "__main__":
    main()
