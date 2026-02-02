import time, threading, random, subprocess, tempfile, os
import numpy as np

BUFFER_SIZE = 2048
HIT_THRESHOLD = 0.05
BEAT_WINDOW = 0.1
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

hit_objects = []

def record_block(duration=0.05):
    tmpfile = tempfile.NamedTemporaryFile(delete=False)
    tmpfile.close()
    try:
        subprocess.run([
            "sox", "-d", "-b", "16", "-c", "1", "-r", "44100", tmpfile.name,
            "trim", "0", str(duration)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        data = np.fromfile(tmpfile.name, dtype=np.int16)
    except Exception:
        data = np.zeros(BUFFER_SIZE, dtype=np.int16)
    os.unlink(tmpfile.name)
    return data / 32768.0

def detect_hits(samples, threshold=HIT_THRESHOLD):
    energy = np.abs(samples)
    hits = np.sum(energy > threshold)
    return hits

def generate_hit_object(hits, timestamp):
    x = random.randint(50, SCREEN_WIDTH-50)
    y = random.randint(50, SCREEN_HEIGHT-50)
    hit_objects.append({'time': timestamp, 'x': x, 'y': y, 'intensity': hits})
    print(f"[Hit Object] {timestamp:.3f}s at ({x},{y}), intensity={hits}")

def run_playable_auto_map():
    start_time = time.time()
    try:
        while True:
            block = record_block()
            hits = detect_hits(block)
            if hits > 0:
                timestamp = time.time() - start_time
                generate_hit_object(hits, timestamp)
            time.sleep(BEAT_WINDOW)
    except KeyboardInterrupt:
        print("Exiting playable auto-map...")

def run_game_loop():
    start_time = time.time()
    print("osu!megamix full playable prototype started. Press Ctrl+C to quit.")
    try:
        while True:
            now = time.time() - start_time
            active_hits = [h for h in hit_objects if abs(h['time']-now)<BEAT_WINDOW]
            if active_hits:
                for h in active_hits:
                    print(f"[PLAY] Hit circle at ({h['x']},{h['y']}) intensity={h['intensity']}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("Exiting game loop...")

def start_full_playable():
    threading.Thread(target=run_playable_auto_map, daemon=True).start()
    run_game_loop()

if __name__ == "__main__":
    start_full_playable()
