import { loadMods, saveMods } from "./mods_store.js";
import { applyBackgroundMods } from "./bg_control.js";

const mods = loadMods();
applyBackgroundMods(mods);

// Tiny API for your mod menu / pause menu to call:
window.MEGAMIX = window.MEGAMIX || {};
window.MEGAMIX.mods = mods;
window.MEGAMIX.setMod = (k, v) => {
  mods[k] = v;
  saveMods(mods);
  applyBackgroundMods(mods);
};

// Example toggles (you’ll call these from the mod menu UI)
window.MEGAMIX.toggleBgImage = () => window.MEGAMIX.setMod("bgImage", !mods.bgImage);
window.MEGAMIX.toggleBgVideo = () => window.MEGAMIX.setMod("bgVideo", !mods.bgVideo);
window.MEGAMIX.setBgDim = (x) => window.MEGAMIX.setMod("bgDim", x);

// Your existing game loop goes here; this file just establishes the mods + gates.
