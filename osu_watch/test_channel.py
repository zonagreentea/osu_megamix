import unittest
from channel import EPOCH, channel_state, load_schedule

class ChannelTests(unittest.TestCase):
    def test_starts_at_first_program(self):
        self.assertEqual(channel_state(EPOCH)['current']['id'], 'megamix')
    def test_advances(self):
        self.assertEqual(channel_state(EPOCH + 600)['current']['id'], 'pulse')
    def test_wraps(self):
        total = sum(p['duration_seconds'] for p in load_schedule())
        self.assertEqual(channel_state(EPOCH + total)['current']['id'], 'megamix')
    def test_next(self):
        self.assertEqual(channel_state(EPOCH)['next']['id'], 'pulse')

if __name__ == '__main__':
    unittest.main()
