import unittest
from flow_router import FlowRouter, default_router

class FlowTests(unittest.TestCase):
    def test_shortest_path(self):
        r = default_router()
        self.assertEqual(r.route("home", "game"),
                         (["home", "play", "mode", "game"], 4))

    def test_direct_shortcut(self):
        r = default_router()
        self.assertEqual(r.route("game", "home"),
                         (["game", "home"], 2))

    def test_same_scene(self):
        r = default_router()
        self.assertEqual(r.route("home", "home"),
                         (["home"], 0))

    def test_unreachable(self):
        r = FlowRouter()
        r.connect("a", "b")
        r.connect("c", "d")
        with self.assertRaises(ValueError):
            r.route("a", "d")

    def test_negative_cost(self):
        with self.assertRaises(ValueError):
            FlowRouter().connect("a", "b", -1)

    def test_invalid_cost(self):
        for cost in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                FlowRouter().connect("a", "b", cost)

    def test_directed(self):
        r = FlowRouter()
        r.connect("a", "b")
        with self.assertRaises(ValueError):
            r.route("b", "a")

    def test_cheaper_branch(self):
        r = FlowRouter()
        r.connect("a", "d", 10)
        r.connect("a", "b", 1)
        r.connect("b", "d", 2)
        self.assertEqual(r.route("a", "d"),
                         (["a", "b", "d"], 3))

if __name__ == "__main__":
    unittest.main(verbosity=2)
