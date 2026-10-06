from lobby import create_lobby


MODES = {
    1: "regular",
    2: "megamix",
    3: "collection",
    4: "rp",
}


def create_multi_lobby(choice):
    if isinstance(choice, int):
        try:
            choice = MODES[choice]
        except KeyError:
            raise ValueError("multi lobby choice must be 1, 2, 3, or 4")

    return create_lobby(choice)


def describe_lobby(lobby):
    return {
        "mode": lobby.mode,
        "voice_chat": lobby.voice_chat,
        "proximity_voice": lobby.proximity_voice,
        "players": list(lobby.players),
        "started": lobby.started,
    }
