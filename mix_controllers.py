
"""Independent controllers for one mix and collections of mixes."""


class Charizard:
    """Controls one mix."""

    def __init__(self, mix):
        self.mix = list(mix)

    def play(self, play_beatmap):
        return [
            play_beatmap(beatmap)
            for beatmap in self.mix
        ]


class Red:
    """Controls multiple mixes."""

    def __init__(self, mixes):
        self.mixes = [list(mix) for mix in mixes]
        self.index = 0

    def next_mix(self):
        if self.index >= len(self.mixes):
            return None

        mix = self.mixes[self.index]
        self.index += 1
        return mix

    def play(self, play_beatmap):
        results = []

        while (mix := self.next_mix()) is not None:
            results.append(
                Charizard(mix).play(play_beatmap)
            )

        return results
