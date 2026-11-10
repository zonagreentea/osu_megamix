"""Compatibility entry point for src.social.network."""

from src.social import network as _implementation

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "server":
        _implementation.serve()
    else:
        _implementation.test()
else:
    import sys

    sys.modules[__name__] = _implementation
