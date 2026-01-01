# Extracted from osu_megamix.py
from __future__ import annotations

class AudioPlayer:
    def __init__(self, path):
        self.path = path
        self.proc = None
        self.t0 = None

    def start(self):
        if not self.path:
            return False
        p = os.path.abspath(self.path)
        if not os.path.exists(p):
            return False

        # Hard truth: macOS afplay
        self.proc = subprocess.Popen(
            ["/usr/bin/afplay", "-q", p],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        self.t0 = time.perf_counter()
        return True

    def stop(self):
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
            self.proc = None

    def now_ms(self):
        if self.t0 is None:
            return int(time.perf_counter() * 1000)
        return int((time.perf_counter() - self.t0) * 1000)
