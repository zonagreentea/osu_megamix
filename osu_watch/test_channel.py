import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen, Request
from .channel import Handler

class ChannelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def test_routes(self):
        for path in ('/', '/index.html', '/studio', '/studio.html', '/style.css', '/app.js', '/api/health', '/api/channel'):
            with self.subTest(path=path), urlopen(self.base + path) as response:
                self.assertEqual(response.status, 200)

    def test_channel_status(self):
        with urlopen(self.base + '/api/channel') as response:
            data = json.load(response)
        self.assertTrue(data['ok']); self.assertFalse(data['live'])
        self.assertTrue(data['schedule'])

    def test_unknown_route(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(self.base + '/missing')
        self.assertEqual(caught.exception.code, 404)

    def test_no_unauthorized_publishing(self):
        with self.assertRaises(HTTPError) as caught:
            urlopen(Request(self.base + '/api/live', data=b'{}', method='POST'))
        self.assertEqual(caught.exception.code, 405)
