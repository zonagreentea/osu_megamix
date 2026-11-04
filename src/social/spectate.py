"""Opt-in, read-only spectating with validated, ordered snapshots."""

import json
import math
import threading


class SpectateError(ValueError):
    """A spectating request or snapshot violates the session policy."""


class SpectateHub:
    """In-memory spectating policy; transport authentication is external."""

    def __init__(self, max_snapshots=256):
        if isinstance(max_snapshots, bool) or not isinstance(max_snapshots, int):
            raise TypeError("max_snapshots must be an integer")
        if max_snapshots < 1:
            raise ValueError("max_snapshots must be positive")

        self.max_snapshots = max_snapshots
        self._opted_in = set()
        self._watchers = {}
        self._snapshots = {}
        self._lock = threading.RLock()

    def set_opt_in(self, target, enabled):
        if not isinstance(target, str) or not target.strip():
            raise SpectateError("target is required")
        if not isinstance(enabled, bool):
            raise SpectateError("opt-in must be a boolean")

        with self._lock:
            if enabled:
                self._opted_in.add(target)
                self._watchers.setdefault(target, set())
                self._snapshots.setdefault(target, [])
            else:
                self._opted_in.discard(target)
                self._watchers.pop(target, None)
                self._snapshots.pop(target, None)

    def watch(self, spectator, target):
        if not spectator or not target:
            raise SpectateError("spectator and target are required")
        if spectator == target:
            raise SpectateError("cannot spectate yourself")

        with self._lock:
            if target not in self._opted_in:
                raise SpectateError("target has not opted in")
            self._watchers.setdefault(target, set()).add(spectator)
            return self.latest(spectator, target)

    def unwatch(self, spectator, target):
        with self._lock:
            self._watchers.get(target, set()).discard(spectator)

    def publish(self, target, timestamp, state):
        if isinstance(timestamp, bool) or not isinstance(timestamp, (int, float)):
            raise SpectateError("timestamp must be numeric")
        if not math.isfinite(timestamp) or timestamp < 0:
            raise SpectateError("timestamp must be finite and non-negative")

        try:
            safe_state = json.loads(json.dumps(state, allow_nan=False))
        except (TypeError, ValueError) as exc:
            raise SpectateError("state must be JSON-compatible") from exc

        with self._lock:
            if target not in self._opted_in:
                raise SpectateError("target has not opted in")

            history = self._snapshots.setdefault(target, [])
            if history and timestamp < history[-1]["time"]:
                raise SpectateError("snapshot time cannot go backwards")

            snapshot = {"time": timestamp, "value": safe_state}
            history.append(snapshot)
            del history[:-self.max_snapshots]
            return json.loads(json.dumps(snapshot))

    def latest(self, spectator, target):
        with self._lock:
            self._require_access(spectator, target)
            history = self._snapshots.get(target, [])
            return json.loads(json.dumps(history[-1])) if history else None

    def history(self, spectator, target):
        with self._lock:
            self._require_access(spectator, target)
            return json.loads(json.dumps(self._snapshots.get(target, [])))

    def _require_access(self, spectator, target):
        if target not in self._opted_in:
            raise SpectateError("target has not opted in")
        if spectator not in self._watchers.get(target, set()):
            raise SpectateError("spectator has no active permission")
