#!/bin/zsh
stty -echo -icanon time 0 min 0; trap 'stty sane; clear; exit' INT TERM
cols=$(tput cols); rows=$(tput lines); HIT=$((rows-6)); FRAME=0.05; SONG=60
LANES=4; BPM=120; BASE=10; tick=0; score=0; combo=0; maxc=0; miss=0
typeset -a notes; start=$(date +%s)
lane_col(){ echo $(( (cols/LANES)*$1 + (cols/LANES)/2 )); }
spawn(){ l=$((RANDOM%LANES)); h=$((RANDOM%5==0)); notes+=("$l:0:$h"); }
draw(){
 clear; e=$(( $(date +%s)-start ))
 printf "osu!Megamix | %02d/%02d | %06d | combo %d | miss %d\n\n" $e $SONG $score $combo $miss
 for ((r=0;r<rows-4;r++)); do
  line=""
  for ((c=0;c<cols;c++)); do
   ch=$([[ $r -eq $HIT ]] && echo "—" || echo " ")
   for n in "${notes[@]}"; do IFS=: read l y h <<< "$n"; lc=$(lane_col $l)
    if [[ $y -eq $r && $lc -eq $c ]]; then
      ch=$([[ $h -eq 1 ]] && echo "◯" || echo "●")
    fi
   done; line+="$ch"
  done; print "$line"
 done
}
while true; do
 now=$(date +%s); (( now-start>=SONG )) && break
 rate=$(( BASE - tick/200 )); (( rate<3 )) && rate=3
 (( tick % rate == 0 )) && spawn
 read -k 1 k
 new=(); hit=false
 for n in "${notes[@]}"; do IFS=: read l y h <<< "$n"; y=$((y+1))
  if [[ -n "$k" && $y -ge $HIT-1 && $y -le $HIT+1 && $hit == false ]]; then
   hit=true; ((combo++)); ((combo>maxc))&&maxc=$combo; ((score+=100*combo))
   [[ $h -eq 1 ]] && new+=("$l:$y:1")
  elif (( y > HIT+1 )); then ((miss++)); combo=0
  else new+=("$l:$y:$h")
  fi
 done
 notes=("${new[@]}"); [[ -n "$k" && $hit == false ]] && { ((miss++)); combo=0; }
 tick=$((tick+1)); draw; sleep $FRAME
done
clear; printf "RESULTS\nScore %d\nMax Combo %d\nMisses %d\n" $score $maxc $miss; stty sane
