class Score:
    def __init__(self):
        self.combo = 0
        self.health = 100  # arcadey health
        self.points = 0

    def hit(self, value=300):
        self.combo += 1
        self.points += value
        self.health = min(100, self.health + 2)  # reward small health on hit
        print(f"Hit! Combo: {self.combo}, Health: {self.health}, Score: {self.points}")

    def miss(self, penalty=10):
        self.combo = 0
        self.health -= penalty
        print(f"Miss! Combo reset, Health: {self.health}")

