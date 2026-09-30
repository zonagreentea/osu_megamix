#!/usr/bin/env python3
import os, sys, urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

ROOT = os.path.abspath(os.getcwd())

def ok_path(p: str) -> bool:
    if not p:
        return False
    ap = os.path.abspath(p)

    # allow repo files
    if ap.startswith(ROOT + os.sep):
        return True

    # allow absolute user files (dev-only; tighten later if desired)
    if ap.startswith("/Users/"):
        return True

    return False

class Handler(SimpleHTTPRequestHandler):
    # serve repo as normal web root
    def translate_path(self, path):
        # keep default behavior (serve from ROOT)
        path = urllib.parse.urlparse(path).path
        path = urllib.parse.unquote(path)
        if path.startswith("/"):
            path = path[1:]
        return os.path.join(ROOT, path)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)

        # absolute file gateway: /__file?path=/Users/...
        if u.path == "/__file":
            qs = urllib.parse.parse_qs(u.query)
            p = urllib.parse.unquote(qs.get("path", [""])[0])

            if (not ok_path(p)) or (not os.path.isfile(p)):
                self.send_response(404)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"not found / not allowed\n")
                return

            ext = os.path.splitext(p)[1].lower()
            ctype = "application/octet-stream"
            if ext in (".mix", ".txt", ".json", ".js", ".css", ".html"):
                ctype = "text/plain; charset=utf-8"
            elif ext == ".mp3":
                ctype = "audio/mpeg"
            elif ext == ".wav":
                ctype = "audio/wav"

            try:
                st = os.stat(p)
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(st.st_size))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                with open(p, "rb") as f:
                    while True:
                        chunk = f.read(1024 * 256)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(("error: %s\n" % e).encode("utf-8"))
            return

        # otherwise: static file serving from repo root
        return super().do_GET()

def main():
    host = "127.0.0.1"
    port = 8000
    argv = sys.argv[1:]

    if len(argv) >= 1:
        port = int(argv[0])
    if len(argv) >= 2:
        host = argv[1]

    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"[mix_server] root={ROOT}")
    print(f"[mix_server] http://{host}:{port}/index.html")
    print(f"[mix_server] file gateway: /__file?path=/Users/...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
