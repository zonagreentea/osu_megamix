#!/bin/zsh
# subtle flex: full 1c pet launch with ball + sliders + spinners + mix + extra modes

# go to project root
cd ~/osu_megamix || exit

# make sure Python can see src/
export PYTHONPATH="$PWD"

# create logs folder
mkdir -p logs

# run the game
python3 - <<'PYCODE'
import sys
sys.path.append(".")
from src.game import run

# modes: add new modes here
MODES = ["osu", "taiko", "ctb", "mania", "mix", "newmode1", "newmode2"]
print("🎮 Mix hub — choose your mode or type 'mix' for all:")
print(" | ".join(MODES))

# safely get input, default to 'mix' if EOF or invalid
try:
    mode = input("Mode: ").strip().lower()
except EOFError:
    mode = "mix"

if mode not in MODES:
    mode = "mix"

# run the game with all features enabled
run(
    mode=mode,
    enable_ball=True,
    enable_sliders=True,
    enable_spinners=True,
    megamix_continuity=True
)
PYCODE

