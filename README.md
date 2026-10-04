# osu!megamix

> a wonderful game with you in mind

## 1. What

**osu!megamix** is a continuous game runtime built around music, time, and on-the-fly changes in gameplay.

A **Mix** changes the active game mode without stopping the runtime.

A **Megamix** is the continuous experience created by those changes.

The Collection is the game's wider world:

* `osu!`
* `osu!taiko`
* `osu!catch`
* `osu!mania`
* `osu!megamix`

The project is intentionally experimental, lightweight, and composable.

---

## 2. How

The implementation is built from small components with one job each.

```text
run
 │
 ▼
osu_megamix.py
 │
 ├── input / output / state
 ├── source access ──► open.zsh
 ├── mixing ──────────► mix
 └── runtime
       │
       ├── timeline
       ├── sound
       ├── rulesets
       └── gameplay
```

`run` is the platform-facing entry point.

`osu_megamix.py` is the runtime brain.

`open.zsh` handles local and network sources.

`map_parser.lib` preserves source data losslessly.

`timeline.py` provides the time model.

`sound.py` handles low-level audio.

`osu_ruleset.py` establishes the ruleset boundary.

`collection.py` manages games, friends, and Keyblades while delegating save/load to the games that own their data.

`keyblades/` provides canonical Keyblade definitions and wardrobe ownership.

`menu.py` enforces the four-option menu structure.

The implementation favors native capabilities, minimal dependencies, and explicit boundaries over a large framework.

---

## 3. Rules

### Time

**Time `t` is authoritative.**

Audio and timeline establish what is happening.

Gameplay rules, modes, and visuals are projections of that timeline.

### Continuity

> **Megamix never stops.**

A failed player path can become a per-player **bust-to-mix** instead of ending the entire experience.

### Menus

Every menu has **exactly four options**.

The rule is enforced by the implementation.

### Collection

Games own their saves.

The Collection does not impose a universal save format.

### Keyblades

> **The game grants the Keyblade; the Collection owns it.**

Keyblades are progression and identity objects.

### SFW

osu!megamix is **permanently SFW by design**.

There is no NSFW mode or intended runtime switch that disables the policy.

### Philosophy

Small components.

Clear contracts.

One job each.

No abstraction without a reason.

---

## 4. Release

### `osu_megamix 2b - trace`

Current release:

```text
osu_megamix-2b-trace
```

`2b - trace` establishes the cohesive runtime foundation, including the permanent SFW policy, Collection architecture, Keyblade framework, four-option menu contract, and targeted cohesion testing.

Run the project with:

```zsh
./run <source> [gamemode]
```

Example:

```zsh
./run song.osu
```

MIT licensed.

---

> **a wonderful game with you in mind**

— ball
