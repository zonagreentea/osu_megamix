<<<<<<< HEAD
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
=======
const canvas = window.canvas;
const ctx = window.ctx;

/* =========================
   ENGINE STATE
========================= */
let mode = "osu";

/* OSU */
let bpm = 120;
let beatInterval = 60000 / bpm;
let lastBeat = -1;
let circles = [];

/* CATCH */
let catcherX = canvas.width / 2;
let targetX = catcherX;

/* =========================
   INPUT FIX
========================= */
window.addEventListener("mousemove", (e) => {
  const r = canvas.getBoundingClientRect();
  targetX = e.clientX - r.left;
});

/* =========================
   REAL OSU SPAWN (NO SINE, NO FAKE MOTION)
========================= */
function spawnCircle(){
  circles.push({
    x: Math.random() * canvas.width,
    y: -10,
    r: 18,
    v: 2
  });
}

/* =========================
   OSU UPDATE (TRUE FALLING OBJECTS)
========================= */
function updateOsu(){
  for (let c of circles) {
    c.y += c.v;

    ctx.beginPath();
    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
    ctx.fillStyle = "white";
    ctx.fill();
  }

  circles = circles.filter(c => c.y < canvas.height + 50);
}

/* =========================
   CATCH UPDATE (SMOOTH ONLY, NO SWING)
========================= */
function updateCatch(){
  catcherX += (targetX - catcherX) * 0.25;

  ctx.fillStyle = "white";
  ctx.fillRect(catcherX - 40, canvas.height - 60, 80, 20);
}

/* =========================
   MAIN LOOP (ONLY ONE SOURCE OF TRUTH)
========================= */
function loop(t){

  ctx.clearRect(0,0,canvas.width,canvas.height);

  if(mode === "osu"){
    const beat = Math.floor(t / beatInterval);

    if(beat !== lastBeat){
      spawnCircle();
      lastBeat = beat;
    }

    updateOsu();
  }

  if(mode === "catch"){
    updateCatch();
  }
>>>>>>> bb605ba (init: clean megamix reset)

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);
<<<<<<< HEAD
=======

/* =========================
   MODE SWITCH RESET
========================= */
window.setMode = (m) => {
  mode = m;
  circles = [];
  lastBeat = -1;
};
>>>>>>> bb605ba (init: clean megamix reset)
