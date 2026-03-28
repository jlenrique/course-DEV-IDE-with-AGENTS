"""Conftest for sensory bridges tests — handles hyphenated directory import."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _SCRIPTS_DIR.parents[2]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _load_module(name: str, filename: str):
    """Load a module by file path, caching in sys.modules."""
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS_DIR / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bridge_utils = _load_module(
    "skills.sensory_bridges.scripts.bridge_utils",
    "bridge_utils.py",
)

sys.modules["skills"] = type(sys)("skills")
sys.modules["skills.sensory_bridges"] = type(sys)("skills.sensory_bridges")
sys.modules["skills.sensory_bridges.scripts"] = type(sys)("skills.sensory_bridges.scripts")
sys.modules["skills.sensory_bridges.scripts.bridge_utils"] = bridge_utils

for mod_name, filename in [
    ("skills.sensory_bridges.scripts.pptx_to_agent", "pptx_to_agent.py"),
    ("skills.sensory_bridges.scripts.pdf_to_agent", "pdf_to_agent.py"),
    ("skills.sensory_bridges.scripts.audio_to_agent", "audio_to_agent.py"),
    ("skills.sensory_bridges.scripts.png_to_agent", "png_to_agent.py"),
    ("skills.sensory_bridges.scripts.video_to_agent", "video_to_agent.py"),
]:
    _load_module(mod_name, filename)
