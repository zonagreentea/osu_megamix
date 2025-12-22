#!/usr/bin/env python3
import tkinter as tk
import time
import threading
import random
import json
import sys

# =============================
# SETTINGS
# =============================
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
CIRCLE_RADIUS = 30
HIT_WINDOW = 0.3  # seconds
BEAT_INTERVAL = 1.0  # seconds between notes

# =============================
# GLOBAL GAME STATE
# =============================
score = 0
combo = 0
max_combo = 0
running = True

# Example beatmap
BEATMAP = [
    {"time": 1.0, "x": 200, "y": 300, "note": "A"},
    {"time": 2.0, "x": 400, "y": 300, "note": "S"},
    {"time": 3.0, "x": 600, "y": 300, "note": "D"},
    {"time": 4.0, "x": 400, "y": 500, "note": "F"},
]

# =============================
# UTILS
# =============================
def clamp(val, min_val, max_val):
    return max(min_val, min(val, max_val))

# =============================
# PLAYER STATS
# =============================
class Player:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.hits = 0
        self.total = 0

player = Player()

# =============================
# GAME WINDOW
# =============================
root = tk.Tk()
root.title("osu!megamix - Full Game")
canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black")
canvas.pack()

# =============================
# HIT CIRCLES
# =============================
active_notes = []

def spawn_note(note):
    global active_notes
    circle = canvas.create_oval(
        note["x"] - CIRCLE_RADIUS,
        note["y"] - CIRCLE_RADIUS,
        note["x"] + CIRCLE_RADIUS,
        note["y"] + CIRCLE_RADIUS,
        fill="white",
    )
    active_notes.append({"id": circle, "note": note})

def remove_note(circle_id):
    global active_notes
    canvas.delete(circle_id)
    active_notes = [n for n in active_notes if n["id"] != circle_id]

# =============================
# INPUT HANDLER
# =============================
key_map = {"a": "A", "s": "S", "d": "D", "f": "F"}

def key_pressed(event):
    global score, combo, max_combo
    key = event.keysym.lower()
    current_time = time.time() - start_time
    hit = False
    for note in active_notes:
        n = note["note"]
        if key_map.get(key, "") == n["note"] and abs(current_time - n["time"]) <= HIT_WINDOW:
            player.score += 300
            player.combo += 1
            player.max_combo = max(player.max_combo, player.combo)
            hit = True
            remove_note(note["id"])
            break
    if not hit:
        player.combo = 0

canvas.bind_all("<Key>", key_pressed)

# =============================
# GAME LOOP
# =============================
start_time = time.time()

def game_loop():
    global running
    idx = 0
    while running and idx < len(BEATMAP):
        current_time = time.time() - start_time
        next_note = BEATMAP[idx]
        if current_time >= next_note["time"]:
            spawn_note(next_note)
            idx += 1
        # Update score/combo display
        canvas.delete("hud")
        canvas.create_text(
            70, 30, text=f"Score: {player.score}", fill="white", font=("Arial", 16), tag="hud"
        )
        canvas.create_text(
            70, 60, text=f"Combo: {player.combo}", fill="white", font=("Arial", 16), tag="hud"
        )
        root.update()
        time.sleep(0.01)

# =============================
# THREAD TO RUN GAME
# =============================
t = threading.Thread(target=game_loop, daemon=True)
t.start()

# =============================
# RUN
# =============================
try:
    root.mainloop()
    running = False
except KeyboardInterrupt:
    running = False
    print(f"Final Score: {player.score}  Max Combo: {player.max_combo}")
