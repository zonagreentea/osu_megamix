#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [[ "${1:-}" == "--web" ]]; then
  if command -v open >/dev/null 2>&1; then
    open "$ROOT/meta_web/index.html"
  else
    echo "Open this in a browser:"
    echo "$ROOT/meta_web/index.html"
  fi
  exit 0
fi

exec python3 -u "$ROOT/src/osu_megamix.py" "$@"
