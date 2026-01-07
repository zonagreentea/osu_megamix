const KEY = "megamix_mods_v2";

export function defaultMods() {
  return {
    // accessibility / visual cherries
    bgImage: true,
    bgVideo: true,
    bgDim: 0.35, // 0..1 (0 = no dim). optional.
  };
}

export function loadMods() {
  try {
    const raw = localStorage.getItem(KEY);
    if (!raw) return defaultMods();
    return { ...defaultMods(), ...JSON.parse(raw) };
  } catch {
    return defaultMods();
  }
}

export function saveMods(mods) {
  localStorage.setItem(KEY, JSON.stringify(mods));
}
