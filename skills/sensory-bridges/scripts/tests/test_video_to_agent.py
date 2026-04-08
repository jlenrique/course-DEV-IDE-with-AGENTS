"""Tests for video sensory bridge."""

import types
from pathlib import Path
import pytest
from unittest.mock import patch

from skills.sensory_bridges.scripts.video_to_agent import (
    _check_ffmpeg,
    _extract_keyframes,
    extract_video,
    resolve_ffmpeg_binary,
)
from skills.sensory_bridges.scripts.bridge_utils import validate_response


class TestFfmpegResolution:
    @patch("skills.sensory_bridges.scripts.video_to_agent.shutil.which", return_value=None)
    def test_resolve_ffmpeg_binary_falls_back_to_imageio(self, mock_which):
        fake_module = types.SimpleNamespace(get_ffmpeg_exe=lambda: "C:/venv/ffmpeg.exe")
        with patch.dict("sys.modules", {"imageio_ffmpeg": fake_module}):
            assert resolve_ffmpeg_binary() == "C:/venv/ffmpeg.exe"
        mock_which.assert_called_once_with("ffmpeg")

    @patch(
        "skills.sensory_bridges.scripts.video_to_agent.resolve_ffmpeg_binary",
        side_effect=RuntimeError("missing"),
    )
    def test_check_ffmpeg_false_when_unresolvable(self, mock_resolve):
        assert _check_ffmpeg() is False
        mock_resolve.assert_called_once_with()

    @patch("skills.sensory_bridges.scripts.video_to_agent.resolve_ffmpeg_binary", return_value="ffmpeg-bin")
    def test_extract_keyframes_falls_back_to_fps_sampling(self, mock_resolve, tmp_path):
        video = tmp_path / "clip.mp4"
        video.write_bytes(b"\x00")
        output_dir = tmp_path / "frames"
        output_dir.mkdir()

        def fake_run(cmd, check, capture_output, timeout):
            output_pattern = cmd[-4]
            filter_graph = cmd[4]
            if filter_graph == "fps=1":
                frame_path = Path(output_pattern.replace("%04d", "0001"))
                frame_path.write_bytes(b"png")

        with patch("skills.sensory_bridges.scripts.video_to_agent.subprocess.run", side_effect=fake_run):
            frames = _extract_keyframes(video, output_dir, ffmpeg_binary="ffmpeg-bin")

        assert len(frames) == 1
        assert frames[0]["frame_path"].endswith("frame_0001.png")
        mock_resolve.assert_called()


class TestExtractVideo:
    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            extract_video("/nonexistent/file.mp4")

    @patch(
        "skills.sensory_bridges.scripts.video_to_agent.resolve_ffmpeg_binary",
        side_effect=RuntimeError("missing"),
    )
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

    @patch(
        "skills.sensory_bridges.scripts.video_to_agent.resolve_ffmpeg_binary",
        side_effect=RuntimeError("missing"),
    )
    def test_nothing_works(self, mock_ffmpeg, tmp_path):
        f = tmp_path / "test.mp4"
        f.write_bytes(b"\x00")

        with patch("skills.sensory_bridges.scripts.audio_to_agent.transcribe_audio", side_effect=Exception("STT failed")):
            result = extract_video(f)

        assert result["confidence"] == "LOW"
        assert validate_response(result) == []
