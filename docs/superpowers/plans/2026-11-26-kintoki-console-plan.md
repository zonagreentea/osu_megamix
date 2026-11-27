# Kintoki Console Build Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a console-first Kintoki dance showcase, beginning with a PS1-native vertical slice and preserving a clean path for a later PSP port.

**Architecture:** Keep dance timing and pose generation platform-neutral. The PS1 adapter owns rendering, input, audio, and disc packaging; the future PSP adapter will consume the same pose data and scene contract. The first slice uses procedural low-poly geometry so the project does not depend on copyrighted third-party assets.

**Tech Stack:** C, PSn00bSDK for PS1, host-side GCC tests, GNU Make, PSPSDK later.

**Spec:** `PSP_RUNTIME.txt` and `CONSOLE_PLAY_GUIDE.md`.

## Global Constraints

- Dance-only showcase: no arrows, score, combo, or rhythm gameplay.
- Target PS1 first; PSP is a later port.
- No commercial ROMs, BIOS files, keys, or copyrighted game dumps.
- No desktop runtime is required for players.
- ISO is claimed only after a real console-compatible build is produced and verified.

## Review Focus

- Pose timing stays deterministic across platforms — host test covers repeatability.
- The loop handles time wraparound — host test covers values before, inside, and after one cycle.
- PS1 build remains isolated from browser code — Makefile and source paths are separate.
- Missing PSn00bSDK fails with a useful message — build documentation covers the prerequisite.
- PSP port has a stable input/output contract — shared headers contain no platform APIs.

### Task 1: Shared dance runtime

**Files:**
- Create: `shared/kintoki/dance.h`
- Create: `shared/kintoki/dance.c`
- Create: `tests/test_kintoki_dance.c`

**Interfaces:** `kintoki_pose_at(float time_seconds)` returns a deterministic `KintokiPose` for a looping 8-second dance.

- [ ] Write failing host tests for deterministic poses and loop wraparound.
- [ ] Run the host test and verify it fails because the module is absent.
- [ ] Implement the minimal pose generator using bounded sine-wave channels.
- [ ] Run the host test and verify it passes.

### Task 2: PS1 vertical slice scaffold

**Files:**
- Create: `ps1/Makefile`
- Create: `ps1/src/main.c`
- Create: `ps1/README.md`

**Interfaces:** Consumes `shared/kintoki/dance.h`; produces a PS1 executable and CD image through PSn00bSDK when the SDK is installed.

- [ ] Add a PSn00bSDK Makefile with an explicit prerequisite check.
- [ ] Add a PS1 main loop with 320x240 scene setup, procedural low-poly Kintoki geometry, looped animation, and exit input.
- [ ] Document the exact build and ISO commands.
- [ ] Run host-side checks and, when PSn00bSDK exists, run the PS1 build.

### Task 3: Console release handoff

**Files:**
- Modify: `CONSOLE_PLAY_GUIDE.md`
- Modify: `PSP_RUNTIME.txt`

- [ ] Document the PS1 output names and verification steps.
- [ ] Record the PSP adapter boundary and remaining port work.
- [ ] Verify no PSP or ISO artifact is claimed before the toolchain build succeeds.
