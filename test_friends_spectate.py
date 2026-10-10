import unittest

from spectate import SpectateError, SpectateHub


class SpectateTests(unittest.TestCase):
    def setUp(self):
        self.hub = SpectateHub(max_snapshots=2)

    def test_spectating_requires_target_opt_in(self):
        with self.assertRaises(SpectateError):
            self.hub.watch("viewer", "player")

    def test_opt_in_watch_and_read_latest_snapshot(self):
        self.hub.set_opt_in("player", True)
        self.assertIsNone(self.hub.watch("viewer", "player"))
        self.hub.publish("player", 1, {"score": 10})
        self.assertEqual(
            self.hub.latest("viewer", "player"),
            {"time": 1, "value": {"score": 10}},
        )

    def test_spectator_cannot_read_without_watching(self):
        self.hub.set_opt_in("player", True)
        with self.assertRaises(SpectateError):
            self.hub.latest("stranger", "player")

    def test_unwatch_revokes_read_access(self):
        self.hub.set_opt_in("player", True)
        self.hub.watch("viewer", "player")
        self.hub.unwatch("viewer", "player")
        with self.assertRaises(SpectateError):
            self.hub.history("viewer", "player")

    def test_opt_out_removes_history_and_access(self):
        self.hub.set_opt_in("player", True)
        self.hub.watch("viewer", "player")
        self.hub.publish("player", 1, {"score": 10})
        self.hub.set_opt_in("player", False)
        with self.assertRaises(SpectateError):
            self.hub.latest("viewer", "player")

    def test_snapshots_must_be_ordered_and_bounded(self):
        self.hub.set_opt_in("player", True)
        self.hub.watch("viewer", "player")
        self.hub.publish("player", 1, {"score": 1})
        self.hub.publish("player", 2, {"score": 2})
        self.hub.publish("player", 3, {"score": 3})
        self.assertEqual(
            [item["time"] for item in self.hub.history("viewer", "player")],
            [2, 3],
        )
        with self.assertRaises(SpectateError):
            self.hub.publish("player", 2, {"score": 0})

    def test_invalid_snapshots_are_rejected(self):
        self.hub.set_opt_in("player", True)
        with self.assertRaises(SpectateError):
            self.hub.publish("player", float("nan"), {})
        with self.assertRaises(SpectateError):
            self.hub.publish("player", 1, {"bad": object()})


if __name__ == "__main__":
    unittest.main()
