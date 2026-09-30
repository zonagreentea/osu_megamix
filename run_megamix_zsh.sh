#!/bin/zsh
# =========================
# osu!megamix ULTRA-HAX • zsh subtle flex
# Infinite Megamix, Modes, Autopilot, Safe Memory
# =========================

alias python=python3.11

# Ensure modules exist
for module in sounddevice numpy; do
    python -c "import $module" 2>/dev/null || python -m pip install --user $module
done

# PYTHONPATH set for src/
export PYTHONPATH="$PWD"

# Logs folder
mkdir -p logs

# Infinite subtle flex loop
while true; do
    echo "💜 Megamix session starting… Subtle flex engaged"

    python main.py \
        --no-audio \
        --mode megamix \
        --enable-npc \
        --safe-mode \
        --show-play-elements \
        --show-modes \
        --log-file logs/megamix_$(date +%Y%m%d_%H%M%S).log

    echo "⚠️ Megamix ended or crashed… subtle flex restart in 2s"
    sleep 2
done

