#!/usr/bin/env python3
"""Player-facing entry point for osu!megamix."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "run"

def main():
    args = sys.argv[1:]
    if not args or args[0] in {"-h", "--help"}:
        print("Usage:")
        print("  python3 play.py file <path> [arguments...]")
        print("  python3 play.py code <language> <source>")
        return 0 if args else 2
    if args[0] == "file":
        if len(args) < 2:
            print("play: file requires a path", file=sys.stderr)
            return 2
        target = Path(args[1]).expanduser()
        if not target.is_absolute():
            target = Path.cwd() / target
        if not target.is_file():
            print(f"play: file not found: {target}", file=sys.stderr)
            return 1
        command = [str(RUN), str(target), *args[2:]]
    elif args[0] == "code":
        if len(args) < 3:
            print("play: code requires a language and source", file=sys.stderr)
            return 2
        command = [str(RUN), "--code", args[1], args[2]]
    else:
        print(f"play: unknown command: {args[0]}", file=sys.stderr)
        print("Use 'python3 play.py --help' for usage.", file=sys.stderr)
        return 2
    if not RUN.is_file():
        print(f"play: runtime not found: {RUN}", file=sys.stderr)
        return 1
    os.execv(str(RUN), command)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
