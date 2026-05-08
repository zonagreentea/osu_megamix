import { state } from '../core/state.js';

const canvas = document.querySelector('canvas');
const ctx = canvas.getContext('2d');

export function resize() {
  canvas.width = innerWidth;
  canvas.height = innerHeight;
}

addEventListener('resize', resize);
resize();

export function render() {

  ctx.clearRect(0,0,canvas.width,canvas.height);

  for (const n of state.notes) {

    if (n.hit) continue;

    ctx.beginPath();
    ctx.arc(n.x, n.y, 40, 0, Math.PI * 2);
    ctx.stroke();
  }

  ctx.fillText(
    'score: ' + state.score,
    20,
    40
  );

  ctx.fillText(
    'combo: ' + state.combo,
    20,
    70
  );
}
