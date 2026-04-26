
/* =========================
   🧠 STATE
========================= */

let state = "menu";
let startTime = 0;

let objects = [];
let score = 0;
let combo = 0;

const MODES = ["osu","taiko","catch","mania"];
let modeIndex = 0;

/* =========================
   ⏱ TIME CORE
========================= */

function now(){
  return Date.now() - startTime;
}

/* =========================
   🎮 START GAME
========================= */

document.getElementById("menu").onclick = () => {
  state = "play";
  document.getElementById("menu").style.display = "none";

  startTime = Date.now();
  objects = [];
  score = 0;
  combo = 0;

  loop();
};

/* =========================
   🌊 PLAYER
========================= */

let player = {
  x: innerWidth/2,
  vx: 0,
  aimX: innerWidth/2
};

window.addEventListener("keydown",(e)=>{
  if(state !== "play") return;

  if(e.key === "z") player.vx -= 1.2;
  if(e.key === "x") player.vx += 1.2;
});

window.addEventListener("mousemove",(e)=>{
  player.aimX = e.clientX;
});

function aim(){
  return player.x * 0.7 + player.aimX * 0.3;
}

/* =========================
   ⚖️ JUDGEMENT
========================= */

function judge(dt){
  dt = Math.abs(dt);

  if(dt < 80) return 300;
  if(dt < 160) return 100;
  if(dt < 260) return 50;

  return -200;
}

/* =========================
   💀 BUST
========================= */

function bust(){
  state = "menu";
  document.getElementById("menu").style.display = "flex";
  document.querySelectorAll(".note").forEach(n=>n.remove());
}

/* =========================
   🎲 SPAWN
========================= */

function spawn(){
  if(Math.random() > 0.02) return;

  const mode = MODES[modeIndex];
  modeIndex = (modeIndex + 1) % MODES.length;

  objects.push({
    mode,
    x: Math.random()*innerWidth,
    y: 0,
    lane: Math.floor(Math.random()*4),
    time: now() + 1600
  });
}

/* =========================
   🎮 MODE LOGIC
========================= */

function update(o){
  if(o.mode === "osu") o.scale = (o.time - now()) / 1600;
  if(o.mode === "taiko") o.x -= 6;
  if(o.mode === "mania") o.y += 6;
  if(o.mode === "catch") o.y += 5;
}

/* =========================
   🎯 INPUT
========================= */

window.addEventListener("mousedown",()=>{

  if(state !== "play") return;
  if(objects.length === 0) return;

  const t = now();
  const o = objects.shift();

  const dx = Math.abs(o.x - aim());
  const dt = Math.abs(o.time - t);

  let result = judge(dt) * (1 - dx/500);

  if(result < -100){
    bust();
    return;
  }

  score += result;
  combo++;
});

/* =========================
   🌊 PLAYER UPDATE
========================= */

function updatePlayer(){
  player.vx *= 0.85;
  player.x += player.vx;

  player.x = Math.max(0, Math.min(innerWidth, player.x));

  document.getElementById("player").style.left = player.x + "px";
}

/* =========================
   🎮 OBJECT UPDATE
========================= */

function updateObjects(){
  const t = now();

  objects.forEach(update);

  objects = objects.filter(o=>{
    if(t - o.time > 400){
      combo = 0;
      return false;
    }
    return true;
  });
}

/* =========================
   🎨 RENDER
========================= */

function render(){

  document.querySelectorAll(".note").forEach(n=>n.remove());

  objects.forEach(o=>{
    const el = document.createElement("div");
    el.className = "note";

    if(o.mode==="osu") el.textContent="●";
    if(o.mode==="taiko") el.textContent="◎";
    if(o.mode==="catch") el.textContent="●";
    if(o.mode==="mania") el.textContent="■";

    el.style.left = o.x + "px";
    el.style.top = o.y + "px";

    document.body.appendChild(el);
  });

  document.getElementById("hud").innerText =
    "score:"+Math.floor(score)+
    " combo:"+combo+
    " mode:"+MODES[modeIndex];
}

/* =========================
   🔁 LOOP
========================= */

function loop(){

  if(state !== "play") return;

  updatePlayer();
  spawn();
  updateObjects();
  render();

  requestAnimationFrame(loop);
}
