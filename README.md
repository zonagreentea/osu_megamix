<<<<<<< HEAD
# 🎵 osu!mix / osu!megamix

> **The mix is running.**
=======
# osu!megamix Readme — Quickstart

## osu!megamix — Quickstart
>>>>>>> origin/10

This project may be called **osu!megamix**, **megamix**, or simply **the mix**.

<<<<<<< HEAD
**Players just call it: osu!**
=======
## What is osu!megamix?
>>>>>>> origin/10

---

<<<<<<< HEAD
## 🌌 What is the Megamix?
=======
## Requirements
>>>>>>> origin/10

osu!megamix is a continuous-play interpretation of osu! built around a living audio timeline called a **`.mix`**.

<<<<<<< HEAD
A `.mix` starts once.
=======
# Launch
>>>>>>> origin/10

Then it **keeps going.**

Players come and go.
Modes rise and fall.
Builders experiment.
The music keeps moving.

> **Players come and go.**
> **The mix persists.**

---

## 🎧 The Core

The Megamix is built around one simple idea:

### **Rhythm is time.**

The audio timeline is the foundation.

Gameplay exists **inside that timeline**, rather than controlling it.

* 🎵 Audio keeps moving.
* 🕐 Time keeps moving.
* 🎮 Gameplay adapts.
* 🔄 Modes can transition.
* 🚪 Players can leave.
* ♾️ The mix continues.

A failure isn't necessarily the end.

It's just another point on the timeline.

---

## 🎮 The Modes

| Mode           | Input            | Rhythm                     |
| -------------- | ---------------- | -------------------------- |
| 🔵 **osu!**    | Mouse / Keyboard | Standard circle hitting    |
| 🥁 **Taiko**   | Drum keys        | Percussive scrolling       |
| 🍎 **Catch**   | Z/X + Shift      | Catch the falling fruit    |
| 🎹 **Mania**   | D/F/J/K          | Four-lane rhythm           |
| 🌈 **Megamix** | Mouse + Z/X/C/V  | Cross-mode adaptive mixing |

The modes are layers.

The mix is the thing underneath them.

---

## ⚡ Burst → Mix

### **You don't have to stop the music.**

Historical prototypes use a **Burst-to-Mix** concept:

1. Gameplay reaches a burst.
2. The player leaves, misses, or transitions.
3. The mix continues.
4. Another layer takes over.
5. The timeline keeps moving.

No hard reset.

No unnecessary interruption.

Just:

**🎵 → 🎮 → 💥 → 🌊 → 🎵**

---

## 🧠 Engine Philosophy

### 🕐 Continuous Time

The timeline is persistent.

Gameplay should adapt to time rather than repeatedly destroying and recreating it.

### 🎚️ Layered Gameplay

Different gameplay systems can exist as layers around the same underlying mix.

### 🔀 Mode Flow

The dominant gameplay layer can change while the audio continues.

### 🤖 Deterministic Logic

Experimental auto-mix systems can use deterministic logic to produce repeatable behavior from the same inputs.

### 🎮 Physical Input

Input enters the runtime, the runtime processes it, and the active layer responds.

**Input → Logic → Output**

Simple.

---

## 🏗️ Builders

Builders are free to experiment.

Build strange things.

Build beautiful things.

Build things that probably shouldn't work.

Then make them work. 😈

But remember:

* Don't unnecessarily stop the mix.
* Don't unnecessarily reset time.
* Don't make the running timeline depend on supervision.
* Keep experimental systems compatible with the larger mix when possible.

### If it requires stopping the music...

**Reconsider it.** 🎵

---

## 🌳 The History Matters

The repository isn't just the current implementation.

**The evolution is part of the project.**

Experiments, prototypes, branches, strange ideas, dead ends, rebuilds, and working systems can all tell part of the story.

`main` is the current mix.

Historical branches are the paths that got us here.

> **Don't erase the journey just because you've reached the destination.**

---

## 🌊 The Mix

A `.mix` represents a living audio timeline.

It can contain real audio such as:

```text
.mp3
.wav
.flac
```

Once the mix begins, its timeline is the foundation.

Everything else happens **around it**.

---

## 💻 Running Locally

The repository contains Python and shell-based prototypes.

A basic Python environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
```

Individual historical prototypes may have additional requirements.

Some prototypes use:

* Python 3.10+
* NumPy
* SoX
* Zsh

The exact requirements depend on the layer being run.

---

## 🧪 Experimental Layers

Historical prototypes include experiments involving:

* 🎮 Playable gameplay
* 🗺️ Auto-map generation
* 🐈 Cat layer integration
* 🎵 Audio-driven gameplay
* 🔀 Mode blending
* 📝 Session logging
* 💾 Persistence
* ⚙️ Runtime experiments
* 🧰 Zsh-native tooling

Not every experiment is the final architecture.

That's the point.

**This is a Megamix.**

---

## 🌐 Branches

```text
main
 ├── builders/*
 ├── experiments
 ├── historical branches
 └── whatever comes next
```

`main` is the running mix.

Builders build toward it.

History remains part of it.

---

## 📜 The Rule

There is one rule that matters:

# **THE MIX IS RUNNING.**

### Build anything that doesn't require stopping it.

---

## ♾️ And then...

The next player joins.

The next beat arrives.

The next layer appears.

The mix continues.

**See you next time. 🎵✨**

---

## 📄 License

This project is licensed under the **MIT License**.

See `LICENSE` for details.
