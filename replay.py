"""Compatibility entry point for src.gameplay.replay."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.gameplay.replay", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.gameplay.replay")
