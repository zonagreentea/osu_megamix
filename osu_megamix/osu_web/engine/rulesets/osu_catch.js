import { Fruit } from "../drawable_objects.js";
import { Score } from "../scoring.js";
import { triggerDeath } from "../death_handler.js";
export class CatchRuleset{
constructor(){this.score=new Score();this.fruits=[new Fruit(100,0,500),new Fruit(200,0,1000)];this.canvas=document.getElementById("gameCanvas");this.ctx=this.canvas.getContext("2d");this.startTime=0;}
start(){this.startTime=performance.now();}
reset(){this.score.reset();this.fruits.forEach(f=>f.hit=false);}
update(){const now=performance.now()-this.startTime;for(let f of this.fruits){if(!f.hit && now>=f.time){f.hit=true;this.score.hit();if(triggerDeath(this.score)) this.reset();}}}
render(){this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);for(let f of this.fruits){if(!f.hit){this.ctx.fillStyle="green";this.ctx.beginPath();this.ctx.arc(f.x,f.y,15,0,2*Math.PI);this.ctx.fill();}}}
}
