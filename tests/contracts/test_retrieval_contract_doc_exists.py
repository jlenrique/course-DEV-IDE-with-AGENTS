"""Gate test — `retrieval-contract.md` must exist and cover the three audiences.

Paige + Amelia green-light ask: the contract doc is load-bearing for
adapter authors AND Tracy AND operators. If it goes missing or loses a
section, the test fails.
"""

from __future__ import annotations

from pathlib import Path

DOC = (
    Path(__file__).parents[2]
    / "skills"
    / "bmad-agent-texas"
    / "references"
    / "retrieval-contract.md"
)


def test_retrieval_contract_doc_exists() -> None:
    assert DOC.exists(), f"{DOC} must exist — see Story 27-0 AC (Paige doc surface)"


def test_retrieval_contract_has_three_audiences() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "## For Tracy" in text, "Missing Tracy (intent authors) section"
    assert "## For operators" in text, "Missing operators section"
    assert "## For dev-agents" in text, "Missing dev-agents section"


def test_retrieval_contract_cross_references_schema() -> None:
    text = DOC.read_text(encoding="utf-8")
    assert "extraction-report-schema.md" in text
    assert "SCHEMA_CHANGELOG.md" in text
