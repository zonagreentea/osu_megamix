#!/usr/bin/env python3
"""Local, authenticated, read-only ball service."""
import hmac
import json
import os
import socketserver

MAX_REQUEST = 4096
ALLOWED = {"ping", "profile", "friends", "requests"}

def dispatch(request, secret):
    if not isinstance(request, dict):
        return {"ok": False, "error": "invalid request"}

    token = request.get("token")
    node = request.get("node")
    action = request.get("action")

    if not isinstance(token, str) or not hmac.compare_digest(
        token.encode(), secret.encode()
    ):
        return {"ok": False, "error": "authentication denied"}

    if not isinstance(node, str) or not node.strip():
        return {"ok": False, "error": "invalid identity"}

    if action not in ALLOWED:
        return {"ok": False, "error": "action denied"}

    if action == "ping":
        return {"ok": True, "message": "pong"}

    if action == "profile":
        return {"ok": True, "profile": {"node": node}}

    if action == "friends":
        return {"ok": True, "friends": []}

    return {"ok": True, "requests": []}

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        self.request.settimeout(3)
        line = self.rfile.readline(MAX_REQUEST + 1)
        if len(line) > MAX_REQUEST or not line.endswith(b"\n"):
            response = {"ok": False, "error": "invalid frame"}
        else:
            try:
                request = json.loads(line)
                response = dispatch(request, self.server.secret)
            except (ValueError, UnicodeError):
                response = {"ok": False, "error": "invalid JSON"}

        self.wfile.write(
            json.dumps(response, separators=(",", ":")).encode() + b"\n"
        )

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

def main():
    secret = os.environ.get("BALL_SERVER_TOKEN", "")
    if len(secret) < 32:
        raise SystemExit("BALL_SERVER_TOKEN must contain at least 32 characters")

    with Server(("127.0.0.1", 5052), Handler) as server:
        server.secret = secret
        print("ball server listening on 127.0.0.1:5052", flush=True)
        server.serve_forever()

if __name__ == "__main__":
    main()
