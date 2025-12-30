#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# imagination* flags live BEFORE `--`
# megamix flags live AFTER `--`

python3 -c '
import sys, subprocess

argv = sys.argv[1:]
im_args, mx_args = [], []
if "--" in argv:
    i = argv.index("--")
    im_args = argv[:i]
    mx_args = argv[i+1:]
else:
    mx_args = argv

# imagination* (optional)
try:
    from imagination_four import run_444
    r = run_444(4)
    if r.get("code") in ("defer", "abort"):
        raise SystemExit(1)
except ModuleNotFoundError:
    pass

cmd = [sys.executable, "src/osu_megamix.py", *mx_args]
raise SystemExit(subprocess.call(cmd))
' -- "$@"
