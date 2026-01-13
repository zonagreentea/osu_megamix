# osu!megamix — Gameplay Consistency & Device Policy

## Core Principle

**osu!megamix gameplay is identical across all devices and platforms.**

There are **no platform-specific mechanics**, no device-based advantages, and no progression systems tied to hardware. Every player plays the same game, regardless of what they are using.

If gameplay differs, it is a bug.

---

## What “Consistency” Means

Across all devices, osu!megamix guarantees:

- Identical timing windows  
- Identical scoring behavior  
- Identical hit detection  
- Identical fail / bust behavior  
- Identical difficulty and density  
- Identical rulesets and logic  

There are **no level-ups**, perks, bonuses, or unlocks based on device, platform, or input method.

Gameplay outcomes must be reproducible on any supported device.

---

## Device Acknowledgement (Allowed, Non-Gameplay Only)

osu!megamix may acknowledge the player’s device **only through subtle, non-mechanical nods**.

These nods are strictly cosmetic or informational.

### Examples of allowed nods

- Small UI indicators or icons showing device type  
- Cosmetic framing or layout accents  
- Subtle animations with no timing impact  
- Informational text or glyphs  

### Requirements for nods

- Must not affect gameplay, timing, scoring, or difficulty  
- Must live **outside the osu!layer**  
- Must be removable without changing gameplay behavior  

If removing a nod changes how the game plays, it is not allowed.

---

## osu!layer Invariant (Hard Rule)

**The osu!layer is device-agnostic and must never branch on hardware or platform.**

The osu!layer must not:

- Check device type  
- Check platform or OS  
- Change behavior based on input method  
- Contain hardware-conditional logic  

The osu!layer operates as if all players are running on the same abstract machine.

All device-specific handling must exist *around* the layer, never *inside* it.

---

## Enforcement Test

When reviewing changes, ask:

> **“Would this play the same on another device?”**

- If **yes** → allowed  
- If **no** → do not merge  

There are no exceptions.

---

## Canon Summary

> **osu!megamix plays the same everywhere.**  
> **Devices are acknowledged, never obeyed.**
