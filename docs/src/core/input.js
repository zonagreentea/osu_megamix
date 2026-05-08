import { state } from './state.js';

export function setupInput() {

  addEventListener('keydown', e => {
    if (e.key === 'z') state.input.z = true;
    if (e.key === 'x') state.input.x = true;
  });

  addEventListener('keyup', e => {
    if (e.key === 'z') state.input.z = false;
    if (e.key === 'x') state.input.x = false;
  });

  addEventListener('mousedown', e => {
    if (e.button === 0) state.input.mouse1 = true;
  });

  addEventListener('mouseup', e => {
    if (e.button === 0) state.input.mouse1 = false;
  });

  addEventListener('mousemove', e => {
    state.input.mouseX = e.clientX;
    state.input.mouseY = e.clientY;
  });
}
