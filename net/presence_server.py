#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, time

PRESENCE = {}
TTL_SECONDS = 25

def prune(now=None):
    now = now or time.time()
    dead = [cid for cid, v in PRESENCE.items() if now - v.get("t", 0) > TTL_SECONDS]
    for cid in dead:
        PRESENCE.pop(cid, None)

class H(BaseHTTPRequestHandler):
    def _json(self, code, obj):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        prune()
        if self.path.startswith("/health"):
            return self._json(200, {"ok": True, "ts": int(time.time())})
        if self.path.startswith("/presence"):
            now = time.time()
            players = [{"id": cid, "name": v.get("name","player")} for cid, v in PRESENCE.items() if now - v.get("t",0) <= TTL_SECONDS]
            return self._json(200, {"ok": True, "count": len(players), "players": players})
        return self._json(404, {"ok": False, "error": "not found"})

    def do_POST(self):
        prune()
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except Exception:
            body = {}

        if self.path.startswith("/presence"):
            cid = str(body.get("id") or "").strip()
            name = str(body.get("name") or "player").strip()
            if not cid:
                return self._json(400, {"ok": False, "error": "missing id"})
            PRESENCE[cid] = {"name": name[:24], "t": time.time()}
            return self._json(200, {"ok": True})

        return self._json(404, {"ok": False, "error": "not found"})

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--bind", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=3999)
    args = ap.parse_args()
    srv = HTTPServer((args.bind, args.port), H)
    print(f"megamix presence server: http://{args.bind}:{args.port}")
    srv.serve_forever()

if __name__ == "__main__":
    main()
