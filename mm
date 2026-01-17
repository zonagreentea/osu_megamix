#!/usr/bin/env zsh
set -euo pipefail
unsetopt BANG_HIST
set +H

cd ~/osu_megamix || exit 1
exec python3 -m http.server 8080
