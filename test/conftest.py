"""
Root conftest – adds all service roots to sys.path so every test suite
can use `from app.xxx import yyy` regardless of where pytest is invoked from.
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
_SERVICES = ["gateway", "event-service", "ai-service", "analytics-service"]

for _svc in _SERVICES:
    _path = str(_ROOT / "services" / _svc)
    if _path not in sys.path:
        sys.path.insert(0, _path)
