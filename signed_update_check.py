"""Compatibility entry point for tools.signed_update_check."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("tools.signed_update_check", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("tools.signed_update_check")
