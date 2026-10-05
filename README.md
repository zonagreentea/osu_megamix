# osu_megamix

> a wonderful game with you in mind

**osu_megamix** is the backend and development project for **osu!megamix**.

It provides the runtime, language, compiler, and tools used to build and run the game.

## What it does

osu_megamix works with **Run**, a simple programming language built around:

* input
* logic
* output
* time

`.mix` and `.run` files contain programs and game content.

`mixc` compiles `.mix` content into runtime data.

`run` is the canonical runtime.

## How to use it

From the project directory:

```sh
./run
```

To compile a `.mix` file:

```sh
./mixc compile <file.mix>
```

The basic flow is:

```text
.mix / .run
    ↓
  mixc
    ↓
 runtime data
    ↓
   run
    ↓
 osu!megamix
```

**osu_megamix builds.
osu!megamix plays.**

— ball
