from dataclasses import dataclass


@dataclass
class Marco:
    name: str = "Marco"
    game: str = "Ball-4-NDS"
    playable: bool = True
    content_moderated: bool = True
    image_file: str = "Marco.svg"

    def profile(self):
        return {
            "name": self.name,
            "game": self.game,
            "playable": self.playable,
            "content_moderated": self.content_moderated,
            "image_file": self.image_file,
        }


marco = Marco()
