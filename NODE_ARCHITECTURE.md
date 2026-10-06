# osu_megamix Node

The node is platform-agnostic.

The core owns authoritative state.

Platforms provide capabilities through adapters.

Current wrapper:

- HTML

Future wrappers may target:

- macOS
- Windows
- Linux
- iOS/iPadOS
- Android
- WebAssembly
- other platforms

## Authority

The platform provides capabilities.

The node owns decisions.

Network communication is transport.

Remote clients do not become authoritative.

## Offline

Offline operation is a first-class mode.

Connectivity must never be required for the core state machine.
