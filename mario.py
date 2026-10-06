from dataclasses import dataclass


@dataclass
class Mario:
    name: str = "Mario"
    game: str = "Ball-4-NDS"
    playable: bool = True
    content_moderated: bool = True

    def profile(self):
        return {
            "name": self.name,
            "game": self.game,
            "playable": self.playable,
            "content_moderated": self.content_moderated,
        }


mario = Mario()
