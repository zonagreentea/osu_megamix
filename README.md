# osu!megamix — Canonical README

osu!megamix is a **continuous-play system** built on top of osu! rulesets.
Its identity is not songs, devices, progression, or hardware — it is **flow through rule changes without stopping time**.

This document defines how the game is meant to be played and how it must be implemented.

If behavior contradicts this document, the behavior is wrong.

---

## Core Idea (One Sentence)

**osu!megamix is a game where the player remains in continuous play while the gameplay ruleset switches over time.**

Everything else is secondary.

---

## Fundamental Abstractions

### 1. Timeline (Authoritative)

- There is exactly **one global timeline**
- The timeline **never stops once play begins**
- Audio is bound to the timeline
- Gameplay events are evaluated against the timeline

Time is not owned by modes, devices, or players.  
Time is owned by the **Megamix layer**.

---

### 2. Megamix Layer (Continuity Layer)

The Megamix layer is the **authoritative system**.

It guarantees:
- Continuous audio playback
- No pauses, resets, or restarts
- No hard failures or eliminations
- A single, uninterrupted play session

The Megamix layer does **not** define gameplay rules.
It defines **continuity**.

---

### 3. Modes (Rulesets)

Modes (osu!, taiko, catch, mania, etc.) are **rulesets**, not game states.

- Modes may change at any time
- Mode switches do not reset the timeline
- Mode switches do not restart music
- Mode switches do not reinitialize the session

Modes answer the question:
> “How do inputs map to scoring *right now*?”

They do not answer:
> “Is the game still running?”

---

## Mix Mode (Playable Definition)

**Mix is a playable mode whose identity is mode switching.**

In Mix:
- Music provides continuity and atmosphere
- The defining mechanic is **switching rulesets**
- The player is always playing
- There are no breaks between modes

If mode switching is removed, Mix does not exist — even if music continues.

---

## Fail Handling — Burst Invariant

**There are no hard failures in Mix or Megamix.**

Instead:

- All failures resolve as a **burst**
- On burst:
  - Gameplay collapses back into the mix
  - Audio continues uninterrupted
  - The timeline does not reset
- Bursts are **per-player**
- Bursts never pause or affect other players

Classic osu! modes outside Megamix may retain traditional fail screens.  
Mix and Megamix never do.

---

## Gameplay Consistency (All Devices)

**Gameplay behavior is identical on all devices and platforms.**

This includes:
- Timing windows
- Hit detection
- Scoring
- Density
- Difficulty
- Fail / burst behavior
- Mode switching behavior

There are:
- No platform-specific mechanics
- No device-based advantages
- No hardware-bound progression
- No “level-ups” or perks

If gameplay differs between devices, it is a bug.

---

## Device Acknowledgement (Strictly Limited)

Devices may be acknowledged **only through non-mechanical nods**.

Allowed:
- Cosmetic UI accents
- Informational icons or text
- Visual flourishes with zero timing impact

Requirements:
- Must not affect gameplay outcomes
- Must live outside the osu!layer
- Must be removable without changing play

Devices are acknowledged, never obeyed.

---

## osu!layer (Protected Core)

The osu!layer is **sacred and device-agnostic**.

It must not:
- Branch on hardware
- Branch on platform or OS
- Branch on input method
- Contain device-conditional logic

The osu!layer operates as if:
> All players are running on the same abstract machine.

---

## Player Mental Model (How to Play Correctly)

When you play osu!megamix:

- Do not wait for songs to change
- Do not expect resets or breaks
- Do not expect failure to end the run
- Treat mode switches as terrain changes, not scene changes
- Stay present in the timeline

You are not clearing stages.
You are **riding the mix**.

---

## Technical Enforcement Tests

Any implementation must pass all of the following:

### Timeline Test
> If anything stops the audio or resets time, the implementation is invalid.

### Mix Test
> If mode switching is removed and Mix still exists, the implementation is invalid.

### Fail Test
> If failure stops play instead of bursting back into the mix, the implementation is invalid.

### Device Test
> If the same run plays differently on another device, the implementation is invalid.

There are no exceptions.

---

## Canon Summary

> **Time never stops.**  
> **Modes change, not music.**  
> **Failures burst, never end.**  
> **Gameplay is the same everywhere.**

---

## Status

This document is **authoritative**.

- It defines intended play
- It defines correct implementation
- It supersedes informal explanations

If it isn’t written here, it isn’t canon.
