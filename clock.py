"""Compatibility entry point for src.core.clock."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.core.clock", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.core.clock")
