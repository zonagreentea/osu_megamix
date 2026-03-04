#!/bin/zsh
# =========================
# osu!megamix full-hax launcher
# “let it run, subtle flex, full hax”
# =========================

export PYTHONPATH="$PWD"
alias python=python3.11

# create logs folder if it doesn't exist
mkdir -p logs

# run Megamix fully dynamic, NPC, safe memory, logging hits
python main.py \
  --no-audio \
  --mode megamix \
  --enable-npc \
  --safe-mode \
  --log-file logs/megamix_$(date +%Y%m%d_%H%M%S).log

