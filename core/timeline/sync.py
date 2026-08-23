from __future__ import annotations

from dataclasses import dataclass

from .clock import ClockSnapshot, TimelineClock


@dataclass(frozen=True)
class SynchronizedBreak:
    time_ns: int
    generation: int


@dataclass(frozen=True)
class SyncSnapshot:
    break_event: SynchronizedBreak
    clock: ClockSnapshot


class TimelineSync:
    """Coordinates simultaneous breaks on the authoritative clock."""

    def __init__(self, clock: TimelineClock) -> None:
        self._clock = clock
        self._break: SynchronizedBreak | None = None

    def break_now(self) -> SynchronizedBreak:
        snapshot = self._clock.snapshot()

        self._break = SynchronizedBreak(
            time_ns=snapshot.time_ns,
            generation=snapshot.generation,
        )

        return self._break

    def snapshot(self) -> SyncSnapshot | None:
        if self._break is None:
            return None

        return SyncSnapshot(
            break_event=self._break,
            clock=self._clock.snapshot(),
        )

    def synchronized(
        self,
        left: SynchronizedBreak,
        right: SynchronizedBreak,
    ) -> bool:
        return (
            left.time_ns == right.time_ns
            and left.generation == right.generation
        )
