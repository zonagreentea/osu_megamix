"""Compatibility entry point for src.audio.music."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.audio.music", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.audio.music")
