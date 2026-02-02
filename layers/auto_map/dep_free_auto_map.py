import subprocess, tempfile, os, time
import numpy as np

BUFFER_SIZE = 2048
HIT_THRESHOLD = 0.05

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

prev_hits = 0

def run_auto_map_layer(callback=None):
    global prev_hits
    try:
        while True:
            block = record_block()
            hits = detect_hits(block)
            if hits != prev_hits:
                prev_hits = hits
                if callback:
                    callback(hits)  # send hits to game engine
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting auto-map layer...")

if __name__ == "__main__":
    print("osu!megamix dep-free auto-map layer running")
    run_auto_map_layer()
