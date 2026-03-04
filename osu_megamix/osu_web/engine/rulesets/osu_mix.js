import { HitCircle, Slider, Spinner, SliderPoint } from "../drawable_objects.js";
import { Score } from "../scoring.js";
import { triggerDeath } from "../death_handler.js";

export class OsuMixRuleset{
constructor(){
this.score=new Score();
this.hitObjects=[
new HitCircle(100,100,1000),
new Slider([new SliderPoint(200,150),new SliderPoint(400,150)],2000),
new Spinner(3000)
];
this.canvas=document.getElementById("gameCanvas");
this.ctx=this.canvas.getContext("2d");
this.startTime=0;
document.addEventListener("keydown",e=>{this.hitInput(e);});
}
start(){this.startTime=performance.now();}
reset(){this.score.reset();this.hitObjects.forEach(o=>o.hit=false);}
hitInput(e){
for(let o of this.hitObjects){
if(!o.hit && e.code==="Space" && performance.now()-this.startTime>=o.time){
o.hit=true;this.score.hit();if(triggerDeath(this.score)) this.reset();
}}
}
update(){}
render(){
this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);
for(let o of this.hitObjects){
if(!o.hit){this.ctx.strokeStyle="white";
if(o instanceof HitCircle){this.ctx.beginPath();this.ctx.arc(o.x,o.y,20,0,2*Math.PI);this.ctx.stroke();}
else if(o instanceof Slider){this.ctx.beginPath();this.ctx.moveTo(o.points[0].x,o.points[0].y);for(let i=1;i<o.points.length;i++)this.ctx.lineTo(o.points[i].x,o.points[i].y);this.ctx.stroke();}
else if(o instanceof Spinner){let r=40+10*Math.sin((performance.now()-this.startTime)/100);this.ctx.beginPath();this.ctx.arc(400,300,r,0,2*Math.PI);this.ctx.stroke();}}}}
}
