# ultra – Timing Lock (Foundation)

Goal: make time (t) explicit and stable in the native loop, before any mode work.

Non-negotiables:
- Use a monotonic clock only (std::chrono::steady_clock).
- Clamp dt to prevent spikes from sleep/backgrounding (e.g. max 50ms).
- Provide a frame cap path (sleep) even before vsync is real.
- Never let timing drift silently: print or expose dt/fps in debug builds.

Definition:
- t is authoritative.
- Rendering + simulation are projections sampled from t.
