"""osu!watch: deterministic 24/7 channel guide and local HTTP viewer (stdlib only)."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
SCHEDULE = ROOT / 'schedule.json'
EPOCH = datetime(2026, 1, 1, tzinfo=timezone.utc).timestamp()


def load_schedule():
    data = json.loads(SCHEDULE.read_text(encoding='utf-8'))
    programs = data['programs']
    if not programs or any(not isinstance(p.get('duration_seconds'), int) or isinstance(p.get('duration_seconds'), bool) or p['duration_seconds'] <= 0 for p in programs):
        raise ValueError('Every program needs a positive integer duration_seconds')
    for p in programs:
        if p.get('kind') == 'sponsor' and not p.get('approved', False):
            raise ValueError('Sponsor segments must be explicitly approved')
    return programs


def channel_state(now=None):
    now = datetime.now(timezone.utc).timestamp() if now is None else now
    programs = load_schedule()
    total = sum(p['duration_seconds'] for p in programs)
    offset = (now - EPOCH) % total
    for index, program in enumerate(programs):
        duration = program['duration_seconds']
        if offset < duration:
            next_program = programs[(index + 1) % len(programs)]
            remaining = duration - offset
            return {'channel': 'osu!watch 1', 'server_time': now, 'current': program,
                    'next': next_program, 'elapsed_seconds': offset,
                    'remaining_seconds': remaining, 'program_started_at': now - offset,
                    'next_starts_at': now + remaining}
        offset -= duration
    raise RuntimeError('Schedule lookup failed')


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == '/api/channel':
            try:
                payload = json.dumps(channel_state()).encode('utf-8')
            except (ValueError, OSError, KeyError) as exc:
                self.send_error(500, str(exc))
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path == '/':
            self.path = '/index.html'
        super().do_GET()


def main():
    parser = argparse.ArgumentParser(description='osu!watch local broadcast channel')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    load_schedule()
    with ThreadingHTTPServer((args.host, args.port), Handler) as server:
        print(f'osu!watch: http://{args.host}:{args.port}', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nBroadcast server stopped.')


if __name__ == '__main__':
    main()
