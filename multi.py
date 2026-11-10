"""Compatibility entry point for src.social.multiplayer."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.social.multiplayer", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.social.multiplayer")
