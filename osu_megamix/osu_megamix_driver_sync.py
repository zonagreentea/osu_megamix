#!/usr/bin/env python3
# osu!megamix driver-sync core

import sounddevice as sd
import numpy as np
import time

# === SETTINGS ===
SAMPLE_RATE = 44100        # audio driver sample rate
BUFFER_SIZE = 1024         # samples per chunk
THRESHOLD = 0.05           # hit detection threshold
PRINT_EVERY = 0.1          # seconds between debug prints

# === GAME STATE ===
beat_count = 0

# === AUDIO CALLBACK ===
def audio_callback(indata, frames, time_info, status):
    global beat_count
    volume = np.linalg.norm(indata) / frames
    if volume > THRESHOLD:
        beat_count += 1
        print(f"💥 Beat detected! Total: {beat_count}")

# === STREAM SETUP ===
try:
    with sd.InputStream(channels=1, callback=audio_callback,
                        blocksize=BUFFER_SIZE,
                        samplerate=SAMPLE_RATE):
        print("🎵 osu!megamix driver-sync running… subtle flex active")
        while True:
            time.sleep(PRINT_EVERY)
except KeyboardInterrupt:
    print("\n🛑 osu!megamix stopped by user")
