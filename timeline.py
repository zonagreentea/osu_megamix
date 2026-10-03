import time

class Timeline:
    def __init__(self):
        self.started = time.monotonic_ns()

    def now(self):
        current = time.monotonic_ns()
        elapsed = current - self.started
        return elapsed
