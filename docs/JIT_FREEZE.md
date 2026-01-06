# JIT Freeze: 2.2.2.2.2.2.2.2.2

Builders are free. We freeze the JIT surface.

Rules:
- No new moving parts in the JIT path unless explicitly unfrozen.
- Determinism + compatibility > cleverness.
- Changes require a new freeze tag (never mutate a freeze).
