# osu!megamix — No-Conflict Rule (Microphone & Audio Sourcing)

## Invariants (locked)
1. **Game audio is the truth.** Playback timeline and routing are authoritative.
2. **Microphone is never an audio source for the mix.** It is analysis-only.
3. **Microphone graph must never connect to speakers.** No `destination` connection, no feedback.
4. **Microphone must not rewire or close the game's AudioContext.**
   - Mic creates/owns its own AudioContext and closes only what it owns.
5. **Mic data is advisory only.**
   - Outputs: `level`/`peak` (0..1) for visuals/aux.
   - Never used as primary timing unless explicitly designed later.

"If it isn't written, it doesn't exist."
