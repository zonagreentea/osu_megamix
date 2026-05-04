function interpret(o,mode){
if(mode==="osu") return {t:o.t,l:o.lane};
if(mode==="taiko") return {t:o.t,type:o.note%2?"don":"ka"};
if(mode==="catch") return {t:o.t,x:o.lane*180};
return {t:o.t,lane:o.lane};
}
