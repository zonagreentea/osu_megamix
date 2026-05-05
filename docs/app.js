const canvas = window.canvas;
const ctx = window.ctx;

let mode = "osu";

/* ===== OSU STATE ===== */
let bpm = 120;
let beatInterval = 60000 / bpm;
let lastBeat = -1;

let circles = [];

/* ===== CATCH STATE ===== */
let catcherX = canvas.width / 2;
let targetX = catcherX;

/* ===== INPUT ===== */
window.addEventListener("mousemove", (e) => {
  const r = canvas.getBoundingClientRect();
  targetX = e.clientX - r.left;
});

/* ===== SPAWN ===== */
function spawnCircle() {
  circles.push({
    x: Math.random() * canvas.width,
    y: -20,
    r: 18,
    v: 2
  });
}

/* ===== OSU UPDATE ===== */
function updateOsu() {
  ctx.clearRect(0,0,canvas.width,canvas.height);

  for (let c of circles) {
    c.y += c.v;

    ctx.beginPath();
    ctx.arc(c.x,c.y,c.r,0,Math.PI*2);
    ctx.fillStyle = "white";
    ctx.fill();
  }

  circles = circles.filter(c => c.y < canvas.height + 50);
}

/* ===== CATCH UPDATE ===== */
function updateCatch() {
  catcherX += (targetX - catcherX) * 0.2;

  ctx.clearRect(0,0,canvas.width,canvas.height);

  ctx.fillStyle = "white";
  ctx.fillRect(catcherX - 40, canvas.height - 60, 80, 20);
}

/* ===== MAIN LOOP ===== */
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

/* ===== MODE SWITCH ===== */
window.setMode = (m) => {
  mode = m;
  circles = [];
  lastBeat = -1;
};
