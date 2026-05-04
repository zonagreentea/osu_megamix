function spawn(o){
let d=document.createElement("div");
d.style.position="absolute";
d.style.left=(o.lane*120||o.x||0)+"px";
d.style.top="0px";
d.style.width="20px";
d.style.height="20px";
d.style.background="white";
document.body.appendChild(d);
setTimeout(()=>d.remove(),1000);
}

function loop(mode){
let t=Stream.time();

for(let o of Beatmap.objects){
let obj=interpret(o,mode);
if(obj.t-t<100 && obj.t-t>-50) spawn(obj);
}

requestAnimationFrame(()=>loop(mode));
}
