let bpm = 120;
let beatInterval = 60000 / bpm;
let lastBeat = -1;

let circles = [];

function spawn(){
  circles.push({
    x: Math.random()*canvas.width,
    y: 0,
    r: 18,
    v: 2
  });
}

window.osuTick = function(t){
  const beat = Math.floor(t / beatInterval);

  if(beat !== lastBeat){
    spawn();
    lastBeat = beat;
  }

  ctx.clearRect(0,0,canvas.width,canvas.height);

  for(let c of circles){
    c.y += c.v;
    ctx.beginPath();
    ctx.arc(c.x,c.y,c.r,0,Math.PI*2);
    ctx.fillStyle="white";
    ctx.fill();
  }

  circles = circles.filter(c=>c.y < canvas.height+50);
};
