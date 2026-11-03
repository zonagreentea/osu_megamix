"""Universal event capture, adjustment, and timed dispatch."""

from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from time import monotonic_ns
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class Event:
    """One value at one timestamp."""
    time: int
    value: Any


class EventHandler:
    """Dispatch events by timestamp, preserving submission order on ties."""

    def __init__(self):
        self._queue = []
        self._sequence = count()

    @property
    def pending(self) -> list[Event]:
        """Compatibility snapshot in original submission order.

        Reading this property costs O(n log n); the dispatch path does not.
        """
        return [event for _, _, event in sorted(self._queue, key=lambda item: item[1])]

    def capture(self, value: Any, time: Optional[int] = None) -> Event:
        """Capture a value, timestamping it unless time is supplied."""
        event = Event(
            time=monotonic_ns() if time is None else time,
            value=value,
        )
        self.submit(event)
        return event

    def adjust(
        self,
        event: Event,
        transform: Callable[[Any], Any],
    ) -> Event:
        """Transform an event's value without changing its timestamp."""
        return Event(time=event.time, value=transform(event.value))

    def submit(self, event: Event) -> None:
        """Queue an event without interpreting its value."""
        if not isinstance(event, Event):
            raise TypeError("submit expects an Event")
        heappush(self._queue, (event.time, next(self._sequence), event))

    def next_batch(self) -> tuple[Event, ...]:
        """Return all earliest-time events in stable submission order."""
        if not self._queue:
            return ()
        earliest = self._queue[0][0]
        batch = []
        while self._queue and self._queue[0][0] == earliest:
            batch.append(heappop(self._queue)[2])
        return tuple(batch)

    def dispatch(
        self,
        handler: Callable[[tuple[Event, ...]], Any],
    ) -> Any:
        """Process one simultaneous batch through the supplied handler."""
        batch = self.next_batch()
        if not batch:
            return None
        return handler(batch)

    def drain(
        self,
        handler: Callable[[tuple[Event, ...]], Any],
    ) -> tuple[Any, ...]:
        """Dispatch batches until the queue is empty."""
        results = []
        while self._queue:
            results.append(self.dispatch(handler))
        return tuple(results)
