"""Bounded optional background work, isolated from gameplay scheduling.

Submit only trusted, non-gameplay tasks. Workers never access the event timeline.
"""
from concurrent.futures import Future, ThreadPoolExecutor
from threading import BoundedSemaphore


class BackgroundWork:
    """Run optional I/O off the gameplay thread with bounded queued work."""

    def __init__(self, workers=1, capacity=8):
        if isinstance(workers, bool) or not isinstance(workers, int) or workers < 1:
            raise ValueError("workers must be a positive integer")
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity < workers:
            raise ValueError("capacity must be an integer >= workers")
        self._slots = BoundedSemaphore(capacity)
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="megamix-bg")
        self._closed = False

    def submit(self, fn, *args, **kwargs):
        """Return a Future, or None when saturated; never wait for a free slot.

        Call from one owner thread, or synchronize concurrent submit/shutdown
        externally. Do not submit work that mutates gameplay state.
        """
        if self._closed:
            raise RuntimeError("background worker is closed")
        if not callable(fn):
            raise TypeError("fn must be callable")
        if not self._slots.acquire(blocking=False):
            return None
        try:
            future = self._pool.submit(fn, *args, **kwargs)
        except BaseException:
            self._slots.release()
            raise
        future.add_done_callback(lambda _future: self._slots.release())
        return future

    def shutdown(self, wait=True, cancel_futures=False):
        """Shut down outside the gameplay critical path."""
        self._closed = True
        self._pool.shutdown(wait=wait, cancel_futures=cancel_futures)
