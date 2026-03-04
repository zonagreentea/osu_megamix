import { TaikoNote } from "../drawable_objects.js";
import { Score } from "../scoring.js";
import { triggerDeath } from "../death_handler.js";

export class TaikoRuleset {
  constructor(){ this.score=new Score(); this.notes=[new TaikoNote(500,'red'), new TaikoNote(1000,'blue')]; this.startTime=0; this.canvas=document.getElementById("gameCanvas"); this.ctx=this.canvas.getContext("2d"); }
  start(){ this.startTime=performance.now(); }
  reset(){ this.score.reset(); this.notes.forEach(n=>n.hit=false); }
  update(){ const now=performance.now()-this.startTime; this.notes.forEach(n=>{ if(!n.hit && now>=n.time){ n.hit=true; this.score.hit(); if(triggerDeath(this.score)) this.reset(); } }); }
  render(){ this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height); this.notes.forEach(n=>{ if(!n.hit){ this.ctx.fillStyle=n.type=='red'?'red':'blue'; this.ctx.fillRect(100,100,30,30); } }); }
}
