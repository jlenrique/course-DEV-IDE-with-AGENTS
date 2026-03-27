"""Tests for gamma_operations module."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gamma_operations
from gamma_operations import (
    download_export,
    generate_from_template,
    generate_slide,
    load_style_guide_gamma,
    merge_parameters,
)


class TestLoadStyleGuideGamma:
    """Tests for style guide loading."""

    def test_returns_empty_when_file_missing(self, tmp_path: Path) -> None:
        with patch.object(
            gamma_operations, "STYLE_GUIDE_PATH",
            tmp_path / "nonexistent.yaml",
        ):
            result = load_style_guide_gamma()
        assert result == {}

    def test_returns_gamma_section(self, tmp_path: Path) -> None:
        style_file = tmp_path / "style_guide.yaml"
        style_file.write_text(
            "tool_parameters:\n  gamma:\n    default_llm: gpt-4o\n    style: medical\n"
        )
        with patch.object(
            gamma_operations, "STYLE_GUIDE_PATH",
            style_file,
        ):
            result = load_style_guide_gamma()
        assert result["default_llm"] == "gpt-4o"
        assert result["style"] == "medical"

    def test_returns_empty_when_no_gamma_section(self, tmp_path: Path) -> None:
        style_file = tmp_path / "style_guide.yaml"
        style_file.write_text("tool_parameters:\n  elevenlabs:\n    voice: Roger\n")
        with patch.object(
            gamma_operations, "STYLE_GUIDE_PATH",
            style_file,
        ):
            result = load_style_guide_gamma()
        assert result == {}


class TestMergeParameters:
    """Tests for parameter cascade merge."""

    def test_later_sources_override_earlier(self) -> None:
        result = merge_parameters(
            {"format": "document", "numCards": 5},
            {"format": "presentation"},
            {"numCards": 1},
        )
        assert result["format"] == "presentation"
        assert result["numCards"] == 1

    def test_empty_values_do_not_override(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {"format": ""},
            {},
        )
        assert result["format"] == "presentation"

    def test_none_values_do_not_override(self) -> None:
        result = merge_parameters(
            {"themeId": "abc123"},
            {"themeId": None},
            {},
        )
        assert result["themeId"] == "abc123"

    def test_all_sources_contribute(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {"numCards": 1},
            {"exportAs": "pdf"},
        )
        assert result == {"format": "presentation", "numCards": 1, "exportAs": "pdf"}


class TestGenerateSlide:
    """Tests for text-based generation."""

    def test_calls_client_with_correct_params(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-123"}
        mock_client.wait_for_generation.return_value = {
            "id": "gen-123",
            "status": "completed",
            "gammaUrl": "https://gamma.app/docs/gen-123",
        }

        params = {
            "input_text": "Test content",
            "text_mode": "preserve",
            "format": "presentation",
            "num_cards": 1,
            "export_as": "pdf",
        }
        result = generate_slide(params, client=mock_client)

        mock_client.generate.assert_called_once_with(
            "Test content",
            "preserve",
            format="presentation",
            num_cards=1,
            export_as="pdf",
        )
        mock_client.wait_for_generation.assert_called_once_with("gen-123")
        assert result["status"] == "completed"

    def test_handles_camelcase_params(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-456"}
        mock_client.wait_for_generation.return_value = {"status": "completed"}

        params = {
            "inputText": "CamelCase input",
            "textMode": "generate",
            "numCards": 3,
            "exportAs": "pptx",
        }
        generate_slide(params, client=mock_client)

        mock_client.generate.assert_called_once()
        call_args = mock_client.generate.call_args
        assert call_args[0][0] == "CamelCase input"
        assert call_args[0][1] == "generate"


class TestGenerateFromTemplate:
    """Tests for template-based generation."""

    def test_calls_client_with_template_params(self) -> None:
        mock_client = MagicMock()
        mock_client.generate_from_template.return_value = {"id": "tpl-789"}
        mock_client.wait_for_generation.return_value = {"status": "completed"}

        result = generate_from_template(
            "gamma_abc123",
            "Replace content with clinical case",
            {"export_as": "pdf", "theme_id": "theme_xyz"},
            client=mock_client,
        )

        mock_client.generate_from_template.assert_called_once_with(
            "gamma_abc123",
            "Replace content with clinical case",
            theme_id="theme_xyz",
            export_as="pdf",
        )
        assert result["status"] == "completed"


class TestDownloadExport:
    """Tests for artifact download."""

    def test_downloads_to_specified_dir(self, tmp_path: Path) -> None:
        with patch.object(gamma_operations, "requests") as mock_req:
            mock_resp = MagicMock()
            mock_resp.content = b"PDF content here"
            mock_resp.raise_for_status = MagicMock()
            mock_req.get.return_value = mock_resp

            result = download_export(
                "https://example.com/export/slide.pdf?token=abc",
                output_dir=tmp_path,
                filename="test-slide.pdf",
            )

        assert result == tmp_path / "test-slide.pdf"
        assert result.read_bytes() == b"PDF content here"

    def test_auto_derives_filename(self, tmp_path: Path) -> None:
        with patch.object(gamma_operations, "requests") as mock_req:
            mock_resp = MagicMock()
            mock_resp.content = b"data"
            mock_resp.raise_for_status = MagicMock()
            mock_req.get.return_value = mock_resp

            result = download_export(
                "https://cdn.gamma.app/exports/my-deck.pdf?sig=xyz",
                output_dir=tmp_path,
            )

        assert result.name == "my-deck.pdf"
