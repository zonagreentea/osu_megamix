const canvas = document.getElementById("game");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

import { Game } from "./core/game.js";

const game = new Game();

function loop() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  game.update();
  game.render(ctx);

  requestAnimationFrame(loop);
}

loop();
