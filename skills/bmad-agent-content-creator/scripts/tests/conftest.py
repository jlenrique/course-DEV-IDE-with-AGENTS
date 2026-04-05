"""Conftest for content-creator tests — handles hyphenated directory imports."""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1]
_SKILL_DIR = _SCRIPTS_DIR.parent
_REPO_ROOT = _SKILL_DIR.parents[1]

if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


def _ensure_stub(name: str) -> None:
    if name not in sys.modules:
        mod = types.ModuleType(name)
        mod.__path__ = []
        sys.modules[name] = mod


def _load_module(name: str, file_path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, file_path)
    assert spec and spec.loader, f"Cannot load {name} from {file_path}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Register sensory-bridges stubs (dependency for perception_contract)
_BRIDGE_SCRIPTS = _REPO_ROOT / "skills" / "sensory-bridges" / "scripts"

_ensure_stub("skills")
_ensure_stub("skills.sensory_bridges")
_ensure_stub("skills.sensory_bridges.scripts")

_load_module(
    "skills.sensory_bridges.scripts.bridge_utils",
    _BRIDGE_SCRIPTS / "bridge_utils.py",
)
_load_module(
    "skills.sensory_bridges.scripts.png_to_agent",
    _BRIDGE_SCRIPTS / "png_to_agent.py",
)
_load_module(
    "skills.sensory_bridges.scripts.perception_cache",
    _BRIDGE_SCRIPTS / "perception_cache.py",
)

# Register content-creator stubs
_ensure_stub("skills.bmad_agent_content_creator")
_ensure_stub("skills.bmad_agent_content_creator.scripts")

_load_module(
    "skills.bmad_agent_content_creator.scripts.perception_contract",
    _SCRIPTS_DIR / "perception_contract.py",
)
_load_module(
    "skills.bmad_agent_content_creator.scripts.visual_reference_injector",
    _SCRIPTS_DIR / "visual_reference_injector.py",
)
_load_module(
    "skills.bmad_agent_content_creator.scripts.manifest_visual_enrichment",
    _SCRIPTS_DIR / "manifest_visual_enrichment.py",
)
