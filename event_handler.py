
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Event:
    time: int
    value: Any


class EventHandler:
    def __init__(self):
        self.pending = []

    def submit(self, event: Event):
        self.pending.append(event)

    def next_batch(self):
        if not self.pending:
            return ()

        self.pending.sort(key=lambda event: event.time)

        time = self.pending[0].time
        batch = tuple(
            event for event in self.pending
            if event.time == time
        )

        self.pending = [
            event for event in self.pending
            if event.time != time
        ]

        return batch
