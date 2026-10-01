#!/usr/bin/env python3
#overheal 2 and osu!megamix

import os
import subprocess

ROOT = subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"],
    text=True
).strip()

env = os.environ.copy()
env["OSU_MEGAMIX_ROOT"] = ROOT

subprocess.run(
    ["bash", "run.sh"],
    env=env,
    check=True
)
