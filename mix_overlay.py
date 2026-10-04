active=False


def activate(payload):
    global active
    if payload.name == "mix_overlay.zip":
        active=True
        return display


def display():
    return "display"


def is_active():
    return active
