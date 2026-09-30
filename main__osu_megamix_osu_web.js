import { OsuMixRuleset } from "./engine/rulesets/osu_mix.js";
import { OsuRuleset } from "./engine/rulesets/osu.js";
import { TaikoRuleset } from "./engine/rulesets/osu_taiko.js";
import { CatchRuleset } from "./engine/rulesets/osu_catch.js";
import { ManiaRuleset } from "./engine/rulesets/osu_mania.js";

const modes={
osu_mix:new OsuMixRuleset(),
osu:new OsuRuleset(),
osu_taiko:new TaikoRuleset(),
osu_catch:new CatchRuleset(),
osu_mania:new ManiaRuleset()
};
let currentMode=null;
window.startMode=(mode)=>{
document.getElementById('menu').style.display='none';
if(currentMode) currentMode.reset();
currentMode=modes[mode];
currentMode.start();
};
function gameLoop(){
if(currentMode){currentMode.update();currentMode.render();}
requestAnimationFrame(gameLoop);
}
gameLoop();
