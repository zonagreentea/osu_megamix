#!/bin/sh
set -eu

PORT="${1:-8000}"

# find a free port
while lsof -nP -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; do
  PORT=$((PORT+1))
done

URL="http://localhost:$PORT"

echo ""
echo "imagination* 4.2.0 — hot coffee"
echo "URL: $URL"
echo ""
echo "Safari (Sequoia):"
echo "  Safari → Settings → Advanced → enable: Show features for web developers"
echo "  Then: Develop → Show Web Inspector → Console"
echo ""
echo "COPY/PASTE (browser console, NOT Terminal):"
echo "------------------------------------------------------------"
cat <<'JS'
typeof MEGAMIX
MEGAMIX && MEGAMIX.mods
MEGAMIX && MEGAMIX.setBgDim(0.35)
MEGAMIX && MEGAMIX.toggleBgImage()
MEGAMIX && MEGAMIX.toggleBgVideo()
JS
echo "------------------------------------------------------------"
echo ""

# open browser
open "$URL" >/dev/null 2>&1 || true

exec python3 -m http.server "$PORT"
