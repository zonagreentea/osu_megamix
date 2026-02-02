#!/bin/zsh

stty -echo -icanon time 0 min 0
trap 'stty sane; clear; exit' INT TERM

cols=$(tput cols)
rows=$(tput lines)

SONG_LEN=60        # seconds
HIT_LINE=$((rows-6))
NOTE_RATE=8        # lower = harder
FRAME=0.05

typeset -a notes
start_time=$(date +%s)

score=0
combo=0
max_combo=0
misses=0
tick=0

spawn_note() {
  col=$((RANDOM % (cols-2) + 1))
  notes+=("$col:0")
}

draw() {
  clear
  elapsed=$(( $(date +%s) - start_time ))
  printf "osu!Megamix | time %02d/%02d | score %06d | combo %d | misses %d\n\n" \
    $elapsed $SONG_LEN $score $combo $misses

  for ((r=0;r<rows-4;r++)); do
    line=""
    for ((c=0;c<cols;c++)); do
      char=" "
      if (( r == HIT_LINE )); then
        char="-"
      fi
      for n in "${notes[@]}"; do
        IFS=: read nc nr <<< "$n"
        if (( nr == r && nc == c )); then
          char="●"
        fi
      done
      line+="$char"
    done
    print "$line"
  done

  print "\nHit ANY key on the line. Ctrl+C to quit."
}

while true; do
  now=$(date +%s)
  (( now - start_time >= SONG_LEN )) && break

  if (( tick % NOTE_RATE == 0 )); then
    spawn_note
  fi

  read -k 1 key

  new_notes=()
  hit=false

  for n in "${notes[@]}"; do
    IFS=: read nc nr <<< "$n"
    nr=$((nr+1))

    if [[ -n "$key" && $nr -ge $HIT_LINE-1 && $nr -le $HIT_LINE+1 && $hit == false ]]; then
      hit=true
      ((combo++))
      ((combo > max_combo)) && max_combo=$combo
      ((score += 100 * combo))
    elif (( nr > HIT_LINE+1 )); then
      ((misses++))
      combo=0
    else
      new_notes+=("$nc:$nr")
    fi
  done

  notes=("${new_notes[@]}")

  if [[ -n "$key" && $hit == false ]]; then
    ((misses++))
    combo=0
  fi

  draw
  tick=$((tick+1))
  sleep $FRAME
done

clear
printf "RUN COMPLETE\n\n"
printf "Score: %d\n" $score
printf "Max Combo: %d\n" $max_combo
printf "Misses: %d\n\n" $misses
printf "Thanks for playing osu!Megamix 💿\n"

stty sane
