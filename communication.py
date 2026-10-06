from __future__ import annotations

import socket
from dataclasses import dataclass
from typing import Iterable, Iterator

_HEADER = 4
_CHUNK = 8192


def bits_to_bytes(bits: Iterable[int]) -> tuple[bytes, int]:
    data = []
    current = 0
    total = 0
    count = 0

    for bit in bits:
        current = (current << 1) | int(bool(bit))
        count += 1
        total += 1

        if count == 8:
            data.append(current)
            current = 0
            count = 0

    if count:
        data.append(current << (8 - count))

    return bytes(data), total


def bytes_to_bits(data: bytes, bit_count: int) -> Iterator[int]:
    for byte in data:
        for shift in range(7, -1, -1):
            if bit_count <= 0:
                return
            yield (byte >> shift) & 1
            bit_count -= 1


@dataclass
class Communication:
    sock: socket.socket

    def send(self, bits: Iterable[int]) -> None:
        payload, bit_count = bits_to_bytes(bits)
        header = len(payload).to_bytes(4, "big")
        count = bit_count.to_bytes(4, "big")
        self.sock.sendall(header + count + payload)

    def receive(self) -> list[int]:
        header = self._read_exact(_HEADER)
        if not header:
            return []

        size = int.from_bytes(header, "big")
        bit_count = int.from_bytes(self._read_exact(4), "big")
        payload = self._read_exact(size)

        return list(bytes_to_bits(payload, bit_count))

    def close(self) -> None:
        self.sock.close()

    def _read_exact(self, size: int) -> bytes:
        data = bytearray()

        while len(data) < size:
            chunk = self.sock.recv(min(_CHUNK, size - len(data)))
            if not chunk:
                raise ConnectionError("communication stream closed")
            data.extend(chunk)

        return bytes(data)


def connect(host: str, port: int) -> Communication:
    sock = socket.create_connection((host, port))
    return Communication(sock)


def listen(host: str = "127.0.0.1", port: int = 0) -> tuple[Communication, tuple[str, int]]:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(1)

    sock, address = server.accept()
    server.close()

    return Communication(sock), address


def local_pair() -> tuple[Communication, Communication]:
    left, right = socket.socketpair()
    return Communication(left), Communication(right)


if __name__ == "__main__":
    a, b = local_pair()
    original = [1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1]

    a.send(original)
    received = b.receive()

    print("communication: PASS" if received == original else "communication: FAIL")

    a.close()
    b.close()
