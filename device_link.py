"""Low-overhead, two-way UDP device link for osu!megamix.

The link carries only current input and game state.  Inputs are intentionally
unreliable: a newer input supersedes an older one, so a delayed packet never
holds up play.
"""

from dataclasses import dataclass
from enum import IntEnum
import select
import socket
import struct
from typing import Callable, Dict, Optional, Tuple


_MAGIC = b"OM"
_VERSION = 1
_HEADER = struct.Struct("!2sBBQ")
_INPUT = struct.Struct("!BBI")
_STATE = struct.Struct("!Bi")


class MessageType(IntEnum):
    HELLO = 1
    WELCOME = 2
    INPUT = 3
    STATE = 4


@dataclass(frozen=True)
class Message:
    kind: MessageType
    device_id: int
    action: Optional[int] = None
    pressed: Optional[bool] = None
    tick: Optional[int] = None
    state: Optional[int] = None
    value: Optional[int] = None


@dataclass(frozen=True)
class InputEvent:
    device_id: int
    action: int
    pressed: bool
    tick: int


def _encode(message: Message) -> bytes:
    packet = _HEADER.pack(_MAGIC, _VERSION, message.kind, message.device_id)
    if message.kind is MessageType.INPUT:
        return packet + _INPUT.pack(message.action, message.pressed, message.tick)
    if message.kind is MessageType.STATE:
        return packet + _STATE.pack(message.state, message.value)
    return packet


def _decode(packet: bytes) -> Optional[Message]:
    if len(packet) < _HEADER.size:
        return None
    magic, version, kind_value, device_id = _HEADER.unpack_from(packet)
    if magic != _MAGIC or version != _VERSION:
        return None
    try:
        kind = MessageType(kind_value)
    except ValueError:
        return None

    payload = packet[_HEADER.size:]
    if kind in (MessageType.HELLO, MessageType.WELCOME):
        return Message(kind, device_id) if not payload else None
    if kind is MessageType.INPUT and len(payload) == _INPUT.size:
        action, pressed, tick = _INPUT.unpack(payload)
        return Message(kind, device_id, action=action, pressed=bool(pressed), tick=tick)
    if kind is MessageType.STATE and len(payload) == _STATE.size:
        state, value = _STATE.unpack(payload)
        return Message(kind, device_id, state=state, value=value)
    return None


class DeviceLink:
    """The game-side endpoint. Call ``poll`` from the game loop."""

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 5051,
        on_input: Optional[Callable[[InputEvent], None]] = None,
    ):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((host, port))
        self._socket.setblocking(False)
        self._sessions: Dict[int, Tuple[str, int]] = {}
        self._on_input = on_input or (lambda event: None)

    @property
    def address(self) -> Tuple[str, int]:
        return self._socket.getsockname()

    def close(self) -> None:
        self._socket.close()

    def poll(self, timeout: float = 0.0, max_messages: int = 64) -> int:
        """Process waiting packets without blocking the game loop by default."""
        ready, _, _ = select.select([self._socket], [], [], timeout)
        if not ready:
            return 0

        handled = 0
        while handled < max_messages:
            try:
                packet, address = self._socket.recvfrom(64)
            except BlockingIOError:
                break
            message = _decode(packet)
            if message is not None:
                self._handle(message, address)
            handled += 1
        return handled

    def publish_state(self, device_id: int, state: int, value: int) -> bool:
        address = self._sessions.get(device_id)
        if address is None:
            return False
        self._socket.sendto(
            _encode(Message(MessageType.STATE, device_id, state=state, value=value)),
            address,
        )
        return True

    def _handle(self, message: Message, address: Tuple[str, int]) -> None:
        if message.kind is MessageType.HELLO:
            self._sessions[message.device_id] = address
            self._socket.sendto(
                _encode(Message(MessageType.WELCOME, message.device_id)), address
            )
        elif message.kind is MessageType.INPUT and self._sessions.get(message.device_id) == address:
            self._on_input(
                InputEvent(
                    message.device_id,
                    message.action,
                    message.pressed,
                    message.tick,
                )
            )


class DeviceClient:
    """A native device endpoint; browsers can implement the packet spec too."""

    def __init__(self, server: Tuple[str, int], device_id: int):
        self._server = server
        self._device_id = device_id
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def close(self) -> None:
        self._socket.close()

    def connect(self) -> None:
        self._send(Message(MessageType.HELLO, self._device_id))

    def send_input(self, action: int, pressed: bool, tick: int) -> None:
        self._send(
            Message(MessageType.INPUT, self._device_id, action=action, pressed=pressed, tick=tick)
        )

    def receive(self, timeout: float = 1.0) -> Message:
        self._socket.settimeout(timeout)
        packet, _ = self._socket.recvfrom(64)
        message = _decode(packet)
        if message is None:
            raise ValueError("invalid device-link packet")
        return message

    def _send(self, message: Message) -> None:
        self._socket.sendto(_encode(message), self._server)
