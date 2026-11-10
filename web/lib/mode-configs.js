export const MODE_DEFS = {
  osu: {
    label: 'osu!',
    lanes: 4,
    speed: 180,
    spawnRate: 0.85,
    colors: ['#ff5c7a', '#5ec8ff', '#63f2b3', '#ffd166'],
    keys: ['d', 'f', 'j', 'k'],
    pitch: 440
  },
  taiko: {
    label: 'Taiko',
    lanes: 2,
    speed: 240,
    spawnRate: 0.7,
    colors: ['#ff7b72', '#5ec8ff'],
    keys: ['f', 'j'],
    pitch: 520
  },
  catch: {
    label: 'Catch',
    lanes: 3,
    speed: 210,
    spawnRate: 0.75,
    colors: ['#63f2b3', '#ffd166', '#5ec8ff'],
    keys: ['a', 's', 'd'],
    pitch: 350
  },
  mania: {
    label: 'Mania',
    lanes: 4,
    speed: 220,
    spawnRate: 0.65,
    colors: ['#ff9ecb', '#7ae582', '#5ec8ff', '#ffd166'],
    keys: ['a', 's', 'k', 'l'],
    pitch: 600
  },
  megamix: {
    label: 'Megamix',
    lanes: 5,
    speed: 250,
    spawnRate: 0.55,
    colors: ['#ff5c7a', '#5ec8ff', '#63f2b3', '#ffd166', '#c77dff'],
    keys: ['a', 's', 'd', 'j', 'k'],
    pitch: 480
  }
};

export function getModeConfig(mode) {
  return MODE_DEFS[mode] || MODE_DEFS.osu;
}
