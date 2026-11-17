"""osu!watch local broadcast server (Python standard library)."""
import argparse
import json
import mimetypes
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
PAGES = {'/': 'index.html', '/index.html': 'index.html', '/studio': 'studio.html', '/studio.html': 'studio.html', '/style.css': 'style.css', '/app.js': 'app.js'}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlsplit(self.path).path
        if path in ('/api/health', '/api/channel'):
            payload = {'ok': True, 'channel': 'osu!watch', 'mode': 'standby', 'live': False, 'time': datetime.now(timezone.utc).isoformat()}
            if path == '/api/channel':
                payload['schedule'] = [{'title': 'osu!megamix', 'status': 'Coming soon'}, {'title': 'osu!watch Originals', 'status': 'Coming soon'}]
            data = json.dumps(payload).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        name = PAGES.get(path)
        if name is None:
            self.send_error(404, 'Route not found')
            return
        data = (ROOT / name).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mimetypes.guess_type(name)[0] or 'application/octet-stream')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        self.send_error(405, 'Broadcast publishing is not enabled')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    with ThreadingHTTPServer((args.host, args.port), Handler) as server:
        print(f'osu!watch: http://{args.host}:{args.port}/', flush=True)
        server.serve_forever()

if __name__ == '__main__':
    main()
