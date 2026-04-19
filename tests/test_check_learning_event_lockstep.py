"""Tests for learning-event lockstep check script."""

from __future__ import annotations

from pathlib import Path

from scripts.utilities.check_learning_event_lockstep import (
    DEFAULT_CAPTURE,
    DEFAULT_MANIFEST,
    DEFAULT_SCHEMA,
    DEFAULT_WIRING,
    run_check,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "learning_event_drift"


def _check_pass_map(payload: dict) -> dict[str, bool]:
    return {item["check"]: bool(item["pass"]) for item in payload["l1_checks_run"]}


def test_check_a_passes_on_clean_fixture() -> None:
    code, payload = run_check(DEFAULT_SCHEMA, DEFAULT_CAPTURE, DEFAULT_WIRING, DEFAULT_MANIFEST)
    assert code == 0
    assert _check_pass_map(payload)["A"] is True


def test_check_b_passes_on_clean_fixture() -> None:
    code, payload = run_check(DEFAULT_SCHEMA, DEFAULT_CAPTURE, DEFAULT_WIRING, DEFAULT_MANIFEST)
    assert code == 0
    assert _check_pass_map(payload)["B"] is True


def test_check_c_passes_on_clean_fixture() -> None:
    code, payload = run_check(DEFAULT_SCHEMA, DEFAULT_CAPTURE, DEFAULT_WIRING, DEFAULT_MANIFEST)
    assert code == 0
    assert _check_pass_map(payload)["C"] is True


def test_check_d_passes_on_clean_fixture() -> None:
    code, payload = run_check(DEFAULT_SCHEMA, DEFAULT_CAPTURE, DEFAULT_WIRING, DEFAULT_MANIFEST)
    assert code == 0
    assert _check_pass_map(payload)["D"] is True


def test_red_path_fixtures_fail_correctly() -> None:
    scenarios = [
        ("circuit_break_in_validator_only", "A"),
        ("marcus_calls_append_at_emits_false_gate", "B"),
    ]
    for fixture_name, expected_check in scenarios:
        fixture = FIXTURES / fixture_name
        code, payload = run_check(
            fixture / "learning-event-schema.yaml",
            fixture / "learning_event_capture.py",
            fixture / "learning_event_wiring.py",
            fixture / "manifest.yaml",
        )
        assert code == 1
        checks = {finding["check"] for finding in payload["findings"]}
        assert expected_check in checks


def test_missing_schema_exits_2(tmp_path: Path) -> None:
    code, payload = run_check(
        tmp_path / "missing-schema.yaml",
        DEFAULT_CAPTURE,
        DEFAULT_WIRING,
        DEFAULT_MANIFEST,
    )
    assert code == 2
    assert payload["closure_gate"] == "STRUCTURAL"
