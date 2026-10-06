from __future__ import annotations

from dataclasses import dataclass

from input import InputEvent, process_value


@dataclass(frozen=True)
class TabletEvent:
    x: float
    y: float
    pressure: float = 0.0
    touching: bool = False
    action: int | None = None


def process(event: TabletEvent) -> list[InputEvent]:
    """Reduce tablet state to the universal input layer."""
    return process_value(
        1.0 if event.touching else event.pressure,
        source="tablet",
        threshold=0.01,
        action=event.action,
    )


def position(event: TabletEvent) -> tuple[float, float]:
    return (
        max(0.0, min(1.0, event.x)),
        max(0.0, min(1.0, event.y)),
    )


def stream(events):
    for event in events:
        yield from process(event)


if __name__ == "__main__":
    event = TabletEvent(
        x=0.5,
        y=0.5,
        pressure=1.0,
        touching=True,
    )

    result = process(event)

    print(
        "tablet: PASS"
        if result and result[0].source == "tablet" and result[0].pressed
        else "tablet: FAIL"
    )
