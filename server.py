#!/usr/bin/env python3
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
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

    def _read_json(self):
        length = int(self.headers.get('Content-Length', 0))
        if length == 0:
            return None
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode('utf-8'))
        except Exception:
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
        body = self._read_json() or {}

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
                from pathlib import Path
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
