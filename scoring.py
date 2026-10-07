"""Score handling for osu!megamix."""

from timing import Judgement


class Score:
    """Track score, combo, and health from timing judgements."""

    def __init__(self):
        self.combo = 0
        self.health = 100
        self.points = 0

    def hit(self, judgement=None):
        """Apply a hit, optionally using a musical timing judgement."""
        self.combo += 1

        if judgement is None:
            value = 300
        else:
            value = judgement.value

        self.points += value
        self.health = min(100, self.health + 2)

        return value

    def miss(self):
        """Apply a miss."""
        self.combo = 0
        self.health = max(0, self.health - 10)

    def apply(self, judgement):
        """Apply a timing judgement or miss."""
        if judgement is None:
            self.miss()
            return 0

        return self.hit(judgement)
