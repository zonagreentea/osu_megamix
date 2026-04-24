import time
import random

energy = 0.0
flow = 100
bpm = 120.0

print("osu!megamix — live core started")
print("press CTRL+C to exit")

while True:
    time.sleep(0.1)

    # fake input simulation (since we haven't wired keyboard yet)
    if random.random() < 0.2:
        energy += 0.5
        flow += 2
        print(f"HIT | energy={energy:.2f} flow={flow}")

    energy *= 0.97
    flow -= 1

    if flow <= 0:
        print("=== BUST TO MIX ===")
        flow = 100
        energy = 0.3

    bpm = 60 + energy * 40
    print(f"state | flow={flow} bpm={bpm:.1f} energy={energy:.2f}")
