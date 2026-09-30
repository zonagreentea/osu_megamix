# JIT Freeze: 2.2.2.2.2.2.2.2.2

Status: FROZEN

Scope:
- JIT execution surface only
- Timing, input, and UI projection must remain deterministic

Builders are free:
- ultra
- cat
- skins
- docs

Rules:
- Do not mutate frozen paths
- Any change requires a new freeze version
- Stability > cleverness

This freeze protects the mix.
