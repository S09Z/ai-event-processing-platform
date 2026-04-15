"""Pytest configuration for event-service – adds app to sys.path."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
