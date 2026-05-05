const canvas = document.querySelector("canvas");
const ctx = canvas.getContext("2d");

canvas.width = innerWidth;
canvas.height = innerHeight;

let mode = "osu";

/* OSU STATE */
let bpm = 120;
let beatInterval = 60000 / bpm;
let lastBeat = -1;

let circles = [];

/* CATCH STATE */
let x = canvas.width / 2;
let target = x;

/* INPUT */
window.addEventListener("mousemove", (e) => {
  const r = canvas.getBoundingClientRect();
  target = e.clientX - r.left;
});

/* SPAWN */
function spawn() {
  circles.push({
    x: Math.random() * canvas.width,
    y: -10,
    r: 18,
    v: 2
  });
}

/* LOOP */
function loop(t) {
  if (mode === "osu") {
    const beat = Math.floor(t / beatInterval);

    if (beat !== lastBeat) {
      spawn();
      lastBeat = beat;
    }

    ctx.clearRect(0,0,canvas.width,canvas.height);

    for (let c of circles) {
      c.y += c.v;

      ctx.beginPath();
      ctx.arc(c.x, c.y, c.r, 0, Math.PI*2);
      ctx.fillStyle = "white";
      ctx.fill();
    }

    circles = circles.filter(c => c.y < canvas.height + 50);
  }

  if (mode === "catch") {
    x += (target - x) * 0.2; // THIS kills swing permanently

    ctx.clearRect(0,0,canvas.width,canvas.height);

    ctx.fillStyle = "white";
    ctx.fillRect(x - 40, canvas.height - 60, 80, 20);
  }

  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);

window.setMode = (m) => {
  mode = m;
  circles = [];
  lastBeat = -1;
};
