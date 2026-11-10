from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator


@dataclass(frozen=True)
class InputEvent:
    source: str
    bit: int
    index: int
    pressed: bool
    action: int | None = None
    value: float | None = None


def file_to_bits(path: str | Path) -> list[int]:
    """Losslessly represent a file as an ordered stream of bits."""
    data = Path(path).read_bytes()
    return [
        (byte >> shift) & 1
        for byte in data
        for shift in range(7, -1, -1)
    ]


def bits_to_bytes(bits: Iterable[int]) -> bytes:
    """Reconstruct complete bytes from a bit stream."""
    out = bytearray()
    current = 0
    count = 0

    for value in bits:
        current = (current << 1) | int(bool(value))
        count += 1
        if count == 8:
            out.append(current)
            current = 0
            count = 0

    if count:
        out.append(current << (8 - count))

    return bytes(out)


def process(
    bits: Iterable[int],
    source: str = "input",
    action: int | None = None,
) -> list[InputEvent]:
    """Normalize any bit source into universal input events."""
    return [
        InputEvent(
            source=source,
            bit=int(bool(bit)),
            index=index,
            pressed=bool(bit),
            action=action,
        )
        for index, bit in enumerate(bits)
    ]


def process_file(path: str | Path) -> list[InputEvent]:
    return process(file_to_bits(path), source=str(path))


def process_bits(
    bits: Iterable[int],
    source: str = "input",
    action: int | None = None,
) -> list[InputEvent]:
    return process(bits, source=source, action=action)


def process_bytes(
    data: bytes,
    source: str = "input",
    action: int | None = None,
) -> list[InputEvent]:
    return process(
        (
            (byte >> shift) & 1
            for byte in data
            for shift in range(7, -1, -1)
        ),
        source=source,
        action=action,
    )


def process_value(
    value: float,
    source: str = "input",
    threshold: float = 0.5,
    action: int | None = None,
) -> list[InputEvent]:
    """Turn an analysis value (for example microphone level) into a bit."""
    bit = int(value >= threshold)
    return process_bits([bit], source=source, action=action)


def stream_bits(
    bits: Iterable[int],
    source: str = "input",
    action: int | None = None,
) -> Iterator[InputEvent]:
    for index, bit in enumerate(bits):
        bit = int(bool(bit))
        yield InputEvent(
            source=source,
            bit=bit,
            index=index,
            pressed=bool(bit),
            action=action,
        )


def read(path: str | Path) -> list[InputEvent]:
    return process_file(path)
