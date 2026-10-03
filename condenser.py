import json
import sys


def parse_hit_object(line):
    parts = line.split(",")

    if len(parts) < 5:
        return None

    x = int(parts[0])
    y = int(parts[1])
    time = int(parts[2])
    object_type = int(parts[3])

    event = {
        "time": time,
        "x": x,
        "y": y,
        "type": object_type,
    }

    if object_type & 1:
        event["kind"] = "circle"
    elif object_type & 2:
        event["kind"] = "slider"
    elif object_type & 8:
        event["kind"] = "spinner"
    else:
        event["kind"] = "unknown"

    return event


def events(beatmap):
    section = None

    for raw_line in beatmap.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if line.startswith("[") and line.endswith("]"):
            section = line
            continue

        if section == "[HitObjects]":
            event = parse_hit_object(line)

            if event is not None:
                yield event


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as file:
            beatmap = file.read()
    else:
        beatmap = sys.stdin.read()

    for event in events(beatmap):
        print(json.dumps(event, separators=(",", ":")))


if __name__ == "__main__":
    main()
