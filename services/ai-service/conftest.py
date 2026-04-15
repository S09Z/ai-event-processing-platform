"""Pytest configuration for ai-service – adds app to sys.path."""

import sys
from pathlib import Path

# Allow `from app.xxx import yyy` in tests without installing the package
sys.path.insert(0, str(Path(__file__).parent))
