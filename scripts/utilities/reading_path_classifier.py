"""Reading-path pattern classifier (Story perception-reading-path-repertoire).

Winston architecture ruling: one shared module under `scripts/utilities/`
rather than two agent-owned wrappers. The classifier is a deterministic
heuristic in v1 — no LLM dependency in the perception critical path.
Classifier-quality refinement (vision model, better evidence extraction)
ships as a follow-on once the 7-pattern enum stabilizes in trials.

Core contract (AC-2 + AC-3):
    classify(evidence_dict) -> ReadingPathClassification

Returns a structured `{pattern, confidence, evidence, fallback}` block that
satisfies the segment-manifest.schema.json `reading_path` sub-object.

Sally UX rider — confidence-gated HIL (from sprint-status riders):
    - confidence >= 0.85 → auto (pattern accepted silently)
    - 0.70 <= confidence < 0.85 → surface in Marcus landing-point summary
    - confidence < 0.70 → pause with top-2 candidates + evidence

The classifier itself does not surface to operators; it returns a posture
via `hil_posture` field so Marcus's landing-point can honor it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

# Closed enum — mirrors state/config/reading-path-patterns.yaml. The 3-way
# parity test asserts this stays aligned with the YAML registry and the
# JSON Schema enum in segment-manifest.schema.json.
READING_PATH_PATTERNS: tuple[str, ...] = (
    "z_pattern",
    "f_pattern",
    "center_out",
    "top_down",
    "multi_column",
    "grid_quadrant",
    "sequence_numbered",
)

# Sally confidence-gate thresholds.
CONFIDENCE_AUTO_FLOOR = 0.85
CONFIDENCE_SURFACE_FLOOR = 0.70

# Classifier fallback-below-floor threshold. When no pattern scores at/above
# this, the classifier falls back to z_pattern with `fallback=True`.
FALLBACK_BELOW = 0.60


HilPosture = Literal["auto", "surface", "pause"]


@dataclass(frozen=True)
class ReadingPathClassification:
    """Classifier output — maps directly to the JSON Schema reading_path sub-object."""

    pattern: str
    confidence: float
    evidence: dict[str, Any] = field(default_factory=dict)
    fallback: bool = False
    hil_posture: HilPosture = "auto"
    # Top-2 candidates for the pause-case (Sally rider):
    # populated only when hil_posture == "pause".
    candidates: tuple[tuple[str, float], ...] = ()

    def to_manifest_block(self) -> dict[str, Any]:
        """Return the dict shape that lands in segment-manifest reading_path."""
        return {
            "pattern": self.pattern,
            "confidence": round(self.confidence, 3),
            "evidence": dict(self.evidence),
            "fallback": self.fallback,
        }


def _score_sequence_numbered(ev: dict[str, Any]) -> float:
    """High when explicit ordinal markers are present. Ordinals override spatial."""
    markers = ev.get("ordinal_markers") or []
    if isinstance(markers, list) and len(markers) >= 2:
        # Ordinals are the strongest override signal in the repertoire.
        return 0.95
    return 0.0


def _score_grid_quadrant(ev: dict[str, Any]) -> float:
    """High on 2×2 / 3×3 matrices with axis labels."""
    axis_labels = ev.get("axis_labels") or []
    quadrant_count = int(ev.get("quadrant_count") or 0)
    if quadrant_count in (4, 9) and isinstance(axis_labels, list) and len(axis_labels) >= 2:
        return 0.90
    if quadrant_count in (4, 9):
        return 0.70
    return 0.0


def _score_multi_column(ev: dict[str, Any]) -> float:
    column_count = int(ev.get("column_count") or 0)
    if 2 <= column_count <= 4:
        headers = ev.get("per_column_headers") or []
        if isinstance(headers, list) and len(headers) == column_count:
            return 0.88
        return 0.72
    return 0.0


def _score_center_out(ev: dict[str, Any]) -> float:
    if ev.get("hero_visual_centroid") is None:
        return 0.0
    annotation_count = int(ev.get("annotation_count") or 0)
    if annotation_count >= 2:
        return 0.82
    return 0.0


def _score_top_down(ev: dict[str, Any]) -> float:
    spine_items = ev.get("spine_items") or []
    if isinstance(spine_items, list) and len(spine_items) >= 3:
        alignment_ratio = float(ev.get("vertical_alignment_ratio") or 0.0)
        if alignment_ratio >= 0.8:
            return 0.82
        return 0.65
    return 0.0


def _score_f_pattern(ev: dict[str, Any]) -> float:
    left_words = int(ev.get("left_column_word_count") or 0)
    evidence_markers = ev.get("evidence_markers") or []
    if left_words >= 120 and isinstance(evidence_markers, list) and len(evidence_markers) >= 2:
        return 0.78
    return 0.0


def _score_z_pattern(ev: dict[str, Any]) -> float:
    """z_pattern is the default; scores mid when the quadrant signals are mixed."""
    zones = [
        bool(ev.get("has_headline")),
        bool(ev.get("has_visual_zone")),
        bool(ev.get("has_cta_zone")),
        bool(ev.get("has_body_text")),
    ]
    present = sum(zones)
    if present == 4:
        return 0.86
    if present == 3:
        return 0.72
    if present >= 1:
        return 0.5
    return 0.3  # Always a floor; z_pattern is the fallback pattern.


_SCORERS = {
    "sequence_numbered": _score_sequence_numbered,
    "grid_quadrant": _score_grid_quadrant,
    "multi_column": _score_multi_column,
    "center_out": _score_center_out,
    "top_down": _score_top_down,
    "f_pattern": _score_f_pattern,
    "z_pattern": _score_z_pattern,
}


def _hil_posture(confidence: float) -> HilPosture:
    if confidence >= CONFIDENCE_AUTO_FLOOR:
        return "auto"
    if confidence >= CONFIDENCE_SURFACE_FLOOR:
        return "surface"
    return "pause"


def classify(evidence: dict[str, Any]) -> ReadingPathClassification:
    """Classify a perception artifact's reading-path pattern.

    ``evidence`` is a dict of detector signals extracted by the perception
    step (layout analysis / vision / OCR). Keys correspond to per-pattern
    evidence fields in `state/config/reading-path-patterns.yaml`.

    Returns a :class:`ReadingPathClassification` — always returns a
    well-formed result, never raises on unknown-pattern input. Unknown keys
    in ``evidence`` are preserved in the output evidence dict.
    """
    scores: dict[str, float] = {
        pattern: scorer(evidence) for pattern, scorer in _SCORERS.items()
    }

    # Pick the top-scoring pattern; tiebreak preserves the enum order so
    # sequence_numbered > grid_quadrant > multi_column > center_out >
    # top_down > f_pattern > z_pattern when scores tie.
    ranked = sorted(
        scores.items(),
        key=lambda kv: (kv[1], -READING_PATH_PATTERNS.index(kv[0])),
        reverse=True,
    )
    top_pattern, top_score = ranked[0]

    if top_score < FALLBACK_BELOW:
        # Classifier cannot commit — fallback to z_pattern with the flag set.
        return ReadingPathClassification(
            pattern="z_pattern",
            confidence=round(top_score, 3),
            evidence=dict(evidence),
            fallback=True,
            hil_posture=_hil_posture(top_score),
            candidates=tuple((p, round(s, 3)) for p, s in ranked[:2]),
        )

    posture = _hil_posture(top_score)
    candidates: tuple[tuple[str, float], ...] = ()
    if posture == "pause":
        candidates = tuple((p, round(s, 3)) for p, s in ranked[:2])
    return ReadingPathClassification(
        pattern=top_pattern,
        confidence=round(top_score, 3),
        evidence=dict(evidence),
        fallback=False,
        hil_posture=posture,
        candidates=candidates,
    )


def normalize_legacy_directive(narration_directive: str | None) -> dict[str, Any] | None:
    """Normalize the Sprint-1 free-text directive to a structured reading_path.

    Called by the Pass-2 emission lint for byte-identical backward compatibility
    with 7-1 canonical fixtures. The `narration_directive: z-pattern-literal-scan`
    convention maps to `reading_path.pattern: z_pattern` with `fallback: false`.

    Returns None when the directive is unknown or absent — caller decides how to
    proceed (classifier run vs. carry-on-with-null).
    """
    if not narration_directive:
        return None
    normalized = narration_directive.strip().lower()
    if normalized in ("z-pattern-literal-scan", "z_pattern_literal_scan", "z-pattern"):
        return {
            "pattern": "z_pattern",
            "confidence": 1.0,
            "evidence": {"legacy_directive": narration_directive},
            "fallback": False,
        }
    return None
