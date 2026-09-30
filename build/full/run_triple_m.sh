#!/bin/zsh
# --- Minimalist Triple M launcher (no-ball) ---

# Kill any process using port 8000
kill -9 $(lsof -t -i:8000 2>/dev/null) 2>/dev/null

# Serve the folder in background
python3 -m http.server 8000 &>/dev/null &

# Open in default browser
open "http://localhost:8000"

echo "🚀 Triple M live — super minimalist, no-ball, all modes"

