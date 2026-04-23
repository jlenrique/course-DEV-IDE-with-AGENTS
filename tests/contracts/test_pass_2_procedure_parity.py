from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PASS_2_PROCEDURE = (
    _REPO_ROOT
    / "skills"
    / "bmad-agent-content-creator"
    / "references"
    / "pass-2-procedure.md"
)
_INTAKE_SCHEMA = (
    _REPO_ROOT / "state" / "config" / "schemas" / "irene-retrieval-intake.schema.json"
)


def test_pass_2_procedure_contains_retrieval_intake_section() -> None:
    text = _PASS_2_PROCEDURE.read_text(encoding="utf-8")
    assert "## Retrieval intake (corroborate-only v1)" in text
    assert "retrieval-intake-contract.md" in text
    assert "evidence_bolster_active" in text
    assert "retrieval_provenance" in text
    assert "retrieval_empty_for_cluster_" in text


def test_pass_2_procedure_contains_convergence_language_map() -> None:
    text = _PASS_2_PROCEDURE.read_text(encoding="utf-8")
    assert "Corroborated by multiple independent sources" in text
    assert "According to scite.ai citation-context analysis" in text
    assert "Per Consensus research synthesis" in text


def test_pass_2_procedure_mentions_schema_required_keys() -> None:
    text = _PASS_2_PROCEDURE.read_text(encoding="utf-8")
    schema = json.loads(_INTAKE_SCHEMA.read_text(encoding="utf-8"))
    for key in schema["required"]:
        assert key in text, f"Pass-2 procedure missing intake key: {key}"
