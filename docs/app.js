console.log("APP LOADED");

const canvas = window.canvas;
const ctx = window.ctx;

let mode = "osu";

/* state */
let circles = [];
let catcherX = canvas.width / 2;
let targetX = catcherX;

/* input */
window.addEventListener("mousemove", e => {
  const r = canvas.getBoundingClientRect();
  targetX = e.clientX - r.left;
});

/* spawn */
function spawn(){
  circles.push({
    x: Math.random()*canvas.width,
    y: -10,
    r: 18,
    v: 2
  });
}

/* loop */
function loop(t){

  ctx.clearRect(0,0,canvas.width,canvas.height);

  /* 🔥 DEBUG VISUAL (THIS MUST SHOW EVEN IF GAME FAILS) */
  ctx.fillStyle = "red";
  ctx.fillRect(10,10,20,20);

  if(mode === "osu"){
    if(Math.floor(t/500) % 60 === 0){
      spawn();
    }

    for(let c of circles){
      c.y += c.v;
      ctx.beginPath();
      ctx.arc(c.x,c.y,c.r,0,Math.PI*2);
      ctx.fillStyle="white";
      ctx.fill();
    }
  }

  if(mode === "catch"){
    catcherX += (targetX - catcherX) * 0.25;

    ctx.fillStyle="white";
    ctx.fillRect(catcherX-40, canvas.height-60, 80, 20);
  }

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);

window.setMode = m => {
  mode = m;
  circles = [];
};
