"""Compatibility alias for src.social.friends."""

import sys
from src.social import friends as _implementation

sys.modules[__name__] = _implementation
