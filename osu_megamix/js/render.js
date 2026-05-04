function loop(){
let t=Stream.time();
for(let e of Megastream.events){
osuJudge(e,t);
megamixInterpret(e,{combo:0});
}
requestAnimationFrame(loop);
}
loop();
