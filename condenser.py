import sys


def events(beatmap):
    for line in beatmap.splitlines():
        line = line.strip()

        if not line or line.startswith("[") or ":" in line:
            continue

        yield line


def main():
    data = sys.stdin.read()
    for event in events(data):
        print(event)


if __name__ == "__main__":
    main()
