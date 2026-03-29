from __future__ import annotations

from pathlib import Path

import pytest

from scripts.utilities.archive_agent_quality_scan import (
    REQUIRED_DIMENSIONS,
    archive_report,
    build_report,
    evaluate_dimensions,
    main,
)


def _valid_dimensions() -> dict[str, float]:
    return {
        "structure_compliance": 0.90,
        "prompt_craft_quality": 0.88,
        "cohesion": 0.87,
        "execution_efficiency": 0.86,
        "script_opportunity_analysis": 0.85,
    }


def test_evaluate_dimensions_pass() -> None:
    outcome = evaluate_dimensions(_valid_dimensions(), threshold=0.80)
    assert outcome.status == "pass"
    assert outcome.blocking is False
    assert outcome.failed_dimensions == []


def test_evaluate_dimensions_fail_on_threshold() -> None:
    dims = _valid_dimensions()
    dims["cohesion"] = 0.70
    outcome = evaluate_dimensions(dims, threshold=0.80)
    assert outcome.status == "fail"
    assert outcome.blocking is True
    assert "cohesion" in outcome.failed_dimensions


def test_evaluate_dimensions_requires_all_keys() -> None:
    dims = _valid_dimensions()
    dims.pop("prompt_craft_quality")
    with pytest.raises(ValueError):
        evaluate_dimensions(dims, threshold=0.80)


def test_evaluate_dimensions_rejects_out_of_range_score() -> None:
    dims = _valid_dimensions()
    dims["cohesion"] = 1.2
    with pytest.raises(ValueError):
        evaluate_dimensions(dims, threshold=0.80)


def test_evaluate_dimensions_rejects_out_of_range_threshold() -> None:
    with pytest.raises(ValueError):
        evaluate_dimensions(_valid_dimensions(), threshold=1.5)


def test_build_report_shape() -> None:
    report = build_report(
        agent_name="marcus",
        dimensions=_valid_dimensions(),
        threshold=0.80,
        scanner="bmad-agent-builder-quality-optimizer",
        notes="unit-test",
        timestamp="20260328T120000",
    )
    assert report["status"] == "pass"
    assert report["blocking"] is False
    assert report["timestamp"] == "20260328T120000"
    assert set(report["dimensions"].keys()) == set(REQUIRED_DIMENSIONS)


def test_archive_report_path(tmp_path: Path) -> None:
    report = build_report(
        agent_name="marcus",
        dimensions=_valid_dimensions(),
        threshold=0.80,
        scanner="bmad-agent-builder-quality-optimizer",
        notes="archive-test",
        timestamp="20260328T120001",
    )
    out_file = archive_report(tmp_path, report)
    expected_suffix = Path("skills/reports/bmad-agent-marcus/quality-scan/20260328T120001.json")
    assert str(out_file).endswith(str(expected_suffix))
    assert out_file.exists()


def test_build_report_rejects_invalid_agent_name() -> None:
    with pytest.raises(ValueError):
        build_report(
            agent_name="../evil",
            dimensions=_valid_dimensions(),
            threshold=0.80,
            scanner="bmad-agent-builder-quality-optimizer",
            notes="bad-agent",
            timestamp="20260328T120002",
        )


def test_build_report_rejects_invalid_timestamp() -> None:
    with pytest.raises(ValueError):
        build_report(
            agent_name="marcus",
            dimensions=_valid_dimensions(),
            threshold=0.80,
            scanner="bmad-agent-builder-quality-optimizer",
            notes="bad-ts",
            timestamp="2026-03-28",
        )


def test_main_returns_nonzero_on_failed_gate() -> None:
    exit_code = main(
        [
            "--agent-name",
            "marcus",
            "--threshold",
            "0.80",
            "--structure-compliance",
            "0.90",
            "--prompt-craft-quality",
            "0.90",
            "--cohesion",
            "0.70",
            "--execution-efficiency",
            "0.90",
            "--script-opportunity-analysis",
            "0.90",
        ]
    )
    assert exit_code == 1
