const canvas = document.querySelector("canvas");
const ctx = canvas.getContext("2d");

canvas.width = innerWidth;
canvas.height = innerHeight;

let mode = "osu";

/* =========================
   STRICT TIME BASE (fix spam)
========================= */
let bpm = 120;
let beatInterval = 60000 / bpm;
let lastBeat = -1;

/* =========================
   OSU OBJECTS
========================= */
let circles = [];

/* =========================
   CATCH STATE (FIXED INPUT)
========================= */
let catcherX = canvas.width / 2;
let targetX = catcherX;

/* =========================
   INPUT (fix broken tracking)
========================= */
window.addEventListener("mousemove", (e) => {
  const rect = canvas.getBoundingClientRect();
  targetX = e.clientX - rect.left;
});

/* =========================
   SPAWN (NO FRAME DRIFT)
========================= */
function spawnCircle() {
  circles.push({
    x: Math.random() * canvas.width,
    y: -20,
    r: 18,
    v: 2
  });
}

/* =========================
   OSU UPDATE
========================= */
function updateOsu() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

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
   CATCH UPDATE (FIXED MOVE)
========================= */
function updateCatch() {
  catcherX += (targetX - catcherX) * 0.2;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "white";
  ctx.fillRect(catcherX - 40, canvas.height - 60, 80, 20);
}

/* =========================
   MAIN LOOP (ONLY ONE SOURCE)
========================= */
function loop(t) {
  if (mode === "osu") {
    const beat = Math.floor(t / beatInterval);

    if (beat !== lastBeat) {
      spawnCircle();
      lastBeat = beat;
    }

    updateOsu();
  }

  if (mode === "catch") {
    updateCatch();
  }

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);

/* =========================
   MODE SWITCH RESET
========================= */
window.setMode = (m) => {
  mode = m;

  circles = [];
  lastBeat = -1;

  catcherX = canvas.width / 2;
  targetX = catcherX;
};
