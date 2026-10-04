import time


class KeybladeReveal:
    def __init__(self, keyblade):
        self.keyblade = keyblade

    def megamix(self):
        print("\n" * 3)
        print("                 .")
        print("              .     .")
        print()
        print("                  ✦")
        time.sleep(0.8)

        print("                 ✦")
        time.sleep(0.5)

        print("              [ keyblade ]")
        time.sleep(1.0)

        print()
        print(f"              {self.keyblade.name}")
        print("            Keyblade acquired")
        time.sleep(1.5)

    def collection(self):
        print(f"        {self.keyblade.name}")
        time.sleep(0.15)
        print("             ↘")
        time.sleep(0.15)
        print("               ↘")
        time.sleep(0.15)
        print("                 🔑")
        time.sleep(0.3)

    def reveal(self, context):
        if context == "megamix":
            self.megamix()
        elif context == "collection":
            self.collection()
