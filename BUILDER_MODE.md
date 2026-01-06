# Builder Mode

Builder Mode is an explicit opt-in that relaxes *developer* constraints while keeping user invariants intact.

Rules:
- Must be enabled explicitly (env var or file flag).
- Must log when active.
- Must never change frozen/JIT surfaces unless a new freeze version is created.
