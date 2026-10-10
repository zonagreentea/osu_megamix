"""Compatibility entry point for recorded or delegated play commands."""

from play import play
import sys


def run(process):
    return play(process)


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
