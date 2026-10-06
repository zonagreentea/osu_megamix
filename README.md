# osu!megamix v6.0.0

**a wonderful game with you in mind**

osu!megamix is a player-first rhythm game built around one simple idea:

> **The architecture can be complicated. The game should not be.**

## The Doorway

Everything starts with:

```bash
./run
```

`run` is the canonical entry point for osu!megamix.

Players should not need to know whether the game is being powered by Python, HTML, a local node, or a network server. They start the game through `run`, and `run` handles the execution path.

```text
player
  ↓
run
  ↓
runtime
  ↓
client / node
  ↓
game
```

## Architecture

osu!megamix is built around a small number of responsibilities.

### `run`

The universal execution spine.

`run` is the glue between the player and the rest of the project. It provides one stable doorway into the game while allowing the implementation underneath it to evolve.

### Runtime

The execution layer behind `run`.

The runtime is responsible for starting the appropriate game or client environment without making the player care about the underlying implementation.

### Node / Client

A node is a player-side instance of osu!megamix.

The node is designed to retain local knowledge and remain useful even when disconnected from the network.

The goal is:

> **power of server, authority of node**

The server can provide shared state and network capabilities, but the node remains the player's local game.

### Server

The server provides shared network authority when network functionality is available.

The network is an addition to the game, not the foundation that determines whether the game exists.

## Offline First

osu!megamix is designed to work without requiring an internet connection.

### Offline

* The local game remains usable.
* The node retains its local knowledge.
* Gameplay does not depend on a remote server.

### Online

* Nodes can communicate.
* Shared multiplayer state can be provided.
* Lobbies and other network capabilities can become available.

The important distinction is simple:

> **The internet adds capability; it does not define the game.**

## Universal Input

Input is designed to flow through one universal interface rather than being tightly coupled to individual devices.

The architecture is designed to accept input from sources such as:

* Keyboard
* Tablet
* Controller
* Microphone
* Rhythm-game kits
* Other compatible devices

The game should care about **what the player did**, not which hardware brand or device identifier produced it.

Physical devices should attach through the interface rather than requiring the game to be built around individual hardware IDs.

## Players

Players are first-class parts of the game.

Player identity can include:

* Player colours
* Cursors
* Pointers
* Local multiplayer state
* Configurable input

The current player-colour direction includes:

* Red
* Blue
* Green
* Yellow

with additional configurable colours supported by the architecture.

## Multiplayer

osu!megamix is designed to support both local and network multiplayer.

The multiplayer direction includes:

* Couch co-op
* Multiple players
* Split-screen play
* Separate displays
* Player cursors
* Shared lobbies
* Network nodes
* Voice communication

The intended experience is that multiple players can participate without the underlying architecture becoming visible to them.

## Game Modes

The project includes osu!-inspired gameplay directions including:

* osu
* taiko
* catch
* mania

Additional game systems are built around the larger Megamix concept.

## Megamix

Megamix is more than another menu option.

It is the place where the different parts of osu!megamix can come together.

One planned visual transition is for player cursors and pointers from different games to converge, compress into one point, and erupt into a supernova revealing:

> **osu!**

The spectacle is part of the identity of the project.

## Lobbies

The multiplayer architecture includes several lobby directions:

* Regular
* Megamix
* Collection
* RP

RP is intended for roleplay-oriented sessions and is marked as **E10+** in the current menu direction.

## Controls

Navigation and gameplay are designed around consistent input behavior.

The current control direction includes:

* Pause during gameplay
* Pause on menus
* Double-tap pause to escape gameplay contexts
* Escape from the main menu to leave the game
* Consistent behavior across solo, multiplayer, Collection, and Megamix contexts
* Gameplay cursor hiding where appropriate

Controls should remain predictable regardless of which game mode is active.

## Collection

Collection is a first-class part of the larger game structure.

The collection direction includes:

* Games
* Friends
* Keyblades
* Collection-oriented lobbies
* Player progression and shared game data

Collection systems are intended to remain compatible with the node-first architecture.

## Project Philosophy

osu!megamix follows a few simple principles.

### One Doorway

`./run` is the canonical way into the project.

### Player First

Players should interact with a game, not an engineering project.

### Offline Capable

The game should remain useful without a server.

### Universal Input

Devices should connect to the game through a common input model.

### Local Authority

A player's node should retain local knowledge rather than becoming useless when disconnected.

### Network as Capability

Servers enhance the experience without becoming a requirement for the basic game.

### Small Core

The runtime should remain lightweight and avoid unnecessary dependencies wherever practical.

### Honest Documentation

Documentation should distinguish between what is implemented, what is canonical, what is experimental, what is planned, and what is historical.

## Project Status

### Canonical

* `run` as the universal runtime entry
* Player-facing simplicity
* Offline-first direction
* Node/client architecture
* Universal input architecture
* Server as shared network authority

### Implemented

* Canonical `run` runtime entry
* Universal input foundation
* Tablet input integration
* Player colour support
* Core pause/escape behavior
* osu!-inspired game experiments and runtime components

### Experimental

The repository contains earlier experiments, prototypes, alternative clients, and development infrastructure.

These may remain useful for development or historical context without being the canonical player-facing architecture.

### Planned

Some parts of the larger vision remain under active development, including:

* Expanded multiplayer
* Voice communication
* Additional device integrations
* Deeper Megamix transitions
* Further node/server capabilities
* Expanded collection systems

Documentation should never imply that a planned feature is already complete.

## Development

For normal use, start with:

```bash
./run
```

The important rule for contributors is to preserve the canonical doorway.

Implementation details may change underneath `run`; the player-facing entry point should remain simple.

## Repository Philosophy

The repository may contain many files, experiments, prototypes, and supporting systems.

That does not mean players need to understand them.

The architecture exists to make the game possible.

The game exists to make the architecture worth having.

## Versioning

Version **6.0.0** establishes the documented architecture and project direction.

Future implementation work may change the systems underneath the architecture without changing the fundamental player-facing model.

The canonical path remains:

```text
player → run → runtime → node/client → game
```

## License

osu!megamix is released under the MIT License.

---

**One doorway. One runtime. One game.**

> a wonderful game with you in mind

— ball

