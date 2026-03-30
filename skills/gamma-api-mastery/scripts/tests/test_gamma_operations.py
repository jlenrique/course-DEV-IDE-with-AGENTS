"""Tests for gamma_operations module."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

_PROJECT_ROOT = str(Path(__file__).resolve().parents[4])
sys.path.insert(0, _PROJECT_ROOT)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gamma_operations  # noqa: E402
from gamma_operations import (  # noqa: E402
    download_export,
    execute_generation,
    generate_deck_mixed_fidelity,
    generate_from_template,
    generate_slide,
    list_themes_and_templates,
    list_style_presets,
    load_style_guide_gamma,
    load_style_preset,
    merge_slide_content,
    merge_parameters,
    normalize_slides_payload,
    resolve_style_preset,
    validate_dispatch_ready,
    validate_outbound_contract,
    validate_theme_mapping_handshake,
)


def _valid_theme_resolution() -> dict[str, object]:
    return {
        "requested_theme_key": "hil-2026-apc-nejal-A",
        "resolved_theme_key": "theme_abc",
        "resolved_parameter_set": "hil-2026-apc-nejal-A",
        "mapping_source": "state/config/gamma-style-presets.yaml",
        "mapping_version": "1",
        "user_confirmation": True,
    }


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


class TestNormalizeSlidesPayload:
    def test_accepts_list_payload_unchanged_when_complete(self) -> None:
        payload = [
            {
                "slide_number": 1,
                "fidelity": "creative",
                "content": "Slide 1 content",
                "source_ref": "extracted.md#Page 1",
            }
        ]
        result = normalize_slides_payload(payload)
        assert len(result) == 1
        assert result[0]["content"] == "Slide 1 content"
        assert result[0]["source_ref"] == "extracted.md#Page 1"

    def test_accepts_object_with_slides_and_derives_source_ref(self) -> None:
        payload = {
            "run_id": "R1",
            "slides": [
                {
                    "slide_number": 2,
                    "fidelity": "literal-text",
                    "source_anchors": ["extracted.md#Page 2", "extracted.md#Page 3"],
                }
            ],
        }
        with pytest.raises(ValueError, match="Slides payload missing required content"):
            normalize_slides_payload(payload)

    def test_allows_placeholders_only_with_explicit_debug_override(self) -> None:
        payload = {
            "slides": [
                {
                    "slide_number": 2,
                    "fidelity": "literal-text",
                    "source_anchors": ["extracted.md#Page 2", "extracted.md#Page 3"],
                }
            ]
        }
        result = normalize_slides_payload(payload, allow_placeholder_content=True)
        assert len(result) == 1
        assert "extracted.md#Page 2; extracted.md#Page 3" == result[0]["source_ref"]
        assert "placeholder derived from pre-dispatch artifacts" in result[0]["content"]

    def test_invalid_payload_raises(self) -> None:
        with pytest.raises(ValueError, match="Expected list or object with 'slides' array"):
            normalize_slides_payload({"slides": "not-a-list"})


class TestMergeSlideContent:
    def test_merges_content_rows_into_fidelity_rows(self) -> None:
        fidelity_payload = {
            "slides": [
                {
                    "slide_number": 1,
                    "fidelity": "creative",
                    "source_anchors": ["extracted.md#Page 1"],
                },
                {
                    "slide_number": 2,
                    "fidelity": "literal-text",
                    "source_anchors": ["extracted.md#Page 2"],
                },
            ]
        }
        content_payload = {
            "slides": [
                {
                    "slide_number": 1,
                    "content": "Creative content",
                    "source_ref": "extracted.md#Page 1",
                },
                {
                    "slide_number": 2,
                    "content": "Literal content",
                    "source_ref": "extracted.md#Page 2",
                },
            ]
        }

        merged = merge_slide_content(fidelity_payload, content_payload)

        assert len(merged) == 2
        assert merged[0]["fidelity"] == "creative"
        assert merged[0]["content"] == "Creative content"
        assert merged[1]["fidelity"] == "literal-text"
        assert merged[1]["content"] == "Literal content"
        assert "placeholder derived from pre-dispatch artifacts" not in merged[1]["content"]

    def test_missing_content_in_merged_payload_fails_without_debug_override(self) -> None:
        fidelity_payload = {
            "slides": [
                {
                    "slide_number": 1,
                    "fidelity": "creative",
                    "source_anchors": ["extracted.md#Page 1"],
                }
            ]
        }
        content_payload = {"slides": []}

        with pytest.raises(ValueError, match="Slides payload missing required content"):
            merge_slide_content(fidelity_payload, content_payload)


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

    def test_log_includes_run_id_when_provided(self, caplog: pytest.LogCaptureFixture) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-runid"}
        mock_client.wait_for_generation.return_value = {"id": "gen-runid", "status": "completed"}
        params = {"input_text": "x", "text_mode": "generate"}
        with caplog.at_level(logging.INFO, logger="gamma_operations"):
            generate_slide(params, client=mock_client, run_id="RUN-ABC-99")
        assert any("RUN-ABC-99" in r.message for r in caplog.records)
        assert any("generation_id=" in r.message for r in caplog.records)

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

    def test_strips_internal_image_option_helper_keys(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-789"}
        mock_client.wait_for_generation.return_value = {"status": "completed"}

        params = {
            "input_text": "Deck content",
            "text_mode": "generate",
            "imageOptions": {
                "source": "aiGenerated",
                "model": "gemini-3.1-flash-image-mini",
                "stylePreset": "illustration",
                "_keywordsHint": "vector, minimalist",
                "referenceImagePath": "course-content/staging/ad-hoc/ref.png",
            },
            "additionalInstructions": "Keep style uniform.",
        }

        generate_slide(params, client=mock_client)

        _, kwargs = mock_client.generate.call_args
        image_options = kwargs["image_options"]
        assert "_keywordsHint" not in image_options
        assert "referenceImagePath" not in image_options
        assert image_options["source"] == "aiGenerated"
        assert image_options["model"] == "gemini-3.1-flash-image-mini"

    def test_promotes_keywords_hint_to_additional_instructions(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-790"}
        mock_client.wait_for_generation.return_value = {"status": "completed"}

        params = {
            "input_text": "Deck content",
            "text_mode": "generate",
            "imageOptions": {
                "source": "aiGenerated",
                "_keywordsHint": "vector, minimalist",
            },
            "additionalInstructions": "Keep style uniform.",
        }

        generate_slide(params, client=mock_client)

        _, kwargs = mock_client.generate.call_args
        ai_text = kwargs["additional_instructions"]
        assert "Keep style uniform." in ai_text
        assert "Visual keyword cues: vector, minimalist." in ai_text


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


class TestListThemesAndTemplates:
    """Tests for TP capability in gamma_operations."""

    def test_returns_themes_and_templates(self, tmp_path: Path) -> None:
        style_file = tmp_path / "style_guide.yaml"
        style_file.write_text(
            """
tool_parameters:
  gamma:
    templates:
      - name: C1 lesson template
        gamma_id: gamma_tpl_1
        scope: C1
        content_type: lecture-slides
      - name: Global fallback
        gamma_id: gamma_tpl_2
        scope: "*"
        content_type: "*"
""".strip(),
            encoding="utf-8",
        )

        mock_client = MagicMock()
        mock_client.list_themes.return_value = [{"id": "theme_abc", "name": "Theme A"}]

        result = list_themes_and_templates(
            scope="C1 > M1",
            content_type="lecture-slides",
            client=mock_client,
            style_guide_path=style_file,
        )

        assert len(result["themes"]) == 1
        assert len(result["templates"]) == 2
        names = [t.get("name") for t in result["templates"]]
        assert "C1 lesson template" in names
        assert "Global fallback" in names

    def test_api_failure_degrades_to_templates_only(self, tmp_path: Path) -> None:
        style_file = tmp_path / "style_guide.yaml"
        style_file.write_text(
            "tool_parameters:\n  gamma:\n    templates:\n      - name: fallback\n        gamma_id: t1\n        scope: '*'\n        content_type: '*'\n",
            encoding="utf-8",
        )
        mock_client = MagicMock()
        mock_client.list_themes.side_effect = RuntimeError("Gamma unavailable")

        result = list_themes_and_templates(
            scope="C1",
            content_type="lecture-slides",
            client=mock_client,
            style_guide_path=style_file,
        )

        assert result["themes"] == []
        assert len(result["templates"]) == 1


class TestExecuteGenerationThemeEnforcement:
    """Regression tests for execute_generation theme handshake behavior."""

    def test_slides_path_requires_theme_handshake(self) -> None:
        with pytest.raises(ValueError, match="Theme mapping handshake failed"):
            execute_generation(
                {"input_text": "hello", "textMode": "generate"},
                slides=[{"slide_number": 1, "content": "A", "fidelity": "creative"}],
            )

    def test_slides_path_enforces_handshake_before_generate(self) -> None:
        mock_client = MagicMock()
        mock_client.generate.return_value = {"id": "gen-1"}
        mock_client.wait_for_generation.return_value = {"id": "gen-1", "status": "completed"}

        result = execute_generation(
            {
                "input_text": "hello",
                "textMode": "generate",
                **_valid_theme_resolution(),
                "themeId": "theme_abc",
            },
            slides=[{"slide_number": 1, "content": "A", "fidelity": "creative"}],
            client=mock_client,
        )

        assert result["status"] == "completed"


class TestGaryOutboundContract:
    """Tests for Story 11.2 outbound contract enforcement."""

    def test_mixed_fidelity_output_contains_required_fields(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal card", "fidelity": "literal-text"},
        ]

        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.side_effect = [{"id": "gen-creative"}, {"id": "gen-literal"}]
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    "exportAs": "png",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        for required_key in (
            "gary_slide_output",
            "quality_assessment",
            "parameter_decisions",
            "recommendations",
            "flags",
        ):
            assert required_key in result

        assert result["flags"]["run_validation_artifact_pointer"].startswith(
            "run://C1-M1-PRES-ADHOC-20260330/"
        )
        assert result["calls_made"] == 2

    def test_visual_description_policy_avoids_pending_export_placeholders(self) -> None:
        slides = [{"slide_number": 1, "content": "Creative card", "fidelity": "creative"}]

        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.return_value = {"id": "gen-creative"}
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        desc = result["gary_slide_output"][0]["visual_description"].lower()
        assert "pending export" not in desc

    def test_mixed_fidelity_file_path_populated_from_generation_urls(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative card", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal card", "fidelity": "literal-text"},
        ]

        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.side_effect = [
                {"id": "gen-creative", "gammaUrl": "https://gamma.app/docs/creative"},
                {"id": "gen-literal", "gammaUrl": "https://gamma.app/docs/literal"},
            ]
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        output = result["gary_slide_output"]
        assert len(output) == 2
        assert output[0]["file_path"] == "https://gamma.app/docs/creative"
        assert output[1]["file_path"] == "https://gamma.app/docs/literal"

    def test_validate_outbound_contract_raises_on_missing_required_field(self) -> None:
        payload = {
            "gary_slide_output": [],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        payload.pop("quality_assessment")
        with pytest.raises(ValueError, match=r"Missing required field\(s\): quality_assessment"):
            validate_outbound_contract(payload)

    def test_validate_outbound_contract_requires_source_ref_when_slide_present(self) -> None:
        payload = {
            "gary_slide_output": [
                {
                    "slide_id": "s-1",
                    "file_path": "course-content/staging/card-01.png",
                    "card_number": 1,
                    "visual_description": "desc",
                    "source_ref": "",
                }
            ],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        with pytest.raises(ValueError, match=r"source_ref must be a non-empty string"):
            validate_outbound_contract(payload)

    def test_validate_outbound_contract_strict_mode_requires_file_path(self) -> None:
        payload = {
            "gary_slide_output": [
                {
                    "slide_id": "s-1",
                    "file_path": None,
                    "card_number": 1,
                    "visual_description": "desc",
                    "source_ref": "slide-brief.md#Slide 1",
                }
            ],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        with pytest.raises(ValueError, match=r"file_path must be a non-empty string"):
            validate_outbound_contract(payload, require_dispatch_paths=True)

    def test_validate_dispatch_ready_uses_strict_file_path_mode(self) -> None:
        payload = {
            "gary_slide_output": [
                {
                    "slide_id": "s-1",
                    "file_path": None,
                    "card_number": 1,
                    "visual_description": "desc",
                    "source_ref": "slide-brief.md#Slide 1",
                }
            ],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        with pytest.raises(ValueError, match=r"file_path must be a non-empty string"):
            validate_dispatch_ready(payload)

    def test_validate_outbound_contract_allows_empty_slide_output(self) -> None:
        payload = {
            "gary_slide_output": [],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": _valid_theme_resolution(),
        }
        validate_outbound_contract(payload)

    def test_validate_outbound_contract_requires_theme_resolution(self) -> None:
        payload = {
            "gary_slide_output": [],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
        }
        with pytest.raises(ValueError, match=r"Missing required field\(s\): theme_resolution"):
            validate_outbound_contract(payload)

    def test_validate_outbound_contract_rejects_invalid_theme_resolution(self) -> None:
        payload = {
            "gary_slide_output": [],
            "quality_assessment": {},
            "parameter_decisions": {},
            "recommendations": [],
            "flags": {},
            "theme_resolution": {
                "requested_theme_key": "a",
                "resolved_theme_key": "b",
                # missing required fields
            },
        }
        with pytest.raises(ValueError, match="Theme mapping handshake failed"):
            validate_outbound_contract(payload)


class TestThemeMappingHandshake:
    """Tests for Story 11.4 theme-selection -> parameter mapping gate."""

    def test_theme_handshake_missing_fields_fails(self) -> None:
        with pytest.raises(ValueError, match=r"Missing required field\(s\):"):
            validate_theme_mapping_handshake(
                {
                    "requested_theme_key": "hil-2026-apc-nejal-A",
                    "resolved_theme_key": "theme_abc",
                    # missing resolved_parameter_set, mapping_source,
                    # mapping_version, user_confirmation
                }
            )

    def test_theme_handshake_requires_explicit_confirmation(self) -> None:
        with pytest.raises(ValueError, match="user_confirmation must be explicit"):
            validate_theme_mapping_handshake(
                {
                    "requested_theme_key": "hil-2026-apc-nejal-A",
                    "resolved_theme_key": "theme_abc",
                    "resolved_parameter_set": "hil-2026-apc-nejal-A",
                    "mapping_source": "state/config/gamma-style-presets.yaml",
                    "mapping_version": "1",
                    "user_confirmation": False,
                }
            )

    def test_mixed_fidelity_requires_theme_handshake(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal", "fidelity": "literal-text"},
        ]
        with pytest.raises(ValueError, match="Theme mapping handshake failed"):
            generate_deck_mixed_fidelity(
                slides,
                {"themeId": "theme_abc"},
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

    def test_mixed_fidelity_theme_handshake_in_payload(self) -> None:
        slides = [
            {"slide_number": 1, "content": "Creative", "fidelity": "creative"},
            {"slide_number": 2, "content": "Literal", "fidelity": "literal-text"},
        ]

        with patch.object(gamma_operations, "generate_slide") as mock_generate:
            mock_generate.side_effect = [{"id": "gen-creative"}, {"id": "gen-literal"}]
            result = generate_deck_mixed_fidelity(
                slides,
                {
                    "themeId": "theme_abc",
                    **_valid_theme_resolution(),
                },
                "C1-M1-PRES-ADHOC-20260330",
                run_id="C1-M1-PRES-ADHOC-20260330",
            )

        assert result["theme_resolution"]["requested_theme_key"] == "hil-2026-apc-nejal-A"
        assert result["theme_resolution"]["resolved_theme_key"] == "theme_abc"
        assert result["parameter_decisions"]["resolved_parameter_set"] == "hil-2026-apc-nejal-A"
        assert result["flags"]["theme_mapping_verified"] is True
