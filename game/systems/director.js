import {mix} from '../engine/state.js';

mix.systems.director = ()=>{

  const t = mix.time * .001;

  mix.density =
    1 +
    Math.sin(t*.1)*.5 +
    Math.sin(t*.27)*.3 +
    t*.002;

  if(mix.busted){
    mix.density *= .6;
  }

  if(mix.hp <= 0){

    mix.busted = true;
    mix.hp = 40;

    mix.camera.shake += 20;
  }

  if(mix.busted){

    mix.hp += .05;

    if(mix.hp > 70){
      mix.busted = false;
    }
  }
};
