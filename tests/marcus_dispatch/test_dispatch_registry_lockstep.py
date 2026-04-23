from __future__ import annotations

from pathlib import Path

import yaml

from scripts.validators.check_dispatch_registry_lockstep import run_check


def test_dispatch_registry_lockstep_passes_current_registry() -> None:
    exit_code, trace = run_check()

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

    exit_code, trace = run_check(registry_path)

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

    exit_code, trace = run_check(registry_path)

    assert exit_code == 1
    assert any(f.get("check") == 3 for f in trace["findings"])
