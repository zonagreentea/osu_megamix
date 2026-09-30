import { ManiaNote } from "../drawable_objects.js";
import { Score } from "../scoring.js";
import { triggerDeath } from "../death_handler.js";
export class ManiaRuleset{
constructor(){this.score=new Score();this.notes=[new ManiaNote(0,500,0),new ManiaNote(1,1000,400),new ManiaNote(2,1500,0),new ManiaNote(3,1800,600)];this.canvas=document.getElementById("gameCanvas");this.ctx=this.canvas.getContext("2d");this.startTime=0;}
start(){this.startTime=performance.now();}
reset(){this.score.reset();this.notes.forEach(n=>n.hit=false);}
update(){const now=performance.now()-this.startTime;for(let n of this.notes){if(!n.hit && now>=n.time){n.hit=true;this.score.hit();if(triggerDeath(this.score)) this.reset();}if(n.duration && now>=n.time && now<=n.time+n.duration){this.score.hit(1);}}}
render(){this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);for(let n of this.notes){if(!n.hit||(n.duration && performance.now()-this.startTime<=n.time+n.duration)){this.ctx.fillStyle="yellow";let x=100+n.lane*50;let y=100;if(n.duration){let h=n.duration/2;this.ctx.fillRect(x,y,20,h);}else{this.ctx.fillRect(x,y,20,50);}}}}
}
