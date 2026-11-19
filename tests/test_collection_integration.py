import unittest
from src.social.collection import Collection

class CollectionIntegrationTests(unittest.TestCase):
    def test_register_and_launch(self):
        c = Collection()
        c.register_game("hidden", "Hidden Game", lambda: 42)
        self.assertEqual(c.launch_game("hidden"), 42)
        self.assertEqual(c.available_games()[0].game_id, "hidden")

    def test_existing_add_game(self):
        c = Collection()
        class Game:
            name = "legacy"
        game = Game()
        c.add_game(game)
        self.assertIs(c.get_game("legacy"), game)
