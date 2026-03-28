"""Tests for bridge_utils shared utilities."""

import pytest
from unittest.mock import patch
from pathlib import Path

from skills.sensory_bridges.scripts.bridge_utils import (
    build_request,
    build_response,
    validate_response,
    VALID_MODALITIES,
    VALID_CONFIDENCE,
    SCHEMA_VERSION,
)


class TestBuildRequest:
    def test_valid_request(self, tmp_path):
        f = tmp_path / "test.pptx"
        f.write_text("dummy")
        req = build_request(f, "pptx", "G3", "fidelity-assessor")
        assert req["modality"] == "pptx"
        assert req["gate"] == "G3"
        assert req["requesting_agent"] == "fidelity-assessor"

    def test_invalid_modality(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("dummy")
        with pytest.raises(ValueError, match="Invalid modality"):
            build_request(f, "spreadsheet", "G3", "test")

    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            build_request("/nonexistent/file.pptx", "pptx", "G3", "test")


class TestBuildResponse:
    def test_valid_response(self):
        resp = build_response(
            modality="pptx",
            artifact_path="/test.pptx",
            confidence="HIGH",
            confidence_rationale="All good",
            slides=[],
            total_slides=0,
        )
        assert resp["schema_version"] == SCHEMA_VERSION
        assert resp["confidence"] == "HIGH"
        assert resp["modality"] == "pptx"
        assert "perception_timestamp" in resp

    def test_invalid_confidence(self):
        with pytest.raises(ValueError, match="Invalid confidence"):
            build_response("pptx", "/test.pptx", "MAYBE", "unsure")


class TestValidateResponse:
    def test_valid_pptx_response(self):
        resp = build_response(
            modality="pptx",
            artifact_path="/test.pptx",
            confidence="HIGH",
            confidence_rationale="OK",
            slides=[{"slide_number": 1, "text_frames": ["Hello"]}],
            total_slides=1,
        )
        errors = validate_response(resp)
        assert errors == []

    def test_valid_audio_response(self):
        resp = build_response(
            modality="audio",
            artifact_path="/test.mp3",
            confidence="HIGH",
            confidence_rationale="OK",
            transcript_text="Hello world",
            timestamped_words=[],
            total_duration_ms=5000,
            wpm=120.0,
        )
        errors = validate_response(resp)
        assert errors == []

    def test_missing_modality_fields(self):
        resp = {
            "schema_version": "1.0",
            "modality": "pptx",
            "artifact_path": "/test.pptx",
            "confidence": "HIGH",
            "confidence_rationale": "OK",
            "perception_timestamp": "2026-03-28T00:00:00Z",
        }
        errors = validate_response(resp)
        assert any("slides" in e for e in errors)
        assert any("total_slides" in e for e in errors)

    def test_missing_common_fields(self):
        resp = {"modality": "pptx"}
        errors = validate_response(resp)
        assert len(errors) >= 4  # missing schema_version, artifact_path, confidence, etc.

    def test_all_modalities_have_required_fields(self):
        for modality in VALID_MODALITIES:
            resp = {"modality": modality}
            errors = validate_response(resp)
            modality_errors = [e for e in errors if f"{modality}-specific" in e]
            assert len(modality_errors) > 0, f"No modality-specific validation for {modality}"
