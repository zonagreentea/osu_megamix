#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")/.."

python3 -m pip install -U pyinstaller >/dev/null
python3 -m PyInstaller --clean --noconfirm --onefile --name imagination --paths src run_imagination.py
echo "[ok] built: dist/imagination"
./dist/imagination
