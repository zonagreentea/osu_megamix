# osu!megamix

This project may be called **osu!megamix**, **megamix**, or **the mix**.

**Players just call it: osu!**

---

## What this is

osu!megamix is a continuous-play interpretation of osu! built around a living audio timeline called a `.mix`.

A `.mix` starts once and keeps running.
Players join and leave.
Builders build around it.
The music does not stop.

---

## Core ideas

- A **`.mix`** is real audio (mp3, wav, flac, etc.) declared alive.
- Once a season starts, its `.mix` runs indefinitely.
- Gameplay adapts to the current moment in the mix.
- Failing or leaving never stops the music.
- Aux ending is a gentle goodbye, not an error.

> Players come and go.
> The mix persists.

---

## Builders

Builders are free to experiment.

- You do not need to start or stop the mix.
- You do not need to reset time.
- You do not need to supervise a running season.

If it requires stopping the music, reconsider it.

---

## Branches

- `main` — the running mix
- `builders/*` — experimentation and exploration

Pull requests flow **toward** `main`.

---

## Running locally

This is a Python project.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

If it imports and runs, it’s working.

---

## One rule that matters

**The mix is running.
Build anything that doesn’t require stopping it.**

See you next time.
