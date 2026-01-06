#!/bin/sh
set -eu
cd "$(dirname "$0")"

PORT="${1:-8000}"

# find a free port starting at PORT
p="$PORT"
while :; do
  if ! lsof -nP -iTCP:"$p" -sTCP:LISTEN >/dev/null 2>&1; then
    break
  fi
  p=$((p+1))
done

echo "[mm] serving on http://127.0.0.1:${p}/index.html"
exec python3 -m http.server "$p"
