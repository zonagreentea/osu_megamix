"""Replay optimization regression tests."""
import json
import tempfile
import unittest
from pathlib import Path
from replay import Replay

class ReplayStorageTests(unittest.TestCase):
    def test_lookup(self):
        r = Replay("player")
        for t, v in [(1, "a"), (2, "b"), (2, "c"), (4, "d")]:
            r.add_event(v, t)
        self.assertEqual([e["value"] for e in r.events_at(2)], ["b", "c"])
        self.assertEqual(r.events_at(3), ())

    def test_compact_roundtrip(self):
        r = Replay("player")
        for i in range(100):
            r.add_event({"key": "K1", "down": bool(i % 2)}, i / 10)
        with tempfile.TemporaryDirectory() as d:
            pretty, compact = Path(d) / "pretty.json", Path(d) / "compact.json"
            r.save(pretty)
            r.save(compact, compact=True)
            self.assertLess(compact.stat().st_size, pretty.stat().st_size)
            self.assertEqual(json.loads(pretty.read_text()), json.loads(compact.read_text()))
            self.assertEqual(list(Replay.load(compact).playback()), list(r.playback()))

if __name__ == "__main__":
    unittest.main()
