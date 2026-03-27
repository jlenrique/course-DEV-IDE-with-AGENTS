"""Tests for GammaEvaluator."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from gamma_evaluator import (
    GammaEvaluator,
    LAYOUT_PATTERNS,
    LEVEL_RUBRIC_WEIGHTS,
)


@pytest.fixture
def evaluator() -> GammaEvaluator:
    return GammaEvaluator()


@pytest.fixture
def l1_brief() -> str:
    return (
        "# Exemplar: Two Processes, One Mind\n\n"
        "## Level: L1 (Simple)\n\n"
        "Single slide. The simplest structural pattern — a parallel comparison layout.\n\n"
        "**Title**: Two Processes, One Mind\n\n"
        "**Left column — Clinical Diagnosis:**\n"
        "- History & Physical\n"
        "**Right column — Design Thinking:**\n"
        "- Empathize with users\n"
    )


@pytest.fixture
def l2_brief() -> str:
    return (
        "# Exemplar: Diagnosis = Innovation\n\n"
        "## Level: L2 (Simple-Moderate)\n\n"
        "Single slide. Text-focused explanatory slide with a bold conceptual headline.\n\n"
        "**Title**: Diagnosis = Innovation\n\n"
        "**Body**: Your clinical training has already prepared you.\n"
    )


class TestGammaEvaluatorProperties:
    def test_tool_name(self, evaluator: GammaEvaluator) -> None:
        assert evaluator.tool_name == "gamma"


class TestAnalyzeExemplar:
    def test_detects_parallel_layout(
        self, evaluator: GammaEvaluator, l1_brief: str
    ) -> None:
        result = evaluator.analyze_exemplar(l1_brief, [])
        assert result["layout_pattern"] == "two-column-parallel"

    def test_detects_title_plus_body(
        self, evaluator: GammaEvaluator, l2_brief: str
    ) -> None:
        result = evaluator.analyze_exemplar(l2_brief, [])
        assert result["layout_pattern"] == "title-plus-body"

    def test_extracts_title(
        self, evaluator: GammaEvaluator, l1_brief: str
    ) -> None:
        result = evaluator.analyze_exemplar(l1_brief, [])
        assert result["title"] == "Two Processes, One Mind"

    def test_detects_multiple_sections(
        self, evaluator: GammaEvaluator, l1_brief: str
    ) -> None:
        result = evaluator.analyze_exemplar(l1_brief, [])
        assert result["has_multiple_sections"] is True

    def test_detects_assessment_type(self, evaluator: GammaEvaluator) -> None:
        brief = "Assessment slide. Comprehension check with categorization."
        result = evaluator.analyze_exemplar(brief, [])
        assert result["pedagogical_type"] == "assessment"

    def test_defaults_to_content_delivery(self, evaluator: GammaEvaluator) -> None:
        brief = "A simple slide about a topic."
        result = evaluator.analyze_exemplar(brief, [])
        assert result["pedagogical_type"] == "content-delivery"


class TestDeriveReproductionSpec:
    def test_basic_spec_for_parallel_layout(
        self, evaluator: GammaEvaluator
    ) -> None:
        analysis = {"layout_pattern": "two-column-parallel", "word_count": 100}
        spec = evaluator.derive_reproduction_spec(analysis, {})
        assert spec["num_cards"] == 1
        assert spec["text_mode"] == "preserve"
        assert spec["export_as"] == "pdf"
        assert "parallel" in spec["additional_instructions"].lower()

    def test_applies_style_guide_theme(self, evaluator: GammaEvaluator) -> None:
        analysis = {"layout_pattern": "title-plus-body", "word_count": 30}
        spec = evaluator.derive_reproduction_spec(
            analysis, {"theme_id": "jcph-navy-123"}
        )
        assert spec["theme_id"] == "jcph-navy-123"

    def test_brief_text_options_for_short_content(
        self, evaluator: GammaEvaluator
    ) -> None:
        analysis = {"layout_pattern": "title-plus-body", "word_count": 20}
        spec = evaluator.derive_reproduction_spec(analysis, {})
        assert spec.get("text_options", {}).get("amount") == "brief"

    def test_no_images_for_faithful_reproduction(
        self, evaluator: GammaEvaluator
    ) -> None:
        analysis = {"layout_pattern": "title-plus-body", "word_count": 50}
        spec = evaluator.derive_reproduction_spec(analysis, {})
        assert spec["image_options"]["source"] == "noImages"


class TestCompareReproduction:
    def test_failed_reproduction_scores_zero(
        self, evaluator: GammaEvaluator
    ) -> None:
        result = evaluator.compare_reproduction(
            [], {"status": "error", "error": "API timeout"}, {}
        )
        for dim in result["scores"].values():
            assert dim["score"] == 0

    def test_successful_reproduction_scores(
        self, evaluator: GammaEvaluator, tmp_path: Path
    ) -> None:
        artifact = tmp_path / "test.pdf"
        artifact.write_bytes(b"PDF data")

        output = {
            "status": "completed",
            "output": {"gammaUrl": "https://gamma.app/docs/test"},
            "artifact_path": str(artifact),
            "api_interaction": {
                "parameters": {
                    "num_cards": 1,
                    "text_mode": "preserve",
                    "export_as": "pdf",
                    "additional_instructions": "Test layout",
                }
            },
        }
        analysis = {"layout_pattern": "two-column-parallel", "pedagogical_type": "content-delivery"}

        result = evaluator.compare_reproduction([], output, analysis)
        assert result["scores"]["structural_fidelity"]["score"] == 4
        assert result["scores"]["parameter_accuracy"]["score"] == 5
        assert "downloaded" in result["conclusion"]


class TestGetCustomRubricWeights:
    def test_l1_weights(self, evaluator: GammaEvaluator) -> None:
        weights = evaluator.get_custom_rubric_weights("L1")
        assert weights["structural_fidelity"] == "high"
        assert weights["creative_quality"] == "low"

    def test_l4_weights(self, evaluator: GammaEvaluator) -> None:
        weights = evaluator.get_custom_rubric_weights("L4")
        assert weights["content_completeness"] == "high"
        assert weights["creative_quality"] == "medium"

    def test_l4_dot_extension(self, evaluator: GammaEvaluator) -> None:
        weights = evaluator.get_custom_rubric_weights("L4.1")
        assert weights["content_completeness"] == "high"

    def test_unknown_level_uses_default(self, evaluator: GammaEvaluator) -> None:
        weights = evaluator.get_custom_rubric_weights("L99")
        assert weights["structural_fidelity"] == "high"
