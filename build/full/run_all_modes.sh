#!/bin/zsh

# All modes
export OSU_MODE=1
python3 main.py &

export TAIKO_MODE=1
python3 main.py &

export CATCH_MODE=1
python3 main.py &

export MANIA_MODE=1
python3 main.py &

export MEGAMIX_CONTINUITY=1
python3 main.py &

wait
