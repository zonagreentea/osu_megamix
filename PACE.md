# osu!megamix – Pace Anchor

Target: 2026-02-14 (Valentine)

Baseline:
- cat-ultra-1 tag exists
- index.html runs (no deps, JS)
- bust-to-mix works
- repo clean

Rules:
- One step at a time
- ≤30 minutes per step
- No hard-coding until hard-code window
- If unsure: stop, do not stack steps

Core Invariant:
- Dimension 1 is time (t). Audio + timeline are authoritative.
- Gameplay rules (modes) and visuals are projections layered on t.
- In Megamix, the mix never stops; bust-to-mix is a per-player reroute, not an ending.

Current Phase:
FOUNDATION (cat + mode scaffolding)
