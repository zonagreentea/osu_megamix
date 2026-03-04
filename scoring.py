class Score:
    def __init__(self):
        self.combo = 0
        self.health = 100
        self.points = 0

    def hit(self):
        self.combo += 1
        self.points += 300
        self.health = min(100, self.health + 2)

    def miss(self):
        self.combo = 0
        self.health -= 10

