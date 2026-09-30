#!/usr/bin/env zsh
set -e
clear

echo "🎵 osu!megamix — zsh pivot"
echo "🔥 bash project, zsh execution"

MODES=("osu" "taiko" "ctb" "mania")
KEYSETS=("z x" "d f" "j k" "1 2 3 4")

MODE_INDEX=$((RANDOM % 4))
MODE=${MODES[$MODE_INDEX]}
KEYS=${KEYSETS[$MODE_INDEX]}

echo "🎮 Mode: $MODE"
echo "⌨️  Keys: $KEYS"
echo "▶️  Press ENTER to start"
read

# ---------- Load beatmap ----------
BEATMAP_FILE="maps/demo.map"
declare -a BEATS
declare -a MAP_KEYS

while read beat time key; do
  [[ "$beat" == "#"* ]] && continue
  BEATS+=("$time")
  MAP_KEYS+=("$key")
done < "$BEATMAP_FILE"

SCORE=0
COMBO=0
MAX_COMBO=0

echo
echo "🔥 GO!"
echo

START_TIME=$(date +%s.%N)

for i in "${!BEATS[@]}"; do
  EXPECTED_KEY=${MAP_KEYS[$i]}
  TARGET_TIME=${BEATS[$i]}

  # wait until target time
  while true; do
    NOW=$(date +%s.%N)
    DIFF=$(echo "$NOW - $START_TIME" | bc)
    (( $(echo "$DIFF >= $TARGET_TIME" | bc -l) )) && break
  done

  echo -n "🎯 Beat $((i+1)) → hit [$EXPECTED_KEY]: "
  read -rsn1 -t 1 INPUT || INPUT=""

  if [[ "$INPUT" == "$EXPECTED_KEY" ]]; then
    SCORE=$((SCORE + 100))
    COMBO=$((COMBO + 1))
    (( COMBO > MAX_COMBO )) && MAX_COMBO=$COMBO
    echo "✅ HIT  +100 | combo $COMBO"
  else
    COMBO=0
    echo "❌ MISS | combo reset"
  fi
done

echo
echo "🏆 Session done! Score: $SCORE | Max combo: $MAX_COMBO"
