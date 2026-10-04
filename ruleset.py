class Ruleset:
    def __init__(self, mode):
        self.name = f"osu!mix - {mode} mode"

    def start(self):
        print(f"{self.name} started")
