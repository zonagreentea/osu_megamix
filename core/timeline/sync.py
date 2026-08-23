from __future__ import annotations

from dataclasses import dataclass

from .clock import ClockSnapshot, TimelineClock


@dataclass(frozen=True)
class SynchronizedTransition:
    """Shared temporal contract for a synchronized jump."""

    break_ns: int
    generation: int

    @property
    def return_ns(self) -> int:
        """The jump always returns to the break anchor."""
        return self.break_ns


@dataclass(frozen=True)
class SyncSnapshot:
    transition: SynchronizedTransition
    clock: ClockSnapshot


class TimelineSync:
    """Coordinates synchronized departure and return."""

    def __init__(self, clock: TimelineClock) -> None:
        self._clock = clock
        self._transition: SynchronizedTransition | None = None

    def break_now(self) -> SynchronizedTransition:
        snapshot = self._clock.snapshot()

        self._transition = SynchronizedTransition(
            break_ns=snapshot.time_ns,
            generation=snapshot.generation,
        )

        return self._transition

    def snapshot(self) -> SyncSnapshot | None:
        if self._transition is None:
            return None

        return SyncSnapshot(
            transition=self._transition,
            clock=self._clock.snapshot(),
        )

    def synchronized(
        self,
        left: SynchronizedTransition,
        right: SynchronizedTransition,
    ) -> bool:
        return (
            left.break_ns == right.break_ns
            and left.generation == right.generation
            and left.return_ns == right.return_ns
        )
