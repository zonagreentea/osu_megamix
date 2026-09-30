from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 8000

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/index.html"
        return super().do_GET()

HTTPServer(("", PORT), Handler).serve_forever()

