"""Compatibility entry point for tools.update_server."""

if __name__ == "__main__":
    import runpy
    runpy.run_module("tools.update_server", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("tools.update_server")
