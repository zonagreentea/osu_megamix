import { setupInput } from './input.js';
import { loadAudio, playAudio, updateAudio } from './audio.js';

import { render } from '../render/renderer.js';

import { osuRuleset } from '../rulesets/osu.js';

import { generateNotes } from '../data/proceduralGenerator.js';

setupInput();

generateNotes();

loadAudio('./song.mp3');

addEventListener('click', () => {
  playAudio();
}, { once: true });

function frame() {

  updateAudio();

  osuRuleset.update();

  render();

  requestAnimationFrame(frame);
}

requestAnimationFrame(frame);
