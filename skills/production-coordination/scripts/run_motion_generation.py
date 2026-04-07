# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Production-coordination entrypoint for Gate 7E motion generation."""

from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TARGET_PATH = PROJECT_ROOT / "skills" / "kling-video" / "scripts" / "run_motion_generation.py"


def _load_target_module():
    spec = importlib.util.spec_from_file_location("kling_run_motion_generation", TARGET_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load Gate 7E target runner from {TARGET_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TARGET_MODULE = _load_target_module()


def main(argv: list[str] | None = None) -> int:
    return TARGET_MODULE.main(argv)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
