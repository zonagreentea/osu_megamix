from __future__ import annotations

from dataclasses import dataclass

NANOSECOND = 1
SECOND = 1_000_000_000


@dataclass(frozen=True)
class ClockSnapshot:
    time_ns: int
    running: bool
    generation: int

    @property
    def seconds(self) -> float:
        return self.time_ns / SECOND


class TimelineClock:
    """Authoritative timeline clock."""

    def __init__(self, time_ns: int = 0) -> None:
        if time_ns < 0:
            raise ValueError("timeline time cannot be negative")

        self._time_ns = time_ns
        self._running = False
        self._generation = 0

    @property
    def time_ns(self) -> int:
        return self._time_ns

    @property
    def running(self) -> bool:
        return self._running

    @property
    def generation(self) -> int:
        return self._generation

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def advance(self, delta_ns: int) -> int:
        if delta_ns < 0:
            raise ValueError("clock cannot advance backwards")

        if self._running:
            self._time_ns += delta_ns

        return self._time_ns

    def seek(self, time_ns: int) -> int:
        if time_ns < 0:
            raise ValueError("timeline time cannot be negative")

        self._time_ns = time_ns
        self._generation += 1

        return self._time_ns

    def snapshot(self) -> ClockSnapshot:
        return ClockSnapshot(
            time_ns=self._time_ns,
            running=self._running,
            generation=self._generation,
        )


def clocks_aligned(
    left: ClockSnapshot,
    right: ClockSnapshot,
) -> bool:
    return (
        left.time_ns == right.time_ns
        and left.generation == right.generation
    )
