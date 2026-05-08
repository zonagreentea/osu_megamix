import { state } from '../core/state.js';

export function generateNotes() {

  for (let i = 0; i < 256; i++) {

    state.notes.push({
      time: i * 500,
      x: 200 + Math.sin(i * 0.4) * 300,
      y: 240 + Math.cos(i * 0.7) * 160,
      hit: false
    });
  }
}
