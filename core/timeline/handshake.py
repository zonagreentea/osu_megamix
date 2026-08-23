from __future__ import annotations

from dataclasses import dataclass

from .clock import ClockSnapshot
from .sync import SynchronizedTransition


@dataclass(frozen=True)
class HandshakeSnapshot:
    accepted: bool
    left_ack: bool
    right_ack: bool
    transition: SynchronizedTransition
    clock: ClockSnapshot


class TimelineHandshake:
    """Two-sided acknowledgement of a synchronized transition."""

    def __init__(
        self,
        transition: SynchronizedTransition,
        clock_snapshot: ClockSnapshot,
    ) -> None:
        self._transition = transition
        self._clock_snapshot = clock_snapshot
        self._left_ack = False
        self._right_ack = False

    @property
    def accepted(self) -> bool:
        return self._left_ack and self._right_ack

    def acknowledge_left(self) -> None:
        self._left_ack = True

    def acknowledge_right(self) -> None:
        self._right_ack = True

    def snapshot(self) -> HandshakeSnapshot:
        return HandshakeSnapshot(
            accepted=self.accepted,
            left_ack=self._left_ack,
            right_ack=self._right_ack,
            transition=self._transition,
            clock=self._clock_snapshot,
        )
