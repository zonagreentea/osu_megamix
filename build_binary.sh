#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

python3 -m pip install --quiet pyinstaller
python3 -m PyInstaller --clean --noconfirm osu_megamix.spec

mkdir -p dist
cp -R "$ROOT/dist/run_bundle" "$ROOT/dist/run_bundle_bak" 2>/dev/null || true
if [ -f "$ROOT/dist/run_bundle/run" ]; then
  cp "$ROOT/dist/run_bundle/run" "$ROOT/dist/run"
fi

echo "Compiled launcher is ready at: $ROOT/dist/run"
