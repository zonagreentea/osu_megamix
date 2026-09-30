from http.server import SimpleHTTPRequestHandler, HTTPServer
import os

PORT = 8000
WEB_DIR = "web"

class GameServer(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIR, **kwargs)

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    print(f"Serving osu!Mix on http://localhost:{PORT}")
    server = HTTPServer(("0.0.0.0", PORT), GameServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.server_close()

