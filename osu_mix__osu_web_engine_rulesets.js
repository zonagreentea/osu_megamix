import { HitCircle, Slider, Spinner, SliderPoint } from "../drawable_objects.js";
import { Score } from "../scoring.js";
import { triggerDeath } from "../death_handler.js";

export class OsuMixRuleset {
  constructor(){
    this.score = new Score();
    this.hitObjects = [
      new HitCircle(100,100,500),
      new Slider([new SliderPoint(150,150), new SliderPoint(300,150)], 1000),
      new Spinner(1500)
    ];
    this.startTime = 0;
    this.canvas = document.getElementById("gameCanvas");
    this.ctx = this.canvas.getContext("2d");
  }
  start(){ this.startTime = performance.now(); }
  reset(){ this.score.reset(); this.hitObjects.forEach(o=>o.hit=false); }
  update(){
    const now = performance.now() - this.startTime;
    this.hitObjects.forEach(obj=>{
      if(!obj.hit && now >= obj.time){
        obj.hit = true;
        this.score.hit();
        if(triggerDeath(this.score)) this.reset();
      }
    });
  }
  render(){
    this.ctx.clearRect(0,0,this.canvas.width,this.canvas.height);
    this.hitObjects.forEach(obj=>{
      if(!obj.hit){
        this.ctx.strokeStyle="white";
        if(obj instanceof HitCircle){
          this.ctx.beginPath(); this.ctx.arc(obj.x,obj.y,20,0,2*Math.PI); this.ctx.stroke();
        } else if(obj instanceof Slider){
          this.ctx.beginPath(); this.ctx.moveTo(obj.points[0].x,obj.points[0].y);
          for(let i=1;i<obj.points.length;i++) this.ctx.lineTo(obj.points[i].x,obj.points[i].y);
          this.ctx.stroke();
        } else if(obj instanceof Spinner){
          let r=40+10*Math.sin((performance.now()-this.startTime)/100);
          this.ctx.beginPath(); this.ctx.arc(400,300,r,0,2*Math.PI); this.ctx.stroke();
        }
      }
    });
  }
}
