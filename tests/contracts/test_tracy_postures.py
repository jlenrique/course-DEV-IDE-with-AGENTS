"""
Tests for Tracy postures and contracts.

Tests the four-part contracts for embellish, corroborate, gap-fill postures.
"""

import sys
from unittest.mock import Mock

import pytest

sys.path.insert(0, ".")

from scripts.utilities.tracy_vocab_lockstep import validate_suggested_resources
from skills.bmad_agent_tracy.scripts.posture_dispatcher import PostureDispatcher


class TestPostureDispatcher:
    """Test the PostureDispatcher class."""

    @pytest.fixture
    def mock_dispatcher(self):
        """Create a mock dispatcher."""
        mock_dispatcher = Mock()
        mock_dispatcher.dispatch.return_value = {
            "sources": ["source1"],
            "classification": "supporting",
            "confidence_score": 0.8,
        }
        return mock_dispatcher

    @pytest.fixture
    def dispatcher(self, mock_dispatcher):
        return PostureDispatcher(mock_dispatcher)

    def test_embellish_not_implemented(self, dispatcher):
        """Test that embellish raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Embellish posture not implemented"):
            dispatcher.embellish("target", "examples")

    def test_corroborate_dispatches_scite_only_when_bolster_disabled(
        self,
        dispatcher,
        mock_dispatcher,
    ):
        """Default corroborate path uses scite-only single-provider retrieval."""
        result = dispatcher.corroborate("claim", "context")

        assert result["status"] == "success"
        assert result["posture"] == "corroborate"
        assert result["output"]["classification"] == "supporting"
        assert result["output"]["evidence_found"] is True

        intent = mock_dispatcher.dispatch.call_args[0][0]
        assert intent["cross_validate"] is False
        assert intent["provider_hints"] == ["scite"]

    def test_corroborate_enables_cross_validation_when_bolster_enabled(
        self,
        dispatcher,
        mock_dispatcher,
    ):
        """Evidence bolster path requests scite+consensus cross-validation."""
        result = dispatcher.corroborate("claim", "context", evidence_bolster=True)

        assert result["status"] == "success"
        intent = mock_dispatcher.dispatch.call_args[0][0]
        assert intent["cross_validate"] is True
        assert intent["provider_hints"] == ["scite", "consensus"]

    def test_gap_fill_not_implemented(self, dispatcher):
        """Test that gap_fill raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Gap-Fill posture not implemented"):
            dispatcher.gap_fill("gap", "type", "scope")


class TestTracyVocabLockstep:
    """Test schema validation for Tracy outputs."""

    def test_valid_embellish_output(self):
        """Test validation of valid embellish output."""
        data = {
            "status": "success",
            "posture": "embellish",
            "intent_class": "narration_citation",
            "intent_detail": "Provides examples",
            "editorial_note": "Added because it illustrates the concept perfectly.",
            "provider_metadata": {"scite": {}},
            "input": {
                "target_element": "plan_unit_1",
                "enrichment_type": "examples",
            },
            "output": {
                "content_added": True,
                "content": "Example content here",
                "sources": ["source1", "source2"],
            },
            "provenance": {
                "retrieval_provider": "scite.ai",
                "query_terms": ["example", "query"],
                "timestamp": "2026-04-18T23:00:00Z",
            },
        }
        assert validate_suggested_resources(data)

    def test_valid_corroborate_output(self):
        """Test validation of valid corroborate output."""
        data = {
            "status": "success",
            "posture": "corroborate",
            "intent_class": "supporting_evidence",
            "intent_detail": "Validates the claim",
            "editorial_note": "Strongly corroborates the finding with recent study.",
            "provider_metadata": {"scite": {}},
            "input": {
                "claim": "Test claim",
                "source_context": "Context here",
            },
            "output": {
                "evidence_found": True,
                "classification": "supporting",
                "confidence_score": 0.8,
                "sources": ["source1"],
            },
            "provenance": {
                "retrieval_provider": "scite.ai",
                "query_terms": ["claim", "verification"],
                "timestamp": "2026-04-18T23:00:00Z",
            },
        }
        assert validate_suggested_resources(data)

    def test_valid_gap_fill_output(self):
        """Test validation of valid gap-fill output."""
        data = {
            "status": "success",
            "posture": "gap-fill",
            "intent_class": "background_primary",
            "intent_detail": "Fills the context gap",
            "editorial_note": "A highly cited overview to fill the unit gap.",
            "provider_metadata": {"scite": {}},
            "input": {
                "gap_description": "Missing background",
                "content_type": "explanation",
                "scope": "unit",
            },
            "output": {
                "gap_filled": True,
                "content": "Gap filler content",
                "relevance_score": 0.9,
                "sources": ["source1"],
            },
            "provenance": {
                "retrieval_provider": "scite.ai",
                "query_terms": ["background", "gap"],
                "timestamp": "2026-04-18T23:00:00Z",
            },
        }
        assert validate_suggested_resources(data)

    def test_invalid_posture(self):
        """Test validation fails for invalid posture."""
        data = {
            "status": "success",
            "posture": "invalid_posture",
            "input": {},
            "output": {},
        }
        assert not validate_suggested_resources(data)

    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        data = {
            "status": "success",
            "posture": "embellish",
            "input": {},
            # Missing output and editorial metadata
        }
        assert not validate_suggested_resources(data)

    def test_valid_failure_mode(self):
        """Test validation of failed status."""
        data = {
            "status": "failed",
            "reason": "API timeout",
            "posture": "embellish",
            "input": {
                "target_element": "plan_unit_1",
                "enrichment_type": "examples",
            },
        }
        assert validate_suggested_resources(data)
