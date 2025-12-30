#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# imagination* flags live BEFORE `--`
# megamix flags live AFTER `--`
python3 - <<'PY' "$@"
import sys, subprocess

argv = sys.argv[1:]
# Split args on `--`
im_args, mx_args = [], []
if "--" in argv:
    i = argv.index("--")
    im_args = argv[:i]
    mx_args = argv[i+1:]
else:
    # If no separator, treat everything as megamix args
    mx_args = argv

# Run imagination* (optional): if your imagination module exists
# If you don't have it, it simply won't run.
try:
    from imagination_four import run_444
    r = run_444(4)
    # no prints by default; hard-stop only on abort/defer
    if r["code"] in ("defer", "abort"):
        raise SystemExit(1)
except ModuleNotFoundError:
    pass

# Run osu!megamix with megamix args
cmd = [sys.executable, "osu_megamix.py", *mx_args]
raise SystemExit(subprocess.call(cmd))
PY
