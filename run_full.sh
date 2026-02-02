#!/usr/bin/env zsh
set -e
clear

echo "🎵 osu!megamix — zsh pivot full flex"
echo "🔥 bash project, zsh execution"

# ---------- MODES ----------
MODES=("osu" "taiko" "ctb" "mania")
KEYSETS=("z x" "d f" "j k" "1 2 3 4")
MODE_INDEX=$(( RANDOM % 4 ))
MODE=${MODES[$MODE_INDEX]}
KEYS=(${(z)KEYSETS[$MODE_INDEX]})

echo "🎮 Mode: $MODE"
echo "⌨️ Keys: ${KEYS[*]}"
echo "▶️ Press ENTER to start"
read

# ---------- BEATMAP ----------
# Quantized beats, 120 BPM, 0.5s per beat
TOTAL_BEATS=32
BEATS=($(seq 0 0.5 15.5))
# Simple alternating keys for prototype
MAP_KEYS=()
for ((i=1; i<=TOTAL_BEATS; i++)); do
  MAP_KEYS+=(${KEYS[$(( (i-1) % ${#KEYS[@]} + 1 ))]})
done

# ---------- GAME STATE ----------
SCORE=0
COMBO=0
MAX_COMBO=0
MULTIPLIER=1

echo
echo "🔥 GO!"
echo

START_TIME=$(date +%s.%N)

# ---------- GAME LOOP ----------
for i in {1..$TOTAL_BEATS}; do
  EXPECTED_KEY=${MAP_KEYS[$i]}
  TARGET_TIME=${BEATS[$i]}

  # wait until the beat time
  while true; do
    NOW=$(date +%s.%N)
    DIFF=$(echo "$NOW - $START_TIME" | bc)
    (( $(echo "$DIFF >= $TARGET_TIME" | bc -l) )) && break
  done

  # visible hit window countdown
  echo -n "🐾 Beat $i → hit [$EXPECTED_KEY] (0.5s): "
  read -rsn1 -t 0.5 INPUT || INPUT=""
  INPUT=${INPUT:l}  # lowercase

  if [[ "$INPUT" == "$EXPECTED_KEY" ]]; then
    SCORE=$((SCORE + 100 * MULTIPLIER))
    COMBO=$((COMBO + 1))
    (( COMBO > MAX_COMBO )) && MAX_COMBO=$COMBO

    # increase multiplier every 5 combo
    if (( COMBO % 5 == 0 )); then
      MULTIPLIER=$((MULTIPLIER + 1))
    fi

    echo "😺 HIT +$((100*MULTIPLIER)) | combo $COMBO | x$MULTIPLIER"
  else
    COMBO=0
    MULTIPLIER=1
    echo "😿 MISS | combo reset | x$MULTIPLIER"
  fi
done

# ---------- RESULTS ----------
echo
echo "🏆 Session done! Score: $SCORE | Max combo: $MAX_COMBO | Final x$MULTIPLIER"
echo "🐾 osu!megamix complete!"
