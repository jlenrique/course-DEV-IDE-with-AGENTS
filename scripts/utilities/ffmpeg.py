"""Shared ffmpeg executable resolution for media-processing scripts."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def resolve_ffmpeg_binary(explicit_path: str | None = None) -> str:
    """Resolve ffmpeg from explicit input, env, bundled, PATH, or imageio-ffmpeg."""
    candidate = explicit_path or os.environ.get("FFMPEG_BINARY")
    if candidate:
        return candidate

    # Check bundled binary
    here = Path(__file__).resolve()
    project_root = here.parents[2]

    # Check bundled binary
    bundled = project_root / "bin" / "ffmpeg.exe"
    if bundled.is_file():
        return str(bundled)

    # Check venv local installs (Windows/Linux)
    venv_ffmpeg_candidates = [
        project_root / ".venv" / "Scripts" / "ffmpeg.exe",
        project_root / ".venv" / "bin" / "ffmpeg",
    ]
    for cand in venv_ffmpeg_candidates:
        if cand.is_file():
            return str(cand)

    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path

    try:
        from imageio_ffmpeg import get_ffmpeg_exe
    except ModuleNotFoundError as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError(
            "ffmpeg is not available. Install imageio-ffmpeg, provide FFMPEG_BINARY, or place bundled ffmpeg.exe in bin/."
        ) from exc

    return str(get_ffmpeg_exe())
