import { state } from '../core/state.js';

export const osuRuleset = {

  update() {

    const t = state.audio.currentTime;

    for (const n of state.notes) {

      if (n.hit) continue;

      const d = Math.abs(n.time - t);

      if (
        d < 80 &&
        (
          state.input.z ||
          state.input.x ||
          state.input.mouse1
        )
      ) {
        n.hit = true;
        state.score += 300;
        state.combo += 1;
      }

      if (t - n.time > 120 && !n.hit) {
        n.hit = true;
        state.combo = 0;
      }
    }
  }
};
