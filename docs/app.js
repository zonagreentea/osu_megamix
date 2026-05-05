console.log("APP LOADED ✔");

const canvas = window.canvas;
const ctx = window.ctx;

/* heartbeat animation (PROVES RENDER WORKS) */
let t = 0;

function loop(){
  t++;

  ctx.clearRect(0,0,canvas.width,canvas.height);

  // 🔴 MUST SEE THIS OR NOTHING IS LOADING
  ctx.fillStyle = "red";
  ctx.fillRect(20,20,30,30);

  // moving circle (visual test)
  ctx.beginPath();
  ctx.arc(
    canvas.width/2 + Math.sin(t*0.02)*100,
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
