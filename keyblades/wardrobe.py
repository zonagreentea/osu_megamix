class Wardrobe:
    def __init__(self):
        self.keyblades = set()

    def add(self, keyblade):
        self.keyblades.add(keyblade)

    def remove(self, keyblade):
        self.keyblades.discard(keyblade)

    def owns(self, keyblade):
        return keyblade in self.keyblades
