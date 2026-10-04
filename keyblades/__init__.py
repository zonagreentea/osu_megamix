from dataclasses import dataclass


@dataclass(frozen=True)
class Keyblade:
    name: str
    image: str
    game: str


LIBRARY = {}


def register(name, image, game):
    keyblade = Keyblade(name, image, game)
    LIBRARY[game] = keyblade
    return keyblade


def get(game):
    return LIBRARY.get(game)
