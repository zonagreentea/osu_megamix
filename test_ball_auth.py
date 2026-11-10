import unittest
from ball_server import dispatch

SECRET = "test-secret-" + "x" * 40

class BallAuthenticationTests(unittest.TestCase):
    def test_valid_token(self):
        result = dispatch(
            {"action": "ping", "node": "alice", "token": SECRET},
            SECRET
        )
        self.assertEqual(result, {"ok": True, "message": "pong"})

    def test_invalid_token(self):
        result = dispatch(
            {"action": "ping", "node": "alice", "token": "wrong"},
            SECRET
        )
        self.assertFalse(result["ok"])

    def test_forbidden_execution(self):
        result = dispatch(
            {"action": "run", "node": "alice", "token": SECRET},
            SECRET
        )
        self.assertFalse(result["ok"])

    def test_forbidden_deletion(self):
        result = dispatch(
            {"action": "delete", "node": "alice", "token": SECRET},
            SECRET
        )
        self.assertFalse(result["ok"])

if __name__ == "__main__":
    unittest.main()
