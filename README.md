osu!mix / osu!megamix

osu!mix (aka Megamix) is a hybrid rhythm engine and playable prototype for all your osu! fantasies, combining osu!standard, taiko, catch, mania, and a custom Megamix mode into a continuous, seamless, player-driven mix. It supports infinite auto-generation, adaptive layer blending, and the Red-Charizard philosophy: fun first, rules second.

It is playable on desktop using mouse + keyboard, with optional hybrid input modes, and is designed for experimentation, prototyping, and endless gameplay.

🎵 Core Gameplay Modes
Mode	Input	Notes
osu!	Mouse / Keyboard	Standard circle hits, fully playable.
Taiko	Default drum keys	Right-to-left scrolling percussion.
Catch	Z/X + Shift	Fast-paced catcher mode with sliding movement.
Mania	D/F/J/K	Four lanes, random musical note generation.
Megamix	Mouse + Z/X/C/V	Cross-mode auto-generation with real-time adaptive blending; Burst-to-Mix ensures you never fail.
🧠 Engine & Gameplay Philosophy

Burst-to-Mix: Players never “end.” Failing triggers a soft transition back into the ongoing mix instead of a fail screen.

Continuous Audio Layer: The audio timeline never pauses. Mode transitions happen seamlessly while gameplay continues.

Mode Flow Display: Text indicates which mode layer is currently dominant to help players anticipate changes.

Hybrid Auto-Mix Engine: Deterministic “Hyborgian flip” heartbeat for infinite, adaptive mix generation.

Full Input Handling: Canon keybinds for all modes; mouse, keyboard, or hybrid.

Ultra-Minimalist Workflow: Zsh-native setup scripts and markdown-driven prototypes for fast, maintainable iteration.

Roaming Title Screen: Click the logo to start; no forced menus — jump straight into the mix.

⚙️ Developer & Prototyping Tools

Full Playable Prototype Layer: Auto-generates hit objects based on audio input.

Cat Layer Integration: Launch playable prototypes seamlessly from the base layer.

Customizable Auto-Map Parameters: Soft-coded until Valentine’s, enabling safe experimentation.

Logging & Persistence: Every Megamix session is logged for replayability and analysis.

📂 Directory Structure
layers/
├─ cat/               # Base layer; hooks to full playable prototype
├─ full_playable/     # Auto-map engine prototype
├─ osu/               # osu!standard mode
├─ taiko/             # osu!taiko mode
├─ catch/             # osu!catch mode
├─ mania/             # osu!mania mode
└─ megamix/           # Cross-mode infinite mix scripts
setup_full_playable.sh # Setup script for playable prototype layer
README.md
LICENSE
🚀 Getting Started on PC

Install Requirements

Python 3.10+

NumPy
 → pip install numpy

SoX
 for audio input

Zsh terminal (recommended for setup scripts; optional on Windows via WSL or Git Bash)

Clone Repository

git clone https://github.com/zonagreentea/osu_megamix.git
cd osu_megamix

Run Full Playable Prototype Setup

./setup_full_playable.sh

Launch Base Cat Layer (includes playable Megamix)

python3 layers/cat/main.py

Controls
| Mode | Input |
|------|-------|
| osu! | Mouse / Keyboard (canonical osu! keys) |
| Taiko | Default drum keys |
| Catch | Z/X + Shift |
| Mania | D/F/J/K |
| Megamix | Mouse + Z/X/C/V, adaptive blending |

Gameplay Notes

Burst-to-Mix is always active. No fail screen.

Mode transitions are dynamic and adaptive to music.

Dominant layers are displayed via Mode Flow Text.

All layers are unlocked automatically; only important layers are emphasized per song section.

💡 Philosophy & Vision

Red-Charizard Ethos: Fun > strict rules. Always prioritize playability and enjoyment.

Long-Term Vitality: Hybrid deterministic engine ensures the mix never stops.

Player-Driven Continuation: “Bust to Mix” preserves momentum without punishment.

Soft-Coded Layers Until Valentine’s: Experimental layers remain flexible for safe modifications.

⚡ Roadmap

Full playable prototype layer refinement

Multi-mode integration (osu!, taiko, catch, mania)

Burst-to-Mix continuity

Spotify / external audio input integration

One-click all-platform release package

Further UI/UX polish for arcade-style gameplay

📝 Contributing

Fork the repository and create a branch.

Maintain Red-Charizard and Burst-to-Mix invariants.

Submit pull requests with clean, modular code.

Follow Zsh + Markdown + soft-coded prototype principles.

📜 License

This project is licensed under the MIT License – see LICENSE for details.
