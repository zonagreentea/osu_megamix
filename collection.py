import json
from pathlib import Path


class Collection:
    def __init__(self, path="collection.json"):
        self.path = Path(path)
        self.games = {}
        self.friends = set()
        self.keyblades = set()
        self.load()

    def load(self):
        if not self.path.exists():
            return

        data = json.loads(self.path.read_text())

        self.games = data.get("games", {})
        self.friends = set(data.get("friends", []))
        self.keyblades = set(data.get("keyblades", []))

    def save(self):
        data = {
            "games": self.games,
            "friends": sorted(self.friends),
            "keyblades": sorted(self.keyblades),
        }

        self.path.write_text(
            json.dumps(data, indent=2) + "\n"
        )

    def add_game(self, game):
        self.games.setdefault(game, {})

    def get_game(self, game):
        return self.games.get(game)

    def set_game_save(self, game, data):
        self.games[game] = data

    def get_game_save(self, game):
        return self.games.get(game)

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

    def trade_keyblade(self, keyblade, friend, other_collection):
        if not self.is_friend(friend):
            raise ValueError("keyblade trades require friendship")

        if not self.has_keyblade(keyblade):
            raise ValueError("keyblade is not owned")

        self.keyblades.remove(keyblade)
        other_collection.keyblades.add(keyblade)
