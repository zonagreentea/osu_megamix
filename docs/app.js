const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
window.onresize = resize;
resize();

let t = 0;

function loop() {
  t += 0.016;
  ctx.clearRect(0,0,canvas.width,canvas.height);

  const x = canvas.width/2 + Math.sin(t)*200;
  const y = canvas.height/2;

  ctx.beginPath();
  ctx.arc(x,y,30,0,Math.PI*2);
  ctx.fillStyle = "white";
  ctx.fill();

  requestAnimationFrame(loop);
}

loop();
