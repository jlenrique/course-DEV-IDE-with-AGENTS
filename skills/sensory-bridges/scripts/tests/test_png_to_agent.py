"""Tests for image sensory bridge."""

import pytest
from pathlib import Path

from skills.sensory_bridges.scripts.png_to_agent import analyze_image
from skills.sensory_bridges.scripts.bridge_utils import validate_response


class TestAnalyzeImage:
    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            analyze_image("/nonexistent/file.png")

    def test_schema_conformance_with_content(self, tmp_path):
        f = tmp_path / "slide.png"
        f.write_bytes(b"\x89PNG")

        result = analyze_image(
            f,
            extracted_text="The Three Macro Trends",
            layout_description="Single column with title and three bullet points",
            visual_elements=[{"type": "icon", "description": "medical cross"}],
            slide_title="The Three Macro Trends",
            text_blocks=["The Three Macro Trends", "Digital transformation", "Workforce evolution"],
        )

        assert result["confidence"] == "HIGH"
        assert result["modality"] == "image"
        assert result["extracted_text"] == "The Three Macro Trends"
        assert len(result["visual_elements"]) == 1
        assert validate_response(result) == []

    def test_empty_extraction_gets_low_confidence(self, tmp_path):
        f = tmp_path / "blank.png"
        f.write_bytes(b"\x89PNG")

        result = analyze_image(f)

        assert result["confidence"] == "LOW"
        assert "No text extracted" in result["confidence_rationale"]
        assert validate_response(result) == []

    def test_custom_confidence(self, tmp_path):
        f = tmp_path / "complex.png"
        f.write_bytes(b"\x89PNG")

        result = analyze_image(
            f,
            extracted_text="Some text",
            confidence="MEDIUM",
            confidence_rationale="Complex diagram, partial text extraction",
        )

        assert result["confidence"] == "MEDIUM"
        assert "Complex diagram" in result["confidence_rationale"]
