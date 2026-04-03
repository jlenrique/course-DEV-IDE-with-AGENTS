"""Utilities for loading skill modules from hyphenated directories.

The repository stores several skills under hyphenated folder names (for example,
`skills/source-wrangler` and `skills/sensory-bridges`), which are not importable
as regular Python packages. These helpers provide a stable dynamic-loader path.
"""

from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path


def load_module_from_path(module_name: str, file_path: Path):
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module spec for {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _ensure_module_stub(name: str) -> None:
    if name not in sys.modules:
        sys.modules[name] = types.ModuleType(name)


def load_sensory_bridge_utils(repo_root: Path):
    scripts_dir = repo_root / "skills" / "sensory-bridges" / "scripts"
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    _ensure_module_stub("skills")
    _ensure_module_stub("skills.sensory_bridges")
    _ensure_module_stub("skills.sensory_bridges.scripts")

    bridge_utils = load_module_from_path(
        "skills.sensory_bridges.scripts.bridge_utils",
        scripts_dir / "bridge_utils.py",
    )
    load_module_from_path(
        "skills.sensory_bridges.scripts.png_to_agent",
        scripts_dir / "png_to_agent.py",
    )
    return bridge_utils


def load_source_wrangler_operations(repo_root: Path):
    return load_module_from_path(
        "source_wrangler_operations",
        repo_root / "skills" / "source-wrangler" / "scripts" / "source_wrangler_operations.py",
    )
