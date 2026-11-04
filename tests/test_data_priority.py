"""Tests for the shared priority contract."""

import unittest

from data_priority import DataPriority, priority_of


class DataPriorityTests(unittest.TestCase):
    def test_order(self):
        self.assertEqual([p.value for p in DataPriority], list(range(7)))
        self.assertLess(DataPriority.TIME_AUDIO, DataPriority.RENDERING)
        self.assertLess(DataPriority.INPUT_GAMEPLAY, DataPriority.OPTIONAL_SERVICES)

    def test_valid_values(self):
        for priority in DataPriority:
            self.assertIs(priority_of(priority.value), priority)

    def test_reject_invalid_values(self):
        for value in (True, None, "1", 7, -1, 1.5):
            with self.subTest(value=value):
                with self.assertRaises((TypeError, ValueError)):
                    priority_of(value)


if __name__ == "__main__":
    unittest.main()
