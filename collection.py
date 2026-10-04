from pathlib import Path


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

    def trade_keyblade(self, keyblade, friend, other_collection):
        if not self.is_friend(friend):
            raise ValueError("keyblade trades require friendship")
        if not self.has_keyblade(keyblade):
            raise ValueError("keyblade is not owned")
        self.keyblades.remove(keyblade)
        other_collection.keyblades.add(keyblade)
