"""Video sensory bridge — keyframe extraction + audio transcription.

Uses ffmpeg for frame extraction and ElevenLabs Scribe v2 for audio
transcription (ElevenLabs STT accepts video files directly).
"""

from __future__ import annotations

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from skills.sensory_bridges.scripts.bridge_utils import build_response

logger = logging.getLogger(__name__)


def _check_ffmpeg() -> bool:
    """Check if ffmpeg is available on the system."""
    return shutil.which("ffmpeg") is not None


def _extract_keyframes(
    video_path: Path,
    output_dir: Path,
    max_frames: int = 30,
) -> list[dict[str, Any]]:
    """Extract keyframes from video using ffmpeg scene detection."""
    output_pattern = str(output_dir / "frame_%04d.png")

    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", f"select='gt(scene,0.3)',showinfo",
        "-vsync", "vfr",
        "-frames:v", str(max_frames),
        output_pattern,
        "-y", "-loglevel", "warning",
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        logger.warning("ffmpeg keyframe extraction failed: %s", e)
        return []

    frames = sorted(output_dir.glob("frame_*.png"))
    return [
        {"frame_index": i, "frame_path": str(f), "timestamp_ms": None}
        for i, f in enumerate(frames)
    ]


def extract_video(
    artifact_path: str | Path,
    gate: str = "G6",
    **kwargs: Any,
) -> dict[str, Any]:
    """Extract keyframes and transcribe audio from a video file.

    Args:
        artifact_path: Path to the video file (.mp4, .webm, etc.).
        gate: Production gate identifier.

    Returns:
        Canonical perception response with keyframes and audio transcript.
    """
    path = Path(artifact_path)
    if not path.exists():
        raise FileNotFoundError(f"Video file not found: {path}")

    keyframes: list[dict[str, Any]] = []
    audio_transcript = ""
    total_duration_ms = 0
    issues: list[str] = []

    if _check_ffmpeg():
        with tempfile.TemporaryDirectory(prefix="sensory_bridge_") as tmpdir:
            keyframes = _extract_keyframes(path, Path(tmpdir))
            if not keyframes:
                issues.append("No keyframes extracted (scene detection may have found no transitions)")
    else:
        issues.append("ffmpeg not available — keyframe extraction skipped")

    try:
        from skills.sensory_bridges.scripts.audio_to_agent import transcribe_audio
        audio_result = transcribe_audio(str(path), gate=gate)
        audio_transcript = audio_result.get("transcript_text", "")
        total_duration_ms = audio_result.get("total_duration_ms", 0)
    except Exception as e:
        issues.append(f"Audio transcription failed: {e}")

    if not keyframes and not audio_transcript:
        confidence = "LOW"
        rationale = f"Neither keyframes nor audio transcript produced. Issues: {'; '.join(issues)}"
    elif issues:
        confidence = "MEDIUM"
        rationale = f"Partial extraction. Issues: {'; '.join(issues)}"
    else:
        confidence = "HIGH"
        rationale = f"{len(keyframes)} keyframes extracted, audio transcribed ({len(audio_transcript)} chars)"

    return build_response(
        modality="video",
        artifact_path=path,
        confidence=confidence,
        confidence_rationale=rationale,
        keyframes=keyframes,
        audio_transcript=audio_transcript,
        total_duration_ms=total_duration_ms,
        scene_changes=len(keyframes),
    )
