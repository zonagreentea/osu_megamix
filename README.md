osu!mix / osu!megamix

osu!mix (aka megamix) is a hybrid rhythm engine and playable prototype for all your osu! fantasies, combining osu!standard, taiko, catch, mania, and a custom Megamix mode in a continuous, seamless, player-driven mix. It’s playable on desktop (mouse + keyboard), supports infinite auto-generation, and respects the Red-Charizard philosophy: fun first, rules second.

🎵 Features
Core Gameplay Modes

osu!mix osu! – Standard circles, fully playable with mouse or keyboard.

osu!taiko – Right-to-left scrolling drum beats, classic taiko rules.

osu!catch – Fast-paced catcher mode, slide-based movement, keys Z/X + Shift by default.

osu!mania – Four lanes, random musical note generation, keyboard-focused.

osu!mix / Megamix – Cross-mode auto-generation, continuous audio timeline, “bust to mix” instead of fail.

Engine & Gameplay Philosophy

Burst-to-Mix: players never “end” or get eliminated; failing triggers a soft transition back into the ongoing mix.

Continuous Audio Layer: the mix never pauses; mode transitions happen seamlessly while the audio keeps playing.

Hybrid Auto-Mix Engine: uses a deterministic “Hyborgian flip” heartbeat for infinite mix generation.

Ultra-Minimalist Zsh/Markdown Workflow: setup scripts are zsh-native, lightweight, and maintainable.

Full Input Handling: canon keybinds for all modes with mouse, keyboard, or hybrid.

Roaming Title Screen: click the logo to start; no forced menus, just jump into the mix.

Developer & Prototyping Tools

Full playable prototype layer (layers/full_playable) auto-generates hit objects based on audio input.

Cat layer integration: seamless launching of playable prototypes from the base layer.

Customizable auto-map parameters: soft-coded until Valentine’s, allowing safe experimentation.

Logging & Persistence: every Megamix session is fully logged for replayability.

🚀 Quick Start
Requirements

Python 3.10+

NumPy
 (pip install numpy)

SoX
 (for audio input / playable prototypes)

Zsh terminal for setup scripts

Setup & Play
# Clone repository
git clone https://github.com/zonagreentea/osu_megamix.git
cd osu_megamix

# Run the full playable prototype setup
./setup_full_playable.sh

# Launch base cat layer (includes playable Megamix)
python3 layers/cat/main.py
Controls

osu!standard: mouse or keyboard (canonical osu! keybinds)

osu!taiko: default drum keys

osu!catch: Z/X + Shift for catcher movement

osu!mania: D/F/J/K for four-lane notes

Burst-to-Mix: always active, no fail screen

📂 Directory Structure
layers/
 ├─ cat/                # Base layer, includes hooks to full playable prototype
 ├─ full_playable/      # Auto-map engine prototype
 ├─ osu/                # osu!standard mode
 ├─ taiko/              # osu!taiko mode
 ├─ catch/              # osu!catch mode
 ├─ mania/              # osu!mania mode
 └─ megamix/            # Cross-mode infinite mix
scripts/
 ├─ setup_full_playable.sh  # Sets up playable prototype layer
README.md
LICENSE
💡 Philosophy & Vision

Red-Charizard ethos: fun > strict rules; the system always prioritizes playability.

Long-term vitality: hybrid deterministic engine ensures the mix never stops.

Player-driven continuation: “Bust to mix” preserves momentum without punishment.

Soft-coded until Valentine’s: experimental layers remain flexible for safe modifications.

⚡ Roadmap

 Full playable prototype layer

 Multi-mode integration (osu!, taiko, catch, mania)

 Burst-to-Mix continuity

 Spotify / external audio input integration

 One-click all-platform release package

 Further UI/UX polish for arcade-style gameplay

📝 Contributing

Fork the repository and create a branch

Maintain Red-Charizard and Bust-to-Mix invariants

Submit pull requests with clean, modular code

Follow zsh + markdown + soft-coded prototype principles

📜 License

This project is licensed under MIT License – see LICENSE
 for details.
