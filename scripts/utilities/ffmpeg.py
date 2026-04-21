"""Canonical repo-local ffmpeg executable resolution.

All repo scripts that invoke ``ffmpeg`` should resolve the executable
through this module first rather than guessing from ``PATH``. This keeps
bundled binaries, ``.venv`` installs, and imageio-managed binaries
discoverable in the same order everywhere.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _repo_local_ffmpeg_candidates(project_root: Path) -> tuple[Path, ...]:
    return (
        project_root / "bin" / "ffmpeg.exe",
        project_root / ".venv" / "Scripts" / "ffmpeg.exe",
        project_root / ".venv" / "bin" / "ffmpeg",
    )


def resolve_ffmpeg_binary(explicit_path: str | None = None) -> str:
    """Resolve ffmpeg from explicit input, env, bundled, PATH, or imageio-ffmpeg."""
    candidate = explicit_path or os.environ.get("FFMPEG_BINARY")
    if candidate:
        return candidate

    project_root = _project_root()
    for cand in _repo_local_ffmpeg_candidates(project_root):
        if cand.is_file():
            return str(cand)

    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path

    try:
        from imageio_ffmpeg import get_ffmpeg_exe
    except ModuleNotFoundError as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError(
            "ffmpeg is not available. Install imageio-ffmpeg, provide "
            "FFMPEG_BINARY, or place bundled ffmpeg.exe in bin/."
        ) from exc

    return str(get_ffmpeg_exe())
