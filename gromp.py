import time, random, math, os

MODES = ["osu", "taiko", "catch", "mania"]
mode_index = 0

start_time = time.time()

def gromp_signal(t):
    # core "gromp energy" — tweak this to change feel
    return math.sin(t * 2) + math.sin(t * 0.5) + random.uniform(-0.3, 0.3)

def gen_osu(t, g):
    x = int((g + 2) / 4 * 512)
    y = int(random.uniform(0, 384))
    return f"● ({x},{y})"

def gen_taiko(t, g):
    return "DON" if g > 0 else "KAT"

def gen_catch(t, g):
    x = int((g + 2) / 4 * 512)
    return f"🍎 -> {x}"

def gen_mania(t, g):
    lanes = 4
    lane = int((g + 2) / 4 * lanes)
    return f"⬇ lane {max(0,min(lanes-1,lane))}"

GENERATORS = {
    "osu": gen_osu,
    "taiko": gen_taiko,
    "catch": gen_catch,
    "mania": gen_mania
}

def clear():
    os.system("cls" if os.name == "nt" else "clear")

while True:
    t = time.time() - start_time
    g = gromp_signal(t)

    # flow timing (faster when gromp is high)
    delay = max(0.1, 0.4 - abs(g) * 0.2)

    mode = MODES[mode_index]
    note = GENERATORS[mode](t, g)

    clear()
    print(f"=== GROMP FLOW ENGINE ===")
    print(f"mode: {mode}")
    print(f"gromp: {round(g, 3)}")
    print(f"note: {note}")

    # occasionally switch modes (flow, not abrupt)
    if random.random() < 0.1:
        mode_index = (mode_index + 1) % len(MODES)

    time.sleep(delay)
