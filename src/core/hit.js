import {state} from './state.js';

export function resolveHit(t){
  let hit=false;

  state.notes.forEach(n=>{
    if(!n.h && Math.abs(n.t - t) < 10){
      n.h = true;
      state.score += 300;
      state.combo += 1;
      state.hp = Math.min(100, state.hp + 2);
      hit = true;
    }
  });

  if(!hit){
    state.combo = 0;
    state.hp -= 10;
  }
}

export function updateMisses(t){
  state.notes.forEach(n=>{
    if(!n.h && t - n.t > 15){
      n.h = true;
      state.combo = 0;
      state.hp -= 10;
      n.missed = true;
    }
  });
}
