import { state } from './state.js';

export let audio = null;

export function loadAudio(src) {
  audio = new Audio(src);
  audio.volume = 0.7;
}

export function playAudio() {
  if (audio) audio.play();
}

export function updateAudio() {
  if (!audio) return;
  state.audio.currentTime = audio.currentTime * 1000;
}
