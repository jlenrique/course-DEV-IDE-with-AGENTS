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
