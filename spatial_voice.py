from voice_moderation import VoiceModerator
from dataclasses import dataclass
from math import sqrt


@dataclass
class VoicePoint:
    x: float
    y: float
    z: float

    def distance_to(self, other):
        return sqrt(
            (self.x - other.x) ** 2
            + (self.y - other.y) ** 2
            + (self.z - other.z) ** 2
        )


@dataclass
class VoiceEmitter:
    player: str
    position: VoicePoint
    speaking: bool = False
    radius: float = 25.0

    def start(self):
        self.speaking = True

    def stop(self):
        self.speaking = False

    def volume_at(self, listener):
        if not self.speaking:
            return 0.0

        distance = self.position.distance_to(listener)

        if distance >= self.radius:
            return 0.0

        return max(0.0, 1.0 - (distance / self.radius))

    def audio_point(self):
        return {
            "player": self.player,
            "position": {
                "x": self.position.x,
                "y": self.position.y,
                "z": self.position.z,
            },
            "speaking": self.speaking,
            "radius": self.radius,
        }


@dataclass
class SpatialVoice:
    emitters: dict[str, VoiceEmitter]

    def __init__(self):
        self.emitters = {}
        self.moderator = VoiceModerator()

    def add_player(self, player, x=0.0, y=0.0, z=0.0, radius=25.0):
        self.emitters[player] = VoiceEmitter(
            player=player,
            position=VoicePoint(x, y, z),
            radius=radius,
        )

    def remove_player(self, player):
        self.emitters.pop(player, None)

    def move_player(self, player, x, y, z):
        emitter = self.emitters[player]
        emitter.position = VoicePoint(x, y, z)

    def start_speaking(self, player, transcript=None):
        result = self.moderator.check(player, transcript)

        if not result.allowed:
            self.emitters[player].stop()
            return result

        self.emitters[player].start()
        return result

    def stop_speaking(self, player):
        self.emitters[player].stop()

    def moderate(self, player, transcript=None):
        result = self.moderator.check(player, transcript)

        if not result.allowed:
            self.emitters[player].stop()

        return result

    def hear(self, listener):
        return {
            player: emitter.volume_at(listener)
            for player, emitter in self.emitters.items()
            if emitter.volume_at(listener) > 0.0
        }

    def points(self):
        return [emitter.audio_point() for emitter in self.emitters.values()]
