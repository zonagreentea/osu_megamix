# osu!megamix 2a — Operations

## HOME — Navigation
HOME / Escape Pod / Back is a push/pull navigation primitive.

- PUSH: preserve the current layer/state.
- PULL: enter the destination layer/state.
- HOME is an absolute navigation destination.
- HOME does not perform maintenance or Lazer updates.

## CHOW — Maintenance
CHOW is an independent push/pull maintenance primitive.

- PUSH: preserve the current runtime state.
- UPDATE/RECONCILE: refresh and reconcile the runtime/Lazer state.
- PULL: restore the refreshed state.
- CHOW does not perform navigation.

## Invariant
HOME != CHOW

HOME = navigation.
CHOW = maintenance.

Both operate through the layered runtime and must remain independent.
