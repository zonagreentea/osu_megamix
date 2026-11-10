import unittest

from portrayal_policy import PortrayalPolicyError, validate_portrayal


class PortrayalPolicyTests(unittest.TestCase):

    def test_fictional_content_allowed(self):
        self.assertTrue(validate_portrayal({
            "real_life_event": False,
            "event_classification": "fictional",
        }))

    def test_real_life_event_rejected(self):
        with self.assertRaises(PortrayalPolicyError):
            validate_portrayal({
                "real_life_event": True,
                "event_classification": "fictional",
            })

    def test_missing_classification_rejected(self):
        with self.assertRaises(PortrayalPolicyError):
            validate_portrayal({})

    def test_string_false_rejected(self):
        with self.assertRaises(PortrayalPolicyError):
            validate_portrayal({
                "real_life_event": "false",
                "event_classification": "fictional",
            })

    def test_unknown_event_type_rejected(self):
        with self.assertRaises(PortrayalPolicyError):
            validate_portrayal({
                "real_life_event": False,
                "event_classification": "unknown",
            })


if __name__ == "__main__":
    unittest.main()
