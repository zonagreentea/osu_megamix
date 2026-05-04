const canvas=document.createElement("canvas");
document.body.appendChild(canvas);
const ctx=canvas.getContext("2d");

function resize(){canvas.width=innerWidth;canvas.height=innerHeight}
addEventListener("resize",resize);resize();

function draw(c,t){

let dt=c.t-t;
let p=1-Math.max(0,Math.min(1,dt/1000));
let r=c.approach.startR-(c.approach.startR-c.approach.r)*p;

ctx.beginPath();
ctx.arc(c.x,c.y,r,0,Math.PI*2);
ctx.strokeStyle="rgba(255,255,255,0.3)";
ctx.stroke();

ctx.beginPath();
ctx.arc(c.x,c.y,c.r,0,Math.PI*2);
ctx.fillStyle=c.hit?"#00ff88":"white";
ctx.fill();
}

function loop(mode){
let t=Stream.time();

ctx.clearRect(0,0,canvas.width,canvas.height);

for(let o of Beatmap.objects){
if(!o.spawned && o.t-t<1000){
o.spawned=true;
spawn(o,mode);
}
}

for(let c of active){
draw(c,t);

let dt=c.t-t;

if(!c.hit && dt<-120){
c.hit=true;
Game.combo=0;
c.alpha=0.2;
}

if(c.hit)c.alpha*=0.95;
}

requestAnimationFrame(()=>loop(mode));
}
