import unittest
from src.social.collection_registry import GameRegistry

class RegistryTests(unittest.TestCase):
    def test_launch(self):
        r = GameRegistry()
        r.register("secret", "Secret Game", lambda: 42)
        self.assertEqual(r.launch("secret"), 42)
    def test_duplicate(self):
        r = GameRegistry()
        r.register("secret", "Secret Game", lambda: None)
        with self.assertRaises(ValueError): r.register("secret", "Duplicate", lambda: None)
    def test_invalid_launcher(self):
        with self.assertRaises(TypeError): GameRegistry().register("secret", "Secret Game", None)
