#!/usr/bin/env run

controls = []

accessibility = {
    "single_input": True,
    "announce_highlight": True,
}

def add(action, beat, text=None):
    controls.append({
        "action": action,
        "beat": beat,
        "text": text or action,
    })

def highlight(time):
    for control in controls:
        if control["beat"] <= time:
            return control

def activate(control):
    return control["action"]

def announce(control):
    print(control["text"])
