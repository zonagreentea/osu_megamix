import socket
import unittest

from device_link import DeviceClient, DeviceLink, MessageType


class DeviceLinkTest(unittest.TestCase):
    def setUp(self):
        self.events = []
        self.link = DeviceLink(host="127.0.0.1", port=0, on_input=self.events.append)
        self.client = DeviceClient(self.link.address, device_id=7)

    def tearDown(self):
        self.client.close()
        self.link.close()

    def test_device_can_send_input_and_receive_game_state(self):
        self.client.connect()
        self.link.poll(timeout=0.5)

        welcome = self.client.receive()
        self.assertEqual(welcome.kind, MessageType.WELCOME)
        self.assertEqual(welcome.device_id, 7)

        self.client.send_input(action=3, pressed=True, tick=1200)
        self.link.poll(timeout=0.5)
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0].action, 3)
        self.assertTrue(self.events[0].pressed)
        self.assertEqual(self.events[0].tick, 1200)

        self.assertTrue(self.link.publish_state(7, state=9, value=42))
        state = self.client.receive()
        self.assertEqual(state.kind, MessageType.STATE)
        self.assertEqual((state.state, state.value), (9, 42))

    def test_unknown_or_malformed_packets_do_not_create_a_session(self):
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addCleanup(sender.close)
        sender.sendto(b"invalid", self.link.address)
        self.link.poll()
        self.assertFalse(self.link.publish_state(99, state=1, value=1))


if __name__ == "__main__":
    unittest.main()
