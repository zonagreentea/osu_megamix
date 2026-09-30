#!/usr/bin/env python3
# osu!megamix playable prototype - audio driver sync minimal

import sounddevice as sd
import numpy as np
import time
import threading
import random

# Settings
BPM = 120
BEAT_INTERVAL = 60 / BPM
HIT_WINDOW = 0.15  # seconds

# Simulated beatmap (random for demo)
beatmap = [i * BEAT_INTERVAL for i in range(32)]

score = 0
hit_index = 0
start_time = None

# Audio callback (just silence, we read driver later if needed)
def callback(outdata, frames, time_info, status):
    outdata[:] = np.zeros((frames, 2))

def run_audio():
    with sd.OutputStream(channels=2, callback=callback, samplerate=44100):
        while hit_index < len(beatmap):
            time.sleep(0.1)

# Terminal display
def run_game():
    global hit_index, score, start_time
    start_time = time.time()
    while hit_index < len(beatmap):
        now = time.time() - start_time
        if hit_index < len(beatmap) and abs(now - beatmap[hit_index]) < HIT_WINDOW:
            print(f"🎯 Hit circle {hit_index+1}! (time {now:.2f}s)")
            score += 100
            hit_index += 1
        time.sleep(0.01)
    print(f"🏆 Done! Score: {score}")

# Run both threads
t1 = threading.Thread(target=run_audio, daemon=True)
t2 = threading.Thread(target=run_game)
t1.start()
t2.start()
t2.join()
