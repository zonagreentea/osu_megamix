#!/usr/bin/env zsh
set -euo pipefail
unsetopt BANG_HIST
set +H
cd "${0:a:h}"

if [[ -x dist/imagination ]]; then
  exec ./dist/imagination "$@"
fi

if [[ -x run/megamix ]]; then
  exec ./run/megamix "$@"
fi

exec python3 ./osu_megamix.py "$@"
