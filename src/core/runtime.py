"""
Centralized runtime state manager for pause/escape input logic.

This module provides a single source of truth for:
- Current game context (MAIN_MENU, COLLECTION, MEGAMIX, SOLO, MULTI, MENU, PAUSED)
- Paused state across all game modes
- Context transitions
"""

from enum import Enum


class GameContext(Enum):
    """Enumeration of all possible game contexts."""
    MAIN_MENU = "main_menu"
    MENU = "menu"
    COLLECTION = "collection"
    MEGAMIX = "megamix"
    SOLO = "solo"
    MULTI = "multi"
    PAUSED = "paused"


class Runtime:
    """Centralized runtime state manager for pause/escape input logic."""

    def __init__(self):
        self._context = GameContext.MAIN_MENU
        self._paused = False
        self._context_stack = []

    def get_context(self):
        return self._context

    def set_context(self, context):
        if not isinstance(context, GameContext):
            raise TypeError(f"context must be GameContext, got {type(context)}")
        self._context = context

    def is_paused(self):
        return self._paused

    def pause(self):
        if not self._paused:
            self._context_stack.append(self._context)
            self._paused = True
            self._context = GameContext.PAUSED

    def resume(self):
        if self._paused and self._context_stack:
            self._paused = False
            self._context = self._context_stack.pop()

    def toggle_pause(self):
        if self._paused:
            self.resume()
        else:
            self.pause()

    def reset_to_main_menu(self):
        self._paused = False
        self._context = GameContext.MAIN_MENU
        self._context_stack = []

    def __repr__(self):
        return f"Runtime(context={self._context.value}, paused={self._paused})"


_runtime_instance = Runtime()


def get_runtime():
    return _runtime_instance
