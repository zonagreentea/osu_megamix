"""Universal event capture, adjustment, and timed dispatch."""

from dataclasses import dataclass
from time import monotonic_ns
from typing import Any, Callable, Optional


@dataclass(frozen=True)
class Event:
    """One value at one timestamp."""
    time: int
    value: Any


class EventHandler:
    """Capture values, adjust them, and dispatch coincident events together."""

    def __init__(self):
        self.pending: list[Event] = []

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
        self.pending.append(event)

    def next_batch(self) -> tuple[Event, ...]:
        """Return all earliest-time events in stable submission order."""
        if not self.pending:
            return ()

        earliest = min(event.time for event in self.pending)
        batch = tuple(
            event for event in self.pending
            if event.time == earliest
        )
        self.pending = [
            event for event in self.pending
            if event.time != earliest
        ]
        return batch

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
        while self.pending:
            results.append(self.dispatch(handler))
        return tuple(results)
