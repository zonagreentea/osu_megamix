"""Persistent player profiles, play history, and keyblade inventory."""

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


class ProfileStore:
    """A small standard-library JSON profile store."""

    def __init__(self, path="profiles.json"):
        self.path = Path(path)
        self.profiles = {}
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as stream:
                data = json.load(stream)
            if data.get("format_version") != 1:
                raise ValueError("unsupported profile store version")
            self.profiles = data.get("profiles", {})

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {"format_version": 1, "profiles": self.profiles},
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
        fd, temporary = tempfile.mkstemp(
            prefix=f".{self.path.name}.",
            suffix=".tmp",
            dir=str(self.path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(payload)
                stream.write("\n")
            os.replace(temporary, self.path)
        except BaseException:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass
            raise

    def create(self, username, profile_id=None):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("username must not be empty")

        profile_id = profile_id or str(uuid.uuid4())
        if profile_id in self.profiles:
            raise ValueError("profile already exists")

        self.profiles[profile_id] = {
            "id": profile_id,
            "username": username.strip(),
            "keyblades": [],
            "plays": [],
        }
        self._save()
        return self.get(profile_id)

    def get(self, profile_id):
        profile = self.profiles.get(profile_id)
        if profile is None:
            return None
        # Return a copy so callers cannot silently mutate stored state.
        return json.loads(json.dumps(profile))

    def list_profiles(self):
        return [self.get(profile_id) for profile_id in self.profiles]

    def award_keyblade(self, profile_id, keyblade):
        profile = self._require(profile_id)
        if not isinstance(keyblade, str) or not keyblade.strip():
            raise ValueError("keyblade must not be empty")
        keyblade = keyblade.strip()
        if keyblade not in profile["keyblades"]:
            profile["keyblades"].append(keyblade)
            self._save()
        return self.get(profile_id)

    def record_play(self, profile_id, replay_id, beatmap_id=None, result=None):
        profile = self._require(profile_id)
        if not isinstance(replay_id, str) or not replay_id:
            raise ValueError("replay_id must be a non-empty string")

        play = {
            "play_id": str(uuid.uuid4()),
            "replay_id": replay_id,
            "beatmap_id": beatmap_id,
            "result": result,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }
        profile["plays"].append(play)
        self._save()
        return json.loads(json.dumps(play))

    def _require(self, profile_id):
        try:
            return self.profiles[profile_id]
        except KeyError:
            raise KeyError(f"unknown profile: {profile_id}") from None
