#!/usr/bin/env zsh
clear
echo "🐱 osu!megamix — cat_net zsh pivot (v2)"

MODES=("osu" "taiko" "ctb" "mania")
KEYSETS=("z x" "d f" "j k" "1 2 3 4")

MODE_INDEX=$(( RANDOM % 4 ))
MODE=${MODES[$MODE_INDEX]}
KEYS=(${(z)KEYSETS[$MODE_INDEX]})

echo "🎮 Mode: $MODE"
echo "⌨️ Keys: ${KEYS[*]}"
echo "▶️ Press ENTER to start"
read

BEATS=($(seq 0 0.5 15))
MAP_KEYS=(${KEYS[1]} ${KEYS[2]} ${KEYS[1]} ${KEYS[2]} ${KEYS[1]} ${KEYS[2]} ${KEYS[1]} ${KEYS[2]} ${KEYS[1]} ${KEYS[2]})

SCORE=0
COMBO=0
MAX_COMBO=0

echo
echo "🔥 GO!"
echo

START_TIME=$(date +%s.%N)

for i in {1..${#BEATS[@]}}; do
  EXPECTED_KEY=${MAP_KEYS[$i]}
  TARGET_TIME=${BEATS[$i]}
  while true; do
    NOW=$(date +%s.%N)
    DIFF=$(echo "$NOW - $START_TIME" | bc)
    (( $(echo "$DIFF >= $TARGET_TIME" | bc -l) )) && break
  done
  echo -n "🐾 Beat $i → hit [$EXPECTED_KEY] (0.5s): "
  read -rsn1 -t 0.5 INPUT || INPUT=""
  INPUT=${INPUT:l} # lowercase

  if [[ "$INPUT" == "$EXPECTED_KEY" ]]; then
    SCORE=$((SCORE + 100))
    COMBO=$((COMBO + 1))
    (( COMBO > MAX_COMBO )) && MAX_COMBO=$COMBO
    echo "😺 HIT +100 | combo $COMBO"
  else
    COMBO=0
    echo "😿 MISS | combo reset"
  fi
done

echo
echo "🏆 Session done! Score: $SCORE | Max combo: $MAX_COMBO"
echo "🐾 Cat mode complete."
