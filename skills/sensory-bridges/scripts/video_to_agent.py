"""Video sensory bridge - keyframe extraction + audio transcription.

Uses ffmpeg for frame extraction and ElevenLabs Scribe v2 for audio
transcription (ElevenLabs STT accepts video files directly).
"""

from __future__ import annotations

import importlib.util
import logging
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    from scripts.utilities.ffmpeg import resolve_ffmpeg_binary
except ModuleNotFoundError:  # pragma: no cover - direct file import fallback
    REPO_ROOT = Path(__file__).resolve().parents[3]
    ffmpeg_module_path = REPO_ROOT / "scripts" / "utilities" / "ffmpeg.py"
    spec = importlib.util.spec_from_file_location("repo_shared_ffmpeg", ffmpeg_module_path)
    if spec is None or spec.loader is None:
        raise
    ffmpeg_module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault("repo_shared_ffmpeg", ffmpeg_module)
    spec.loader.exec_module(ffmpeg_module)
    resolve_ffmpeg_binary = ffmpeg_module.resolve_ffmpeg_binary
from skills.sensory_bridges.scripts.bridge_utils import build_response

logger = logging.getLogger(__name__)


def _check_ffmpeg() -> bool:
    """Check if ffmpeg is resolvable in the current environment."""
    try:
        resolve_ffmpeg_binary()
    except RuntimeError:
        return False
    return True


def _extract_keyframes(
    video_path: Path,
    output_dir: Path,
    max_frames: int = 30,
    ffmpeg_binary: str | None = None,
) -> list[dict[str, Any]]:
    """Extract keyframes from video using scene detection with fps fallback."""
    ffmpeg = resolve_ffmpeg_binary(ffmpeg_binary)

    def _run_extract(filter_graph: str) -> list[Path]:
        output_pattern = str(output_dir / "frame_%04d.png")
        for existing in output_dir.glob("frame_*.png"):
            existing.unlink()

        cmd = [
            ffmpeg,
            "-i",
            str(video_path),
            "-vf",
            filter_graph,
            "-vsync",
            "vfr",
            "-frames:v",
            str(max_frames),
            output_pattern,
            "-y",
            "-loglevel",
            "warning",
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=120)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            logger.warning("ffmpeg keyframe extraction failed: %s", exc)
            return []

        return sorted(output_dir.glob("frame_*.png"))

    frames = _run_extract("select='gt(scene,0.3)',showinfo")
    if not frames:
        frames = _run_extract("fps=1")

    return [
        {"frame_index": i, "frame_path": str(frame), "timestamp_ms": None}
        for i, frame in enumerate(frames)
    ]


def _classify_temporal_event_density(
    *,
    keyframes: list[dict[str, Any]],
    total_duration_ms: int,
    audio_transcript: str,
) -> tuple[str, str]:
    """Summarize how much visual change the narrator may need to track."""
    duration_seconds = max(total_duration_ms / 1000.0, 0.0)
    keyframe_count = len(keyframes)
    events_per_10_seconds = 0.0
    if duration_seconds > 0:
        events_per_10_seconds = (keyframe_count / duration_seconds) * 10.0

    transcript_words = len(audio_transcript.split())
    score = 0
    if keyframe_count >= 3:
        score += 1
    if keyframe_count >= 7:
        score += 1
    if events_per_10_seconds >= 1.5:
        score += 1
    if events_per_10_seconds >= 3.0:
        score += 1
    if transcript_words >= 40 and keyframe_count <= 2:
        score -= 1

    if score <= 1:
        level = "low"
    elif score <= 3:
        level = "moderate"
    else:
        level = "high"

    summary = (
        f"{level.title()} temporal event density: {keyframe_count} keyframe(s)"
        + (f" across {duration_seconds:.1f}s" if duration_seconds > 0 else "")
        + ". "
    )
    if duration_seconds > 0:
        summary += f"Approximate event pace is {events_per_10_seconds:.1f} key moments per 10 seconds. "
    if level == "low":
        summary += "Narration can stay concept-led because the clip appears visually steady."
    elif level == "moderate":
        summary += "Narration should track the main transitions without calling every frame."
    else:
        summary += "Narration should stay tightly aligned to visible changes because the clip evolves quickly."

    return level, summary


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

    ffmpeg_binary: str | None = None
    try:
        ffmpeg_binary = resolve_ffmpeg_binary()
    except RuntimeError:
        issues.append("ffmpeg not available - keyframe extraction skipped")

    if ffmpeg_binary:
        with tempfile.TemporaryDirectory(prefix="sensory_bridge_") as tmpdir:
            keyframes = _extract_keyframes(path, Path(tmpdir), ffmpeg_binary=ffmpeg_binary)
            if not keyframes:
                issues.append("No keyframes extracted (scene detection may have found no transitions)")

    try:
        from skills.sensory_bridges.scripts.audio_to_agent import transcribe_audio

        audio_result = transcribe_audio(str(path), gate=gate)
        audio_transcript = audio_result.get("transcript_text", "")
        total_duration_ms = audio_result.get("total_duration_ms", 0)
    except Exception as exc:
        issues.append(f"Audio transcription failed: {exc}")

    if not keyframes and not audio_transcript:
        confidence = "LOW"
        rationale = f"Neither keyframes nor audio transcript produced. Issues: {'; '.join(issues)}"
    elif issues:
        confidence = "MEDIUM"
        rationale = f"Partial extraction. Issues: {'; '.join(issues)}"
    else:
        confidence = "HIGH"
        rationale = f"{len(keyframes)} keyframes extracted, audio transcribed ({len(audio_transcript)} chars)"

    density_level, density_summary = _classify_temporal_event_density(
        keyframes=keyframes,
        total_duration_ms=total_duration_ms,
        audio_transcript=audio_transcript,
    )

    return build_response(
        modality="video",
        artifact_path=path,
        confidence=confidence,
        confidence_rationale=rationale,
        keyframes=keyframes,
        audio_transcript=audio_transcript,
        total_duration_ms=total_duration_ms,
        scene_changes=len(keyframes),
        temporal_event_density_level=density_level,
        temporal_event_density_summary=density_summary,
    )
