"""Tests for video sensory bridge."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from skills.sensory_bridges.scripts.video_to_agent import extract_video, _check_ffmpeg
from skills.sensory_bridges.scripts.bridge_utils import validate_response


class TestExtractVideo:
    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            extract_video("/nonexistent/file.mp4")

    @patch("skills.sensory_bridges.scripts.video_to_agent._check_ffmpeg", return_value=False)
    def test_no_ffmpeg_but_audio_works(self, mock_ffmpeg, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")

        mock_result = {
            "transcript_text": "Hello world",
            "total_duration_ms": 5000,
        }

        with patch("skills.sensory_bridges.scripts.audio_to_agent.transcribe_audio", return_value=mock_result):
            result = extract_video(f)

        assert result["confidence"] == "MEDIUM"
        assert "ffmpeg not available" in result["confidence_rationale"]
        assert result["audio_transcript"] == "Hello world"
        assert validate_response(result) == []

    @patch("skills.sensory_bridges.scripts.video_to_agent._check_ffmpeg", return_value=False)
    def test_nothing_works(self, mock_ffmpeg, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")

        with patch("skills.sensory_bridges.scripts.audio_to_agent.transcribe_audio", side_effect=Exception("STT failed")):
            result = extract_video(f)

        assert result["confidence"] == "LOW"
        assert validate_response(result) == []
