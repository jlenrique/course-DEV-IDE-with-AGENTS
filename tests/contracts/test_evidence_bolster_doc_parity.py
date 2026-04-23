"""Lockstep checks for evidence_bolster docs and runtime schema wiring."""

from __future__ import annotations

from pathlib import Path

from scripts.utilities import run_constants as rc

ROOT = Path(__file__).resolve().parents[2]


def _minimal_run_constants(*, evidence_bolster: bool) -> dict[str, object]:
    return {
        "run_id": "DOC-PARITY-1",
        "lesson_slug": "doc-parity",
        "bundle_path": "course-content/staging/tracked/source-bundles/doc-parity",
        "primary_source_file": "C:/example/source.pdf",
        "optional_context_assets": [],
        "theme_selection": "theme-a",
        "theme_paramset_key": "theme-a",
        "execution_mode": "tracked/default",
        "quality_preset": "production",
        "evidence_bolster": evidence_bolster,
    }


def test_research_knobs_guide_uses_canonical_field_name() -> None:
    guide = (ROOT / "docs" / "research-knobs-guide.md").read_text(encoding="utf-8")

    assert "evidence_bolster" in guide
    assert "evidence_bolster_active" in guide
    assert "cross_validate" in guide
    assert "CONSENSUS_API_KEY" in guide


def test_operations_context_points_to_research_knobs_guide() -> None:
    operations = (ROOT / "docs" / "operations-context.md").read_text(encoding="utf-8")

    assert "docs/research-knobs-guide.md" in operations
    assert "EVIDENCE_BOLSTER" in operations
    assert "evidence_bolster_active" in operations
    assert "cross_validate" in operations


def test_doc_knob_name_round_trips_with_run_constants_parser() -> None:
    parsed = rc.parse_run_constants(_minimal_run_constants(evidence_bolster=True))

    assert parsed.evidence_bolster is True
