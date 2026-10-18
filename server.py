#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import hmac
import os
from pathlib import Path
import urllib
import shutil
import tempfile
import sys

PORT = 8000
WEB_DIR = "node"

# Keep behaviour backward compatible: serve files from node/ by default.

class APIServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

    # ULTRA_FLOW_API_GUARD_V1
    MAX_JSON_BYTES = 1024 * 1024

    def _request_guard(self):
        # Reject browser requests from other origins before authentication.
        origin = self.headers.get("Origin")
        if origin:
            from urllib.parse import urlsplit
            try:
                parsed = urlsplit(origin)
                host = parsed.hostname
                port = parsed.port
                valid = (parsed.scheme == "http" and
                         host in ("localhost", "127.0.0.1") and
                         port == self.server.server_port and
                         parsed.username is None and parsed.password is None and
                         parsed.path in ("", "/") and not parsed.query and not parsed.fragment)
            except ValueError:
                valid = False
            if not valid:
                self._send_json({"ok": False, "reason": "origin denied"}, 403)
                return None
        # Validate size before reading, even for unauthenticated clients.
        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length) if raw_length is not None else -1
        except ValueError:
            length = -1
        if length > self.MAX_JSON_BYTES:
            # Reject oversized bodies without retaining them in memory.
            # Drain bounded chunks before replying to avoid Windows resets.
            remaining = length
            while remaining:
                chunk = self.rfile.read(min(65536, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
            self._send_json({"ok": False, "reason": "request too large"}, 413)
            return None
        if length < 0 or self.headers.get("Transfer-Encoding"):
            self._send_json({"ok": False, "reason": "invalid request length"}, 400)
            return None
        # Fail closed when no token is configured. Never use a hard-coded secret.
        token = os.environ.get("OSU_MEGAMIX_API_TOKEN", "")
        authorization = self.headers.get("Authorization", "")
        expected = "Bearer " + token
        if not token or len(token) < 32 or not hmac.compare_digest(authorization, expected):
            self._send_json({"ok": False, "reason": "unauthorized"}, 401)
            return None
        return length

    def _read_json(self, length):
        if length == 0:
            return None
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            return data if isinstance(data, dict) else None
        except (UnicodeDecodeError, ValueError):
            return None

    def _send_json(self, obj, code=200):
        data = json.dumps(obj, indent=2).encode('utf-8')
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        # Local-only API: check, grade, run, share
        path = urllib.parse.urlparse(self.path).path
        if path not in ("/check", "/grade", "/run", "/share"):
            return self._send_json({"ok": False, "reason": "unknown endpoint"}, 404)
        length = self._request_guard()
        if length is None:
            return
        body = self._read_json(length)
        if body is None:
            return self._send_json({"ok": False, "reason": "JSON object required"}, 400)

        if path == "/check":
            # expects {"homework_path": "...", "target": "macos"}
            hw = body.get("homework_path")
            target = body.get("target")
            if not hw or not target:
                return self._send_json({"ok": False, "reason": "homework_path and target required"}, 400)
            try:
                import homework
                res = homework.check_execution_compatibility(Path(hw), target)
                return self._send_json({"ok": True, "result": res})
            except Exception as e:
                return self._send_json({"ok": False, "reason": str(e)}, 500)

        if path == "/grade":
            hw = body.get("homework_path")
            target = body.get("target")
            force = bool(body.get("force", False))
            out_dir = Path(body.get("out_dir") or "dist")
            if not hw or not target:
                return self._send_json({"ok": False, "reason": "homework_path and target required"}, 400)
            try:
                import homework
                out_dir.mkdir(parents=True, exist_ok=True)
                manifest = None
                # perform compatibility check
                check = homework.check_execution_compatibility(Path(hw), target)
                # Decide output filename
                name = Path(hw).stem
                out_name = f"{name}_{target}.homework"
                dest = out_dir / out_name
                if dest.exists() and not force:
                    return self._send_json({"ok": False, "reason": f"destination exists: {dest}", "path": str(dest)}, 409)
                # pack
                homework.pack_homework(Path(hw), dest)
                # verify
                with tempfile.TemporaryDirectory(prefix="grade-") as temp:
                    unpack_dir = Path(temp) / "verified"
                    homework.unpack_homework(dest, unpack_dir, verify=True)
                # success
                report = {
                    "ok": True,
                    "package": str(dest),
                    "compatibility": check,
                }
                return self._send_json(report)
            except Exception as e:
                return self._send_json({"ok": False, "reason": str(e)}, 500)

        if path == "/run":
            hw = body.get("homework_path")
            target = body.get("target")
            if not hw or not target:
                return self._send_json({"ok": False, "reason": "homework_path and target required"}, 400)
            try:
                import homework
                rc = homework.run_homework(Path(hw), target)
                return self._send_json({"ok": True, "rc": rc})
            except Exception as e:
                return self._send_json({"ok": False, "reason": str(e)}, 500)

        if path == "/share":
            # Basic local export: copy archive to share_dir
            archive = body.get("archive_path")
            share_dir = Path(body.get("share_dir") or "shared")
            if not archive:
                return self._send_json({"ok": False, "reason": "archive_path required"}, 400)
            try:
                share_dir.mkdir(parents=True, exist_ok=True)
                dest = share_dir / Path(archive).name
                shutil.copy2(archive, dest)
                return self._send_json({"ok": True, "shared_path": str(dest)})
            except Exception as e:
                return self._send_json({"ok": False, "reason": str(e)}, 500)

        return self._send_json({"ok": False, "reason": "unknown endpoint"}, 404)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    print(f"Serving osu!megamix node UI and API on http://localhost:{PORT}")
    server = HTTPServer(("127.0.0.1", PORT), APIServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.server_close()
