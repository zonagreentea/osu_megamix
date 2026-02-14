#!/bin/zsh
# =========================
# osu!megamix ULTRA-HAX + Autopilot
# “let it run, subtle flex, infinite Megamix, autopilot edition”
# =========================

alias python=python3.11

# Auto-install dependencies
for module in sounddevice numpy; do
    python -c "import $module" 2>/dev/null || python -m pip install --user $module
done

export PYTHONPATH="$PWD"
mkdir -p logs

# Infinite Megamix loop with play elements
while true; do
    echo "💜 Starting Megamix session with Autopilot…"
    
    python main.py \
        --no-audio \
        --mode megamix \
        --enable-npc \   # Autopilot ON
        --safe-mode \
        --show-play-elements \  # NEW FLAG: prints object types, density, hits
        --log-file logs/megamix_$(date +%Y%m%d_%H%M%S).log

    echo "⚠️ Megamix crashed or ended, restarting in 2s..."
    sleep 2
done

