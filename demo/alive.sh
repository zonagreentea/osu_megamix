#!/bin/zsh

stty -echo -icanon time 0 min 0
trap 'stty sane; clear; exit' INT TERM

cols=$(tput cols)
rows=$(tput lines)
tick=0
score=0

draw() {
  clear
  printf "osu!Megamix — ALIVE  | score: %d\n\n" $score
  for ((i=0;i<rows-4;i++)); do
    line=""
    for ((j=0;j<cols;j++)); do
      if (( (i+j+tick) % 17 == 0 )); then
        line+="●"
      elif (( (i*j+tick) % 97 == 0 )); then
        line+="✦"
      else
        line+=" "
      fi
    done
    print "$line"
  done
  print "\npress keys. ctrl+c to quit."
}

while true; do
  read -k 1 key
  if [[ -n "$key" ]]; then
    ((score+=10))
    tick=$((tick+5))
  else
    tick=$((tick+1))
  fi
  draw
  sleep 0.05
done
