import { OsuMixRuleset } from "./engine/rulesets/osu_mix.js";
import { TaikoRuleset } from "./engine/rulesets/taiko.js";
import { CatchRuleset } from "./engine/rulesets/catch.js";
import { ManiaRuleset } from "./engine/rulesets/mania.js";

const modes = {
  osu_mix: new OsuMixRuleset(),
  taiko: new TaikoRuleset(),
  catch: new CatchRuleset(),
  mania: new ManiaRuleset()
};

let currentMode = null;

window.startMode = (modeName) => {
  document.getElementById('menu').style.display='none';
  if (currentMode) currentMode.reset();
  currentMode = modes[modeName];
  currentMode.start();
};

function gameLoop() {
  if(currentMode){
    currentMode.update();
    currentMode.render();
  }
  requestAnimationFrame(gameLoop);
}

gameLoop();
