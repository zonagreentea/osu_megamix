"""Compatibility entry point for src.input.device_link."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.input.device_link", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.input.device_link")
