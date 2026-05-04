function loop(mode){

let t=Stream.time();

for(let o of Beatmap.objects){
if(!o.spawned && o.t-t<1000){
o.spawned=true;
spawn(o,mode);
}
}

for(let c of active){

let dt=c.t-t;

if(keys[" "] && !c.hit){
let s=judge(dt);
if(s){
c.hit=true;
Game.score+=s;
Game.combo++;
}
}
}

requestAnimationFrame(()=>loop(mode));
}

addEventListener("keydown",async()=>{
if(!window.started){
window.started=true;
if(window.AudioCtx) await AudioCtx.resume();
loop("osu");
}
});
