"""Test configuration for gamma-api-mastery scripts."""

import sys
from pathlib import Path

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
_SCRIPTS_DIR = str(Path(__file__).resolve().parents[1])

if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
