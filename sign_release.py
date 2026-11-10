"""Compatibility entry point for tools.sign_release."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("tools.sign_release", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("tools.sign_release")
