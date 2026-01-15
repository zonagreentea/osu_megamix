#!/usr/bin/env python3
import sys, os, time, threading, termios, tty
from collections import deque

# ===== clock =====
def now_ns() -> int:
    return time.perf_counter_ns()

def ns_to_ms(ns: int) -> float:
    return ns / 1_000_000.0

# ===== config =====
BPM = float(os.environ.get("BPM", "140"))
BEAT_NS = int(round((60.0 / BPM) * 1_000_000_000))

W_300_NS = int(float(os.environ.get("W300", "0.040")) * 1_000_000_000)
W_100_NS = int(float(os.environ.get("W100", "0.090")) * 1_000_000_000)
W_50_NS  = int(float(os.environ.get("W50",  "0.140")) * 1_000_000_000)

HUD_W = int(os.environ.get("HUDW", "60"))
FPS   = float(os.environ.get("FPS", "30"))  # keep render lighter in terminal

OFFSET_NS = int(float(os.environ.get("OFFSET_MS", "0.0")) * 1_000_000)         # calibration
LATE_BIAS_NS = int(float(os.environ.get("LATE_BIAS_MS", "10.0")) * 1_000_000)  # prefer previous beat

def grade(dt_ns: int) -> str:
    a = abs(dt_ns)
    if a <= W_300_NS: return "300"
    if a <= W_100_NS: return "100"
    if a <= W_50_NS:  return "50"
    return "MISS"

def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x

def phase_bar(phase01, gate):
    p = int(clamp(phase01, 0.0, 0.999999) * HUD_W)
    bar = ["-"] * HUD_W
    if 0 <= p < HUD_W: bar[p] = "|"
    bar[HUD_W//2] = "•"
    s = "".join(bar)
    if gate == "300": tag = "<<< PRESS (300) >>>"
    elif gate == "100": tag = "<<< PRESS (100) >>>"
    elif gate == "50": tag = "<<< PRESS (50) >>>"
    else: tag = ""
    return s, tag

def cls():
    sys.stdout.write("\033[2J\033[H")

# ===== shared state for renderer =====
state_lock = threading.Lock()
state = {
    "alive": True,
    "beat": 0,
    "pending": 0,
    "last_grade": "—",
    "last_dt_ms": 0.0,
    "next_ms": 0.0,
    "delta_ms": 0.0,
    "phase_pct": 0.0,
    "gate": "",
    "key_echo": "—",
    "s300": 0, "s100": 0, "s50": 0, "smiss": 0,
}

# ===== input queue =====
inq_lock = threading.Lock()
inq = deque()  # (t_ns, ch)

def input_thread():
    # blocks waiting for bytes; timestamps at arrival
    fd = sys.stdin.fileno()
    while True:
        try:
            ch = os.read(fd, 1)
        except Exception:
            break
        if not ch:
            break
        t = now_ns()
        with inq_lock:
            inq.append((t, ch.decode(errors="ignore")))
        # allow clean shutdown
        with state_lock:
            if not state["alive"]:
                break

def render_loop():
    cls()
    interval = 1.0 / FPS
    next_frame = time.perf_counter()

    while True:
        t = time.perf_counter()
        if t < next_frame:
            time.sleep(next_frame - t)
        next_frame += interval

        with state_lock:
            if not state["alive"]:
                break
            beat = state["beat"]; pending = state["pending"]
            last_grade = state["last_grade"]; last_dt_ms = state["last_dt_ms"]
            next_ms = state["next_ms"]; delta_ms = state["delta_ms"]
            phase_pct = state["phase_pct"]; gate = state["gate"]
            key_echo = state["key_echo"]
            s300 = state["s300"]; s100 = state["s100"]; s50 = state["s50"]; smiss = state["smiss"]

        bar, tag = phase_bar(phase_pct/100.0, gate)

        sys.stdout.write("\033[H")
        sys.stdout.write("osu!megamix — TERMINAL (input-thread)\n")
        sys.stdout.write("="*78 + "\n")
        sys.stdout.write(f"BPM {BPM:>6.1f} | beat {beat:04d} | pending {pending:3d} | FPS {FPS:g}\n")
        sys.stdout.write(f"next +{next_ms:7.1f}ms | Δ(nearest) {delta_ms:+8.1f}ms | phase {phase_pct:5.1f}%\n")
        sys.stdout.write(f"offset {ns_to_ms(OFFSET_NS):+6.1f}ms | late-bias {ns_to_ms(LATE_BIAS_NS):.1f}ms\n")
        sys.stdout.write(f"[{bar}]\n")
        sys.stdout.write(f"{tag}\n" if tag else "\n")
        sys.stdout.write("-"*78 + "\n")
        sys.stdout.write(f"last: {last_grade:<4} dt={last_dt_ms:+8.1f}ms key={key_echo}\n")
        sys.stdout.write(f"300 {s300:6d} | 100 {s100:6d} |  50 {s50:6d} | MISS {smiss:6d}\n")
        sys.stdout.write("\nSPACE=hit  q=quit\n")
        sys.stdout.flush()

def main():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)

    pending = deque()  # (index, beat_time_ns)

    try:
        t0 = now_ns()
        beat = 0
        next_beat = t0 + BEAT_NS

        s300 = s100 = s50 = smiss = 0
        last_grade = "—"
        last_dt_ns = 0
        key_echo = "—"

        rt = threading.Thread(target=render_loop, daemon=True)
        it = threading.Thread(target=input_thread, daemon=True)
        rt.start()
        it.start()

        # logic tick (fine-grained; input is decoupled now)
        while True:
            t = now_ns()

            while t >= next_beat:
                beat += 1
                pending.append((beat, next_beat))
                next_beat += BEAT_NS

            while pending and t > (pending[0][1] + W_50_NS):
                pending.popleft()
                smiss += 1
                last_grade = "MISS"
                last_dt_ns = 0
                key_echo = "—"

            # live feedback relative to nearest beat
            k_near = int(round((t - t0) / BEAT_NS))
            t_near = t0 + k_near * BEAT_NS
            delta_ns = (t - t_near) - OFFSET_NS
            delta_ms = ns_to_ms(delta_ns)

            phase01 = ((t - t0) % BEAT_NS) / BEAT_NS
            phase_pct = phase01 * 100.0
            next_ms = max(0.0, ns_to_ms(next_beat - t))

            ad = abs(delta_ns)
            if ad <= W_300_NS: gate = "300"
            elif ad <= W_100_NS: gate = "100"
            elif ad <= W_50_NS: gate = "50"
            else: gate = ""

            # consume all queued inputs (true arrival timestamps)
            while True:
                with inq_lock:
                    if not inq:
                        break
                    t_key, ch = inq.popleft()

                if ch == 'q':
                    raise SystemExit(0)

                key_echo = repr(ch)

                if ch == ' ':
                    t_hit = t_key
                    best_i = None
                    best_score = None
                    best_dt = None

                    for i, (bidx, bt) in enumerate(pending):
                        dt = (t_hit - bt) - OFFSET_NS
                        adt = abs(dt)
                        if adt <= W_50_NS:
                            score = adt
                            if dt > 0:
                                score = max(0, score - LATE_BIAS_NS)  # prefer late hits
                            if best_score is None or score < best_score:
                                best_score = score
                                best_i = i
                                best_dt = dt

                    if best_i is None:
                        smiss += 1
                        last_grade = "MISS"
                        last_dt_ns = 0
                    else:
                        g = grade(best_dt)
                        last_grade = g
                        last_dt_ns = best_dt
                        if g == "300": s300 += 1
                        elif g == "100": s100 += 1
                        elif g == "50": s50 += 1
                        else: smiss += 1
                        del pending[best_i]

            with state_lock:
                state["beat"] = beat
                state["pending"] = len(pending)
                state["last_grade"] = last_grade
                state["last_dt_ms"] = ns_to_ms(last_dt_ns)
                state["next_ms"] = next_ms
                state["delta_ms"] = delta_ms
                state["phase_pct"] = phase_pct
                state["gate"] = gate
                state["key_echo"] = key_echo
                state["s300"] = s300; state["s100"] = s100; state["s50"] = s50; state["smiss"] = smiss

            # cheap yield; input thread is doing the real work
            time.sleep(0.0005)

    except SystemExit:
        pass
    finally:
        with state_lock:
            state["alive"] = False
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        print("\n[osu!megamix] session ended")

if __name__ == "__main__":
    main()
