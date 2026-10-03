#!/usr/bin/env run

settings = {
    "accessibility": {
        "single_input": False,
        "announce_highlight": False,
        "screen_reader": False,
        "spoken_menus": False,
        "spoken_gameplay_events": False,
        "remap_controls": True,
        "simplified_controls": False,
        "one_handed_layout": False,
        "remove_button_mashing": False,
        "remove_simultaneous_inputs": False,
        "remove_complex_gestures": False,
        "remove_required_dragging": False,
        "pause_anywhere": True,
        "reduced_motion": False,
        "reduced_flashing": True,
        "reduced_visual_effects": False,
        "high_contrast": False,
        "large_targets": False,
        "subtitles": True,
        "captions": True,
        "visual_timing_cues": True,
        "haptic_timing_cues": True,
        "text_to_speech": False,
        "speech_to_text": False,
    },

    "audio": {
        "master_volume": 1.0,
        "music_volume": 1.0,
        "effects_volume": 1.0,
        "dialogue_volume": 1.0,
        "mono_audio": False,
    },

    "video": {
        "brightness": 1.0,
        "contrast": 1.0,
        "ui_scale": 1.0,
        "fullscreen": True,
        "vsync": True,
    },

    "gameplay": {
        "difficulty": 1.0,
        "game_speed": 1.0,
        "timing_window": 1.0,
        "practice_mode": False,
        "hints": True,
        "tutorials": True,
    },

    "interface": {
        "text_size": 1.0,
        "show_tooltips": True,
        "show_control_hints": True,
        "confirm_actions": True,
        "reduce_clutter": False,
    },

    "easter_eggs": {
        "mysterious_button": False,
    },
}


controls = []


def add(action, input, context=None, label=None):
    controls.append({
        "action": action,
        "input": input,
        "context": context,
        "label": label or action,
    })


# Common controls
add("up", "up")
add("down", "down")
add("left", "left")
add("right", "right")
add("confirm", "enter")
add("back", "escape")
add("pause", "escape")


# Easter egg
if settings["easter_eggs"]["mysterious_button"]:
    add(
        "easter_egg",
        "mysterious",
        label="🥚 Mysterious Button",
    )


def mapper(input, context=None):
    for control in controls:
        if control["input"] == input and (
            control["context"] is None
            or control["context"] == context
        ):
            return control["action"]

    return input
