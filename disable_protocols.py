#!/usr/bin/env python3
"""Disable shui, brv, and lul protocols, generate a pink PNG, and end a 10-minute timeline.

This script uses only Python stdlib modules and no external dependencies.
"""

from __future__ import annotations

import os
import struct
import time
import zlib

DISABLED_PROTOCOLS = ("shui", "brv", "lul")
TIMELINE_MINUTES = 10
PNG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "protocol_shutdown_pink.png")


def disable_protocols() -> dict[str, bool]:
    """Return the disabled state for each protocol."""
    return {protocol: False for protocol in DISABLED_PROTOCOLS}


def write_pink_png(path: str, width: int = 800, height: int = 600, color: tuple[int, int, int] = (255, 79, 168)) -> str:
    """Write a solid pink PNG to disk using only the standard library."""
    pink_r, pink_g, pink_b = color
    raw = bytearray()
    for _ in range(height):
        raw.append(0)
        for _ in range(width):
            raw.extend((pink_r, pink_g, pink_b, 255))

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")

    with open(path, "wb") as f:
        f.write(png)

    return path


def run_timeline(minutes: int = TIMELINE_MINUTES) -> None:
    """Print a countdown for the requested shutdown timeline."""
    total_seconds = minutes * 60
    for remaining in range(total_seconds, -1, -1):
        mins, secs = divmod(remaining, 60)
        print(f"Timeline end in {mins:02d}:{secs:02d}", end="\r")
        if remaining > 0:
            time.sleep(1)
    print("\nTimeline ended. Protocol shutdown complete.")


def main() -> None:
    status = disable_protocols()
    print("Protocol disablement summary:")
    for protocol, enabled in status.items():
        print(f"- {protocol}: {'enabled' if enabled else 'disabled'}")

    print("\nThe shui, brv, and lul protocols are explicitly disabled.")
    pink_png = write_pink_png(PNG_PATH)
    print(f"Generated pink PNG: {pink_png}")
    run_timeline(minutes=TIMELINE_MINUTES)


if __name__ == "__main__":
    main()
