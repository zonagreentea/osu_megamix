/* =========================
   OSU!MEGAMIX CORE ENGINE
   SINGLE LOOP • CLEAN STATE
========================= */

const canvas = window.canvas || document.querySelector("canvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

/* =========================
   MODE
========================= */
let mode = "osu";

/* =========================
   OSU STATE
========================= */
let bpm = 120;
let beatInterval = 60000 / bpm;
let lastBeat = -1;

let circles = [];

/* =========================
   CATCH STATE
========================= */
let catcherX = canvas.width / 2;
let targetX = catcherX;

/* =========================
   INPUT
========================= */
window.addEventListener("mousemove", (e) => {
  const rect = canvas.getBoundingClientRect();
  targetX = e.clientX - rect.left;
});

/* =========================
   SPAWN CIRCLE
========================= */
function spawnCircle() {
  circles.push({
    x: Math.random() * canvas.width,
    y: -20,
    r: 18,
    speed: 2 + Math.random() * 2
  });
}

/* =========================
   UPDATE OSU
========================= */
function updateOsu() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let c of circles) {
    c.y += c.speed;

    ctx.beginPath();
    ctx.arc(c.x, c.y, c.r, 0, Math.PI * 2);
    ctx.fillStyle = "white";
    ctx.fill();
  }

  circles = circles.filter(c => c.y < canvas.height + 50);
}

/* =========================
   UPDATE CATCH
========================= */
function updateCatch() {
  catcherX += (targetX - catcherX) * 0.2;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "white";
  ctx.fillRect(catcherX - 40, canvas.height - 60, 80, 20);
}

/* =========================
   MAIN LOOP (ONLY ONE)
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
   MODE SWITCH
========================= */
window.setMode = (m) => {
  mode = m;

  // hard reset state to prevent drift bugs
  circles = [];
  lastBeat = -1;
  catcherX = canvas.width / 2;
  targetX = catcherX;

  console.log("mode:", mode);
};
