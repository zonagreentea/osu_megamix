from dataclasses import dataclass, field
import time


@dataclass
class ModerationResult:
    allowed: bool
    reason: str = ""
    action: str = "allow"


@dataclass
class Moderator:
    blocked_players: set[str] = field(default_factory=set)
    muted_players: set[str] = field(default_factory=set)
    violations: dict[str, int] = field(default_factory=dict)
    last_action: dict[str, float] = field(default_factory=dict)

    prohibited: set[str] = field(default_factory=lambda: {
        "slur",
        "threat",
        "dox",
        "doxxing",
    })

    def check(self, player, content):
        if player in self.blocked_players:
            return ModerationResult(False, "player blocked", "block")

        if player in self.muted_players:
            return ModerationResult(False, "player muted", "mute")

        text = (content or "").lower().strip()

        if any(word in text.split() for word in self.prohibited):
            self.record_violation(player)
            return ModerationResult(False, "prohibited content", "mute")

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


moderator = Moderator()
