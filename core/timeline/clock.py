from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import time


# POLIFY:
# The engine treats its smallest representable temporal quantum as fundamental.
# Master time is therefore an integer count of nanoseconds from clock origin.
QUANTUM_NS = 1


class ClockState(str, Enum):
    STOPPED = "stopped"
    RUNNING = "running"


@dataclass(frozen=True)
class ClockSnapshot:
    time_ns: int
    generation: int
    state: ClockState

    @property
    def time_s(self) -> float:
        return self.time_ns / 1_000_000_000


class TimelineClock:
    """Authoritative monotonic, integer-quantized master clock.

    Invariant:
        time_ns is monotonically non-decreasing while the clock exists.
        The clock never waits for downstream systems.
    """

    def __init__(self, *, clock=time.monotonic_ns) -> None:
        self._clock = clock
        self._wall_origin_ns = None
        self._wall_offset_ns = 0
        self._origin_ns: int | None = None
        self._offset_ns = 0
        self._last_ns = 0
        self._generation = 0
        self._state = ClockState.STOPPED

    def start(self) -> None:
        if self._state is ClockState.RUNNING:
            return

        now = self._clock()

        if self._wall_origin_ns is None:
            # Calibrate wall time against the monotonic source.
            # Pick the tightest bracket to minimize origin uncertainty.
            best = None
            for _ in range(32):
                mono_a = time.monotonic_ns()
                wall = time.time_ns()
                mono_b = time.monotonic_ns()
                span = mono_b - mono_a

                if best is None or span < best[0]:
                    best = (span, wall, (mono_a + mono_b) // 2)

            _, wall, mono = best
            self._wall_origin_ns = wall
            self._wall_offset_ns = wall - mono

        if self._origin_ns is None:
            self._origin_ns = now - self._offset_ns
        else:
            self._origin_ns = now - self._offset_ns

        self._state = ClockState.RUNNING
        self._generation += 1

    def stop(self) -> None:
        if self._state is ClockState.STOPPED:
            return

        self._offset_ns = self.now()
        self._state = ClockState.STOPPED
        self._generation += 1

    def now(self) -> int:
        if self._state is ClockState.STOPPED:
            return self._last_ns

        assert self._origin_ns is not None

        elapsed = self._clock() - self._origin_ns
        if elapsed < self._last_ns:
            elapsed = self._last_ns

        self._last_ns = elapsed // QUANTUM_NS * QUANTUM_NS
        return self._last_ns

    def advance(self, delta_ns: int) -> int:
        """Deterministic/manual advancement for tests and simulation."""
        if delta_ns < 0:
            raise ValueError("delta_ns must be non-negative")

        self._last_ns += delta_ns
        if self._state is ClockState.RUNNING and self._origin_ns is not None:
            self._origin_ns = self._clock() - self._last_ns

        return self._last_ns

    def wall_time_ns(self) -> int:
        if self._wall_origin_ns is None:
            raise RuntimeError("clock must be started before wall_time_ns()")

        return time.monotonic_ns() + self._wall_offset_ns

    def wall_datetime(self):
        from datetime import datetime, timezone
        return datetime.fromtimestamp(
            self.wall_time_ns() / 1_000_000_000,
            tz=timezone.utc,
        ).astimezone()

    def snapshot(self) -> ClockSnapshot:
        return ClockSnapshot(
            time_ns=self.now(),
            generation=self._generation,
            state=self._state,
        )

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def state(self) -> ClockState:
        return self._state
