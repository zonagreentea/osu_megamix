import "../modes/router.js";

let mode = "osu";

window.setMode = (m) => mode = m;

function loop(t){
  window._tick?.(t, mode);
  requestAnimationFrame(loop);
}

requestAnimationFrame(loop);
