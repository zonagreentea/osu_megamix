import subprocess
import sys


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


def condense(beatmap):
    process = subprocess.run(
        ["python3", "condenser.py"],
        input=beatmap,
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


def run(source, gamemode="osu"):
    beatmap = open_source(source)
    events = condense(beatmap)
    return mix(events, gamemode)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: run <source> [gamemode]")
        raise SystemExit(1)

    source = sys.argv[1]
    gamemode = sys.argv[2] if len(sys.argv) > 2 else "osu"

    output(run(source, gamemode))
