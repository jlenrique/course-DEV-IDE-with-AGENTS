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
    list_style_presets,
    load_style_guide_gamma,
    load_style_preset,
    merge_parameters,
    resolve_style_preset,
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


# ---------------------------------------------------------------------------
# Style Preset Tests
# ---------------------------------------------------------------------------

_SAMPLE_PRESETS_YAML = """\
presets:
  - name: hil-2026-apc-nejal-A
    description: HIL branded deck Approach A
    approach: A
    scope: "*"
    theme_id: njim9kuhfnljvaa
    theme_name: "2026 HIL APC Nejal"
    parameters:
      textMode: generate
      textOptions:
        amount: detailed
        language: en
      imageOptions:
        source: aiGenerated
        model: nano-banana-2-mini
        stylePreset: illustration
        keywords:
          - vector
          - minimalist
          - flat-color
      cardOptions:
        dimensions: "16x9"
      format: presentation
      formatVariant: classic
      numCards: 10
      additionalInstructions: "Keep the style of all the images uniform."
    provenance:
      source: exemplar-match
      established: "2026-03-27"
    version: 1
  - name: hil-2026-apc-nejal-B
    description: HIL branded deck Approach B
    approach: B
    scope: "*"
    theme_id: njim9kuhfnljvaa
    theme_name: "2026 HIL APC Nejal"
    parameters:
      textMode: generate
      imageOptions:
        source: aiGenerated
        model: flux-kontext-pro
        stylePreset: custom
        style: "Line drawing illustration. Clean black ink on white."
        keywords:
          - vector
          - minimalist
        referenceImagePath: "course-content/staging/ad-hoc/ref.png"
      numCards: 10
      additionalInstructions: "Keep the style of all the images uniform."
    provenance:
      source: gary-proposed
      established: "2026-03-27"
    version: 1
  - name: startup-bold
    description: Bold startup style
    approach: A
    scope: "C2"
    theme_id: theme_startup_xyz
    theme_name: "Startup Bold"
    parameters:
      textMode: generate
      imageOptions:
        source: aiGenerated
        model: flux-2-pro
        stylePreset: photorealistic
    provenance:
      source: user-defined
      established: "2026-03-28"
    version: 1
"""


def _write_presets(tmp_path: Path) -> Path:
    p = tmp_path / "gamma-style-presets.yaml"
    p.write_text(_SAMPLE_PRESETS_YAML, encoding="utf-8")
    return p


class TestListStylePresets:
    """Tests for listing style presets."""

    def test_returns_all_presets(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        presets = list_style_presets(path=path)
        assert len(presets) == 3  # A, B, startup-bold

    def test_filters_by_scope_wildcard(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        presets = list_style_presets(scope="C1", path=path)
        # Only wildcard presets match C1 (A and B are both scope="*")
        names = [p["name"] for p in presets]
        assert "hil-2026-apc-nejal-A" in names
        assert "hil-2026-apc-nejal-B" in names
        assert "startup-bold" not in names

    def test_filters_by_scope_exact(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        presets = list_style_presets(scope="C2", path=path)
        # Wildcard (A + B) and C2 match
        assert len(presets) == 3

    def test_filters_by_scope_prefix(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        presets = list_style_presets(scope="C2 > M1", path=path)
        # Wildcard (A + B) and C2 all match
        assert len(presets) == 3

    def test_returns_empty_when_file_missing(self, tmp_path: Path) -> None:
        presets = list_style_presets(path=tmp_path / "nonexistent.yaml")
        assert presets == []


class TestLoadStylePreset:
    """Tests for loading a single preset by name."""

    def test_loads_by_name(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        params = load_style_preset("hil-2026-apc-nejal-A", path=path)
        assert params is not None
        assert params["textMode"] == "generate"
        assert params["imageOptions"]["model"] == "nano-banana-2-mini"

    def test_returns_none_for_unknown_name(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        assert load_style_preset("nonexistent", path=path) is None


class TestResolveStylePreset:
    """Tests for multi-strategy preset resolution."""

    def test_resolve_by_name(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset("startup-bold", path=path)
        assert result["textMode"] == "generate"
        assert result["imageOptions"]["model"] == "flux-2-pro"

    def test_resolve_by_theme_id_returns_first_match(self, tmp_path: Path) -> None:
        # Both A and B share the same theme_id; first in file wins
        path = _write_presets(tmp_path)
        result = resolve_style_preset(theme_id="njim9kuhfnljvaa", path=path)
        assert result["themeId"] == "njim9kuhfnljvaa"
        assert result["imageOptions"]["model"] == "nano-banana-2-mini"  # A comes first

    def test_resolve_by_scope_most_specific(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset(scope="C2 > M1", path=path)
        # C2 is more specific than * for scope "C2 > M1"
        assert result["textMode"] == "generate"

    def test_resolve_returns_empty_when_no_match(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset(name="totally-unknown", path=path)
        assert result == {}

    def test_resolve_returns_empty_when_file_missing(self, tmp_path: Path) -> None:
        result = resolve_style_preset(
            name="hil-2026-apc-nejal",
            path=tmp_path / "gone.yaml",
        )
        assert result == {}

    def test_flatten_includes_theme_id(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-A", path=path)
        assert result["themeId"] == "njim9kuhfnljvaa"


class TestMergeParametersWithPreset:
    """Tests for the updated merge_parameters with style_preset layer."""

    def test_preset_overrides_style_guide(self) -> None:
        result = merge_parameters(
            {"textMode": "generate"},
            {},
            {},
            style_preset={"textMode": "condense"},
        )
        assert result["textMode"] == "condense"

    def test_content_template_overrides_preset(self) -> None:
        result = merge_parameters(
            {},
            {"textMode": "preserve"},
            {},
            style_preset={"textMode": "condense"},
        )
        assert result["textMode"] == "preserve"

    def test_envelope_overrides_all(self) -> None:
        result = merge_parameters(
            {"textMode": "generate"},
            {"textMode": "condense"},
            {"textMode": "preserve"},
            style_preset={"textMode": "condense"},
        )
        assert result["textMode"] == "preserve"

    def test_preset_contributes_new_keys(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {},
            {},
            style_preset={"imageOptions": {"model": "recraft-v3"}},
        )
        assert result["format"] == "presentation"
        assert result["imageOptions"]["model"] == "recraft-v3"

    def test_backward_compatible_without_preset(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {"numCards": 1},
            {"exportAs": "pdf"},
        )
        assert result == {"format": "presentation", "numCards": 1, "exportAs": "pdf"}


class TestFlattenPresetKeywords:
    """Tests for keyword handling in _flatten_preset_params."""

    def test_approach_a_keywords_become_hint(self, tmp_path: Path) -> None:
        """Approach A: keywords stored as _keywordsHint, not in style."""
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-A", path=path)
        img = result["imageOptions"]
        # stylePreset preserved as named value
        assert img["stylePreset"] == "illustration"
        # keywords become hint, not appended to style
        assert "_keywordsHint" in img
        assert "vector" in img["_keywordsHint"]
        # no 'style' key sent (API ignores it for named stylePreset)
        assert "style" not in img
        # keywords list removed
        assert "keywords" not in img

    def test_approach_a_no_reference_image_path(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-A", path=path)
        assert "referenceImagePath" not in result["imageOptions"]

    def test_approach_b_keywords_appended_to_style(self, tmp_path: Path) -> None:
        """Approach B: keywords appended to style prompt string."""
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-B", path=path)
        img = result["imageOptions"]
        assert img["stylePreset"] == "custom"
        style = img["style"]
        assert "Line drawing" in style
        assert "vector" in style
        assert "minimalist" in style
        assert "keywords" not in img

    def test_approach_b_reference_image_path_preserved(self, tmp_path: Path) -> None:
        """Approach B: referenceImagePath kept for Gary to study."""
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-B", path=path)
        assert "referenceImagePath" in result["imageOptions"]
        assert "ref.png" in result["imageOptions"]["referenceImagePath"]

    def test_approach_a_preset_includes_new_fields(self, tmp_path: Path) -> None:
        path = _write_presets(tmp_path)
        result = resolve_style_preset("hil-2026-apc-nejal-A", path=path)
        assert result["numCards"] == 10
        assert result["format"] == "presentation"
        assert result["formatVariant"] == "classic"
        assert "Keep the style" in result["additionalInstructions"]


class TestMergeAdditionalInstructionsConcatenation:
    """Tests for additionalInstructions concatenation across layers."""

    def test_preset_base_plus_content_type(self) -> None:
        result = merge_parameters(
            {},
            {"additionalInstructions": "One concept per card."},
            {},
            style_preset={"additionalInstructions": "Keep style uniform."},
        )
        ai = result["additionalInstructions"]
        assert "Keep style uniform." in ai
        assert "One concept per card." in ai
        # Preset comes before content template
        assert ai.index("Keep style uniform.") < ai.index("One concept per card.")

    def test_all_three_layers_concatenated(self) -> None:
        result = merge_parameters(
            {"additionalInstructions": "Base."},
            {"additionalInstructions": "Content-type."},
            {"additionalInstructions": "Envelope."},
            style_preset={"additionalInstructions": "Preset."},
        )
        ai = result["additionalInstructions"]
        assert ai == "Base. Preset. Content-type. Envelope."

    def test_empty_fragments_skipped(self) -> None:
        result = merge_parameters(
            {"additionalInstructions": ""},
            {},
            {"additionalInstructions": "Only this."},
            style_preset={"additionalInstructions": ""},
        )
        assert result["additionalInstructions"] == "Only this."

    def test_no_additional_instructions_anywhere(self) -> None:
        result = merge_parameters(
            {"format": "presentation"},
            {},
            {},
            style_preset={"textMode": "generate"},
        )
        assert "additionalInstructions" not in result

    def test_other_params_still_override(self) -> None:
        """Non-AI params still use last-wins, only AI concatenates."""
        result = merge_parameters(
            {"textMode": "preserve"},
            {"textMode": "condense"},
            {},
            style_preset={
                "textMode": "generate",
                "additionalInstructions": "Preset base.",
            },
        )
        # textMode: content template wins (later in cascade)
        assert result["textMode"] == "condense"
        # additionalInstructions: concatenated
        assert result["additionalInstructions"] == "Preset base."
