"""Shared-tick on/off bit assignments for input sources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


def s(events: tuple[object, ...] | list[object]) -> bool:
    """Return whether transition records share one tick and edge."""
    if not events:
        return False
    first = events[0]
    key = (first.tick, first.previous, first.current)
    return all(
        (event.tick, event.previous, event.current) == key
        for event in events
    )


@dataclass(frozen=True)
class BitTransition:
    """One input bit changing state at a shared logical tick."""

    source: str
    position: int
    previous: int
    current: int
    edge: str
    tick: int
    timestamp_ns: int
    mask_before: int
    mask_after: int


@dataclass(frozen=True)
class BitComparison:
    """The sampled on/off relationship between two assigned bits."""

    left_source: str
    right_source: str
    left: int
    right: int

    @property
    def same_state(self) -> bool:
        return self.left == self.right

    @property
    def both_on(self) -> bool:
        return self.left == self.right == 1

    @property
    def both_off(self) -> bool:
        return self.left == self.right == 0

    @property
    def xor(self) -> int:
        return self.left ^ self.right


class BitAssignments:
    """Assign one stable mask bit to each input source and track its edges."""

    def __init__(self) -> None:
        self._positions: dict[str, int] = {}
        self._states: dict[str, int] = {}
        self._mask = 0
        self._last_tick: int | None = None
        self._last_timestamp_ns: int | None = None

    def register(self, source: str) -> int:
        if not isinstance(source, str) or not source:
            raise ValueError("bit source must be a non-empty string")
        if source not in self._positions:
            self._positions[source] = len(self._positions)
            self._states[source] = 0
        return self._positions[source]

    def state(self, source: str) -> int:
        try:
            return self._states[source]
        except KeyError:
            raise KeyError(f"unregistered bit source: {source}") from None

    @property
    def mask(self) -> int:
        return self._mask

    def snapshot(self) -> dict[str, int]:
        return dict(self._states)

    @property
    def last_tick(self) -> int | None:
        return self._last_tick

    def assign(
        self,
        values: Mapping[str, int | bool],
        tick: int,
        timestamp_ns: int,
    ) -> tuple[BitTransition, ...]:
        """Apply one atomic bit sample at a discrete clock tick."""
        if not isinstance(values, Mapping):
            raise TypeError("bit assignments must be a mapping of source to 0/1")
        if isinstance(tick, bool) or not isinstance(tick, int) or tick < 0:
            raise TypeError("bit tick must be a non-negative integer")
        if isinstance(timestamp_ns, bool) or not isinstance(timestamp_ns, int):
            raise TypeError("bit timestamp_ns must be an integer")
        if timestamp_ns < 0:
            raise ValueError("bit timestamp_ns cannot be negative")
        if self._last_tick is not None:
            if tick < self._last_tick:
                raise ValueError("bit ticks must be non-decreasing")
            if tick == self._last_tick and timestamp_ns != self._last_timestamp_ns:
                raise ValueError("all assignments on one tick must share a timestamp")
            if tick > self._last_tick and timestamp_ns <= self._last_timestamp_ns:
                raise ValueError("timestamps must increase when the tick advances")

        normalized: dict[str, int] = {}
        for source, value in values.items():
            if source not in self._positions:
                raise KeyError(f"unregistered bit source: {source}")
            if isinstance(value, bool):
                normalized[source] = int(value)
            elif isinstance(value, int) and value in (0, 1):
                normalized[source] = value
            else:
                raise ValueError("bit values must be 0 or 1")

        mask_before = self._mask
        mask_after = mask_before
        for source, current in normalized.items():
            flag = 1 << self._positions[source]
            mask_after = mask_after | flag if current else mask_after & ~flag

        transitions = tuple(
            BitTransition(
                source=source,
                position=self._positions[source],
                previous=self._states[source],
                current=current,
                edge="rise" if current else "fall",
                tick=tick,
                timestamp_ns=timestamp_ns,
                mask_before=mask_before,
                mask_after=mask_after,
            )
            for source, current in normalized.items()
            if self._states[source] != current
        )

        self._states.update(normalized)
        self._mask = mask_after
        self._last_tick = tick
        self._last_timestamp_ns = timestamp_ns
        return transitions

    def compare(self, left_source: str, right_source: str) -> BitComparison:
        return BitComparison(
            left_source=left_source,
            right_source=right_source,
            left=self.state(left_source),
            right=self.state(right_source),
        )
