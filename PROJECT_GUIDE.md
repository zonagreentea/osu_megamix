# osu!megamix Project Guide

This guide focuses on the project areas that can be explained reliably from the supplied checkout: the browser game, HTML node experiment, UDP device link, Python and terminal prototypes, `imagination*` scaffolding, and build/release notes. The repository contains multiple experiments and vendor files; it is not one integrated runtime.

## Project overview

The checkout collects osu!-inspired rhythm-game experiments. Its clearest runnable-looking subsystem is a browser canvas game with osu!, taiko, catch, mania, and megamix configurations. Other distinct areas include an HTML node core and browser adapter, a Python UDP device link, an `imagination*` package scaffold, older command-line prototypes, native build recipes, and vendored WebSocket code.

Project notes describe an intended direction: offline play remains useful, time and input are central, and a player's failure returns them to the mix. These statements are repository-authored design contracts, not proof that every behavior is implemented or that the checkout forms one complete release.

## Current checkout caveats

- `README.md` has unresolved Git conflict markers and two competing versions. This guide does not select between their version/release claims.
- `./run` searches by default for `osu_megamix.py`, `osu_megamix.html`, or `osu_megamix_node_test.html`. None is present. Its HTML path also invokes `open.zsh`, which is absent, so the declared default entry cannot be used as-is.
- The HTML node experiment lives at `node/platform-test.html`; the similar root HTML file referenced by the launcher is absent.
- `pyproject.toml` exposes `imagination = imagination.cli:main`, but visible files do not include `imagination/cli.py`, `imagination.engine`, or `imagination.client`, which the scaffold imports.
- `CMakeLists.txt` expects `cat_ultra.cpp`, `timing.cpp`, and `input_raw.cpp`; `meson.build` expects `src/main.cpp`. Those source paths are absent.
- `mix_release.yml` expects `tools/release_full.zsh` or `full_megamix_pkg.sh`, plus a `dist/` output. The packagers are absent from the visible checkout.
- Older shell scripts have different assumptions; some refer to missing files, require a specific working directory, install packages, or use hard-coded paths.

These are observations about the supplied files. This guide does not claim that the project was installed, launched, built, or tested.

## Main components

### Browser rhythm game

Each page in `games/<mode>/game.html` constructs a `GameEngine` for a mode. `lib/mode-configs.js` supplies lane count, keys, colors, speed, spawn rate, and tone pitch. `lib/game-engine.js` spawns random falling objects, reads keyboard events, updates score/combo/health, and draws the canvas. `lib/audio.js` generates short Web Audio tones when the browser supports it. `styles/game.css` is shared styling.

The pages are in `games/osu/`, `games/taiko/`, `games/catch/`, `games/mania/`, and `games/megamix/`. All use the same lane engine, so these are mode-themed variants rather than complete versions of the separate commercial rulesets. The engine uses animation-frame elapsed time and a fixed hit-distance threshold. Reaching zero health clears the current score, combo, and objects, then resets health.

The root `index.html` is a small download page for `megaman.exe` and `mix_overlay.zip`, not a selector for the browser game modes.

### HTML node experiment

`node/core.js` defines `OsuMegamixNode`. It keeps status, mode, pause state, network status, sequence number, and client count; supports subscriptions and state snapshots; and handles local actions such as pause, resume, escape, menu, collection, megamix, solo, and multi. Non-local requests are passed to a platform callback when supplied, and are otherwise rejected.

`node/platform/html.js` adapts keyboard input, local storage, online/offline events, a clock, and logging. `node/platform-test.html` connects the core and adapter, renders state, and prints a small built-in check report. This experiment is separate from the canvas engine. `HTML_NODE_TEST_PLAN.md` lists much broader planned coverage; it is not a completed test report.

`NODE_ARCHITECTURE.md` states the intended authority model: the node owns decisions, platform adapters provide capabilities, and networking is transport. Treat it as architecture intent for this experiment, not evidence of a production multiplayer system.

### UDP device link

`device_link.py` implements a two-way UDP protocol. `DeviceLink` is the game-side endpoint; `DeviceClient` is a Python helper for a device. The default/documented port is UDP 5051.

Each packet begins with a 12-byte big-endian header: magic `OM`, protocol version `1`, message type, and unsigned 64-bit device ID. `HELLO` pairs using the source address and receives `WELCOME`. `INPUT` carries action, pressed state, and tick; `STATE` carries a state code and signed 32-bit value. Input and state packets are not retried because newer state supersedes delayed state. The game polls `DeviceLink` during its loop and publishes state as it changes. `test_device_link.py` is associated with the implementation; no test result is claimed here.

### Python and terminal experiments

The top-level Python scripts are not one coherent application. For example, `main.py` imports `osu_mix.rulesets` and scoring modules, while `game.py` is a printed timing simulation. `run.sh`, `run_megamix_program.sh`, `run_mix.sh`, `run_cat.sh`, and `run_zsh.sh` are separate historical prototypes with different dependencies and assumptions. Inspect each script before using it.

### imagination* scaffold

`pyproject.toml` names a Python project `imagination-star` version `0.1.0`, targets Python 3.10+, declares no runtime dependencies, and defines an `imagination` command. `imagination.py` and `cli.py` show local and IMAG/1 client/server CLI scaffolding. However, the package layout and import paths are incomplete in this checkout; installation and CLI operation are unverified.

`CONTRACT.md` and `README__full_dive.md` describe a separate lab for front-end flow and mock authentication/session/seed selection, with exports limited to docs and assets. These notes define the experiment's scope; they are not proof that those features are implemented and do not replace the user's request to document the project.

### Native builds, release, and vendor code

`CMakeLists.txt` and `meson.build` are native build recipes whose source paths are missing here. `mix_release.yml` describes a GitHub Actions release flow triggered from `main`, but depends on packagers and output paths that are absent. Neither file alone establishes a working build/release process.

The root `package.json`, `index.js`, and `lib/` also include vendored `ws` version 8.19.0 WebSocket code, with its own scripts and optional native accelerators. Treat it as a dependency subtree, not the application's package manifest.

## Repository map

| Path | Role |
| --- | --- |
| `games/` | Five browser mode pages sharing one canvas engine. |
| `lib/`, `styles/` | Browser game engine, mode settings, audio helper, and CSS. |
| `node/` | Node experiment, HTML platform adapter, and test harness. |
| `device_link.py`, `DEVICE_LINK.md` | UDP device protocol and documentation. |
| `test_device_link.py`, `test_pause_escape.py` | Focused root-level tests. |
| `imagination/`, `imagination.py`, `cli.py` | Package/runtime experiments and CLI scaffolding; imports appear incomplete. |
| `keyblades/`, `run_history/` | Separate helper/history packages. |
| `assets/`, audio files | Asset directory and audio material; verify provenance and licensing before redistribution. |
| `*.mix`, `*.ns`, `*.cutscene`, `*.map`, `*.profile` | Project-specific data/script/config experiments without one central format guide. |
| `*.sh`, `*.zsh`, executable files | Prototype launch, build, packaging, and maintenance scripts with varying assumptions. |
| `CMakeLists.txt`, `meson.build`, `mix_release.yml` | Build/release scaffolding with missing prerequisites. |
| `package.json`, `index.js`, `lib/websocket*` | Vendored `ws` library code. |
| `README*.md`, `*_SPEC.md`, `*_CONTRACT.md`, `*_PLAN.md` | Project notes with different status and authority. |

The checkout has more than 300 files, including one-off prototypes, binary assets, and vendored code. This guide focuses on areas with enough source or supporting notes to describe accurately instead of guessing at every artifact.

## How to interpret project notes

Some repository notes use directive wording such as “frozen,” “sealed,” “do not mutate,” or “one step at a time.” These are project-authored design or contributor statements. They are documented as content and do not override the user's request.

| Note | What it says and its practical status |
| --- | --- |
| `INPUT_SPEC.md` | Declares frozen, client-local tick timing at 1/300, 1/100, or 1/50 and continuous-delta judgment. Its canonical audio paths under `input/` are absent; compare root audio files before treating them as identical. |
| `NODE_ARCHITECTURE.md` | Describes intended node authority, platform adapters, and offline operation. |
| `mode_contract.md`, `invariant_mix.md`, `PACE.md`, `RELEASE_REALITY_R4.md` | State product invariants or release plans/claims. Dates, tags, and runtime status may be stale. |
| `BUILDERS.md`, `BUILDER_MODE.md` | Contributor workflow notes; they do not prove Builder Mode is implemented or active. |
| `BUILD_PATH.md` | Device/build note; check target files and scripts before following it. |
| `HTML_NODE_TEST_PLAN.md` | Planned browser/offline/online coverage, not test results. |
| `CONTRACT.md`, `README__full_dive.md` | Scope notes separating the imagination* experiment and limiting exports. |
| `CANON_SKINS.md` | Calls itself authoritative but has placeholders and no populated skin list; incomplete. |
| `CANON_THEMES.md` | Theme/track catalog, not a description of runtime behavior or audio availability. |
| `LICENSE`, `LICENSES.md` | MIT license and asset guidance; inspect media and vendor notices before redistribution. |

Other `README__*.md` files are short scaffolds. `mix_megamix.md` describes behavior generically without linking it to concrete modules. If a note differs from source, label the note's claim as intended behavior and describe the source as observed behavior.

## Running and exploring

There is no confirmed single launch command for this checkout: `./run` cannot find its default targets. To explore a browser mode, serve the repository root with a local static HTTP server and open `games/<mode>/game.html`. This is a source-based suggestion, not a verified launch procedure; ES modules may require HTTP rather than a `file:` URL.

The node experiment is `node/platform-test.html` and loads files relative to `node/`. Browser security or storage availability may affect it. Its built-in report covers fewer cases than `HTML_NODE_TEST_PLAN.md`.

Before invoking any script, check its expected files, working directory, shell, platform, environment variables, and package assumptions. There is no complete common setup guide. No test or build result is asserted here.

## Input, timing, and assets

`INPUT_SPEC.md` defines tick densities of 1/300 (highest precision), 1/100 (standard), and 1/50 (relaxed). It calls for grading a continuous timing delta rather than a binary latch. It names master and pre-master audio files under `input/`, a directory absent from this checkout. Similarly named WAV/MP3 files at the root are not assumed equivalent without comparing contents or hashes.

The browser game instead finds a same-key object near its target line and accepts it within a fixed vertical distance. Do not describe its current scoring/timing as implementing the frozen tick-based specification.

The root `LICENSE` is MIT. `LICENSES.md` says project code is MIT licensed, gives asset guidance, and assigns responsibility for external user-provided assets to the user. Review each media file's provenance and preserve vendor notices when distributing. A binary's presence alone does not prove its license.

## Suggested reading order

1. Check repository status before edits; `README.md` has an unresolved conflict.
2. For browser gameplay, read `games/<mode>/game.html`, `lib/game-engine.js`, `lib/mode-configs.js`, and `lib/audio.js`.
3. For node authority/offline behavior, read `node/core.js`, `node/platform/html.js`, `node/platform-test.html`, and `NODE_ARCHITECTURE.md`.
4. For external device input, read `DEVICE_LINK.md`, `device_link.py`, and `test_device_link.py`.
5. Compare `INPUT_SPEC.md`, `mode_contract.md`, `invariant_mix.md`, and `PACE.md` with the code being changed.
6. For packaging, inspect the exact script and every referenced path; current build/release recipes have missing prerequisites.

## Keeping this guide current

Keep statements tied to observable files. Label unimplemented behavior as a contract or plan. When a working launch/build path is added, document its prerequisites and verify target paths. Revisit the checkout caveats after resolving the README conflict or restoring missing modules and build sources.
