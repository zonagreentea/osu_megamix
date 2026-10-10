from pathlib import Path


# Populate these when the game's official keyblade catalogue is defined.
KEYBLADES = ()
COMPLETION_KEYBLADE = None


def collection(
    profile_id,
    keyblades=(),
    required_keyblades=KEYBLADES,
    completion_keyblade=COMPLETION_KEYBLADE,
):
    """Return a profile's keyblade collection and completion status."""
    collected = tuple(dict.fromkeys(keyblades))
    required = tuple(dict.fromkeys(required_keyblades))
    owned = set(collected)

    complete = bool(required) and set(required).issubset(owned)

    return {
        "profile_id": profile_id,
        "keyblades": collected,
        "complete": complete,
        "completion_keyblade": (
            completion_keyblade if complete else None
        ),
    }


class Collection:
    def __init__(self, path="collection"):
        self.path = Path(path)
        self.games = {}
        self.friends = set()
        self.keyblades = set()

    def add_game(self, game):
        self.games[game.name] = game

    def get_game(self, name):
        return self.games.get(name)

    def save(self, game):
        return game.save(self.path / game.name)

    def load(self, game):
        return game.load(self.path / game.name)

    def add_friend(self, player):
        self.friends.add(player)

    def remove_friend(self, player):
        self.friends.discard(player)

    def is_friend(self, player):
        return player in self.friends

    def award_keyblade(self, keyblade):
        self.keyblades.add(keyblade)

    def has_keyblade(self, keyblade):
        return keyblade in self.keyblades

    def profile_collection(
        self,
        profile_id,
        required_keyblades=KEYBLADES,
    ):
        """Export this collection as profile-ready data."""
        return collection(
            profile_id,
            keyblades=self.keyblades,
            required_keyblades=required_keyblades,
        )

    def trade_keyblade(self, keyblade, friend, other_collection):
        if not self.is_friend(friend):
            raise ValueError("keyblade trades require friendship")
        if not self.has_keyblade(keyblade):
            raise ValueError("keyblade is not owned")
        self.keyblades.remove(keyblade)
        other_collection.keyblades.add(keyblade)
