#!/usr/bin/env python3
import os
import random

# ==============================
# Paths
# ==============================
HOME = os.path.expanduser("~")
BEATMAP_DIR = os.path.join(HOME, "osu_beatmaps")
PLAYER_HISTORY_FILE = os.path.join(HOME, "playerbase_history.txt")

# ==============================
# Gamemodes (internal vs UI)
# ==============================
INTERNAL_MODES = ["Megamix", "osu", "taiko", "catch", "mania"]
UI_MODES = ["osu!megamix", "osu!", "osu!taiko", "osu!catch", "osu!mania"]

MEGAMIX_INTERNAL = "Megamix"
MEGAMIX_UI = "osu!megamix"

# ==============================
# Load beatmaps
# ==============================
def load_beatmaps():
    beatmaps = []
    if os.path.exists(BEATMAP_DIR):
        for root, _, files in os.walk(BEATMAP_DIR):
            for f in files:
                if f.endswith(".osu"):
                    beatmaps.append(os.path.join(root, f))
    print(f"[osu!megamix] Loaded {len(beatmaps)} beatmaps")
    return beatmaps

# ==============================
# Player history
# ==============================
def load_player_history():
    if os.path.exists(PLAYER_HISTORY_FILE):
        with open(PLAYER_HISTORY_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_player_history(history):
    with open(PLAYER_HISTORY_FILE, "w") as f:
        for entry in history:
            f.write(entry + "\n")

# ==============================
# Select mode
# ==============================
def select_mode():
    print("Select gamemode (press Enter for default: osu!megamix):")
    for i, mode in enumerate(UI_MODES, 1):
        print(f"{i}. {mode}")
    choice = input("Enter number: ").strip()
    if not choice:
        selected_internal = MEGAMIX_INTERNAL
        selected_ui = MEGAMIX_UI
    else:
        try:
            idx = int(choice) - 1
            if idx < 0 or idx >= len(UI_MODES):
                raise ValueError
            selected_internal = INTERNAL_MODES[idx]
            selected_ui = UI_MODES[idx]
        except:
            print("Invalid choice, defaulting to osu!megamix")
            selected_internal = MEGAMIX_INTERNAL
            selected_ui = MEGAMIX_UI
    print(f"[osu!megamix] Mode selected: {selected_ui}")
    return selected_internal, selected_ui

# ==============================
# Play mode
# ==============================
def play_mode(mode_internal, beatmaps):
    if mode_internal == MEGAMIX_INTERNAL:
        print("[osu!megamix] Starting MEGAMIX mode: real-time shuffled beatmaps")
        if not beatmaps:
            print("[osu!megamix] No beatmaps found!")
            return
        random.shuffle(beatmaps)
        for bm in beatmaps:
            print(f"[osu!megamix] Playing: {os.path.basename(bm)}")
        print("[osu!megamix] MEGAMIX session complete!")
    else:
        print(f"[osu!megamix] Playing standard mode: {mode_internal}")
        if beatmaps:
            bm = random.choice(beatmaps)
            print(f"[osu!megamix] Playing: {os.path.basename(bm)}")
        else:
            print("[osu!megamix] No beatmaps available!")

# ==============================
# Main
# ==============================
def main():
    beatmaps = load_beatmaps()
    history = load_player_history()
    mode_internal, mode_ui = select_mode()
    play_mode(mode_internal, beatmaps)
    history.append(mode_ui)
    save_player_history(history)
    print("[osu!megamix] Session complete, history updated.")

if __name__ == "__main__":
    main()
