import time

class Timeline:

    def __init__(self):
        self.started = time.monotonic_ns()

    def now(self):
        return (time.monotonic_ns() - self.started) / 1_000_000_000
