window.osuJudge=(e,t)=>{
let dt=Math.abs(e.t-t);
return dt<50?"SS":dt<100?"S":dt<160?"A":null;
};
