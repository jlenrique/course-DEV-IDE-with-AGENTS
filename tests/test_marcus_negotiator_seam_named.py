"""Negotiator seam named contract (AC-T.9).

Pins the seam contract 30-3a will plug into:
* ``NEGOTIATOR_SEAM`` constant equals ``"marcus-negotiator"``.
* Seam documented in ``marcus/orchestrator/__init__.py`` docstring under
  a titled "Negotiator seam" section.
* Adjacent one-line comment names the string-sentinel vs structural-marker
  upgrade path (Q-4 rider).
"""

from __future__ import annotations

from pathlib import Path


def test_negotiator_seam_constant_value() -> None:
    """AC-T.9 — ``NEGOTIATOR_SEAM == "marcus-negotiator"``."""
    from marcus.orchestrator import NEGOTIATOR_SEAM

    assert NEGOTIATOR_SEAM == "marcus-negotiator"


def test_orchestrator_docstring_names_the_seam_section() -> None:
    """AC-T.9 — 'Negotiator seam' section present in orchestrator docstring."""
    import marcus.orchestrator as orchestrator

    docstring = orchestrator.__doc__ or ""
    assert "Negotiator seam" in docstring, (
        "marcus/orchestrator/__init__.py docstring must include a titled "
        "'Negotiator seam' section explaining the 30-3a upgrade contract."
    )


def test_negotiator_seam_has_upgrade_comment() -> None:
    """AC-T.9 (Q-4 rider) — adjacent comment names the sentinel-vs-marker hedge."""
    source_path = (
        Path(__file__).parent.parent / "marcus" / "orchestrator" / "__init__.py"
    )
    source = source_path.read_text(encoding="utf-8")
    assert "# NEGOTIATOR_SEAM: string sentinel" in source, (
        "marcus/orchestrator/__init__.py must carry an adjacent comment "
        "noting the string-sentinel-to-structural-marker upgrade path so "
        "30-3a's dev agent discovers it via grep."
    )
