# /// script
# requires-python = ">=3.10"
# ///
"""Build run-scoped YAML context entities under state/config/."""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.utilities.file_helpers import project_root
except ModuleNotFoundError:
    def _load_file_helpers() -> Any:
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "scripts" / "utilities" / "file_helpers.py"
            if candidate.exists():
                spec = importlib.util.spec_from_file_location("file_helpers_local", candidate)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
        raise

    project_root = _load_file_helpers().project_root


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def run_context_dir(run_id: str, base_dir: str | Path | None = None) -> Path:
    if base_dir:
        return Path(base_dir) / run_id
    return project_root() / "state" / "config" / "runs" / run_id


def build_run_context(
    *,
    run_id: str,
    course: str,
    module: str,
    lesson: str,
    content_type: str,
    preset: str,
    base_dir: str | Path | None = None,
) -> dict[str, Path]:
    """Create canonical run-scoped context YAML files and return their paths."""
    base = run_context_dir(run_id, base_dir=base_dir)
    base.mkdir(parents=True, exist_ok=True)

    course_yaml = {
        "run_id": run_id,
        "course_code": course,
        "created_at": _now(),
        "preset": preset,
        "context_scope": "course",
    }
    module_yaml = {
        "run_id": run_id,
        "course_code": course,
        "module_id": module,
        "lesson_id": lesson,
        "created_at": _now(),
        "context_scope": "module",
    }
    asset_yaml = {
        "run_id": run_id,
        "content_type": content_type,
        "created_at": _now(),
        "assets": [],
        "release_manifest": {
            "ready": False,
            "quality_certified": False,
        },
    }

    paths = {
        "course_context": base / "course_context.yaml",
        "module_context": base / "module_context.yaml",
        "asset_specs": base / "asset_specs.yaml",
    }

    paths["course_context"].write_text(yaml.safe_dump(course_yaml, sort_keys=False), encoding="utf-8")
    paths["module_context"].write_text(yaml.safe_dump(module_yaml, sort_keys=False), encoding="utf-8")
    paths["asset_specs"].write_text(yaml.safe_dump(asset_yaml, sort_keys=False), encoding="utf-8")

    return paths


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Create run-scoped context YAML files")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--course", default="")
    parser.add_argument("--module", default="")
    parser.add_argument("--lesson", default="")
    parser.add_argument("--content-type", default="unknown")
    parser.add_argument("--preset", default="draft")
    parser.add_argument("--base-dir", default=None)
    args = parser.parse_args(argv)

    paths = build_run_context(
        run_id=args.run_id,
        course=args.course,
        module=args.module,
        lesson=args.lesson,
        content_type=args.content_type,
        preset=args.preset,
        base_dir=args.base_dir,
    )

    print(json.dumps({k: str(v) for k, v in paths.items()}, indent=2))


if __name__ == "__main__":
    main()
