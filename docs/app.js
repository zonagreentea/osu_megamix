console.log("APP LOADED ✔");

const canvas = window.canvas;
const ctx = window.ctx;

let t = 0;

function loop(){
  t++;

  ctx.clearRect(0,0,canvas.width,canvas.height);

  // 🔴 VISUAL PROOF (you MUST see this)
  ctx.fillStyle = "red";
  ctx.fillRect(20,20,30,30);

  // spinning circle (visual fallback)
  ctx.beginPath();
  ctx.arc(
    canvas.width/2 + Math.sin(t*0.02)*120,
    canvas.height/2,
    20,
    0,
    Math.PI*2
  );
  ctx.fillStyle = "white";
  ctx.fill();

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);
