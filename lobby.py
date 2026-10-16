from portrayal_policy import validate_portrayal
from voice import voice_for
from dataclasses import dataclass, field


@dataclass
class Lobby:
    mode: str
    players: list[str] = field(default_factory=list)
    voice_chat: bool = True
    proximity_voice: bool = False
    started: bool = False
    voice: object = None

    def join(self, player):
        self.voice = self.voice or voice_for(self.mode)
        self.voice.join(player)
        if player not in self.players:
            self.players.append(player)

    def leave(self, player):
        if player in self.players:
            self.players.remove(player)

    def start(self):
        self.started = True
        self.voice = voice_for(self.mode)
        return self.enter_gameplay()

    def rejoin(self, player):
        if self.mode in {"megamix", "collection"}:
            self.join(player)
            return self.enter_gameplay(restart=True)

        self.join(player)
        self.voice = self.voice or voice_for(self.mode)
        self.voice.join(player)
        return self.enter_gameplay()

    def enter_gameplay(self, restart=False):
        return {
            "mode": self.mode,
            "gameplay": True,
            "restart_from_start": restart,
            "voice_chat": self.voice_chat,
            "proximity_voice": self.proximity_voice,
            "players": list(self.players),
        }


class RegularLobby(Lobby):
    def __init__(self):
        super().__init__("regular")


class MegamixLobby(Lobby):
    def __init__(self):
        super().__init__("megamix")


class CollectionLobby(Lobby):
    def __init__(self):
        super().__init__("collection")


class RPLobby(Lobby):
    def __init__(self):
        super().__init__("rp", proximity_voice=True)

    def create_character(
        self,
        player,
        character,
        *,
        fictional=None,
        real_people=None,
        scope="rp character portrayal",
        consents=(),
    ):
        """Create a character only after its portrayal category is explicit."""
        validate_portrayal(character)
        from portrayal_consent import authorize_portrayal

        if isinstance(character, dict):
            if fictional is None and "fictional" in character:
                fictional = character["fictional"]
            if real_people is None and "real_people" in character:
                real_people = character["real_people"]
            scope = character.get("scope", scope)

        if real_people is not None:
            if isinstance(real_people, str):
                real_people = (real_people,)
            else:
                real_people = tuple(real_people)
            if fictional is True:
                raise ValueError(
                    "Character cannot be both fictional and a real-person portrayal."
                )
            if not authorize_portrayal(real_people, scope, tuple(consents)):
                raise PermissionError(
                    "Real-person portrayal requires explicit, active consent "
                    "for every person and this exact scope."
                )
        elif fictional is not True:
            raise ValueError(
                "Explicitly classify the character as fictional=True or "
                "provide real_people and matching consents."
            )

        self.join(player)
        return {
            "mode": "rp",
            "character_created": True,
            "player": player,
            "character": character,
            "gameplay": True,
            "voice_chat": self.voice_chat,
            "proximity_voice": self.proximity_voice,
        }


def create_lobby(mode):
    lobbies = {
        "regular": RegularLobby,
        "megamix": MegamixLobby,
        "collection": CollectionLobby,
        "rp": RPLobby,
    }

    try:
        return lobbies[mode]()
    except KeyError:
        raise ValueError(f"unknown lobby mode: {mode}")
