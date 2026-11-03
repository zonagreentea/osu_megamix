"""Compatibility alias for src.social.collection."""

import sys
from src.social import collection as _implementation

sys.modules[__name__] = _implementation
