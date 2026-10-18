"""Red-phase API security contract tests. Do not execute homework projects."""
import http.client
import json
import threading
import unittest
from http.server import HTTPServer

import server


class ServerSecurityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(("127.0.0.1", 0), server.APIServer)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=3)

    def request(self, endpoint, body=b"{}", headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.httpd.server_port, timeout=5)
        try:
            conn.request("POST", endpoint, body=body, headers={
                "Content-Type": "application/json",
                "Host": f"127.0.0.1:{self.httpd.server_port}",
                **(headers or {}),
            })
            response = conn.getresponse()
            response.read()
            return response.status
        finally:
            conn.close()

    def test_unauthenticated_requests_rejected_for_every_endpoint(self):
        for endpoint in ("/check", "/grade", "/run", "/share"):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.request(endpoint), 401)

    def test_bad_bearer_token_rejected_for_every_endpoint(self):
        for endpoint in ("/check", "/grade", "/run", "/share"):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.request(endpoint, headers={
                    "Authorization": "Bearer invalid-test-token"
                }), 401)

    def test_cross_origin_request_rejected_before_dispatch(self):
        for endpoint in ("/check", "/grade", "/run", "/share"):
            with self.subTest(endpoint=endpoint):
                self.assertEqual(self.request(endpoint, headers={
                    "Origin": "https://attacker.example",
                }), 403)

    def test_oversized_json_body_rejected_before_dispatch(self):
        payload = json.dumps({"padding": "X" * (1024 * 1024 + 1)}).encode()
        self.assertEqual(self.request("/check", body=payload), 413)


if __name__ == "__main__":
    unittest.main()
