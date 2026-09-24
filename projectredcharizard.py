#!/usr/bin/env python3

from datetime import datetime, timedelta


# ─────────────────────────────────────────────────────────────
# osu!megamix — Recursive Safety Net Selection Algorithm
#
# Title     → termination
# Author    → schedule
# Terminate → time
#
# Uncertainty is always NO.
# ─────────────────────────────────────────────────────────────

def safety_net(song):
    """
    Every requirement must be explicitly confirmed.
    Anything other than YES is a denial.
    """
    checks = (
        song["law"],
        song["privacy"],
        song["consent"],
    )

    return all(check == "YES" for check in checks)


def schedule(author, start_time):
    """
    The author establishes the scheduling identity.
    """
    return {
        "author": author,
        "scheduled": start_time,
    }


def terminate(title, termination_time):
    """
    The title identifies what the termination applies to.
    Time determines when termination occurs.
    """
    return {
        "title": title,
        "terminate_at": termination_time,
    }


def select(songs, index=0):
    """
    Recursive selection.

    A rejected or uncertain song is never selected.
    The function moves to the next candidate.
    """
    if index >= len(songs):
        return None

    song = songs[index]

    if not safety_net(song):
        return select(songs, index + 1)

    return song


def megamix(songs, start_time, duration):
    """
    Build one authorized recursive selection.
    """
    song = select(songs)

    if song is None:
        return None

    scheduled = schedule(song["author"], start_time)
    ending = start_time + timedelta(seconds=duration)

    termination = terminate(song["title"], ending)

    return {
        "song": song,
        "schedule": scheduled,
        "termination": termination,
    }


# ─────────────────────────────────────────────────────────────
# Example
# ─────────────────────────────────────────────────────────────

songs = [
    {
        "title": "Example Map",
        "author": "Example Mapper",
        "duration": 180,
        "law": "YES",
        "privacy": "YES",
        "consent": "YES",
    },
    {
        "title": "Second Map",
        "author": "Another Mapper",
        "duration": 210,
        "law": "UNKNOWN",
        "privacy": "YES",
        "consent": "YES",
    },
]

start = datetime.now()

result = megamix(
    songs,
    start,
    songs[0]["duration"]
)

if result:
    print("TITLE:", result["song"]["title"])
    print("AUTHOR:", result["song"]["author"])
    print("SCHEDULED:", result["schedule"]["scheduled"])
    print("TERMINATE:", result["termination"]["terminate_at"])
else:
    print("NO AUTHORIZED SONG")
