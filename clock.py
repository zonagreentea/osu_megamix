import time


class Clock:
    def __init__(self, source="monotonic"):
        sources = {
            "monotonic": time.monotonic_ns,
            "wall": time.time_ns,
        }

        if source not in sources:
            raise ValueError("Unknown clock source")

        self.source = source
        self._read = sources[source]
        self.start_ns = self._read()

    def now_ns(self):
        return self._read() - self.start_ns

    def now(self):
        return self.now_ns() / 1_000_000_000

    def timestamp_ns(self):
        return self._read()

    def reset(self):
        self.start_ns = self._read()
