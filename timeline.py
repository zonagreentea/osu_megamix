import time

class Timeline:
    def __init__(self):
        self.start_ns = time.monotonic_ns()

    def now_ns(self):
        return time.monotonic_ns() - self.start_ns

    def now(self):
        return self.now_ns() / 1_000_000_000
