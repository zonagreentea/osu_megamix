from __future__ import annotations

from dataclasses import dataclass

from .clock import ClockSnapshot, TimelineClock


@dataclass(frozen=True)
class ReturnSnapshot:
    anchor_ns: int
    position: float
    returned: bool
    clock: ClockSnapshot


class TimelineReturn:
    """A jump that always returns to its synchronized break anchor."""

    def __init__(
        self,
        clock: TimelineClock,
        anchor_ns: int,
        duration_ns: int,
    ) -> None:
        if anchor_ns < 0:
            raise ValueError("return anchor cannot be negative")

        if duration_ns <= 0:
            raise ValueError("return duration must be positive")

        self._clock = clock
        self._anchor_ns = anchor_ns
        self._start_ns = clock.time_ns
        self._duration_ns = duration_ns

    @property
    def anchor_ns(self) -> int:
        return self._anchor_ns

    @property
    def position(self) -> float:
        elapsed = self._clock.time_ns - self._start_ns

        if elapsed <= 0:
            return 0.0

        if elapsed >= self._duration_ns:
            return 1.0

        return elapsed / self._duration_ns

    @property
    def returned(self) -> bool:
        return self._clock.time_ns >= (
            self._start_ns + self._duration_ns
        )

    def snapshot(self) -> ReturnSnapshot:
        return ReturnSnapshot(
            anchor_ns=self._anchor_ns,
            position=self.position,
            returned=self.returned,
            clock=self._clock.snapshot(),
        )
