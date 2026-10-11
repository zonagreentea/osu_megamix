"""Generate a shared gameplay timeline from osu! and custom beatmaps."""

import csv
import json
import sys
from pathlib import Path


DEFAULT_MODES = ("osu", "taiko", "catch", "mania", "megamix")


def read_beatmap(path):
    """Read beatmap metadata, media references, and timed hit objects."""
    path = Path(path)
    text = path.read_text(encoding="utf-8-sig", errors="replace")

    if not text.lstrip().startswith("osu file format v"):
        raise ValueError(f"Not a standard osu! beatmap: {path}")

    sections = {}
    section = None

    for raw_line in text.splitlines():
        line = raw_line.strip()

        if not line or line.startswith("//"):
            continue

        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            sections.setdefault(section, [])
        elif section:
            sections[section].append(line)

    def fields(section_name):
        result = {}
        for line in sections.get(section_name, []):
            if ":" in line:
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result

    general = fields("General")
    metadata = fields("Metadata")

    objects = []
    for line in sections.get("HitObjects", []):
        parts = line.split(",")
        if len(parts) < 5:
            continue

        try:
            x, y, time, object_type = map(int, parts[:4])
        except ValueError:
            continue

        if object_type & 1:
            kind = "circle"
        elif object_type & 2:
            kind = "slider"
        elif object_type & 8:
            kind = "spinner"
        else:
            kind = "unknown"

        objects.append({
            "time": time,
            "x": x,
            "y": y,
            "type": object_type,
            "kind": kind,
        })

    objects.sort(key=lambda obj: obj["time"])

    if "HitObjects" not in sections or not objects:
        raise ValueError(f"Beatmap has no valid hit objects: {path}")

    video = None
    for line in sections.get("Events", []):
        try:
            parts = next(csv.reader([line], skipinitialspace=True))
        except (csv.Error, StopIteration):
            continue

        if len(parts) >= 3 and parts[0].strip() == "Video":
            try:
                video_offset = int(parts[1].strip())
            except ValueError:
                video_offset = 0

            video = {
                "file": parts[2].strip(),
                "offset_ms": video_offset,
            }
            break

    return {
        "source": str(path),
        "title": metadata.get("Title", path.stem),
        "artist": metadata.get("Artist", "Unknown"),
        "creator": metadata.get("Creator", "Unknown"),
        "difficulty": metadata.get("Version", "Unknown"),
        "audio": general.get("AudioFilename"),
        "video": video,
        "objects": objects,
        "duration_ms": objects[-1]["time"] + 1 if objects else 0,
    }



def read_custom_map(path):
    """Read '# beat_number | seconds | key' maps into normalized events."""
    path = Path(path)
    rows = []
    previous_time = -1

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        if len(parts) != 3:
            raise ValueError(
                f"{path}:{line_number}: expected beat_number seconds key"
            )

        try:
            beat_number = int(parts[0])
            time_ms = round(float(parts[1]) * 1000)
        except ValueError as exc:
            raise ValueError(
                f"{path}:{line_number}: invalid beat number or time"
            ) from exc

        key = parts[2]
        if beat_number < 1 or time_ms < 0:
            raise ValueError(
                f"{path}:{line_number}: beat number must be positive "
                "and time must not be negative"
            )
        if time_ms < previous_time:
            raise ValueError(
                f"{path}:{line_number}: events must be in time order"
            )

        rows.append({
            "time": time_ms,
            "beat": beat_number,
            "key": key,
            "kind": "key",
            "type": "input",
        })
        previous_time = time_ms

    if not rows:
        raise ValueError(f"Custom map has no events: {path}")

    return {
        "source": str(path),
        "title": path.stem,
        "artist": "Unknown",
        "creator": "Unknown",
        "difficulty": "Custom",
        "audio": None,
        "video": None,
        "objects": rows,
        "duration_ms": rows[-1]["time"] + 1,
    }


def read_source(path):
    """Choose the adapter by file extension; never silently accept unknowns."""
    path = Path(path)
    suffix = path.suffix.lower()

    if suffix == ".osu":
        return read_beatmap(path)
    if suffix == ".map":
        return read_custom_map(path)

    raise ValueError(f"Unsupported beatmap format: {path.suffix or '(no extension)'}")


def generate_mix(paths, modes=DEFAULT_MODES, segment_ms=30000):
    """Build ordered segments with a shared, monotonically increasing timeline."""
    if not paths:
        raise ValueError("Provide at least one beatmap.")
    if not modes:
        raise ValueError("Provide at least one gameplay mode.")
    if segment_ms <= 0:
        raise ValueError("segment_ms must be positive.")

    beatmaps = [read_source(path) for path in paths]
    segments = []
    timeline_end = 0
    mode_index = 0

    for beatmap in beatmaps:
        duration = beatmap["duration_ms"]
        if duration <= 0:
            continue

        for local_start in range(0, duration, segment_ms):
            local_end = min(local_start + segment_ms, duration)
            selected_mode = modes[mode_index % len(modes)]
            mode_index += 1

            segment_objects = []
            for obj in beatmap["objects"]:
                if local_start <= obj["time"] < local_end:
                    event = dict(obj)
                    event["time"] = timeline_end + obj["time"] - local_start
                    event["source_time"] = obj["time"]
                    segment_objects.append(event)

            segments.append({
                "mode": selected_mode,
                "timeline_start": timeline_end,
                "timeline_end": timeline_end + local_end - local_start,
                "source": beatmap["source"],
                "title": beatmap["title"],
                "artist": beatmap["artist"],
                "audio": beatmap["audio"],
                "audio_start_ms": local_start,
                "video": beatmap["video"],
                "video_start_ms": local_start,
                "objects": segment_objects,
            })

            timeline_end += local_end - local_start

    return {
        "format": "osu_megamix_generation_v1",
        "duration_ms": timeline_end,
        "modes": list(modes),
        "segments": segments,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a Megamix timeline from osu! or custom beatmaps."
    )
    parser.add_argument(
        "--segment-ms",
        type=int,
        default=30000,
        help="duration of each mode segment in milliseconds (default: 30000)",
    )
    parser.add_argument(
        "--modes",
        default=",".join(DEFAULT_MODES),
        help="comma-separated mode rotation (default: osu,taiko,catch,mania,megamix)",
    )
    parser.add_argument(
        "beatmaps",
        nargs="+",
        help="input .osu and/or .map files",
    )
    args = parser.parse_args()

    modes = tuple(mode.strip() for mode in args.modes.split(",") if mode.strip())
    try:
        plan = generate_mix(args.beatmaps, modes=modes, segment_ms=args.segment_ms)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print(json.dumps(plan, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
