"""Record, save, load, and replay timed gameplay events."""

import json
import math
import os
import tempfile
import uuid
from pathlib import Path


FORMAT_VERSION = 1


def _validate_time(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("event time must be an integer or float")
    if not math.isfinite(value) or value < 0:
        raise ValueError("event time must be finite and non-negative")
    return value


class Replay:
    """A play's metadata plus an ordered sequence of value/time events."""

    def __init__(
        self,
        player_id,
        beatmap_id=None,
        beatmap_version=None,
        play_id=None,
        result=None,
        loadout=None,
        events=None,
    ):
        if not isinstance(player_id, str) or not player_id:
            raise ValueError("player_id must be a non-empty string")

        self.play_id = play_id or str(uuid.uuid4())
        self.player_id = player_id
        self.beatmap_id = beatmap_id
        self.beatmap_version = beatmap_version
        self.result = result
        self.loadout = dict(loadout or {})
        self.events = []

        for event in events or ():
            self.add_event(event["value"], event["time"])

    def add_event(self, value, time):
        """Append one event containing exactly one value and one time."""
        time = _validate_time(time)

        if self.events and time < self.events[-1]["time"]:
            raise ValueError("event times must be non-decreasing")

        # Validate JSON compatibility now, rather than failing at save time.
        json.dumps(value, allow_nan=False)
        self.events.append({"value": value, "time": time})

    def events_at(self, time):
        """Return all events at a coincident timestamp, in insertion order."""
        time = _validate_time(time)
        return tuple(event for event in self.events if event["time"] == time)

    def playback(self):
        """Yield a copy of each recorded event in original order."""
        for event in self.events:
            yield {"value": event["value"], "time": event["time"]}

    def to_dict(self):
        return {
            "format_version": FORMAT_VERSION,
            "play_id": self.play_id,
            "player_id": self.player_id,
            "beatmap_id": self.beatmap_id,
            "beatmap_version": self.beatmap_version,
            "result": self.result,
            "loadout": self.loadout,
            "events": self.events,
        }

    def save(self, path):
        """Atomically save a replay as JSON."""
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            self.to_dict(),
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )

        fd, temporary = tempfile.mkstemp(
            prefix=f".{destination.name}.",
            suffix=".tmp",
            dir=str(destination.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(payload)
                stream.write("\n")
            os.replace(temporary, destination)
        except BaseException:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise

        return destination

    @classmethod
    def load(cls, path):
        with Path(path).open("r", encoding="utf-8") as stream:
            data = json.load(stream)

        if data.get("format_version") != FORMAT_VERSION:
            raise ValueError("unsupported replay format version")

        return cls(
            player_id=data["player_id"],
            beatmap_id=data.get("beatmap_id"),
            beatmap_version=data.get("beatmap_version"),
            play_id=data["play_id"],
            result=data.get("result"),
            loadout=data.get("loadout", {}),
            events=data.get("events", []),
        )
