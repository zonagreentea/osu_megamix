window.keys={};

addEventListener("click",e=>{

let t=Stream.time();

for(let c of active){

let dx=c.x-e.clientX;
let dy=c.y-e.clientY;
let dist=Math.sqrt(dx*dx+dy*dy);

let dt=c.t-t;

if(!c.hit && dist<40){
let g=judge(dt);

if(g){
c.hit=true;
Game.score+=g;
Game.combo++;
tick();
}
}
}
});
