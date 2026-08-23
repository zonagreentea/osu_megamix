# Timeline

The timeline is the source of truth.

All architecture interprets the same clock.

## Invariants

- Time is authoritative.
- Audio interprets the timeline.
- Gameplay interprets the timeline.
- Visuals interpret the timeline.
- RP interprets the timeline.
- Multiplayer interprets the timeline.
- Maintained forms synchronize to the same temporal coordinate.
- Routing does not reset time.
- A break does not stop time.
- A landing resumes from the same timeline.

## Flow

CLOCK → FLOW → MOVEMENT → LANDING → HANDSHAKE

The timeline continues through every transition.

## Authority

There is one authoritative temporal coordinate.

Consumers interpret time; they do not independently redefine it.
