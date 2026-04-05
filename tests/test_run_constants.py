"""Tests for frozen bundle run-constants.yaml loading (production wiring)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.utilities import run_constants as rc


def _write_valid_constants(bundle: Path, root: Path, *, bundle_rel: str | None = None) -> None:
    rel = bundle_rel or str(bundle.relative_to(root)).replace("\\", "/")
    data = {
        "schema_version": 1,
        "frozen_at_utc": "2026-04-03T00:00:00Z",
        "run_id": "T-UNIT-001",
        "lesson_slug": "lesson-unit",
        "bundle_path": rel,
        "primary_source_file": str(root / "primary.pdf"),
        "optional_context_assets": [],
        "theme_selection": "theme-a",
        "theme_paramset_key": "preset-a",
        "execution_mode": "tracked/default",
        "quality_preset": "production",
        "double_dispatch": False,
    }
    (bundle / "run-constants.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )


def test_load_run_constants_happy_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    bundle = root / "bundles" / "lesson-unit-001"
    bundle.mkdir(parents=True)
    (root / "primary.pdf").write_text("x", encoding="utf-8")
    _write_valid_constants(bundle, root)

    loaded = rc.load_run_constants(bundle, root=root)
    assert loaded.run_id == "T-UNIT-001"
    assert loaded.execution_mode == "tracked/default"
    assert loaded.optional_context_assets == ()
    assert loaded.double_dispatch is False


def test_bundle_path_must_match_directory(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    bundle = root / "bundles" / "lesson-unit-001"
    bundle.mkdir(parents=True)
    (root / "primary.pdf").write_text("x", encoding="utf-8")
    _write_valid_constants(bundle, root, bundle_rel="bundles/wrong-folder")

    with pytest.raises(rc.RunConstantsError, match="bundle_path"):
        rc.load_run_constants(bundle, root=root)


def test_verify_paths_requires_primary_file(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    bundle = root / "b" / "c"
    bundle.mkdir(parents=True)
    data = {
        "run_id": "X",
        "lesson_slug": "ls",
        "bundle_path": "b/c",
        "primary_source_file": str(root / "missing.pdf"),
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
    }
    (bundle / "run-constants.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(rc.RunConstantsError, match="primary_source_file"):
        rc.load_run_constants(bundle, root=root, verify_paths_exist=True)


def test_execution_mode_aliases(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    bundle = root / "b"
    bundle.mkdir(parents=True)
    (root / "p.pdf").write_text("1", encoding="utf-8")
    data = {
        "run_id": "X",
        "lesson_slug": "ls",
        "bundle_path": "b",
        "primary_source_file": str(root / "p.pdf"),
        "optional_context_assets": "none",
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked",
        "quality_preset": "draft",
    }
    (bundle / "run-constants.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    loaded = rc.load_run_constants(bundle, root=root)
    assert loaded.execution_mode == "tracked/default"


def test_parse_invalid_quality_preset() -> None:
    raw = {
        "run_id": "a",
        "lesson_slug": "b",
        "bundle_path": "c",
        "primary_source_file": "d",
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "nope",
        "double_dispatch": False,
    }
    with pytest.raises(rc.RunConstantsError, match="quality_preset"):
        rc.parse_run_constants(raw)


def test_parse_invalid_double_dispatch_type() -> None:
    raw = {
        "run_id": "a",
        "lesson_slug": "b",
        "bundle_path": "c",
        "primary_source_file": "d",
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
        "double_dispatch": "yes",
    }
    with pytest.raises(rc.RunConstantsError, match="double_dispatch"):
        rc.parse_run_constants(raw)


def test_main_json_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "r"
    bundle = root / "z"
    bundle.mkdir(parents=True)
    (root / "f.pdf").write_text("1", encoding="utf-8")
    _write_valid_constants(bundle, root, bundle_rel="z")

    code = rc.main(["--bundle-dir", str(bundle), "--root", str(root), "--json"])
    assert code == 0
    out = capsys.readouterr().out
    assert "T-UNIT-001" in out
    assert '"status": "pass"' in out
