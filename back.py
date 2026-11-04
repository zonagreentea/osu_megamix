"""Compatibility entry point for src.core.runtime."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.core.runtime", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.core.runtime")
