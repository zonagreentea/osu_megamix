#!/bin/zsh
set -euo pipefail

log_file="${BALL_LOG:-$HOME/.osu_megamix/ball.log}"
mkdir -p "${log_file:h}"

ts="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
print -r -- "$ts $*" >> "$log_file"
