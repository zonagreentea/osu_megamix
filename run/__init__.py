#!/usr/bin/env python3

from play import play
import sys


def run(process):
    return play(process)


if __name__ == "__main__":
    run(" ".join(sys.argv[1:]))
