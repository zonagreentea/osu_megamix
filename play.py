#!/usr/bin/env python3

import subprocess
import sys


def play(process):
    if callable(process):
        return process()

    if isinstance(process, (list, tuple)):
        return subprocess.run(process, check=True)

    if isinstance(process, str):
        return subprocess.run(process, shell=True, check=True)

    raise TypeError(f"cannot play {type(process).__name__}")


if __name__ == "__main__":
    play(sys.argv[1:])
