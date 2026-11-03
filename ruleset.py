"""Compatibility entry point for src.gameplay.ruleset."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.gameplay.ruleset", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.gameplay.ruleset")
