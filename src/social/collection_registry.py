from dataclasses import dataclass

@dataclass(frozen=True)
class GameEntry:
    game_id: str
    title: str
    launch: object

class GameRegistry:
    def __init__(self): self._games = {}
    def register(self, game_id, title, launch):
        if not isinstance(game_id, str) or not game_id.strip(): raise ValueError("Invalid game ID")
        if not isinstance(title, str) or not title.strip(): raise ValueError("Invalid title")
        if not callable(launch): raise TypeError("Launcher must be callable")
        if game_id in self._games: raise ValueError("Duplicate game")
        entry = GameEntry(game_id, title, launch)
        self._games[game_id] = entry
        return entry
    def list_games(self): return tuple(self._games.values())
    def launch(self, game_id, *args, **kwargs): return self._games[game_id].launch(*args, **kwargs)
