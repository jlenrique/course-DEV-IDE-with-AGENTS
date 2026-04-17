"""Tests for APP session readiness service (Story G.3).

Marked ``trial_critical`` — on the pre-Prompt-1 trial path. Must pass before
firing any trial production run. See ``docs/dev-guide/testing.md``.
"""

from __future__ import annotations

import importlib
import json
import sqlite3
from pathlib import Path

import pytest
import yaml

from scripts.state_management.db_init import init_database
from scripts.utilities import app_session_readiness as readiness

pytestmark = pytest.mark.trial_critical


def _write_support_modules(root: Path) -> None:
    scripts_dir = root / "skills" / "production-coordination" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    (scripts_dir / "observability_hooks.py").write_text("VALUE = 1\n", encoding="utf-8")
    (scripts_dir / "run_reporting.py").write_text("VALUE = 2\n", encoding="utf-8")


def _write_mode_state(root: Path, payload: dict[str, object]) -> None:
    mode_file = root / "state" / "runtime" / "mode_state.json"
    mode_file.parent.mkdir(parents=True, exist_ok=True)
    mode_file.write_text(json.dumps(payload), encoding="utf-8")


def _setup_minimal_runtime(root: Path, *, create_db: bool) -> None:
    (root / "state" / "config").mkdir(parents=True, exist_ok=True)
    (root / "state" / "runtime").mkdir(parents=True, exist_ok=True)
    _write_mode_state(root, {"mode": "default"})
    _write_support_modules(root)
    if create_db:
        init_database(root / "state" / "runtime" / "coordination.db")


def _check_by_name(report: dict[str, object], name: str) -> dict[str, object]:
    checks = report["checks"]
    assert isinstance(checks, list)
    for check in checks:
        if check["name"] == name:
            return check
    raise AssertionError(f"Missing check result for {name}")


def test_run_readiness_happy_path(tmp_path: Path) -> None:
    _setup_minimal_runtime(tmp_path, create_db=True)

    report = readiness.run_readiness(root=tmp_path)

    assert report["overall_status"] == "pass"
    assert _check_by_name(report, "coordination_db")["status"] == "pass"
    assert _check_by_name(report, "state:state/config")["status"] == "pass"
    assert _check_by_name(report, "imports")["status"] == "pass"
    assert _check_by_name(report, "bundle_run_constants")["status"] == "skip"


def test_run_readiness_validates_run_constants_when_bundle_dir_set(tmp_path: Path) -> None:
    _setup_minimal_runtime(tmp_path, create_db=True)
    bundle = tmp_path / "track" / "b1"
    bundle.mkdir(parents=True)
    (tmp_path / "primary.pdf").write_text("x", encoding="utf-8")
    rc_data = {
        "run_id": "RC-1",
        "lesson_slug": "b1-lesson",
        "bundle_path": "track/b1",
        "primary_source_file": str((tmp_path / "primary.pdf").resolve()),
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "production",
    }
    (bundle / "run-constants.yaml").write_text(yaml.safe_dump(rc_data), encoding="utf-8")

    report = readiness.run_readiness(root=tmp_path, bundle_dir=bundle)

    assert _check_by_name(report, "bundle_run_constants")["status"] == "pass"
    assert report["overall_status"] == "pass"


def test_run_readiness_initializes_missing_db(tmp_path: Path) -> None:
    _setup_minimal_runtime(tmp_path, create_db=False)

    report = readiness.run_readiness(root=tmp_path)

    assert report["overall_status"] == "pass"
    db_check = _check_by_name(report, "coordination_db")
    assert db_check["status"] == "pass"
    assert "initialized" in db_check["detail"]
    assert (tmp_path / "state" / "runtime" / "coordination.db").exists()


def test_run_readiness_repairs_partial_db_schema(tmp_path: Path) -> None:
    _setup_minimal_runtime(tmp_path, create_db=False)
    db_path = tmp_path / "state" / "runtime" / "coordination.db"

    conn = sqlite3.connect(str(db_path))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS legacy_table (id INTEGER PRIMARY KEY, note TEXT)"
    )
    conn.commit()
    conn.close()

    report = readiness.run_readiness(root=tmp_path)

    assert report["overall_status"] == "pass"
    db_check = _check_by_name(report, "coordination_db")
    assert db_check["status"] == "pass"
    assert "repaired" in db_check["detail"]


def test_run_readiness_fails_when_state_subtree_missing(tmp_path: Path) -> None:
    (tmp_path / "state" / "runtime").mkdir(parents=True, exist_ok=True)
    _write_mode_state(tmp_path, {"mode": "default"})
    _write_support_modules(tmp_path)
    init_database(tmp_path / "state" / "runtime" / "coordination.db")

    report = readiness.run_readiness(root=tmp_path)

    assert report["overall_status"] == "fail"
    assert _check_by_name(report, "state:state/config")["status"] == "fail"


def test_run_readiness_fails_when_state_dir_not_writable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _setup_minimal_runtime(tmp_path, create_db=True)

    monkeypatch.setattr(
        readiness,
        "_is_dir_writable",
        lambda path: path.name != "config",
    )

    report = readiness.run_readiness(root=tmp_path)

    assert report["overall_status"] == "fail"
    assert _check_by_name(report, "state:state/config")["status"] == "fail"


def test_run_readiness_fails_on_invalid_mode_state_json(tmp_path: Path) -> None:
    _setup_minimal_runtime(tmp_path, create_db=True)
    (tmp_path / "state" / "runtime" / "mode_state.json").write_text("{bad json", encoding="utf-8")

    report = readiness.run_readiness(root=tmp_path)

    assert report["overall_status"] == "fail"
    assert _check_by_name(report, "mode_state")["status"] == "fail"


def test_run_readiness_warns_on_unusual_mode_value(tmp_path: Path) -> None:
    _setup_minimal_runtime(tmp_path, create_db=True)
    _write_mode_state(tmp_path, {"mode": "experimental"})

    report = readiness.run_readiness(root=tmp_path)

    assert report["overall_status"] == "warn"
    assert _check_by_name(report, "mode_state")["status"] == "warn"


def test_run_readiness_fails_on_import_sanity(tmp_path: Path) -> None:
    _setup_minimal_runtime(tmp_path, create_db=True)
    (tmp_path / "skills" / "production-coordination" / "scripts" / "run_reporting.py").write_text(
        "raise RuntimeError('boom')\n",
        encoding="utf-8",
    )

    report = readiness.run_readiness(root=tmp_path)

    assert report["overall_status"] == "fail"
    assert _check_by_name(report, "imports")["status"] == "fail"


def test_run_readiness_includes_preflight_phase_when_requested(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _setup_minimal_runtime(tmp_path, create_db=True)

    monkeypatch.setattr(
        readiness,
        "_run_preflight_phase",
        lambda _root, motion_enabled=False: readiness.CheckResult(
            name="preflight_tools",
            status="warn",
            detail="mock preflight warning",
            resolution="resolve mock issue",
        ),
    )

    report = readiness.run_readiness(root=tmp_path, with_preflight=True)

    assert report["overall_status"] == "warn"
    assert _check_by_name(report, "preflight_tools")["status"] == "warn"


def test_preflight_phase_returns_fail_when_module_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _setup_minimal_runtime(tmp_path, create_db=True)

    original_import = importlib.import_module

    def fake_import(name: str):
        if name == "skills.pre_flight_check.scripts.preflight_runner":
            raise ModuleNotFoundError("missing preflight")
        return original_import(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    report = readiness.run_readiness(root=tmp_path, with_preflight=True)

    assert report["overall_status"] == "fail"
    assert _check_by_name(report, "preflight_tools")["status"] == "fail"


def test_main_returns_exit_2_for_warn_in_strict_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        readiness,
        "run_readiness",
        lambda root=None, with_preflight=False, motion_enabled=False, bundle_dir=None: {
            "timestamp": "2026-03-29T00:00:00+00:00",
            "root": "x",
            "overall_status": "warn",
            "checks": [],
        },
    )

    rc = readiness.main(["--strict", "--json-only"])
    assert rc == 2


def test_run_readiness_passes_motion_enabled_to_preflight(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _setup_minimal_runtime(tmp_path, create_db=True)

    seen: dict[str, bool] = {}

    def fake_preflight(_root: Path, *, motion_enabled: bool = False) -> readiness.CheckResult:
        seen["motion_enabled"] = motion_enabled
        return readiness.CheckResult(
            name="preflight_tools",
            status="pass",
            detail="mock preflight ok",
            resolution="",
        )

    monkeypatch.setattr(readiness, "_run_preflight_phase", fake_preflight)

    report = readiness.run_readiness(
        root=tmp_path,
        with_preflight=True,
        motion_enabled=True,
    )

    assert report["overall_status"] == "pass"
    assert seen["motion_enabled"] is True
