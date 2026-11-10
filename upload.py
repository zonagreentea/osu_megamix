"""Compatibility entry point for tools.upload."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("tools.upload", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("tools.upload")
