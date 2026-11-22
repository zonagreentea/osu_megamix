"""BITWISE 2.0: bounded-memory, integrity-checked binary streaming (stdlib only).

BS10 framing: !4sII (magic, payload length, CRC32), zero-length EOF.
BS10 has no whole-stream digest or sequence number; SHA-256 is verified when an
expected digest is supplied or returned by the sender. Never treat CRC as authentication.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import os
from pathlib import Path
import struct
import tempfile
import zlib

MAGIC = b"BS10"
HEADER = struct.Struct("!4sII")
MAX_FRAME = 64 * 1024
DEFAULT_CHUNK = 4096

class BitwiseError(ValueError):
    pass

def _read_exact(source, n):
    result = bytearray()
    while len(result) < n:
        block = source.read(n - len(result))
        if not block:
            raise BitwiseError("Truncated stream")
        result.extend(block)
    return bytes(result)

def encode(source, destination, chunk_size=DEFAULT_CHUNK):
    """Write BS10 frames; return (payload_bytes, sha256_hex, frames)."""
    if not 1 <= chunk_size <= MAX_FRAME:
        raise ValueError("chunk_size must be between 1 and 65536")
    sha = hashlib.sha256()
    total = frames = 0
    while True:
        block = source.read(chunk_size)
        if not block:
            break
        if not isinstance(block, bytes):
            raise TypeError("Source must be a binary stream")
        destination.write(HEADER.pack(MAGIC, len(block), zlib.crc32(block) & 0xffffffff))
        destination.write(block)
        sha.update(block)
        total += len(block)
        frames += 1
    destination.write(HEADER.pack(MAGIC, 0, 0))
    return total, sha.hexdigest(), frames

def decode(source, destination, *, expected_sha256=None, max_bytes=None):
    """Decode BS10 stream; return (payload_bytes, sha256_hex, frames).

    Destination may contain partial output on error. Use copy_file() for atomic
    replacement of filesystem destinations.
    """
    if max_bytes is not None and max_bytes < 0:
        raise ValueError("max_bytes must be nonnegative")
    sha = hashlib.sha256()
    total = frames = 0
    while True:
        magic, size, crc = HEADER.unpack(_read_exact(source, HEADER.size))
        if magic != MAGIC:
            raise BitwiseError("Invalid frame magic")
        if size > MAX_FRAME:
            raise BitwiseError("Frame exceeds maximum size")
        if size == 0:
            if crc != 0:
                raise BitwiseError("Invalid EOF checksum")
            if source.read(1):
                raise BitwiseError("Trailing bytes after EOF")
            break
        if max_bytes is not None and total + size > max_bytes:
            raise BitwiseError("Payload exceeds allowed size")
        payload = _read_exact(source, size)
        if zlib.crc32(payload) & 0xffffffff != crc:
            raise BitwiseError("CRC32 mismatch")
        destination.write(payload)
        sha.update(payload)
        total += size
        frames += 1
    digest = sha.hexdigest()
    if expected_sha256 is not None and digest.lower() != expected_sha256.lower():
        raise BitwiseError("SHA-256 mismatch")
    return total, digest, frames

def verify(data, expected_sha256):
    """Compare raw bytes to a trusted expected SHA-256 hex digest."""
    return hashlib.sha256(data).hexdigest() == expected_sha256.lower()

def copy_file(source_path, destination_path, *, chunk_size=DEFAULT_CHUNK,
              expected_sha256=None, max_bytes=None, overwrite=False):
    """Copy via BS10, verifying into a temporary file before replacement.

    Uses a temporary framed stream on disk to keep RAM bounded. Existing output
    is preserved on verification failure. Not a secure sandbox for hostile paths.
    """
    src = Path(source_path)
    dst = Path(destination_path)
    if src.resolve() == dst.resolve():
        raise ValueError("Source and destination must differ")
    if not dst.parent.is_dir():
        raise FileNotFoundError(f"Destination directory does not exist: {dst.parent}")
    if dst.exists() and not overwrite:
        raise FileExistsError(dst)
    staged_path = framed_path = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".bitwise-frame-", dir=dst.parent, delete=False) as framed:
            framed_path = Path(framed.name)
            with src.open("rb") as original:
                sent_bytes, sent_digest, sent_frames = encode(original, framed, chunk_size)
        with tempfile.NamedTemporaryFile(prefix=".bitwise-stage-", dir=dst.parent, delete=False) as staged:
            staged_path = Path(staged.name)
            with framed_path.open("rb") as framed:
                result = decode(framed, staged, expected_sha256=expected_sha256 or sent_digest,
                                max_bytes=max_bytes)
            staged.flush()
            os.fsync(staged.fileno())
        if result != (sent_bytes, sent_digest, sent_frames):
            raise BitwiseError("Transfer metadata mismatch")
        if not overwrite and dst.exists():
            raise FileExistsError(dst)
        if overwrite:
            os.replace(staged_path, dst)
        else:
            # Exclusive creation prevents overwriting an existing destination.
            os.link(staged_path, dst)
            staged_path.unlink()
        staged_path = None
        return result
    finally:
        for path in (staged_path, framed_path):
            if path is not None:
                path.unlink(missing_ok=True)

def selftest():
    import unittest
    class Tests(unittest.TestCase):
        def roundtrip(self, data, chunk=4096):
            wire, output = io.BytesIO(), io.BytesIO()
            sent = encode(io.BytesIO(data), wire, chunk)
            wire.seek(0)
            received = decode(wire, output, expected_sha256=sent[1])
            self.assertEqual(sent, received)
            self.assertEqual(data, output.getvalue())
        def test_empty(self): self.roundtrip(b"")
        def test_hello(self): self.roundtrip(b"Hello World")
        def test_random(self): self.roundtrip(os.urandom(100000), 137)
        def test_max_frame(self): self.roundtrip(os.urandom(MAX_FRAME * 2 + 3), MAX_FRAME)
        def test_crc(self):
            wire = io.BytesIO(); encode(io.BytesIO(b"hello"), wire)
            bad = bytearray(wire.getvalue()); bad[HEADER.size] ^= 1
            with self.assertRaises(BitwiseError): decode(io.BytesIO(bad), io.BytesIO())
        def test_truncated(self):
            wire = io.BytesIO(); encode(io.BytesIO(b"hello"), wire)
            with self.assertRaises(BitwiseError): decode(io.BytesIO(wire.getvalue()[:-1]), io.BytesIO())
        def test_trailing(self):
            wire = io.BytesIO(); encode(io.BytesIO(b"hello"), wire)
            with self.assertRaises(BitwiseError): decode(io.BytesIO(wire.getvalue()+b"x"), io.BytesIO())
        def test_limit(self):
            wire = io.BytesIO(); encode(io.BytesIO(b"hello"), wire)
            with self.assertRaises(BitwiseError): decode(io.BytesIO(wire.getvalue()), io.BytesIO(), max_bytes=4)
        def test_bad_sha(self):
            wire = io.BytesIO(); encode(io.BytesIO(b"hello"), wire)
            with self.assertRaises(BitwiseError): decode(io.BytesIO(wire.getvalue()), io.BytesIO(), expected_sha256="0"*64)
        def test_files(self):
            with tempfile.TemporaryDirectory() as tmp:
                a, b = Path(tmp)/"a", Path(tmp)/"b"
                a.write_bytes(os.urandom(100000))
                copy_file(a,b)
                self.assertEqual(a.read_bytes(),b.read_bytes())
                with self.assertRaises(FileExistsError): copy_file(a,b)
                with self.assertRaises(BitwiseError): copy_file(a,b,overwrite=True,expected_sha256="0"*64)
                self.assertEqual(a.read_bytes(),b.read_bytes())
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(Tests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return result.wasSuccessful()

def main():
    parser = argparse.ArgumentParser(description="BITWISE 2.0: binary framing and integrity")
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("selftest")
    hello = subs.add_parser("hello")
    copy = subs.add_parser("copy")
    copy.add_argument("source"); copy.add_argument("destination")
    copy.add_argument("--chunk", type=int, default=DEFAULT_CHUNK)
    copy.add_argument("--sha256", help="trusted expected source SHA-256")
    copy.add_argument("--max-bytes", type=int)
    copy.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if args.command == "selftest":
        raise SystemExit(0 if selftest() else 1)
    if args.command == "hello":
        wire, output = io.BytesIO(), io.BytesIO()
        sent = encode(io.BytesIO(b"Hello World"), wire)
        wire.seek(0)
        decode(wire, output, expected_sha256=sent[1])
        print(output.getvalue().decode("ascii"))
        print(f"payload={sent[0]} bytes frames={sent[2]} sha256={sent[1]}")
    elif args.command == "copy":
        try:
            size, digest, frames = copy_file(args.source,args.destination,chunk_size=args.chunk,
                expected_sha256=args.sha256,max_bytes=args.max_bytes,overwrite=args.overwrite)
        except (OSError, ValueError) as error:
            parser.exit(1, f"BITWISE ERROR: {error}\n")
        print(f"OK bytes={size} frames={frames} sha256={digest}")

if __name__ == "__main__":
    main()
