"""Compatibility entry point for src.input.universal_client."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("src.input.universal_client", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("src.input.universal_client")
