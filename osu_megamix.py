#!/usr/bin/env python3

"""osu!megamix universal interface and session runner."""

import os
import random
import subprocess
import sys
import time

from scoring import Score
from timing import JudgementWindow, TimedHit
from timeline import Timeline


RC_COLOR = "\033[38;2;255;42;141m"
RESET = "\033[0m"

BEATMAP_DIRS = ["osu_beatmaps", "osu_mix_beatmaps"]

MODES_DISPLAY = [
    "osu!megamix",
    "osu!",
    "osu!taiko",
    "osu!catch",
    "osu!mania",
]

MODES_INTERNAL = [
    "red-charizard",
    "osu!",
    "taiko",
    "catch",
    "mania",
]

JUDGEMENT_WINDOWS = (
    JudgementWindow(8, 300),
    JudgementWindow(4, 100),
    JudgementWindow(2, 50),
)


# ---------------------------------------------------------------------------
# Universal interface
# ---------------------------------------------------------------------------

def state(value=None):
    return value


def input(value=None):
    if value is not None:
        return value
    return sys.stdin.readline().rstrip("\n")


def output(value=None):
    if value is not None:
        print(value)
    return value


def agreement(query):
    return input(query)


def open_source(source):
    process = subprocess.run(
        ["./open.zsh", source],
        capture_output=True,
        text=True,
        check=True,
    )
    return process.stdout


def mix(events, gamemode="osu"):
    process = subprocess.run(
        ["./mix", gamemode],
        input=events,
        capture_output=True,
        text=True,
        check=True,
    )
    return process.stdout


# ---------------------------------------------------------------------------
# osu!megamix session
# ---------------------------------------------------------------------------

def rc_log(message):
    print(f"{RC_COLOR}[osu!megamix]{RESET} {message}")


def load_beatmaps():
    """Discover available beatmaps."""
    beatmaps = []

    for directory in BEATMAP_DIRS:
        if not os.path.exists(directory):
            continue

        for filename in os.listdir(directory):
            if filename.endswith(".osu") or filename.endswith(".mix"):
                beatmaps.append(os.path.join(directory, filename))

    return beatmaps


def select_mode():
    """Select the visible game mode."""
    print("Select gamemode (press Enter for default: osu!megamix):")

    for index, name in enumerate(MODES_DISPLAY, start=1):
        print(f"{index}. {name}")

    choice = input("Enter number: ").strip()

    if choice.isdigit() and 1 <= int(choice) <= len(MODES_DISPLAY):
        index = int(choice) - 1
    else:
        index = 0

    return MODES_DISPLAY[index], MODES_INTERNAL[index]


def play_timed_session(score, timeline, bpm=120.0, count=5):
    """Run a small real-time musical timing session."""
    beat = 60.0 / bpm
    start = timeline.now() + beat

    rc_log(f"Timing engine active: {bpm:g} BPM")

    for index in range(count):
        target = start + (beat * index)

        hit = TimedHit(
            target_time=target,
            bpm=bpm,
            windows=JUDGEMENT_WINDOWS,
        )

        while timeline.now() < target:
            time.sleep(0.001)

        input_time = timeline.now()
        judgement = hit.judge(input_time)

        if judgement is None:
            score.apply(None)

            rc_log(
                f"💯 Note {index + 1}: MISS "
                f"(combo={score.combo})"
            )
        else:
            score.apply(judgement)

            rc_log(
                f"🎯 Note {index + 1}: "
                f"1/{judgement.subdivision} "
                f"value={judgement.value} "
                f"distance={judgement.distance * 1000:.2f}ms"
            )

    return score


def session():
    """Run an osu!megamix session."""
    beatmaps = load_beatmaps()

    rc_log(
        f"Loaded {len(beatmaps)} beatmaps "
        "(Red-Charizard aware!)"
    )

    selected_display, selected_internal = select_mode()

    rc_log(
        f"Mode selected: {selected_display} "
        f"(internally: {selected_internal})"
    )

    score = Score()
    timeline = Timeline()

    if selected_internal == "red-charizard":
        if beatmaps:
            rc_log(
                "osu!megamix MEGAMIX starting: "
                "auto-preloading shuffled beatmaps..."
            )

            playlist = random.sample(
                beatmaps,
                min(50, len(beatmaps)),
            )

            for index, beatmap in enumerate(playlist, start=1):
                rc_log(
                    f"Cooking beatmap "
                    f"{index}/{len(playlist)}: {beatmap}"
                )

            rc_log("Starting musical timing session...")
            play_timed_session(score, timeline)
        else:
            rc_log(
                "No beatmaps found for osu!megamix "
                "(Red-Charizard sad)."
            )
    else:
        rc_log(f"Starting {selected_display} session...")

        if beatmaps:
            play_timed_session(score, timeline)
        else:
            rc_log(f"No beatmaps available for {selected_display}!")

    history_file = os.path.expanduser(
        "~/playerbase_history.txt"
    )

    with open(history_file, "a") as history:
        history.write(f"{selected_display}\n")

    rc_log(
        f"Session complete. "
        f"Score: {score.points} | "
        f"Combo: {score.combo} | "
        f"Health: {score.health}"
    )

    return score


def run(source=None, gamemode="osu"):
    """Universal execution entry point."""
    if source is None:
        return session()

    return source


if __name__ == "__main__":
    if len(sys.argv) < 2:
        session()
    else:
        source = sys.argv[1]
        gamemode = sys.argv[2] if len(sys.argv) > 2 else "osu"
        output(run(source, gamemode))
