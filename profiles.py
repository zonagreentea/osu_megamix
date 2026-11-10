"""Compatibility alias for src.social.profiles."""

import sys
from src.social import profiles as _implementation

sys.modules[__name__] = _implementation
