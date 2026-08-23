from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .clock import ClockSnapshot, TimelineClock


class FlowState(Enum):
    FLOW = "flow"
    MOVEMENT = "movement"
    BREAK = "break"
    LANDING = "landing"
    HANDSHAKE = "handshake"


@dataclass(frozen=True)
class FlowSnapshot:
    state: FlowState
    clock: ClockSnapshot


class TimelineFlow:
    """Movement through the authoritative timeline."""

    def __init__(self, clock: TimelineClock) -> None:
        self._clock = clock
        self._state = FlowState.FLOW

    @property
    def state(self) -> FlowState:
        return self._state

    def snapshot(self) -> FlowSnapshot:
        return FlowSnapshot(
            state=self._state,
            clock=self._clock.snapshot(),
        )

    def enter_movement(self) -> None:
        self._state = FlowState.MOVEMENT

    def break_flow(self) -> None:
        self._state = FlowState.BREAK

    def land(self) -> None:
        self._state = FlowState.LANDING

    def handshake(self) -> None:
        self._state = FlowState.HANDSHAKE

    def continue_flow(self) -> None:
        self._state = FlowState.FLOW

