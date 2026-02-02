#!/usr/bin/env bash
# osu!megamix — bash edition

set -e
clear

echo "osu!megamix — full flex pivot"
echo

# ---------- MODES ----------
MODES=("osu" "taiko" "ctb" "mania")
KEYSETS=("z x" "d f" "j k" "1 2 3 4")

MODE_INDEX=$((RANDOM % 4))
MODE="${MODES[$MODE_INDEX]}"
KEYS="${KEYSETS[$MODE_INDEX]}"

echo "Mode: $MODE"
echo "Keys: $KEYS"
echo "Press ENTER to start..."
read

TOTAL_BEATS=32
HIT_WINDOW=1        # seconds
SCORE=0
COMBO=0
MAX_COMBO=0

echo
echo "GO!"
echo

# ---------- GAME LOOP ----------
for i in $(seq 1 $TOTAL_BEATS); do
  echo -n "Beat $i → hit [$KEYS]: "
  read INPUT
  if echo " $KEYS " | grep -q " $INPUT "; then
    SCORE=$((SCORE + 100))
    COMBO=$((COMBO + 1))
    (( COMBO > MAX_COMBO )) && MAX_COMBO=$COMBO
    echo "HIT +100 | combo $COMBO"
  else
    COMBO=0
    echo "MISS | combo reset"
  fi
done

echo
echo "Session done!"
echo "Score: $SCORE | Max combo: $MAX_COMBO"

#!/usr/bin/env bash
# osu!megamix — full flex bash prototype
# Linux-native, terminal-playable, zero dependencies

set -e
clear

echo "osu!megamix — bash prototype"
echo "full flex pivot — bash mode"
echo

# ---------- MODES ----------
MODES=("osu" "taiko" "ctb" "mania")
KEYSETS=("z x" "d f" "j k" "1 2 3 4")

MODE_INDEX=$((RANDOM % 4))
MODE="${MODES[$MODE_INDEX]}"
KEYS="${KEYSETS[$MODE_INDEX]}"

echo "Mode: $MODE"
echo "Keys: $KEYS"
echo "Press ENTER to start."
read

# ---------- GAME SETTINGS ----------
TOTAL_BEATS=32
HIT_WINDOW=1        # seconds
SCORE=0
COMBO=0
MAX_COMBO=0

echo
echo "GO!"
echo

# ---------- GAME LOOP ----------
for ((i=1; i<=TOTAL_BEATS; i++)); do
  echo -n "Beat $i → hit [$KEYS]: "
  
  read -rsn1 -t "$HIT_WINDOW" INPUT || INPUT=""

  if [[ " $KEYS " == *" $INPUT "* ]]; then
    SCORE=$((SCORE + 100))
    COMBO=$((COMBO + 1))
    (( COMBO > MAX_COMBO )) && MAX_COMBO=$COMBO
    echo "HIT +100 | combo $COMBO"
  else
    COMBO=0
    echo "MISS | combo reset"
  fi
done

echo
echo "Session done! Score: $SCORE | Max combo: $MAX_COMBO"
echo "osu!megamix bash session complete"

