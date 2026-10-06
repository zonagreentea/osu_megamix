#!/usr/bin/env python3
import os
import sys
import subprocess

ROOT = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.join(ROOT, "run")

def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "osu_megamix.html"
    return subprocess.call([RUN, target, *sys.argv[2:]])

if __name__ == "__main__":
    raise SystemExit(main())
