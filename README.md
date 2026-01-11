# osu!megamix

## Canon

This project is governed by explicit, written invariants.
If it is not written, it does not exist.

---

## Canon: Ball & Tertiation (Authoritative)

**Invariant:**
> **No ball, no rules.**

Ball is **not** a rule, a feature flag, or a safety check.

**Ball is the tertiation.**

### Meaning
- Ball decides whether *authority exists at all*.
- Rules do not fail when ball is absent — they **do not exist**.
- Enforcement is conditional and opt-in.

### Execution Semantics
- **Ball present** → authority granted → rules may execute.
- **Ball absent** → **tertiation** → immediate refusal; rulespace is never entered.

This is implemented via an explicit guard (`tools/require_ball.zsh`) which exits:
- `0` when ball is present (authority granted)
- `121` when ball is absent (tertiated)

### Log Semantics
- `BALL OK` → authority granted
- `BALL DENY` → tertiated (not an error)

### Canon Statement
> **Ball is the tertiation that decides whether rules exist at all.**

This invariant is foundational. Any script, check, or safety mechanism that enforces rules **must** be ball-gated. Anything enforcing rules without ball is non-canon.
