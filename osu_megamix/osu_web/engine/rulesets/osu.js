import { HitCircle } from "../drawable_objects.js";
import { Score } from "../scoring.js";
import { triggerDeath } from "../death_handler.js";
export class OsuRuleset{
constructor(){this.score=new Score();this.hitObjects=[new HitCircle(100,100,1000),new HitCircle(300,200,2000)];this.canvas=document.getElementById("gameCanvas");this.ctx=this.canvas.getContext("2d");this.startTime=0;document.addEventListener("keydown",e=>{this.hitInput(e);});}
start(){this.startTime=performance.now();}
reset(){this.score.reset();this.hitObjects.forEach(o=>o.hit=false);}
hitInput(e){for(let o of this.hitObjects){if(!o.hit && e.code==="Space" && performance.now()-this.startTime>=o.time){o.hit=true;this.score.hit();if(triggerDeath(this.score)) this.reset();}}}
update(){}
render(){this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);for(let o of this.hitObjects){if(!o.hit){this.ctx.strokeStyle="white";this.ctx.beginPath();this.ctx.arc(o.x,o.y,20,0,2*Math.PI);this.ctx.stroke();}}}
}
