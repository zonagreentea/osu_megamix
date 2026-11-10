"""Regression tests for chronological, stable event scheduling."""

import unittest

from event_handler import Event, EventHandler


class EventSchedulerTests(unittest.TestCase):
    def test_empty(self):
        handler = EventHandler()
        self.assertEqual(handler.next_batch(), ())
        self.assertIsNone(handler.dispatch(lambda batch: batch))

    def test_out_of_order_and_ties(self):
        handler = EventHandler()
        for time, value in ((20, "later"), (10, "first"), (10, "second"), (5, "early")):
            handler.submit(Event(time, value))
        self.assertEqual([e.value for e in handler.pending],
                         ["later", "first", "second", "early"])
        self.assertEqual([e.value for e in handler.next_batch()], ["early"])
        self.assertEqual([e.value for e in handler.next_batch()], ["first", "second"])
        self.assertEqual([e.value for e in handler.next_batch()], ["later"])
        self.assertEqual(handler.next_batch(), ())

    def test_capture_adjust_and_drain(self):
        handler = EventHandler()
        original = handler.capture("a", time=7)
        changed = handler.adjust(original, str.upper)
        self.assertEqual(changed, Event(7, "A"))
        self.assertEqual(original, Event(7, "a"))
        handler.submit(changed)
        self.assertEqual(handler.drain(lambda batch: tuple(e.value for e in batch)),
                         (("a", "A"),))

    def test_reentrant_submission(self):
        handler = EventHandler()
        handler.submit(Event(1, "start"))

        def callback(batch):
            if batch[0].value == "start":
                handler.submit(Event(2, "next"))
            return batch[0].value

        self.assertEqual(handler.drain(callback), ("start", "next"))

    def test_invalid_event(self):
        with self.assertRaises(TypeError):
            EventHandler().submit("not an event")


if __name__ == "__main__":
    unittest.main()
