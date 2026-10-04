OPTIONS = 4


class Menu:
    def __init__(self, title, options):
        if len(options) != OPTIONS:
            raise ValueError("menus must contain exactly four options")
        self.title = title
        self.options = options

    def show(self):
        print()
        print(self.title)
        print()
        for number, option in enumerate(self.options, 1):
            print(f"{number}. {option}")
        print()

    def choose(self):
        while True:
            self.show()
            choice = input("> ").strip()
            if choice in {"1", "2", "3", "4"}:
                return int(choice)
            print("choose 1, 2, 3, or 4")


def main_menu():
    return Menu("osu!megamix", ["Play", "Multi", "Collection", "Settings"])


def play_menu():
    return Menu("Play", ["Solo", "Megamix", "Practice", "Back"])


def multi_menu():
    return Menu("Multi", ["Standard", "Megamix", "Collection", "Back"])


def collection_menu():
    return Menu("Collection", ["Games", "Saves", "Keyblades", "Back"])


def settings_menu():
    return Menu("Settings", ["Gameplay", "Audio", "Display", "Back"])
