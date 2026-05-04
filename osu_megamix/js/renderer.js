const canvas = document.createElement("canvas");
document.body.appendChild(canvas);
const ctx = canvas.getContext("2d");

function resize(){
  canvas.width = innerWidth;
  canvas.height = innerHeight;
}
addEventListener("resize", resize);
resize();

function loop(){
  ctx.clearRect(0,0,canvas.width,canvas.height);

  ctx.fillStyle="white";
  ctx.fillText("osu!megamix: " + getModeName(),20,30);

  requestAnimationFrame(loop);
}

loop();
