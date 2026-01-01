from __future__ import annotations
import os

def append_player_history(selected_display: str, history_file: str | None = None) -> None:
    """
    Append the selected mode/session display name to local history.
    Defaults to ~/playerbase_history.txt to preserve existing behavior.
    """
    if history_file is None:
        history_file = os.path.expanduser("~/playerbase_history.txt")
    os.makedirs(os.path.dirname(history_file), exist_ok=True) if os.path.dirname(history_file) else None
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(f"{selected_display}\n")
