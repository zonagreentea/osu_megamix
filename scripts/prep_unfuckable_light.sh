#!/usr/bin/env bash
# Prep script — clears builddir, validates assets, runs light demo

set -euo pipefail
echo "[Prep] Starting unfuckable oneshot workflow…"

# 1️⃣ Cleanup builddir
rm -rf builddir/*
mkdir -p builddir
echo "[Prep] builddir cleared"

# 2️⃣ Validate assets
ASSET_COUNT=$(ls -1 assets | wc -l)
if [ "$ASSET_COUNT" -eq 0 ]; then
  echo "[ERROR] No assets found! Release blocked."
  exit 1
fi
echo "[Prep] Assets validated ($ASSET_COUNT files)"

# 3️⃣ Run demo header
echo "[Prep] Running light demo header"
ruby osu_megamix_1a_demo_light.rb

# 4️⃣ Generate BUILD_PATH.md
echo "[Prep] Generating BUILD_PATH.md"
cat <<EOL > BUILD_PATH.md
# osu!megamix 1.a visual — device path

Assets directory: ./assets
Build directory: ./builddir
Devices:
  - Desktop (default)
  - Low-power (set LOW_POWER=1)
  - Handheld (set HANDHELD=1)
EOL
echo "[Prep] BUILD_PATH.md created"

# 5️⃣ Optional GPT-5-mini sanity check
if [ -n "${OPENAI_API_KEY:-}" ]; then
  echo "[Prep] Running API sanity check"
  python3 - <<'PYTHON'
import os, openai

log_path = "builddir/build.log"
if not os.path.exists(log_path):
    print("[API Check] No build.log found — skipping sanity check")
else:
    with open(log_path) as f:
        content = f.read()
    resp = openai.ChatCompletion.create(
        model="gpt-5-mini",
        messages=[{"role":"user",
                   "content": f"Check this osu!megamix build log for issues, misconfigs, or warnings. One-line summary:\n{content}"}]
    )
    print("[API Check]", resp['choices'][0]['message']['content'])
PYTHON
else
  echo "[Prep] OPENAI_API_KEY not set — skipping API check"
fi

echo "[Prep] Oneshoot workflow complete — unfuckable status ✅"
