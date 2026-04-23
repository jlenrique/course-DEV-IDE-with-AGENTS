"""Irene-side retrieval intake contract utilities.

This package hosts deterministic helpers for consuming Tracy/Texas retrieval
artifacts at Irene Pass 2 time.
"""

from marcus.irene.intake import (
    CONVERGENCE_NARRATION_PATTERNS,
    ConvergenceSignal,
    IreneRetrievalDecision,
    IreneRetrievalIntake,
    RetrievalProvenance,
    apply_corroborate_intake,
    load_irene_retrieval_intake,
    parse_irene_retrieval_intake,
    resolve_convergence_narration,
)

__all__ = (
    "CONVERGENCE_NARRATION_PATTERNS",
    "ConvergenceSignal",
    "IreneRetrievalDecision",
    "IreneRetrievalIntake",
    "RetrievalProvenance",
    "apply_corroborate_intake",
    "load_irene_retrieval_intake",
    "parse_irene_retrieval_intake",
    "resolve_convergence_narration",
)
