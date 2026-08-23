from __future__ import annotations

from dataclasses import dataclass

from .clock import ClockSnapshot, TimelineClock


@dataclass(frozen=True)
class MovementSnapshot:
    start_ns: int
    landing_ns: int
    position: float
    complete: bool
    clock: ClockSnapshot


class TimelineMovement:
    """A movement occurring across the authoritative timeline."""

    def __init__(
        self,
        clock: TimelineClock,
        duration_ns: int,
    ) -> None:
        if duration_ns <= 0:
            raise ValueError("movement duration must be positive")

        self._clock = clock
        self._start_ns = clock.time_ns
        self._landing_ns = self._start_ns + duration_ns

    @property
    def start_ns(self) -> int:
        return self._start_ns

    @property
    def landing_ns(self) -> int:
        return self._landing_ns

    @property
    def complete(self) -> bool:
        return self._clock.time_ns >= self._landing_ns

    @property
    def position(self) -> float:
        elapsed = self._clock.time_ns - self._start_ns
        duration = self._landing_ns - self._start_ns

        if elapsed <= 0:
            return 0.0

        if elapsed >= duration:
            return 1.0

        return elapsed / duration

    def snapshot(self) -> MovementSnapshot:
        return MovementSnapshot(
            start_ns=self._start_ns,
            landing_ns=self._landing_ns,
            position=self.position,
            complete=self.complete,
            clock=self._clock.snapshot(),
        )
