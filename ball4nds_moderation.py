from dataclasses import dataclass, field
import time


@dataclass
class ContentResult:
    allowed: bool
    action: str = "allow"
    reason: str = ""


@dataclass
class Ball4NDSModerator:
    flagged_players: set[str] = field(default_factory=set)
    muted_players: set[str] = field(default_factory=set)
    blocked_players: set[str] = field(default_factory=set)
    violations: dict[str, int] = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)

    prohibited: set[str] = field(default_factory=lambda: {
        "slur",
        "threat",
        "dox",
        "doxxing",
    })

    def check(self, player, content, content_type="text"):
        if player in self.blocked_players:
            return ContentResult(False, "block", "player blocked")

        if player in self.muted_players:
            return ContentResult(False, "mute", "player muted")

        text = (content or "").lower().strip()

        if any(word in text.split() for word in self.prohibited):
            return self.flag(
                player,
                content_type,
                "prohibited content",
            )

        return ContentResult(True)

    def flag(self, player, content_type, reason):
        self.flagged_players.add(player)
        self.violations[player] = self.violations.get(player, 0) + 1

        self.events.append({
            "player": player,
            "type": content_type,
            "reason": reason,
            "timestamp": time.monotonic(),
        })

        if self.violations[player] >= 3:
            self.muted_players.add(player)
            return ContentResult(False, "mute", reason)

        return ContentResult(False, "flag", reason)

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
            "flagged": player in self.flagged_players,
            "muted": player in self.muted_players,
            "blocked": player in self.blocked_players,
            "violations": self.violations.get(player, 0),
        }

    def audit_log(self):
        return list(self.events)


ball4nds_moderator = Ball4NDSModerator()
