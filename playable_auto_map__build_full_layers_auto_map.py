import subprocess, tempfile, os, time, threading
import numpy as np

BUFFER_SIZE = 2048
HIT_THRESHOLD = 0.05
BEAT_WINDOW = 0.1  # seconds for one hit object

# Minimal in-memory hit object storage
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
    # Minimal hit object: time + intensity
    hit_objects.append({'time': timestamp, 'intensity': hits})
    print(f"[Auto-Map] Hit Object at {timestamp:.3f}s, intensity={hits}")

def run_playable_auto_map(timeline_start=0.0):
    start_time = time.time() - timeline_start
    try:
        while True:
            block = record_block()
            hits = detect_hits(block)
            if hits > 0:
                timestamp = time.time() - start_time
                generate_hit_object(hits, timestamp)
            time.sleep(BEAT_WINDOW)
    except KeyboardInterrupt:
        print("Exiting playable auto-map layer...")

# Run in thread if imported
def start_auto_map_layer():
    threading.Thread(target=run_playable_auto_map, daemon=True).start()

if __name__ == "__main__":
    print("osu!megamix full playable auto-map layer running")
    run_playable_auto_map()
