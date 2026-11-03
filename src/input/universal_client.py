#!/usr/bin/env python3
"""Universal, hardware-agnostic client core for osu!megamix."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from time import monotonic_ns, sleep
from typing import Callable
from typing import Any, Dict, FrozenSet, Optional

from event_handler import Event, EventHandler


class ClientState(str, Enum):
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"


@dataclass(frozen=True)
class ClientAttachment:
    name: str
    capabilities: FrozenSet[str] = frozenset()
    metadata: Dict[str, Any] = field(default_factory=dict)


class UniversalClient:
    """Coordinate attachments, session state, plans, and timestamped events."""

    def __init__(self) -> None:
        self.state = ClientState.READY
        self.events = EventHandler()
        self.attachments: Dict[str, ClientAttachment] = {}
        self.plan: Optional[Dict[str, Any]] = None
        self.dispatched: list[Event] = []

    def attach(
        self,
        name: str,
        *capabilities: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ClientAttachment:
        if not name:
            raise ValueError("Attachment name cannot be empty.")
        if name in self.attachments:
            raise ValueError(f"Attachment already exists: {name}")
        if not capabilities or any(not item for item in capabilities):
            raise ValueError("At least one valid capability is required.")

        attachment = ClientAttachment(
            name=name,
            capabilities=frozenset(capabilities),
            metadata=dict(metadata or {}),
        )
        self.attachments[name] = attachment
        return attachment

    def detach(self, name: str) -> Optional[ClientAttachment]:
        return self.attachments.pop(name, None)

    def sources(self, capability: str) -> tuple[ClientAttachment, ...]:
        return tuple(
            item for item in self.attachments.values()
            if capability in item.capabilities
        )

    def load_plan(self, plan: dict[str, Any]) -> int:
        if not isinstance(plan, dict):
            raise TypeError("Plan must be a dictionary.")
        if plan.get("format") != "osu_megamix_generation_v1":
            raise ValueError("Unsupported generation-plan format.")

        segments = plan.get("segments")
        duration = plan.get("duration_ms")
        if not isinstance(segments, list):
            raise ValueError("Plan segments must be a list.")
        if not isinstance(duration, (int, float)) or isinstance(duration, bool):
            raise ValueError("Plan duration must be numeric.")
        if duration < 0:
            raise ValueError("Plan duration cannot be negative.")

        event_count = 0
        previous_end = 0

        for segment in segments:
            if not isinstance(segment, dict):
                raise ValueError("Each segment must be an object.")
            start = segment.get("timeline_start")
            end = segment.get("timeline_end")
            objects = segment.get("objects")
            mode = segment.get("mode")

            if not isinstance(mode, str) or not mode:
                raise ValueError("Each segment needs a mode.")
            if not isinstance(start, (int, float)) or isinstance(start, bool):
                raise ValueError("Segment start must be numeric.")
            if not isinstance(end, (int, float)) or isinstance(end, bool):
                raise ValueError("Segment end must be numeric.")
            if start < previous_end or end < start or end > duration:
                raise ValueError("Segment timeline is invalid.")
            if not isinstance(objects, list):
                raise ValueError("Segment objects must be a list.")

            for obj in objects:
                if not isinstance(obj, dict):
                    raise ValueError("Each plan event must be an object.")
                time = obj.get("time")
                if not isinstance(time, (int, float)) or isinstance(time, bool):
                    raise ValueError("Each plan event needs a numeric time.")
                if time < start or time > end:
                    raise ValueError("Plan event falls outside its segment.")
                event_count += 1

            previous_end = end

        self.plan = plan
        return event_count

    def start(self) -> None:
        if self.state == ClientState.RUNNING:
            raise RuntimeError("Client session is already running.")
        self.state = ClientState.RUNNING

    def stop(self) -> None:
        self.state = ClientState.STOPPED

    def capture(self, source: str, value: Any, time: Optional[int] = None) -> Event:
        attachment = self.attachments.get(source)
        if attachment is None:
            raise ValueError(f"Unknown attachment: {source}")
        if "input" not in attachment.capabilities:
            raise ValueError(f"Attachment cannot provide input: {source}")
        return self.events.capture(value, time=time)

    def dispatch_next(self) -> tuple[Event, ...]:
        """Dispatch the earliest timestamp and retain coincident event order."""
        batch = self.events.next_batch()
        self.dispatched.extend(batch)
        return batch

    def playback_events(self) -> tuple[Event, ...]:
        """Build a stable, timestamp-ordered stream from the loaded plan.

        This method is deterministic and does not sleep. A real-time runner
        can use the event timestamps against one monotonic session clock.
        """
        if self.plan is None:
            raise RuntimeError("Load a plan before preparing playback.")

        timeline = []
        order = 0

        for segment in self.plan["segments"]:
            timeline.append((
                segment["timeline_start"],
                order,
                {"type": "mode_change", "mode": segment["mode"]},
            ))
            order += 1

            for item in segment["objects"]:
                timeline.append((item["time"], order, {
                    "type": "plan_event",
                    "mode": segment["mode"],
                    "event": dict(item),
                }))
                order += 1

        timeline.sort(key=lambda entry: (entry[0], entry[1]))
        return tuple(
            Event(value=value, time=int(timestamp))
            for timestamp, _, value in timeline
        )

    def run_playback(
        self,
        handler: Callable[[tuple[Event, ...]], Any],
        *,
        clock: Optional[Callable[[], int]] = None,
        sleeper: Optional[Callable[[float], Any]] = None,
    ) -> int:
        """Dispatch plan events against one monotonic real-time clock."""
        if self.plan is None:
            raise RuntimeError("Load a plan before starting playback.")
        if self.state == ClientState.RUNNING:
            raise RuntimeError("Client session is already running.")

        clock = clock or monotonic_ns
        sleeper = sleeper or sleep
        timeline = self.playback_events()
        started_ns = clock()
        self.start()
        batches = 0

        try:
            index = 0
            while index < len(timeline):
                timestamp_ms = timeline[index].time
                end = index + 1
                while end < len(timeline) and timeline[end].time == timestamp_ms:
                    end += 1

                deadline_ns = started_ns + int(timestamp_ms * 1_000_000)
                while True:
                    remaining_ns = deadline_ns - clock()
                    if remaining_ns <= 0:
                        break
                    sleeper(remaining_ns / 1_000_000_000)

                batch = timeline[index:end]
                self.dispatched.extend(batch)
                handler(batch)
                batches += 1
                index = end
        finally:
            self.stop()

        return batches

    def snapshot(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "attachments": tuple(self.attachments),
            "input_sources": tuple(item.name for item in self.sources("input")),
            "plan_loaded": self.plan is not None,
            "pending_events": len(self.events.pending),
            "dispatched_events": len(self.dispatched),
        }


def load_plan_file(path: Any) -> Dict[str, Any]:
    """Load a generated plan from JSON without third-party dependencies."""
    import json

    return json.loads(Path(path).read_text(encoding="utf-8"))
