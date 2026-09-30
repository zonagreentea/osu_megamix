#!/bin/zsh
stty -echo -icanon time 0 min 0; trap 'stty sane; clear; exit' INT TERM
cols=$(tput cols); rows=$(tput lines); HIT=$((rows-6)); FRAME=0.04; SONG=75
LANES=4; BASE=9; tick=0; score=0; combo=0; maxc=0; miss=0; fever=0
typeset -a notes; start=$(date +%s)
lane_col(){ echo $(( (cols/LANES)*$1 + (cols/LANES)/2 )); }
spawn(){ l=$((RANDOM%LANES)); t=$((RANDOM%7==0)); notes+=("$l:0:$t"); }
draw(){
 clear; e=$(( $(date +%s)-start ))
 printf "osu!Megamix v2 | %02d/%02d | %07d | combo %d | miss %d | fever %d\n\n" $e $SONG $score $combo $miss $fever
 for ((r=0;r<rows-4;r++)); do
  line=""
  for ((c=0;c<cols;c++)); do
   ch=$([[ $r -eq $HIT ]] && echo "═" || echo " ")
   for n in "${notes[@]}"; do IFS=: read l y t <<< "$n"; lc=$(lane_col $l)
    if [[ $y -eq $r && $lc -eq $c ]]; then
      ch=$([[ $t -eq 1 ]] && echo "◯" || echo "●")
    fi
   done; line+="$ch"
  done; print "$line"
 done
}
while true; do
 now=$(date +%s); (( now-start>=SONG )) && break
 rate=$(( BASE - tick/180 - fever/20 )); (( rate<2 )) && rate=2
 (( tick % rate == 0 )) && spawn
 read -k 1 k
 new=(); hit=false
 for n in "${notes[@]}"; do IFS=: read l y t <<< "$n"; y=$((y+1))
  if [[ -n "$k" && $y -ge $HIT-1 && $y -le $HIT+1 && $hit == false ]]; then
   hit=true; ((combo++)); ((combo>maxc))&&maxc=$combo
   ((fever+=combo>=10?1:0))
   ((score+= (100+fever*20)*combo))
   [[ $t -eq 1 ]] && new+=("$l:$y:1")
  elif (( y > HIT+1 )); then ((miss++)); combo=0; ((fever>0))&&fever=$((fever-1))
  else new+=("$l:$y:$t")
  fi
 done
 notes=("${new[@]}"); [[ -n "$k" && $hit == false ]] && { ((miss++)); combo=0; ((fever>0))&&fever=$((fever-1)); }
 tick=$((tick+1)); draw; sleep $FRAME
done
clear; printf "V2 COMPLETE\nScore %d\nMax Combo %d\nMisses %d\nPeak Fever %d\n" $score $maxc $miss $fever; stty sane
