"""Compatibility entry point for src.audio.sound."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.audio.sound", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.audio.sound")
