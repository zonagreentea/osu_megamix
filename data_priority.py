"""Shared logical data priorities for the offline-first runtime.

Priority controls scheduling importance, never chronological event order.
"""

from enum import IntEnum


class DataPriority(IntEnum):
    INTEGRITY = 0
    TIME_AUDIO = 1
    INPUT_GAMEPLAY = 2
    EVENT_SCHEDULING = 3
    RENDERING = 4
    STORAGE_CONTENT = 5
    OPTIONAL_SERVICES = 6


def priority_of(value):
    """Validate an engine-assigned priority (reject bool and unknown values)."""
    if isinstance(value, bool) or not isinstance(value, (int, DataPriority)):
        raise TypeError("priority must be an integer")
    try:
        return DataPriority(value)
    except ValueError as exc:
        raise ValueError("unknown data priority") from exc
