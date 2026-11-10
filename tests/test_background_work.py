"""Background work must not block event scheduling."""
import threading
import unittest
from background_work import BackgroundWork
from event_handler import Event, EventHandler


class BackgroundWorkTests(unittest.TestCase):
    def test_saturation_does_not_block_gameplay(self):
        started = threading.Event()
        release = threading.Event()
        def slow():
            started.set()
            release.wait(timeout=2)
            return "done"
        worker = BackgroundWork(workers=1, capacity=1)
        try:
            future = worker.submit(slow)
            self.assertTrue(started.wait(timeout=2))
            self.assertIsNone(worker.submit(lambda: "skipped"))
            timeline = EventHandler()
            timeline.submit(Event(1, "hit"))
            self.assertEqual(timeline.next_batch(), (Event(1, "hit"),))
        finally:
            release.set()
            worker.shutdown()
        self.assertEqual(future.result(), "done")

    def test_error_and_reuse(self):
        worker = BackgroundWork(workers=1, capacity=1)
        try:
            def fail():
                raise ValueError("expected")
            future = worker.submit(fail)
            with self.assertRaises(ValueError):
                future.result(timeout=2)
            self.assertEqual(worker.submit(lambda: 42).result(timeout=2), 42)
        finally:
            worker.shutdown()
        with self.assertRaises(RuntimeError):
            worker.submit(lambda: None)


if __name__ == "__main__":
    unittest.main()
