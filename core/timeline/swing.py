from __future__ import annotations

from dataclasses import dataclass

from .clock import ClockSnapshot, TimelineClock
from .handshake import TimelineHandshake
from .sync import SynchronizedTransition, TimelineSync


@dataclass(frozen=True)
class SwingSnapshot:
    transition: SynchronizedTransition
    handshake_accepted: bool
    complete: bool
    clock: ClockSnapshot


class TimelineSwing:
    """Atomic synchronized swing through the timeline."""

    def __init__(self, clock: TimelineClock) -> None:
        self._clock = clock
        self._sync = TimelineSync(clock)

        self._transition: SynchronizedTransition | None = None
        self._handshake: TimelineHandshake | None = None

    def begin(self) -> SynchronizedTransition:
        if self._transition is not None:
            raise RuntimeError("swing already active")

        self._transition = self._sync.break_now()

        self._handshake = TimelineHandshake(
            self._transition,
            self._clock.snapshot(),
        )

        return self._transition

    def acknowledge_left(self) -> None:
        self._require_active()
        self._handshake.acknowledge_left()

    def acknowledge_right(self) -> None:
        self._require_active()
        self._handshake.acknowledge_right()

    @property
    def complete(self) -> bool:
        return (
            self._handshake is not None
            and self._handshake.accepted
        )

    def snapshot(self) -> SwingSnapshot:
        self._require_active()

        return SwingSnapshot(
            transition=self._transition,
            handshake_accepted=self._handshake.accepted,
            complete=self.complete,
            clock=self._clock.snapshot(),
        )

    def _require_active(self) -> None:
        if self._transition is None or self._handshake is None:
            raise RuntimeError("swing has not begun")
