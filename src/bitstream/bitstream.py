#!/usr/bin/env python3
"""BITSTREAM 1.0: one-bit-wide, framed streaming link (standard library only)."""
import argparse
import io
import os
import struct
import sys
import time
import zlib

MAGIC = b'BS10'
HEADER = struct.Struct('!4sII')  # magic, payload length, CRC32
MAX_FRAME = 64 * 1024


def transmit_bitwise(data):
    """Yield one binary state per step; never yield an entire byte."""
    for byte in data:
        for shift in range(7, -1, -1):
            yield (byte >> shift) & 1


def receive_bytes(bits):
    """Reassemble bytes from a serial bit iterator."""
    value = 0
    count = 0
    for bit in bits:
        if bit not in (0, 1):
            raise ValueError('Wire must carry only 0 or 1')
        value = (value << 1) | bit
        count += 1
        if count == 8:
            yield value
            value = 0
            count = 0
    if count:
        raise ValueError('Truncated final byte')


def frames(source, chunk_size=4096):
    if not 1 <= chunk_size <= MAX_FRAME:
        raise ValueError('Invalid chunk size')
    while True:
        payload = source.read(chunk_size)
        if not payload:
            break
        yield HEADER.pack(MAGIC, len(payload), zlib.crc32(payload)) + payload
    yield HEADER.pack(MAGIC, 0, 0)  # explicit end-of-stream


def serial_bits(source, chunk_size=4096):
    for frame in frames(source, chunk_size):
        yield from transmit_bitwise(frame)


def decode_stream(bits, destination):
    """Read exactly one bit at a time, verify each frame, and write incrementally."""
    byte_iter = iter(receive_bytes(bits))
    def read_exact(n):
        buf = bytearray()
        for _ in range(n):
            try:
                buf.append(next(byte_iter))
            except StopIteration:
                raise ValueError('Truncated transmission') from None
        return bytes(buf)
    total = 0
    count = 0
    while True:
        magic, size, checksum = HEADER.unpack(read_exact(HEADER.size))
        if magic != MAGIC:
            raise ValueError('Invalid frame header / synchronization lost')
        if size > MAX_FRAME:
            raise ValueError('Oversized frame rejected')
        if size == 0:
            if checksum != 0:
                raise ValueError('Invalid end-of-stream frame')
            try:
                next(byte_iter)
            except StopIteration:
                return total, count
            raise ValueError('Unexpected trailing data')
        payload = read_exact(size)
        if zlib.crc32(payload) != checksum:
            raise ValueError(f'CRC mismatch in frame {count + 1}')
        destination.write(payload)
        total += size
        count += 1


def transfer(source, destination, chunk_size=4096):
    start = time.perf_counter()
    size, frame_count = decode_stream(serial_bits(source, chunk_size), destination)
    elapsed = time.perf_counter() - start
    return size, frame_count, elapsed


def selftest():
    samples = [b'Hello World', bytes(range(256)) * 10, os.urandom(100_000), b'']
    for sample in samples:
        output = io.BytesIO()
        size, count, elapsed = transfer(io.BytesIO(sample), output, 4096)
        assert output.getvalue() == sample and size == len(sample)
        print(f'PASS: {size:,} bytes, {count} data frames, {elapsed:.3f}s')
    original = list(serial_bits(io.BytesIO(b'Hello World')))
    original[HEADER.size * 8 + 3] ^= 1  # flip one payload bit
    try:
        decode_stream(iter(original), io.BytesIO())
    except ValueError as exc:
        assert 'CRC mismatch' in str(exc)
        print('PASS: injected bit error detected by CRC32')
    else:
        raise AssertionError('Corruption was not detected')
    try:
        decode_stream(iter(original[:-10]), io.BytesIO())
    except ValueError:
        print('PASS: malformed/truncated transmission rejected')
    else:
        raise AssertionError('Malformed transmission was not rejected')
    print('ALL TESTS PASSED')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('selftest')
    hello = sub.add_parser('hello', help='Send Hello World over the one-bit channel')
    copy = sub.add_parser('copy', help='Stream a file through the one-bit channel')
    copy.add_argument('source')
    copy.add_argument('destination')
    copy.add_argument('--chunk', type=int, default=4096)
    args = parser.parse_args()
    if args.command == 'selftest':
        selftest()
        return
    if args.command == 'hello':
        source, dest = io.BytesIO(b'Hello World'), io.BytesIO()
        size, count, elapsed = transfer(source, dest)
        print(dest.getvalue().decode())
    else:
        if os.path.abspath(args.source) == os.path.abspath(args.destination):
            parser.error('Source and destination must differ')
        if not 1 <= args.chunk <= MAX_FRAME:
            parser.error(f'--chunk must be between 1 and {MAX_FRAME}')
        # A failed transfer leaves a .partial file, never a falsely completed output.
        partial = args.destination + '.partial'
        if os.path.exists(partial):
            parser.error(f'Partial destination already exists: {partial}')
        try:
            with open(args.source, 'rb') as source, open(partial, 'xb') as dest:
                size, count, elapsed = transfer(source, dest, args.chunk)
            os.replace(partial, args.destination)
        except Exception:
            raise
        print(f'Transferred to {args.destination}')
    print(f'{size:,} bytes | {size*8:,} payload bits | {count} frames | {elapsed:.3f}s')
    if elapsed:
        print(f'Payload throughput: {size*8/elapsed:,.0f} bits/s (software simulation)')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
