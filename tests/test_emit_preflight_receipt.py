from __future__ import annotations

import json
import os
import time
from pathlib import Path

import yaml

from scripts.utilities import emit_preflight_receipt as receipt_module
from scripts.utilities import app_session_readiness as readiness_module
from scripts.utilities.emit_preflight_receipt import emit_preflight_receipt
from scripts.utilities.file_helpers import project_root
from scripts.utilities.workflow_policy import DEFAULT_WORKFLOW_POLICY, load_workflow_policy


def test_load_workflow_policy_returns_defaults_when_file_missing(tmp_path: Path) -> None:
    assert load_workflow_policy(tmp_path) == DEFAULT_WORKFLOW_POLICY


def test_load_workflow_policy_uses_yaml_overrides(tmp_path: Path) -> None:
    config_path = tmp_path / "state" / "config" / "workflow-policy.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        yaml.safe_dump(
            {
                "poll_min_open_minutes": 5,
                "poll_auto_close_minutes": 20,
                "session_receipt_max_age_minutes": 90,
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    assert load_workflow_policy(tmp_path) == {
        "poll_min_open_minutes": 5,
        "poll_auto_close_minutes": 20,
        "session_receipt_max_age_minutes": 90,
    }


def test_emit_preflight_receipt_uses_fresh_session_receipt(
    tmp_path: Path,
    monkeypatch,
) -> None:
    session_receipt = tmp_path / "session.json"
    cached_report = {
        "overall_status": "pass",
        "checks": [],
        "root": str(tmp_path.resolve()),
        "timestamp": "now",
    }
    session_receipt.write_text(json.dumps(cached_report), encoding="utf-8")
    now = time.time()
    os.utime(session_receipt, (now, now))

    def _fail_run_readiness(**_: object) -> dict[str, object]:
        raise AssertionError("run_readiness should not be called when session receipt is fresh")

    monkeypatch.setattr(receipt_module, "run_readiness", _fail_run_readiness)

    report = emit_preflight_receipt(root=tmp_path, session_receipt=session_receipt)

    assert report == cached_report


def test_emit_preflight_receipt_falls_back_when_session_receipt_is_stale(
    tmp_path: Path,
    monkeypatch,
) -> None:
    config_path = tmp_path / "state" / "config" / "workflow-policy.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("session_receipt_max_age_minutes: 1\n", encoding="utf-8")

    session_receipt = tmp_path / "session.json"
    session_receipt.write_text(json.dumps({"overall_status": "stale"}), encoding="utf-8")
    stale = time.time() - 61 * 60
    os.utime(session_receipt, (stale, stale))

    live_report = {"overall_status": "pass", "checks": [], "root": "live", "timestamp": "now"}
    monkeypatch.setattr(receipt_module, "run_readiness", lambda **_: live_report)

    report = emit_preflight_receipt(
        root=tmp_path,
        with_preflight=True,
        motion_enabled=True,
        session_receipt=session_receipt,
    )

    assert report == live_report


def test_emit_preflight_receipt_rejects_cached_receipt_with_wrong_root(
    tmp_path: Path,
    monkeypatch,
) -> None:
    session_receipt = tmp_path / "session.json"
    session_receipt.write_text(
        json.dumps(
            {
                "overall_status": "pass",
                "checks": [],
                "root": "C:/wrong-root",
                "timestamp": "now",
            }
        ),
        encoding="utf-8",
    )
    now = time.time()
    os.utime(session_receipt, (now, now))

    live_report = {
        "overall_status": "pass",
        "checks": [],
        "root": str(tmp_path),
        "timestamp": "now",
    }
    monkeypatch.setattr(receipt_module, "run_readiness", lambda **_: live_report)

    report = emit_preflight_receipt(root=tmp_path, session_receipt=session_receipt)

    assert report == live_report


def test_load_workflow_policy_falls_back_when_yaml_is_invalid(tmp_path: Path) -> None:
    config_path = tmp_path / "state" / "config" / "workflow-policy.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("poll_min_open_minutes: [\n", encoding="utf-8")

    assert load_workflow_policy(tmp_path) == DEFAULT_WORKFLOW_POLICY


def test_main_writes_output_from_cached_session_receipt(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    session_receipt = tmp_path / "session.json"
    output = tmp_path / "bundle" / "preflight-results.json"
    cached_report = {
        "overall_status": "pass",
        "checks": [],
        "root": str(project_root().resolve()),
        "timestamp": "now",
    }
    session_receipt.write_text(json.dumps(cached_report), encoding="utf-8")
    now = time.time()
    os.utime(session_receipt, (now, now))

    def _fail_run_readiness(**_: object) -> dict[str, object]:
        raise AssertionError("run_readiness should not be called when cache is reused")

    monkeypatch.setattr(receipt_module, "run_readiness", _fail_run_readiness)

    rc = receipt_module.main(
        [
            "--output",
            str(output),
            "--session-receipt",
            str(session_receipt),
        ]
    )

    assert rc == 0
    assert json.loads(output.read_text(encoding="utf-8")) == cached_report
    assert "Using cached session receipt" in capsys.readouterr().out


def test_main_rejects_cached_session_receipt_with_wrong_root(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    session_receipt = tmp_path / "session.json"
    output = tmp_path / "bundle" / "preflight-results.json"
    session_receipt.write_text(
        json.dumps(
            {
                "overall_status": "pass",
                "checks": [],
                "root": "C:/wrong-root",
                "timestamp": "now",
            }
        ),
        encoding="utf-8",
    )
    now = time.time()
    os.utime(session_receipt, (now, now))

    live_report = {
        "overall_status": "pass",
        "checks": [],
        "root": str(project_root().resolve()),
        "timestamp": "now",
    }
    monkeypatch.setattr(receipt_module, "run_readiness", lambda **_: live_report)

    rc = receipt_module.main(
        [
            "--output",
            str(output),
            "--session-receipt",
            str(session_receipt),
        ]
    )

    assert rc == 0
    assert json.loads(output.read_text(encoding="utf-8")) == live_report
    captured = capsys.readouterr().out
    assert "cache missing, unreadable, or stale" in captured.lower()


def test_main_returns_exit_30_for_missing_bolster_credentials(
    tmp_path: Path,
    monkeypatch,
) -> None:
    output = tmp_path / "bundle" / "preflight-results.json"
    report = {
        "overall_status": "fail",
        "checks": [
            {
                "name": "bundle_run_constants",
                "status": "fail",
                "detail": readiness_module.EVIDENCE_BOLSTER_MISSING_KEY_REASON,
                "resolution": "set key",
            }
        ],
        "root": str(project_root().resolve()),
        "timestamp": "now",
    }
    monkeypatch.setattr(receipt_module, "run_readiness", lambda **_: report)

    rc = receipt_module.main(["--output", str(output)])

    assert rc == 30
    assert json.loads(output.read_text(encoding="utf-8"))["overall_status"] == "fail"
