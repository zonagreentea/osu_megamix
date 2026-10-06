# osu!megamix v5.1.0

**a wonderful game with you in mind**

osu!megamix is a game built around one idea:

**everything should lead back to the player.**

## Start the game

```sh
./run
```

That is the entry point.

`run` is the canonical runtime entry for osu!megamix. It is the glue between the project, its clients, its nodes, and the game itself.

## Built to keep playing

osu!megamix is designed **offline-first**.

When connected, nodes can communicate and participate in the wider game. When disconnected, the local game remains useful instead of becoming a shell waiting for a server.

The network adds capability. It does not define whether the game exists.

## Universal input

Different players use different devices.

osu!megamix routes input through a universal input layer so keyboards, tablets, controllers, and future devices can become part of the same game without the game needing to care where the input originated.

## Nodes

A node is a player-side instance of the game.

Nodes are intended to be lightweight, portable, and capable of operating independently while participating in multiplayer when a connection is available.

The player should experience **the game**, not the machinery underneath it.

## The megamix

osu!megamix brings different game experiences together into one larger experience.

The goal is not simply to put games next to each other.

The goal is to make them feel like they belong together.

## Philosophy

- **One entry point.**
- **One runtime.**
- **Universal input.**
- **Offline-first.**
- **Nodes for players.**
- **Servers for shared authority.**
- **The player comes first.**

The architecture can be complicated.

**The game should not be.**

---

## License

MIT
