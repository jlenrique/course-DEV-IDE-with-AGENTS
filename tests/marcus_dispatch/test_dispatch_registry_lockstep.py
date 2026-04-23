from __future__ import annotations

from pathlib import Path

import yaml

from scripts.validators import check_dispatch_registry_lockstep as lockstep


def test_dispatch_registry_lockstep_passes_current_registry() -> None:
    exit_code, trace = lockstep.run_check()

    assert exit_code == 0
    assert trace["closure_gate"] == "PASS"


def test_dispatch_registry_lockstep_fails_when_kind_missing(tmp_path: Path) -> None:
    registry_path = tmp_path / "dispatch-registry.yaml"
    registry_payload = {
        "schema_version": "1.0",
        "dispatch_edges": [
            {
                "dispatch_kind": "irene_pass2",
                "specialist_id": "irene",
            },
            {
                "dispatch_kind": "kira_motion",
                "specialist_id": "kira",
            },
        ],
    }
    registry_path.write_text(
        yaml.safe_dump(registry_payload, sort_keys=False),
        encoding="utf-8",
    )

    exit_code, trace = lockstep.run_check(registry_path)

    assert exit_code == 1
    assert trace["closure_gate"] == "FAIL"
    findings = trace["findings"]
    assert any(f.get("check") == 2 for f in findings)


def test_dispatch_registry_lockstep_fails_on_specialist_mismatch(tmp_path: Path) -> None:
    registry_path = tmp_path / "dispatch-registry.yaml"
    registry_payload = {
        "schema_version": "1.0",
        "dispatch_edges": [
            {
                "dispatch_kind": "irene_pass2",
                "specialist_id": "irene",
            },
            {
                "dispatch_kind": "kira_motion",
                "specialist_id": "kira",
            },
            {
                "dispatch_kind": "texas_retrieval",
                "specialist_id": "irene",
            },
        ],
    }
    registry_path.write_text(
        yaml.safe_dump(registry_payload, sort_keys=False),
        encoding="utf-8",
    )

    exit_code, trace = lockstep.run_check(registry_path)

    assert exit_code == 1
    assert any(f.get("check") == 3 for f in trace["findings"])


def test_dispatch_registry_lockstep_trace_paths_are_unique(tmp_path: Path, monkeypatch) -> None:
    payload = {
        "lane": "L1",
        "scope": "dispatch-registry-lockstep",
        "timestamp": "2026-04-23T00:00:00+00:00",
        "closure_gate": "PASS",
        "l1_checks_run": [],
        "findings": [],
    }
    monkeypatch.setattr(lockstep, "REPORTS_ROOT", tmp_path)

    first_path = lockstep._write_trace(payload, 0)
    second_path = lockstep._write_trace(payload, 0)

    assert first_path != second_path
    assert first_path.exists()
    assert second_path.exists()
