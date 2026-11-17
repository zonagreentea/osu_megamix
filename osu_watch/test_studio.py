"""Regression tests for studio security and existing schedule."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import channel


class StudioTests(unittest.TestCase):
    def test_local_only_without_token(self):
        with patch.object(channel, 'STUDIO_TOKEN', ''):
            self.assertTrue(channel.studio_authorized('127.0.0.1', ''))
            self.assertTrue(channel.studio_authorized('::1', ''))
            self.assertFalse(channel.studio_authorized('192.168.1.3', ''))
            self.assertFalse(channel.studio_authorized('not-an-ip', ''))

    def test_remote_requires_configured_token(self):
        with patch.object(channel, 'STUDIO_TOKEN', 'secret-example'):
            self.assertFalse(channel.studio_authorized('127.0.0.1', ''))
            self.assertFalse(channel.studio_authorized('192.168.1.3', 'wrong'))
            self.assertTrue(channel.studio_authorized('192.168.1.3', 'secret-example'))

    def test_schedule_unchanged(self):
        programs = channel.load_schedule()
        self.assertEqual(channel.channel_state(channel.EPOCH)['current']['id'], programs[0]['id'])
        total = sum(p['duration_seconds'] for p in programs)
        self.assertEqual(channel.channel_state(channel.EPOCH + total)['current']['id'], programs[0]['id'])

    def test_studio_assets_exist(self):
        root = Path(__file__).resolve().parent
        self.assertIn('studio.js', (root/'studio.html').read_text())
        script = (root/'studio.js').read_text()
        for feature in ('captureStream', 'createDynamicsCompressor', 'getDisplayMedia',
                        'RTCPeerConnection', 'api/live/register', 'stopBroadcast'):
            self.assertIn(feature, script)


if __name__ == '__main__':
    unittest.main()
