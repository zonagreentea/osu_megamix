#!/usr/bin/env python3

def encode(data: bytes) -> str:
    """Convert bytes to a continuous binary bit string."""
    if not isinstance(data, bytes):
        raise TypeError("encode() requires bytes")
    return ''.join(f'{byte:08b}' for byte in data)


def decode(bits: str) -> bytes:
    """Convert a binary bit string back to bytes."""
    if not isinstance(bits, str):
        raise TypeError("decode() requires a string")

    bits = ''.join(bits.split())

    if any(bit not in '01' for bit in bits):
        raise ValueError("bit string may contain only 0 and 1")

    if len(bits) % 8:
        raise ValueError("bit string length must be a multiple of 8")

    return bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, len(bits), 8)
    )


if __name__ == "__main__":
    original = b"hot lava"
    encoded = encode(original)
    restored = decode(encoded)

    assert restored == original

    print("original:", original)
    print("bits:    ", encoded)
    print("restored:", restored)
    print("round-trip: PASS")
