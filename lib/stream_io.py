"""Lossless binary stream transfer for osu!megamix."""

import hashlib
import sys

BUFFER_SIZE = 65536


def transfer(source, destination, chunk_size=BUFFER_SIZE):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    digest = hashlib.sha256()
    total = 0

    while True:
        data = source.read(chunk_size)

        if data is None:
            raise OSError("Input returned no data")

        if not data:
            break

        view = memoryview(data)

        while view:
            written = destination.write(view)

            if written is None or written <= 0:
                raise OSError("Incomplete output")

            if written > len(view):
                raise OSError("Invalid write count")

            digest.update(view[:written])
            total += written
            view = view[written:]

    destination.flush()

    return {
        "bytes": total,
        "sha256": digest.hexdigest(),
    }


def main():
    result = transfer(
        sys.stdin.buffer,
        sys.stdout.buffer
    )

    print(
        f"Transferred {result['bytes']} bytes\n"
        f"SHA-256: {result['sha256']}",
        file=sys.stderr
    )


if __name__ == "__main__":
    main()
