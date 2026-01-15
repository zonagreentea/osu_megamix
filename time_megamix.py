#!/usr/bin/env python3
import sys, time, os, select, termios, tty
from collections import deque

BPM = float(os.environ.get("BPM", "140"))
BEAT = 60.0 / BPM

# judgement windows (seconds)
W_300 = float(os.environ.get("W300", "0.040"))
W_100 = float(os.environ.get("W100", "0.090"))
W_50  = float(os.environ.get("W50",  "0.140"))

def now():
    return time.monotonic()

def grade(dt):
    a = abs(dt)
    if a <= W_300: return "300"
    if a <= W_100: return "100"
    if a <= W_50:  return "50"
    return "MISS"

def key_nonblock():
    r,_,_ = select.select([sys.stdin], [], [], 0)
    return sys.stdin.read(1) if r else None

def cls():
    sys.stdout.write("\033[2J\033[H")

def hud(beat, pending, last, s300, s100, s50, smiss):
    sys.stdout.write("\033[H")
    sys.stdout.write("osu!megamix — TERMINAL HUD\n")
    sys.stdout.write("="*40 + "\n")
    sys.stdout.write(f"BPM: {BPM:>5.1f}   Beat: {beat:04d}   Pending: {pending:3d}\n")
    sys.stdout.write(f"Last: {last:<5}\n")
    sys.stdout.write("-"*40 + "\n")
    sys.stdout.write(f"300: {s300:5d}   100: {s100:5d}\n")
    sys.stdout.write(f" 50: {s50:5d}   MISS:{smiss:5d}\n")
    sys.stdout.write("\nSPACE = hit   q = quit\n")
    sys.stdout.flush()

def main():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    try:
        cls()
        t0 = now()

        beat = 0
        next_beat = t0 + BEAT

        # pending beats: deque of (index, beat_time)
        pending = deque()

        s300 = s100 = s50 = smiss = 0
        last = "—"

        hud(beat, len(pending), last, s300, s100, s50, smiss)

        TICK = 1/240

        while True:
            t = now()

            # enqueue beats at scheduled times (no drift)
            while t >= next_beat:
                beat += 1
                pending.append((beat, next_beat))
                next_beat += BEAT
                hud(beat, len(pending), last, s300, s100, s50, smiss)

            # auto-miss beats whose hit window has fully passed
            # IMPORTANT: this is what you were missing before
            while pending and t > (pending[0][1] + W_50):
                bidx, bt = pending.popleft()
                smiss += 1
                last = "MISS"
                hud(beat, len(pending), last, s300, s100, s50, smiss)

            k = key_nonblock()
            if k:
                if k == 'q':
                    break
                if k == ' ':
                    # match SPACE to closest pending beat within W_50
                    best_i = None
                    best_dt = None
                    for i, (bidx, bt) in enumerate(pending):
                        dt = t - bt
                        adt = abs(dt)
                        if adt <= W_50 and (best_dt is None or adt < abs(best_dt)):
                            best_i = i
                            best_dt = dt

                    if best_i is None:
                        # off-beat hit: count as MISS (explicit + measurable)
                        smiss += 1
                        last = "MISS"
                        hud(beat, len(pending), last, s300, s100, s50, smiss)
                    else:
                        bidx, bt = pending[best_i]
                        dt = best_dt
                        g = grade(dt)
                        last = g
                        if g == "300": s300 += 1
                        elif g == "100": s100 += 1
                        elif g == "50": s50 += 1
                        else: smiss += 1
                        # remove that beat from pending
                        del pending[best_i]
                        hud(beat, len(pending), last, s300, s100, s50, smiss)

            time.sleep(TICK)

        print("\n[osu!megamix] session ended")
        print(f"[osu!megamix] 300={s300} 100={s100} 50={s50} MISS={smiss}")
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

if __name__ == "__main__":
    main()
