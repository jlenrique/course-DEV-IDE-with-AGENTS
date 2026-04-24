"""Tests for the reading-path classifier (Story perception-reading-path-repertoire).

K target 16-18 per Amelia green-light rider. This file covers the classifier
+ lint-side wiring. Schema parity + docs lockstep tests live in
tests/contracts/test_reading_path_parity.py.

Coverage:
  Classifier — core (7):
    1. z_pattern default when quadrant signals all present
    2. sequence_numbered wins when ordinal markers present (overrides spatial)
    3. grid_quadrant wins on 2x2 matrix with axis labels
    4. multi_column wins on parallel columns with headers
    5. center_out wins with hero + 2+ annotations
    6. top_down wins on spine with strong vertical alignment
    7. f_pattern wins on dense left column + evidence markers

  Classifier — fallback / HIL posture (3):
    8. Fallback to z_pattern when all scores < FALLBACK_BELOW
    9. HIL posture = pause below 0.70; top-2 candidates populated
   10. HIL posture = surface between 0.70 and 0.85

  Normalize legacy directive (2):
   11. z-pattern-literal-scan → z_pattern with confidence=1.0
   12. Unknown directive → None (classifier run required)

  Manifest-block contract (1):
   13. to_manifest_block() emits the dict shape the schema accepts

  Lint integration (3):
   14. reading_path.pattern=sequence_numbered without ordinals → reading-path-fail
   15. reading_path.pattern=grid_quadrant without compare/contrast → reading-path-warn
   16. Legacy narration_directive=z-pattern-literal-scan → z_pattern check runs
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent

# Load the classifier from its file path — it lives under scripts/utilities
# which does ship as a package, but loading explicitly keeps the test robust
# to import-ordering quirks.
_CLASSIFIER_PATH = _ROOT / "scripts" / "utilities" / "reading_path_classifier.py"
_spec = importlib.util.spec_from_file_location(
    "reading_path_classifier_tests", _CLASSIFIER_PATH
)
assert _spec is not None and _spec.loader is not None
classifier = importlib.util.module_from_spec(_spec)
sys.modules["reading_path_classifier_tests"] = classifier
_spec.loader.exec_module(classifier)

_LINT_PATH = _ROOT / "scripts" / "validators" / "pass_2_emission_lint.py"
_lint_spec = importlib.util.spec_from_file_location(
    "pass_2_emission_lint_tests", _LINT_PATH
)
assert _lint_spec is not None and _lint_spec.loader is not None
lint = importlib.util.module_from_spec(_lint_spec)
sys.modules["pass_2_emission_lint_tests"] = lint
_lint_spec.loader.exec_module(lint)


# ---------------------------------------------------------------------------
# Classifier core
# ---------------------------------------------------------------------------


def test_z_pattern_wins_on_full_quadrant_signals() -> None:
    result = classifier.classify(
        {
            "has_headline": True,
            "has_visual_zone": True,
            "has_cta_zone": True,
            "has_body_text": True,
        }
    )
    assert result.pattern == "z_pattern"
    assert result.confidence >= 0.85
    assert result.fallback is False


def test_sequence_numbered_wins_when_ordinals_present() -> None:
    result = classifier.classify(
        {
            "ordinal_markers": ["1", "2", "3"],
            # Even with full quadrant signals, ordinals override.
            "has_headline": True,
            "has_visual_zone": True,
            "has_cta_zone": True,
            "has_body_text": True,
        }
    )
    assert result.pattern == "sequence_numbered"
    assert result.confidence >= 0.90


def test_grid_quadrant_wins_on_2x2_with_axis_labels() -> None:
    result = classifier.classify(
        {
            "axis_labels": ["benefit", "effort"],
            "quadrant_count": 4,
        }
    )
    assert result.pattern == "grid_quadrant"
    assert result.confidence >= 0.85


def test_multi_column_wins_on_parallel_columns_with_headers() -> None:
    result = classifier.classify(
        {
            "column_count": 3,
            "per_column_headers": ["A", "B", "C"],
        }
    )
    assert result.pattern == "multi_column"


def test_center_out_wins_with_hero_and_annotations() -> None:
    result = classifier.classify(
        {
            "hero_visual_centroid": [0.5, 0.5],
            "annotation_count": 4,
        }
    )
    assert result.pattern == "center_out"


def test_top_down_wins_on_vertical_spine() -> None:
    result = classifier.classify(
        {
            "spine_items": ["intake", "triage", "work-up", "disposition"],
            "vertical_alignment_ratio": 0.92,
        }
    )
    assert result.pattern == "top_down"


def test_f_pattern_wins_on_dense_left_column_with_markers() -> None:
    result = classifier.classify(
        {
            "left_column_word_count": 250,
            "evidence_markers": ["callout-1", "callout-2", "callout-3"],
        }
    )
    assert result.pattern == "f_pattern"


# ---------------------------------------------------------------------------
# Fallback / HIL posture
# ---------------------------------------------------------------------------


def test_fallback_when_all_scores_below_floor() -> None:
    # Empty evidence — only z_pattern's floor of 0.3 applies, which is below
    # the FALLBACK_BELOW=0.60 threshold.
    result = classifier.classify({})
    assert result.pattern == "z_pattern"
    assert result.fallback is True
    assert result.confidence < classifier.FALLBACK_BELOW
    assert len(result.candidates) == 2


def test_hil_posture_pause_below_surface_floor() -> None:
    # Evidence just below 0.70 — above FALLBACK (0.60), below SURFACE (0.70).
    # z_pattern with 1 zone score 0.5.
    result = classifier.classify({"has_headline": True})
    assert result.pattern == "z_pattern"
    assert result.fallback is True  # 0.5 < 0.60
    assert result.hil_posture == "pause"
    assert len(result.candidates) == 2


def test_hil_posture_surface_in_mid_band() -> None:
    # top_down without high alignment: score 0.65 → surface (0.70 > 0.65 ? below SURFACE)
    # Let's use f_pattern evidence that scores exactly 0.78 → above SURFACE 0.70, below AUTO 0.85.
    result = classifier.classify(
        {
            "left_column_word_count": 200,
            "evidence_markers": ["a", "b"],
        }
    )
    assert result.pattern == "f_pattern"
    assert 0.70 <= result.confidence < 0.85
    assert result.hil_posture == "surface"


# ---------------------------------------------------------------------------
# Normalize legacy directive
# ---------------------------------------------------------------------------


def test_normalize_legacy_directive_z_pattern_scan() -> None:
    block = classifier.normalize_legacy_directive("z-pattern-literal-scan")
    assert block is not None
    assert block["pattern"] == "z_pattern"
    assert block["confidence"] == 1.0
    assert block["fallback"] is False


def test_normalize_unknown_directive_returns_none() -> None:
    assert classifier.normalize_legacy_directive("bespoke-scan") is None
    assert classifier.normalize_legacy_directive(None) is None


# ---------------------------------------------------------------------------
# Manifest-block contract
# ---------------------------------------------------------------------------


def test_to_manifest_block_emits_schema_shape() -> None:
    result = classifier.classify(
        {
            "ordinal_markers": ["1", "2"],
        }
    )
    block = result.to_manifest_block()
    assert set(block.keys()) == {"pattern", "confidence", "evidence", "fallback"}
    assert isinstance(block["confidence"], float)
    assert isinstance(block["evidence"], dict)
    assert isinstance(block["fallback"], bool)


# ---------------------------------------------------------------------------
# Lint integration
# ---------------------------------------------------------------------------


def test_lint_sequence_numbered_without_ordinals_fails_closed() -> None:
    manifest = {
        "schema_version": "1.1",
        "run_id": "test",
        "generated_at_utc": "2026-04-24T00:00:00Z",
        "generated_by": "test",
        "reading_path": {"pattern": "sequence_numbered"},
        "segments": [
            {
                "id": "seg-01",
                "slide_id": "seg-01",
                "card_number": 1,
                "visual_mode": "static",
                "motion_asset_path": None,
                "motion_duration_seconds": None,
                "visual_file": "slides/seg-01.png",
                "narration_text": (
                    "This segment describes the process broadly without any "
                    "explicit ordinal markers mentioned inline."
                ),
            }
        ],
    }
    findings = lint.lint_manifest(manifest, receipt_durations={})
    kinds = [f.kind for f in findings]
    assert "reading-path-fail" in kinds


def test_lint_grid_quadrant_without_compare_contrast_is_warning() -> None:
    manifest = {
        "schema_version": "1.1",
        "run_id": "test",
        "generated_at_utc": "2026-04-24T00:00:00Z",
        "generated_by": "test",
        "reading_path": {"pattern": "grid_quadrant"},
        "segments": [
            {
                "id": "seg-01",
                "slide_id": "seg-01",
                "card_number": 1,
                "visual_mode": "static",
                "motion_asset_path": None,
                "motion_duration_seconds": None,
                "visual_file": "slides/seg-01.png",
                "narration_text": (
                    "The matrix organizes the four quadrants with benefit on "
                    "the vertical axis and effort on the horizontal axis."
                ),
            }
        ],
    }
    findings = lint.lint_manifest(manifest, receipt_durations={})
    kinds = [f.kind for f in findings]
    assert "reading-path-warn" in kinds
    assert "reading-path-fail" not in kinds


def test_lint_legacy_narration_directive_skips_pattern_check() -> None:
    """Sprint-1 byte-identical contract: legacy `narration_directive` normalizes
    to z_pattern at the resolver layer, but the pattern-aware shape check is
    SKIPPED for legacy-sourced patterns so existing Sprint-1 fixtures remain
    lint-clean. Structured `reading_path` must be emitted explicitly to opt
    into the pattern-aware check."""
    manifest = {
        "schema_version": "1.1",
        "run_id": "test",
        "generated_at_utc": "2026-04-24T00:00:00Z",
        "generated_by": "test",
        "narration_directive": "z-pattern-literal-scan",
        "segments": [
            {
                "id": "seg-01",
                "slide_id": "seg-01",
                "card_number": 1,
                "visual_mode": "static",
                "motion_asset_path": None,
                "motion_duration_seconds": None,
                "visual_file": "slides/seg-01.png",
                "narration_text": (
                    "This narration does not trace a particular spatial path."
                ),
            }
        ],
    }
    findings = lint.lint_manifest(manifest, receipt_durations={})
    kinds = [f.kind for f in findings]
    # NO warnings/fails — legacy path is explicitly skipped.
    assert "reading-path-warn" not in kinds
    assert "reading-path-fail" not in kinds


def test_lint_z_pattern_with_sweep_tokens_passes_cleanly() -> None:
    manifest = {
        "schema_version": "1.1",
        "run_id": "test",
        "generated_at_utc": "2026-04-24T00:00:00Z",
        "generated_by": "test",
        "reading_path": {"pattern": "z_pattern"},
        "segments": [
            {
                "id": "seg-01",
                "slide_id": "seg-01",
                "card_number": 1,
                "visual_mode": "static",
                "motion_asset_path": None,
                "motion_duration_seconds": None,
                "visual_file": "slides/seg-01.png",
                "narration_text": (
                    "The headline names the problem; the body expands on the "
                    "driver; the visual anchors the frame; the call to action "
                    "closes the loop."
                ),
            }
        ],
    }
    findings = lint.lint_manifest(manifest, receipt_durations={})
    kinds = [f.kind for f in findings]
    assert "reading-path-warn" not in kinds
    assert "reading-path-fail" not in kinds
