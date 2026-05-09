import {mix} from '../engine/state.js';

mix.systems.scheduler = ()=>{

  while(
    mix.chartIndex < mix.chart.length &&
    mix.chart[mix.chartIndex].t <
    mix.time + 2000
  ){

    const src =
      mix.chart[mix.chartIndex++];

    const n =
      mix.pool.pop() || {};

    Object.assign(n,src);

    n.hit = false;

    mix.notes.push(n);
  }
};
