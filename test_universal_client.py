import unittest

from universal_client import ClientState, UniversalClient, load_plan_file


class UniversalClientTests(unittest.TestCase):
    def setUp(self):
        self.client = UniversalClient()

    def test_attachment_capabilities(self):
        self.client.attach("keyboard", "input", "keys")
        self.client.attach("screen", "view")
        self.assertEqual(
            [item.name for item in self.client.sources("input")],
            ["keyboard"],
        )
        self.assertEqual(
            [item.name for item in self.client.sources("view")],
            ["screen"],
        )

    def test_events_batch_by_timestamp(self):
        self.client.attach("keyboard", "input")
        self.client.capture("keyboard", {"key": "d"}, time=20)
        self.client.capture("keyboard", {"key": "f"}, time=10)
        self.client.capture("keyboard", {"key": "j"}, time=10)

        batch = self.client.dispatch_next()
        self.assertEqual([event.time for event in batch], [10, 10])
        self.assertEqual(len(self.client.events.pending), 1)
        self.assertEqual(self.client.dispatch_next()[0].time, 20)

    def test_rejects_non_input_source(self):
        self.client.attach("screen", "view")
        with self.assertRaises(ValueError):
            self.client.capture("screen", "click", time=1)

    def test_session_lifecycle(self):
        self.assertEqual(self.client.state, ClientState.READY)
        self.client.start()
        self.assertEqual(self.client.state, ClientState.RUNNING)
        with self.assertRaises(RuntimeError):
            self.client.start()
        self.client.stop()
        self.assertEqual(self.client.state, ClientState.STOPPED)

    def test_loads_real_generated_plan(self):
        plan = load_plan_file("/tmp/osu-megamix-plan.json")
        count = self.client.load_plan(plan)
        self.assertEqual(count, 6)
        self.assertTrue(self.client.snapshot()["plan_loaded"])

    def test_rejects_invalid_plan(self):
        with self.assertRaises(ValueError):
            self.client.load_plan({"format": "wrong", "segments": []})


    def test_playback_events_follow_one_timeline(self):
        from universal_client import load_plan_file

        client = UniversalClient()
        client.load_plan(load_plan_file("/tmp/osu-megamix-plan.json"))
        events = client.playback_events()

        mode_changes = [
            event for event in events
            if event.value["type"] == "mode_change"
        ]
        plan_events = [
            event for event in events
            if event.value["type"] == "plan_event"
        ]

        self.assertEqual(
            [(event.time, event.value["mode"]) for event in mode_changes],
            [(0, "osu"), (1000, "taiko"), (2000, "osu")],
        )
        self.assertEqual(
            [event.time for event in plan_events],
            [0, 500, 1000, 1500, 2000, 2500],
        )
        self.assertEqual(
            [event.time for event in events],
            sorted(event.time for event in events),
        )
        at_boundary = [
            event for event in events if event.time == 1000
        ]
        self.assertEqual(len(at_boundary), 2)


    def test_realtime_playback_uses_one_clock_and_batches(self):
        from universal_client import ClientState, load_plan_file

        client = UniversalClient()
        client.load_plan(load_plan_file("/tmp/osu-megamix-plan.json"))
        now = [0]
        batches = []

        def clock():
            return now[0]

        def sleeper(seconds):
            now[0] += round(seconds * 1_000_000_000)

        count = client.run_playback(
            batches.append, clock=clock, sleeper=sleeper
        )

        self.assertEqual(count, 6)
        self.assertEqual(
            [batch[0].time for batch in batches],
            [0, 500, 1000, 1500, 2000, 2500],
        )
        self.assertEqual(len(batches[2]), 2)
        self.assertEqual(client.state, ClientState.STOPPED)
        self.assertEqual(len(client.dispatched), 9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
