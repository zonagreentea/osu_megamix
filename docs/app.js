/* =========================
   MEGAMIX CORE FIXED LOOP
========================= */

const canvas = window.canvas || document.querySelector("canvas");
const ctx = window.ctx || canvas.getContext("2d");

let mode = "osu";

/* ===== OSU STATE ===== */
let bpm = 120;
let beatInterval = 60000 / bpm;
let lastBeat = -1;

/* ===== CATCH STATE ===== */
let catcherX = 0;
let targetX = 0;

/* =========================
   INPUT (single source)
========================= */
window.addEventListener("mousemove", (e) => {
  const rect = canvas.getBoundingClientRect();
  targetX = e.clientX - rect.left;
});

/* =========================
   OSU SPAWN (1 per beat)
========================= */
function spawnCircle() {
  console.log("spawn");
}

/* =========================
   CATCH UPDATE
========================= */
function updateCatch() {
  catcherX += (targetX - catcherX) * 0.25;
}

/* =========================
   DRAW CATCH (minimal test)
========================= */
function drawCatch() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "white";
  ctx.fillRect(catcherX, canvas.height - 50, 80, 20);
}

/* =========================
   MAIN LOOP (ONE ONLY)
========================= */
function loop(t) {
  if (mode === "osu") {
    const beat = Math.floor(t / beatInterval);

    if (beat !== lastBeat) {
      spawnCircle();
      lastBeat = beat;
    }
  }

  if (mode === "catch") {
    updateCatch();
    drawCatch();
  }

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);

/* =========================
   DEBUG SWITCH
========================= */
window.setMode = (m) => {
  mode = m;

  // hard reset prevents ghost state bugs
  lastBeat = -1;
  catcherX = 0;
  targetX = 0;

  console.log("mode:", mode);
};
