const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const lanes = 4;
const laneWidth = canvas.width / lanes;
const hitLineY = canvas.height - 150;

let notes = [];
let score = 0;

const keys = {
  d: 0,
  f: 1,
  j: 2,
  k: 3
};

document.addEventListener("keydown", (e) => {
  const lane = keys[e.key];
  if (lane !== undefined) {
    checkHit(lane);
  }
});

function spawnNote() {
  const lane = Math.floor(Math.random() * lanes);
  notes.push({
    lane,
    y: -20,
    speed: 4
  });
}

function checkHit(lane) {
  for (let i = 0; i < notes.length; i++) {
    const n = notes[i];
    if (n.lane === lane && Math.abs(n.y - hitLineY) < 30) {
      notes.splice(i, 1);
      score += 100;
      return;
    }
  }
}

function update() {
  notes.forEach(n => n.y += n.speed);
  notes = notes.filter(n => n.y < canvas.height);
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // lanes
  for (let i = 0; i < lanes; i++) {
    ctx.strokeStyle = "#222";
    ctx.strokeRect(i * laneWidth, 0, laneWidth, canvas.height);
  }

  // hit line
  ctx.fillStyle = "white";
  ctx.fillRect(0, hitLineY, canvas.width, 5);

  // notes
  ctx.fillStyle = "lime";
  notes.forEach(n => {
    ctx.fillRect(
      n.lane * laneWidth + laneWidth * 0.2,
      n.y,
      laneWidth * 0.6,
      20
    );
  });

  // score
  ctx.fillStyle = "white";
  ctx.font = "24px Arial";
  ctx.fillText("Score: " + score, 20, 40);
}

function gameLoop() {
  update();
  draw();
  requestAnimationFrame(gameLoop);
}

setInterval(spawnNote, 600);
gameLoop();
