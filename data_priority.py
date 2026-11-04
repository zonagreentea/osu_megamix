"""Compatibility entry point for src.core.data_priority."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.core.data_priority", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.core.data_priority")
