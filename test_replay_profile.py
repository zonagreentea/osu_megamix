import json
import tempfile
import unittest
from pathlib import Path

from profiles import ProfileStore
from replay import Replay


class ReplayTests(unittest.TestCase):
    def test_events_have_only_value_and_time(self):
        replay = Replay("player-1")
        replay.add_event({"action": "hit", "lane": 2}, 1.25)
        self.assertEqual(
            replay.events,
            [{"value": {"action": "hit", "lane": 2}, "time": 1.25}],
        )
        self.assertEqual(set(replay.events[0]), {"value", "time"})

    def test_coincident_events_keep_order(self):
        replay = Replay("player-1")
        replay.add_event("left", 1)
        replay.add_event("right", 1)
        self.assertEqual(
            [event["value"] for event in replay.events_at(1)],
            ["left", "right"],
        )

    def test_time_cannot_go_backwards(self):
        replay = Replay("player-1")
        replay.add_event("first", 2)
        with self.assertRaises(ValueError):
            replay.add_event("earlier", 1)

    def test_save_load_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "replays" / "play.json"
            original = Replay(
                "player-1",
                beatmap_id="map-1",
                result={"score": 1234},
                loadout={"keyblades": ["Kingdom Key"]},
            )
            original.add_event("hit", 0.5)
            original.add_event({"pause": True}, 1.0)
            original.save(path)
            loaded = Replay.load(path)
            self.assertEqual(loaded.to_dict(), original.to_dict())
            self.assertEqual(list(loaded.playback()), original.events)

    def test_rejects_non_json_event(self):
        replay = Replay("player-1")
        with self.assertRaises(TypeError):
            replay.add_event(object(), 0)


class ProfileTests(unittest.TestCase):
    def test_profile_inventory_and_play_history_persist(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profiles.json"
            store = ProfileStore(path)
            profile = store.create("Shizuka", "player-1")
            store.award_keyblade(profile["id"], "Kingdom Key")
            store.record_play(
                profile["id"],
                "replay-1",
                beatmap_id="map-1",
                result={"score": 9000},
            )

            reloaded = ProfileStore(path).get("player-1")
            self.assertEqual(reloaded["username"], "Shizuka")
            self.assertEqual(reloaded["keyblades"], ["Kingdom Key"])
            self.assertEqual(len(reloaded["plays"]), 1)
            self.assertEqual(reloaded["plays"][0]["replay_id"], "replay-1")

    def test_duplicate_keyblade_is_not_duplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ProfileStore(Path(directory) / "profiles.json")
            store.create("Shizuka", "player-1")
            store.award_keyblade("player-1", "Kingdom Key")
            store.award_keyblade("player-1", "Kingdom Key")
            self.assertEqual(
                store.get("player-1")["keyblades"],
                ["Kingdom Key"],
            )

    def test_unknown_profile_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ProfileStore(Path(directory) / "profiles.json")
            with self.assertRaises(KeyError):
                store.award_keyblade("missing", "Kingdom Key")


if __name__ == "__main__":
    unittest.main(verbosity=2)
