import "../modes/osu.js";
import "../modes/catch.js";

window._tick = function(t, mode){
  if(mode === "osu") window.osuTick?.(t);
  if(mode === "catch") window.catchTick?.(t);
};
