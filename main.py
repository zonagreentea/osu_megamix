#!/usr/bin/env python3

"""Top-level osu!megamix launcher."""

import subprocess


def main():
    return subprocess.run(["./run"], check=True).returncode


if __name__ == "__main__":
    raise SystemExit(main())
