#!/bin/zsh
set -euo pipefail

# Mix Base — authoritative working root for Megamix state/assets
# Depends on Power Saves root, but chooses a specific sub-root for mix.

PS_ROOT="${POWER_SAVES_ROOT:-}"
if [[ -z "$PS_ROOT" ]]; then
  # try resolver if env not sourced
  if [[ -x "./tools/power_saves_root.zsh" ]]; then
    PS_ROOT="$(./tools/power_saves_root.zsh)"
  else
    PS_ROOT="$HOME"
  fi
fi

# Default subdir name; can be overridden
SUB="${MIX_BASE_SUBDIR:-mix_base}"
MB="$PS_ROOT/$SUB"

mkdir -p "$MB"
print -r -- "$MB"
