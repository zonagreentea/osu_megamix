let x = 0;
let target = 0;

window.addEventListener("mousemove",(e)=>{
  target = e.clientX;
});

window.catchTick = function(){
  x += (target - x) * 0.2;

  ctx.clearRect(0,0,canvas.width,canvas.height);

  ctx.fillStyle="white";
  ctx.fillRect(x-40,canvas.height-60,80,20);
};
