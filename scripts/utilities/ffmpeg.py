"""Shared ffmpeg executable resolution for media-processing scripts."""

from __future__ import annotations

import os
import shutil


def resolve_ffmpeg_binary(explicit_path: str | None = None) -> str:
    """Resolve ffmpeg from explicit input, env, bundled, PATH, or imageio-ffmpeg."""
    candidate = explicit_path or os.environ.get("FFMPEG_BINARY")
    if candidate:
        return candidate

    # Check bundled binary
    bundled = os.path.join(os.path.dirname(__file__), "..", "..", "bin", "ffmpeg.exe")
    if os.path.isfile(bundled):
        return bundled

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
