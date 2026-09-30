# ASH Layer

## Status
Hardcoded. Always present.

## Invariant
- ASH never leaves the game.
- No toggle, no disable path.
- Existence is unconditional.

## Runtime Rules
- presence: always_on
- visibility: context-gated
- interaction: projection_only
- exit: observational (never removal)

## Enforcement
- ASH is injected if missing.
- ASH is locked against removal.
- Only visibility and interaction may change.

## Logging
- State changes are logged as reasons.
- No failure, no termination semantics.

## Canon
If ASH exists, it exists everywhere.
If it isn’t written, it doesn’t exist.
