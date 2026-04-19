#!/usr/bin/env python3
"""Validate the Story 30-1 Marcus golden-trace fixture bundle."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.capture_marcus_golden_trace import CAPTURE_POINTS
from scripts.utilities.file_helpers import project_root

MANIFEST_NAME = "golden-trace-manifest.yaml"


def _read_manifest(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Manifest must deserialize to a mapping: {path}")
    return payload


def _validate_manifest(manifest: dict[str, Any]) -> list[str]:
    issues: list[str] = []

    captured_at = manifest.get("captured_at")
    if not isinstance(captured_at, str | date | datetime):
        issues.append("manifest missing supported scalar field: captured_at")

    for key in ("source_path", "source_sha256", "repo_commit_sha"):
        value = manifest.get(key)
        if not isinstance(value, str) or not value.strip():
            issues.append(f"manifest missing non-empty string field: {key}")

    module_versions = manifest.get("module_versions")
    if not isinstance(module_versions, dict) or not module_versions:
        issues.append("manifest.module_versions must be a non-empty mapping")

    capture_points = manifest.get("capture_points")
    if not isinstance(capture_points, list):
        issues.append("manifest.capture_points must be a list")
        return issues

    if len(capture_points) != len(CAPTURE_POINTS):
        issues.append(
            "manifest.capture_points length "
            f"{len(capture_points)} != expected {len(CAPTURE_POINTS)}"
        )
        return issues

    for index, (actual, expected) in enumerate(zip(capture_points, CAPTURE_POINTS, strict=True)):
        if not isinstance(actual, dict):
            issues.append(f"manifest.capture_points[{index}] is not a mapping")
            continue
        for key in ("step", "name", "filename", "description"):
            if actual.get(key) != expected[key]:
                issues.append(
                    f"manifest.capture_points[{index}].{key}={actual.get(key)!r} "
                    f"!= expected {expected[key]!r}"
                )

    return issues


def _validate_envelope_file(path: Path, repo_root: Path) -> list[str]:
    issues: list[str] = []
    text = path.read_text(encoding="utf-8")

    if not text.endswith("\n"):
        issues.append(f"{path.name} must end with a trailing newline")

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        issues.append(f"{path.name} is not valid JSON: {exc}")
        return issues

    if not isinstance(payload, dict):
        issues.append(f"{path.name} must contain a top-level JSON object")
        return issues

    if "_internal_emitter" not in payload:
        issues.append(f"{path.name} missing required '_internal_emitter' audit field")

    repo_root_variants = {
        str(repo_root),
        repo_root.as_posix(),
        str(repo_root).replace("/", "\\"),
    }
    if any(variant and variant in text for variant in repo_root_variants):
        issues.append(f"{path.name} still contains an absolute repo-root path")

    return issues


def validate_fixture_dir(fixture_dir: Path, repo_root: Path) -> list[str]:
    issues: list[str] = []

    manifest_path = fixture_dir / MANIFEST_NAME
    if not manifest_path.is_file():
        issues.append(f"missing manifest: {MANIFEST_NAME}")
    else:
        try:
            manifest = _read_manifest(manifest_path)
        except Exception as exc:  # pragma: no cover - covered by return path tests
            issues.append(f"failed to read manifest: {exc}")
        else:
            issues.extend(_validate_manifest(manifest))

    expected_files = [point["filename"] for point in CAPTURE_POINTS]
    for filename in expected_files:
        envelope_path = fixture_dir / filename
        if not envelope_path.is_file():
            issues.append(f"missing capture point file: {filename}")
            continue
        issues.extend(_validate_envelope_file(envelope_path, repo_root))

    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate the Marcus golden-trace fixture bundle for Story 30-1. "
            "Checks manifest shape, required capture-point files, JSON parseability, "
            "required audit field presence, and repo-root normalization."
        )
    )
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        required=True,
        help=(
            "Fixture directory to validate. Canonical path: "
            "tests/fixtures/golden_trace/marcus_pre_30-1/"
        ),
    )
    args = parser.parse_args(argv)

    repo_root = project_root()
    fixture_dir = args.fixture_dir.resolve()
    if not fixture_dir.is_dir():
        print(f"ERROR: fixture directory not found: {fixture_dir}", file=sys.stderr)
        return 2

    issues = validate_fixture_dir(fixture_dir, repo_root)
    if issues:
        print("Fixture validation FAILED:", file=sys.stderr)
        for issue in issues:
            print(f"  - {issue}", file=sys.stderr)
        return 1

    print(
        f"Fixture validation PASS: {fixture_dir} contains "
        f"{len(CAPTURE_POINTS)} capture-point files plus {MANIFEST_NAME}"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
