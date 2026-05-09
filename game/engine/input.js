import {mix} from './state.js';

addEventListener('keydown',e=>{
  mix.keys[e.key.toLowerCase()] = true;
});

addEventListener('keyup',e=>{
  mix.keys[e.key.toLowerCase()] = false;
});

addEventListener('mousemove',e=>{
  mix.mouse.x = e.clientX;
  mix.mouse.y = e.clientY;
});

addEventListener('mousedown',()=>{
  mix.mouse.down = true;
});

addEventListener('mouseup',()=>{
  mix.mouse.down = false;
});
