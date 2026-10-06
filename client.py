#!/usr/bin/env python3
import signal
import sys
import time

running = True

def stop(_signum, _frame):
    global running
    running = False

def main():
    global running

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)

    print("osu!megamix client online")

    while running:
        time.sleep(0.25)

    print("osu!megamix client offline")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
