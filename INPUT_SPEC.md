# osu!megamix — Input Handling Spec (FROZEN)

Status: **SEALED / FROZEN**
Rule: input layer is closed; any future change is a **new spec**, not a patch.

## Authority
- Input timing is **client-local authoritative**
- Render/visuals are **non-authoritative** (informational only)

## Time Model
- Discrete tick evaluation (not frame-bound)
- Supported tick densities:
  - 1/300 (highest precision)
  - 1/100 (standard)
  - 1/50  (relaxed)

## Judgment
- Continuous timing delta → graded result
- No binary latch “in/out” as the correctness primitive

## Canonical Audio Artifacts (Hardware Reference)
These files represent the intended input feel. The WAV is archival truth.

### Canonical master
- `input/final_input_handle_MASTER.wav` (immutable)
- `input/final_input_handle_MASTER.mp3` (distribution copy)

### Pre-master reference
- `input/final_input_handle_clean.wav`
- `input/final_input_handle_clean.mp3`

## Integrity (SHA-256)
- final_input_handle_MASTER.wav: 1562dd387f5ad346e58630ae48c26feb421204b68013424b7d3372c41796a4dd
- final_input_handle_MASTER.mp3: e4db2835c1fac3bdb3b9dff9857e80288dde76d9c737666dadc759ae843b2a13
- final_input_handle_clean.wav:  b683c7823404ddd40ce6c71fbcb8955a454d391aa2e7379000430811a40d6d22
- final_input_handle_clean.mp3:  44f14217e9ec71e798b16103cb22ffff17a8efd47ca13cab8ee849221889ef4d

## Change Policy
This spec is closed. Any modification requires:
- a new spec document
- explicit versioning
- explicit statement of replacement (not revision)
