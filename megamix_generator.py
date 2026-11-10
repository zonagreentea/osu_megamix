"""Compatibility entry point for tools.megamix_generator."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("tools.megamix_generator", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("tools.megamix_generator")
