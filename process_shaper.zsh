#!/bin/zsh

# osu_megamix process controls

SHUI=on
PLAYER_ID="zonagreentea"
SHUI_COMMAND="See you next time."

# Immediately disable lul.
pkill -x lul 2>/dev/null

# Immediately disable Dream Drop.
pkill -x dream_drop 2>/dev/null

# SHUI command.
if [[ "$SHUI" == "on" ]]; then
    printf '%s\n' "$SHUI_COMMAND"
fi

exit 0