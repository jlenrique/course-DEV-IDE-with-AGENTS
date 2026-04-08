"""Tests for elevenlabs_operations.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "elevenlabs_operations.py"
SPEC = importlib.util.spec_from_file_location("elevenlabs_operations", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class TestStyleGuideHelpers:
    def test_load_style_guide_returns_empty_when_missing(self, tmp_path: Path) -> None:
        with patch.object(MODULE, "STYLE_GUIDE_PATH", tmp_path / "missing.yaml"):
            assert MODULE.load_style_guide_elevenlabs() == {}

    def test_load_voice_preview_profiles_returns_empty_when_missing(
        self, tmp_path: Path
    ) -> None:
        with patch.object(MODULE, "VOICE_PROFILES_PATH", tmp_path / "missing.yaml"):
            assert MODULE.load_voice_preview_profiles() == {}

    def test_merge_parameters_prefers_overrides(self) -> None:
        result = MODULE.merge_parameters(
            {"default_voice_id": "voice-a", "model_id": "m1"},
            {"model_id": "m2"},
        )
        assert result["default_voice_id"] == "voice-a"
        assert result["model_id"] == "m2"


class TestFormattingHelpers:
    def test_build_pronunciation_pls_contains_terms(self) -> None:
        xml = MODULE.build_pronunciation_pls({"resiliency": "rih-ZIL-ee-en-see"})
        assert "<grapheme>resiliency</grapheme>" in xml
        assert "<phoneme>rih-ZIL-ee-en-see</phoneme>" in xml

    def test_alignment_to_vtt_builds_word_cues(self) -> None:
        alignment = {
            "characters": list("Hi all"),
            "character_start_times_seconds": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
            "character_end_times_seconds": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
        }
        vtt = MODULE.alignment_to_vtt(alignment)
        assert "WEBVTT" in vtt
        assert "Hi" in vtt
        assert "all" in vtt


class TestVoicePreviewFlow:
    def test_preview_voice_options_uses_verified_language_preview_url(self) -> None:
        client = Mock()
        client.list_voices.return_value = [
            {
                "voice_id": "voice-en",
                "name": "Locale Aware",
                "preview_url": "",
                "verified_languages": [
                    {
                        "language": "en",
                        "locale": "en-US",
                        "preview_url": "https://samples/en-us.mp3",
                    }
                ],
                "category": "premade",
                "description": "Warm professional narrator",
                "labels": {"use_case": "narration", "language": "en"},
            },
            {
                "voice_id": "voice-b",
                "name": "Backup One",
                "preview_url": "https://samples/b.mp3",
                "category": "premade",
                "description": "Clear educational narrator",
                "labels": {"use_case": "educational", "language": "en"},
            },
            {
                "voice_id": "voice-c",
                "name": "Backup Two",
                "preview_url": "https://samples/c.mp3",
                "category": "premade",
                "description": "Calm professional instructor",
                "labels": {"use_case": "narration", "language": "en"},
            },
        ]

        result = MODULE.preview_voice_options(
            mode="default_plus_alternatives",
            presentation_attributes={"content_type": "narrated-deck-video-export"},
            style_defaults={"default_voice_id": "voice-en"},
            client=client,
        )

        assert result["candidate_voices"][0]["preview_url"] == "https://samples/en-us.mp3"

    def test_preview_voice_options_returns_anchor_and_alternatives(
        self, tmp_path: Path
    ) -> None:
        client = Mock()
        client.list_voices.return_value = [
            {
                "voice_id": "voice-prev",
                "name": "Dr. Anchor",
                "preview_url": "https://samples/anchor.mp3",
                "category": "premade",
                "description": "Warm professional narrator",
                "labels": {"accent": "American", "use_case": "narration"},
            },
            {
                "voice_id": "voice-alt-1",
                "name": "Calm Explainer",
                "preview_url": "https://samples/alt1.mp3",
                "category": "premade",
                "description": "Calm educational clinical voice",
                "labels": {"use_case": "educational"},
            },
            {
                "voice_id": "voice-alt-2",
                "name": "Clear Authority",
                "preview_url": "https://samples/alt2.mp3",
                "category": "professional",
                "description": "Credible professional narrator for medical education",
                "labels": {"use_case": "narration"},
            },
            {
                "voice_id": "voice-weird",
                "name": "Cartoon Chaos",
                "preview_url": "https://samples/weird.mp3",
                "category": "generated",
                "description": "Cartoon parody character voice",
                "labels": {"use_case": "comedy"},
            },
        ]
        manifest_path = tmp_path / "segment-manifest.yaml"
        script_path = tmp_path / "narration-script.md"
        manifest_path.write_text("lesson_id: C1\nsegments: []\n", encoding="utf-8")
        script_path.write_text("# Script\n", encoding="utf-8")
        previous_receipt = tmp_path / "voice-preview-decision.json"
        previous_receipt.write_text(
            '{"selected_voice_id": "voice-prev"}',
            encoding="utf-8",
        )
        output_path = tmp_path / "voice-preview-options.json"

        result = MODULE.preview_voice_options(
            mode="continuity_preview",
            presentation_attributes={
                "audience": "healthcare practitioners",
                "tone": "clear, warm, authoritative",
                "content_type": "clinical lesson narration",
            },
            previous_voice_receipt_path=previous_receipt,
            style_defaults={"default_voice_id": "voice-default"},
            locked_manifest_path=manifest_path,
            locked_script_path=script_path,
            output_path=output_path,
            client=client,
        )

        assert result["status"] == "selection_required"
        assert result["mode"] == "continuity_preview"
        assert result["candidate_voices"][0]["voice_id"] == "voice-prev"
        assert result["candidate_voices"][0]["source"] == "previous_presentation_voice"
        assert result["candidate_voices"][0]["rank"] == 1
        assert len(result["candidate_voices"]) == 3
        assert result["presentation_voice_source"]["type"] == "previous_presentation_voice"
        assert result["locked_manifest_hash"]
        assert result["locked_script_hash"]
        assert output_path.exists()
        assert "voice-weird" not in [item["voice_id"] for item in result["candidate_voices"]]

    def test_description_led_preview_uses_profile_keyword_overrides(self) -> None:
        client = Mock()
        client.list_voices.return_value = [
            {
                "voice_id": "voice-us",
                "name": "Warm Clinician",
                "preview_url": "https://samples/us.mp3",
                "category": "premade",
                "description": "Warm professional clinical narrator",
                "labels": {"accent": "american", "use_case": "narration"},
            },
            {
                "voice_id": "voice-uk",
                "name": "Measured British Expert",
                "preview_url": "https://samples/uk.mp3",
                "category": "premade",
                "description": "Measured authoritative expert narrator",
                "labels": {"accent": "british", "use_case": "narration"},
            },
            {
                "voice_id": "voice-alt-1",
                "name": "Backup One",
                "preview_url": "https://samples/alt1.mp3",
                "category": "premade",
                "description": "Calm clear explainer",
                "labels": {"accent": "american", "use_case": "educational"},
            },
            {
                "voice_id": "voice-alt-2",
                "name": "Backup Two",
                "preview_url": "https://samples/alt2.mp3",
                "category": "premade",
                "description": "Professional warm instructor",
                "labels": {"accent": "american", "use_case": "narration"},
            },
        ]

        result = MODULE.preview_voice_options(
            mode="description_driven_search",
            presentation_attributes={"content_type": "narrated-deck-video-export"},
            ideal_voice_description="British, measured, authoritative physician educator",
            style_defaults={"voice_selection_profile": "clinical-instructional"},
            client=client,
        )

        assert result["profile_name"] == "clinical-instructional"
        assert result["candidate_voices"][0]["voice_id"] == "voice-uk"

    def test_preview_voice_options_supports_description_led_recommendations(
        self, tmp_path: Path
    ) -> None:
        client = Mock()
        client.list_voices.return_value = [
            {
                "voice_id": "voice-a",
                "name": "Measured Clinician",
                "preview_url": "https://samples/a.mp3",
                "category": "premade",
                "description": "Measured authoritative clinical narrator",
                "labels": {"use_case": "educational"},
            },
            {
                "voice_id": "voice-b",
                "name": "Warm Professor",
                "preview_url": "https://samples/b.mp3",
                "category": "professional",
                "description": "Warm, articulate professor voice",
                "labels": {"accent": "American"},
            },
            {
                "voice_id": "voice-c",
                "name": "High Energy Host",
                "preview_url": "https://samples/c.mp3",
                "category": "generated",
                "description": "Energetic presenter voice",
                "labels": {"use_case": "presenter"},
            },
            {
                "voice_id": "voice-d",
                "name": "No Sample",
                "preview_url": "",
                "category": "premade",
                "description": "Would have matched but lacks preview",
                "labels": {"use_case": "educational"},
            },
        ]
        manifest_path = tmp_path / "segment-manifest.yaml"
        script_path = tmp_path / "narration-script.md"
        manifest_path.write_text("lesson_id: C1\nsegments: []\n", encoding="utf-8")
        script_path.write_text("# Script\n", encoding="utf-8")

        result = MODULE.preview_voice_options(
            mode="description_driven_search",
            presentation_attributes={"audience": "physicians"},
            ideal_voice_description="measured, authoritative, warm clinical educator",
            style_defaults={"default_voice_id": "voice-a"},
            locked_manifest_path=manifest_path,
            locked_script_path=script_path,
            client=client,
        )

        assert result["status"] == "selection_required"
        assert result["selection_mode"] == "description_recommendation"
        assert len(result["candidate_voices"]) == 3
        assert result["candidate_voices"][0]["voice_id"] == "voice-a"
        assert all(item["preview_url"] for item in result["candidate_voices"])
        assert all(item["source"] == "description_recommendation" for item in result["candidate_voices"])
        assert result["locked_manifest_hash"]
        assert result["locked_script_hash"]

    def test_finalize_voice_selection_requires_override_for_non_primary_choice(
        self, tmp_path: Path
    ) -> None:
        preview_receipt = tmp_path / "voice-preview-options.json"
        preview_receipt.write_text(
            """
{
  "status": "selection_required",
  "candidate_voices": [
    {"rank": 1, "voice_id": "voice-a", "name": "Primary"},
    {"rank": 2, "voice_id": "voice-b", "name": "Alternative"}
  ]
}
""".strip()
            + "\n",
            encoding="utf-8",
        )
        try:
            MODULE.finalize_voice_selection(
                preview_receipt,
                selected_voice_id="voice-b",
            )
        except ValueError as exc:
            assert "override_reason" in str(exc)
        else:  # pragma: no cover - defensive
            raise AssertionError("Expected override_reason guard for non-primary choice")

    def test_finalize_voice_selection_persists_operator_choice(
        self, tmp_path: Path
    ) -> None:
        preview_receipt = tmp_path / "voice-preview-options.json"
        preview_receipt.write_text(
            """
{
  "status": "selection_required",
  "candidate_voices": [
    {"rank": 1, "voice_id": "voice-a", "name": "Primary"},
    {"rank": 2, "voice_id": "voice-b", "name": "Alternative"}
  ]
}
""".strip()
            + "\n",
            encoding="utf-8",
        )
        decision_path = tmp_path / "voice-preview-decision.json"

        result = MODULE.finalize_voice_selection(
            preview_receipt,
            selected_voice_id="voice-a",
            output_path=decision_path,
            operator_notes="best fit",
        )

        assert result["status"] == "approved"
        assert result["selected_voice_id"] == "voice-a"
        assert decision_path.exists()

    def test_voice_preview_cli_writes_output_file(self, tmp_path: Path) -> None:
        output_path = tmp_path / "voice-preview.json"
        manifest_path = tmp_path / "segment-manifest.yaml"
        script_path = tmp_path / "narration-script.md"
        manifest_path.write_text("lesson_id: C1\nsegments: []\n", encoding="utf-8")
        script_path.write_text("# Script\n", encoding="utf-8")
        with patch.object(
            MODULE,
            "preview_voice_options",
            return_value={"status": "success", "candidate_voices": []},
        ):
            exit_code = MODULE.main(
                [
                    "voice-preview",
                    "--mode",
                    "default_plus_alternatives",
                    "--presentation-attributes-json",
                    '{"audience":"clinicians"}',
                    "--locked-manifest",
                    str(manifest_path),
                    "--locked-script",
                    str(script_path),
                    "--output-path",
                    str(output_path),
                ]
            )
        assert exit_code == 0


class TestNarrationFlow:
    def test_generate_narration_writes_vtt_and_returns_duration(
        self, tmp_path: Path
    ) -> None:
        client = Mock()
        client.text_to_speech_with_timestamps_file.return_value = {
            "request_id": "req-1",
            "output_format": "mp3_44100_128",
            "audio_path": str(tmp_path / "clip.mp3"),
            "alignment": {
                "characters": list("Hi"),
                "character_start_times_seconds": [0.0, 0.1],
                "character_end_times_seconds": [0.1, 0.2],
            },
        }
        with patch.object(
            MODULE,
            "load_style_guide_elevenlabs",
            return_value={"default_voice_id": "voice-a", "model_id": "m1"},
        ):
            result = MODULE.generate_narration(
                "Hi",
                output_dir=tmp_path,
                filename_stem="clip",
                client=client,
            )
        assert result["voice_id"] == "voice-a"
        assert result["narration_duration"] == 0.2
        assert (tmp_path / "clip.vtt").exists()
        client.text_to_speech_with_timestamps_file.assert_called_once()

    def test_generate_narration_requires_voice_id(self, tmp_path: Path) -> None:
        with patch.object(MODULE, "load_style_guide_elevenlabs", return_value={}):
            try:
                MODULE.generate_narration("Hi", output_dir=tmp_path, client=Mock())
            except ValueError as exc:
                assert "voice_id" in str(exc)
            else:  # pragma: no cover - defensive
                raise AssertionError("Expected ValueError for missing voice_id")

    def test_generate_manifest_narration_writes_back_outputs(
        self, tmp_path: Path
    ) -> None:
        manifest_path = tmp_path / "manifest.yaml"
        manifest_path.write_text(
            """
lesson_id: C1-M1-L1
segments:
  - id: seg-01
    narration_text: "Hello world"
    voice_id: null
    sfx: null
  - id: seg-02
    narration_text: ""
    voice_id: null
    sfx: null
""".strip()
            + "\n",
            encoding="utf-8",
        )

        def fake_generate_narration(*args, **kwargs):
            audio_dir = Path(kwargs["output_dir"])
            audio_dir.mkdir(parents=True, exist_ok=True)
            audio_path = audio_dir / "seg-01.mp3"
            vtt_path = audio_dir / "seg-01.vtt"
            audio_path.write_bytes(b"audio")
            vtt_path.write_text("WEBVTT\n\n", encoding="utf-8")
            return {
                "status": "success",
                "voice_id": "voice-a",
                "audio_path": str(audio_path),
                "vtt_path": str(vtt_path),
                "request_id": "req-1",
                "narration_duration": 1.5,
                "output_format": "mp3_44100_128",
            }

        with (
            patch.object(
                MODULE,
                "load_style_guide_elevenlabs",
                return_value={"default_voice_id": "voice-a"},
            ),
            patch.object(MODULE, "generate_narration", side_effect=fake_generate_narration),
        ):
            result = MODULE.generate_manifest_narration(manifest_path)

        saved = MODULE.load_manifest(manifest_path)
        first = saved["segments"][0]
        second = saved["segments"][1]
        assert result["status"] == "success"
        assert first["narration_duration"] == 1.5
        assert first["narration_file"].endswith("seg-01.mp3")
        assert first["narration_vtt"].endswith("seg-01.vtt")
        assert second["narration_duration"] == 0.0
        assert second["narration_file"] is None


class TestDictionaryAndBinaryFlows:
    def test_create_pronunciation_dictionary_writes_pls(self, tmp_path: Path) -> None:
        client = Mock()
        client.create_pronunciation_dictionary_from_file.return_value = {"id": "dict-1"}
        terms = {
            "resiliency": "rih-ZIL-ee-en-see",
            "tachycardia": "tak-ih-KAR-dee-uh",
            "bradycardia": "bray-dee-KAR-dee-uh",
            "hemodynamic": "hee-moh-dye-NAM-ik",
            "arrhythmia": "uh-RITH-mee-uh",
            "angiogenesis": "an-jee-oh-JEN-uh-sis",
            "myocardium": "my-oh-KAR-dee-um",
            "neuroplasticity": "nyur-oh-plas-TIS-ih-tee",
            "pathophysiology": "path-oh-fiz-ee-OL-oh-jee",
            "electrophysiology": "ee-lek-troh-fiz-ee-OL-oh-jee",
        }
        result = MODULE.create_pronunciation_dictionary(
            "medical",
            terms,
            output_dir=tmp_path,
            client=client,
        )
        assert (tmp_path / "medical.pls").exists()
        pls_content = (tmp_path / "medical.pls").read_text(encoding="utf-8")
        assert pls_content.count("<lexeme>") == 10
        assert result["id"] == "dict-1"

    def test_generate_sound_effect_returns_output_path(self, tmp_path: Path) -> None:
        client = Mock()
        result = MODULE.generate_sound_effect(
            "soft whoosh",
            output_dir=tmp_path,
            filename="whoosh.mp3",
            client=client,
        )
        assert result["sfx_path"].endswith("whoosh.mp3")
        client.text_to_sound_effect_file.assert_called_once()

    def test_generate_dialogue_returns_output_path(self, tmp_path: Path) -> None:
        client = Mock()
        result = MODULE.generate_dialogue(
            [{"text": "Hello", "voice_id": "voice-a"}],
            output_dir=tmp_path,
            filename="dialogue.mp3",
            client=client,
        )
        assert result["dialogue_path"].endswith("dialogue.mp3")
        client.text_to_dialogue_file.assert_called_once()

    def test_generate_music_returns_output_path(self, tmp_path: Path) -> None:
        client = Mock()
        result = MODULE.generate_music(
            output_dir=tmp_path,
            filename="music.mp3",
            client=client,
            prompt="reflective underscore",
        )
        assert result["music_path"].endswith("music.mp3")
        client.generate_music_file.assert_called_once()
