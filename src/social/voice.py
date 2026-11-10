from dataclasses import dataclass, field


@dataclass
class VoiceChannel:
    enabled: bool = True
    muted: set[str] = field(default_factory=set)
    speaking: set[str] = field(default_factory=set)
    proximity: bool = False

    def join(self, player):
        self.muted.discard(player)

    def leave(self, player):
        self.muted.discard(player)
        self.speaking.discard(player)

    def mute(self, player):
        self.muted.add(player)
        self.speaking.discard(player)

    def unmute(self, player):
        self.muted.discard(player)

    def start_speaking(self, player):
        if self.enabled and player not in self.muted:
            self.speaking.add(player)

    def stop_speaking(self, player):
        self.speaking.discard(player)

    def status(self):
        return {
            "enabled": self.enabled,
            "proximity": self.proximity,
            "muted": sorted(self.muted),
            "speaking": sorted(self.speaking),
        }


def voice_for(mode):
    return VoiceChannel(
        enabled=True,
        proximity=(mode == "rp"),
    )
