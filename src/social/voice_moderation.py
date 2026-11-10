from dataclasses import dataclass, field
import time


@dataclass
class ModerationResult:
    allowed: bool
    reason: str = ""
    action: str = "allow"


@dataclass
class VoiceModerator:
    blocked_players: set[str] = field(default_factory=set)
    muted_players: set[str] = field(default_factory=set)
    violations: dict[str, int] = field(default_factory=dict)
    last_action: dict[str, float] = field(default_factory=dict)

    def check(self, player, transcript=None):
        if player in self.blocked_players:
            return ModerationResult(False, "player blocked", "block")

        if player in self.muted_players:
            return ModerationResult(False, "player muted", "mute")

        if transcript:
            text = transcript.lower().strip()

            prohibited = {
                "slur",
                "threat",
                "dox",
                "doxxing",
            }

            if any(word in text.split() for word in prohibited):
                self.record_violation(player)
                return ModerationResult(
                    False,
                    "prohibited speech",
                    "mute",
                )

        return ModerationResult(True)

    def record_violation(self, player):
        self.violations[player] = self.violations.get(player, 0) + 1
        self.last_action[player] = time.monotonic()

        if self.violations[player] >= 3:
            self.muted_players.add(player)

    def mute(self, player):
        self.muted_players.add(player)

    def unmute(self, player):
        self.muted_players.discard(player)

    def block(self, player):
        self.blocked_players.add(player)

    def unblock(self, player):
        self.blocked_players.discard(player)

    def status(self, player):
        return {
            "player": player,
            "muted": player in self.muted_players,
            "blocked": player in self.blocked_players,
            "violations": self.violations.get(player, 0),
        }
