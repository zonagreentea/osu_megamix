"""osu!megamix binary I/O core."""

import os


def read(fd, size=65536):
    while True:
        try:
            return os.read(fd, size)
        except InterruptedError:
            continue


def write(fd, data):
    view = memoryview(data)
    total = 0

    while total < len(view):
        try:
            count = os.write(fd, view[total:])
        except InterruptedError:
            continue

        if count <= 0:
            raise OSError("Output stopped")

        total += count

    return total


def transfer(source_fd, target_fd, size=65536):
    total = 0

    while True:
        data = read(source_fd, size)

        if not data:
            return total

        total += write(target_fd, data)
