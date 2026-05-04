window.active=[];

function spawn(o,mode){
let c={
x:200+o.lane*120,
y:300,
t:o.t,
r:mode==="mania"?15:20,
color:"white",
hit:false
};

if(mode==="taiko") c.color=o.note%2?"red":"blue";
if(mode==="catch") c.x=o.lane*180;

active.push(c);
}
