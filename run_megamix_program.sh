#!/bin/zsh
# =========================
# osu!megamix full-hax program
# “let it run forever, subtle flex”
# =========================

# Force Python 3.11
alias python=python3.11

# Make sure Python modules exist
for module in sounddevice numpy; do
    python -c "import $module" 2>/dev/null || python -m pip install --user $module
done

# Set PYTHONPATH to current folder
export PYTHONPATH="$PWD"

# Create logs folder
mkdir -p logs

# Infinite loop for “never stop the mix”
while true; do
    # Run Megamix safely with all modes + NPC + logging
    python main.py \
        --no-audio \
        --mode megamix \
        --enable-npc \
        --safe-mode \
        --log-file logs/megamix_$(date +%Y%m%d_%H%M%S).log

    echo "💜 Megamix crashed or ended, restarting in 2s..."
    sleep 2
done

