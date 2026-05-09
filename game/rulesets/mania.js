import {mix} from '../engine/state.js';

mix.rulesets.mania = {

  update(n){

    n.y =
      (n.t - mix.time) * .7;
  },

  render(n){

    const ctx = mix.ctx;

    const lanes = 4;
    const laneW =
      mix.canvas.width / lanes;

    ctx.fillStyle = '#fff';

    ctx.fillRect(
      n.lane * laneW + 8,
      n.y,
      laneW - 16,
      20
    );

    const binds =
      ['z','x','c','v'];

    if(
      mix.keys[
        binds[n.lane]
      ] &&
      Math.abs(
        n.y -
        (mix.canvas.height-140)
      ) < 30
    ){

      n.hit = true;

      mix.score += 300;
      mix.combo++;

      mix.camera.shake += 1;
    }

    if(
      n.y > mix.canvas.height &&
      !n.hit
    ){

      n.hit = true;

      mix.combo = 0;
      mix.hp -= 8;
    }
  }
};
