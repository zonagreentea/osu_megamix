import subprocess
import sys


def read(path):
    with open(path, "rb") as file:
        return file.read()


def write(path, data):
    with open(path, "wb") as file:
        file.write(data)


def play(path):
    return subprocess.Popen(
        ["afplay", path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def stop(process):
    if process is not None:
        process.terminate()


def sound(path):
    data = read(path)
    return play(path), data


def main():
    if len(sys.argv) != 2:
        print("usage: sound.py <sound>")
        raise SystemExit(1)

    process, data = sound(sys.argv[1])

    print(f"bytes={len(data)}")
    process.wait()


if __name__ == "__main__":
    main()
