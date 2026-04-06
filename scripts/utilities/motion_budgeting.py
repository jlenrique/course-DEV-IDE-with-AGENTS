"""Shared motion budgeting helpers for Epic 14 workflows."""

from __future__ import annotations

MODEL_CREDIT_ESTIMATES = {"std": 4.0, "pro": 8.0}


def normalize_motion_mode(mode: str) -> str:
    """Return a supported motion mode, defaulting invalid inputs to std."""
    normalized_mode = str(mode or "std").strip().lower() or "std"
    if normalized_mode not in MODEL_CREDIT_ESTIMATES:
        return "std"
    return normalized_mode


def estimate_motion_credits(duration_seconds: float, mode: str) -> float:
    """Estimate credits for a single motion clip."""
    normalized_mode = normalize_motion_mode(mode)
    base = MODEL_CREDIT_ESTIMATES[normalized_mode]
    return round(base * (max(float(duration_seconds), 5.0) / 5.0), 2)
