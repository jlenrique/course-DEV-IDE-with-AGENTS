"""Contract tests for Story 33-1 findings document structure."""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_FINDINGS_DOC = _ROOT / "_bmad-output" / "specs" / "33-1-generator-discovery-findings.md"
_REQUIRED_SECTIONS = (
    "## Summary",
    "## Generator Location",
    "## Generator Inputs",
    "## Generator Outputs",
    "## Regeneration Procedure",
    "## Drift Between Generator and On-Disk v4.2",
    "## Gap Analysis",
    "## Kill-switch Decision",
    "## Escalation",
    "## Evidence Index",
)
_ADDENDUM_REQUIRED_MARKERS = (
    "state/config/pipeline-manifest.yaml",
    "`04.5` (polling) and `04.55` (lock) split",
    "insert_between(before_id, after_id, new_step)",
)


def test_findings_doc_has_required_sections() -> None:
    """Story 33-1 findings doc includes all required level-2 headings."""
    assert _FINDINGS_DOC.exists(), (
        "Missing required findings doc for Story 33-1 at "
        f"{_FINDINGS_DOC.as_posix()}"
    )
    content = _FINDINGS_DOC.read_text(encoding="utf-8")
    missing_sections = [section for section in _REQUIRED_SECTIONS if section not in content]
    assert not missing_sections, (
        "Findings doc is missing required sections: "
        + ", ".join(missing_sections)
        + ". Please add all required '##' headings to stay in contract."
    )


def test_findings_doc_reflects_addendum_rulings() -> None:
    """Story 33-1 findings doc reflects the post-close addendum rulings."""
    content = _FINDINGS_DOC.read_text(encoding="utf-8")
    missing_markers = [marker for marker in _ADDENDUM_REQUIRED_MARKERS if marker not in content]
    assert not missing_markers, (
        "Findings doc is missing required addendum alignment markers: "
        + ", ".join(missing_markers)
        + ". Ensure 33-1 reflects A-1/A-2/A-3 decisions."
    )
