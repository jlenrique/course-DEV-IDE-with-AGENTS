from __future__ import annotations

import types
from unittest.mock import patch

import pytest

from scripts.utilities.ffmpeg import resolve_ffmpeg_binary


def test_explicit_path_wins() -> None:
    assert resolve_ffmpeg_binary("C:/tools/ffmpeg.exe") == "C:/tools/ffmpeg.exe"


def test_env_var_used_when_explicit_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FFMPEG_BINARY", "C:/env/ffmpeg.exe")
    assert resolve_ffmpeg_binary() == "C:/env/ffmpeg.exe"


@patch("scripts.utilities.ffmpeg.shutil.which", return_value="C:/path/ffmpeg.exe")
def test_path_used_when_env_missing(mock_which) -> None:
    assert resolve_ffmpeg_binary() == "C:/path/ffmpeg.exe"
    mock_which.assert_called_once_with("ffmpeg")


@patch("scripts.utilities.ffmpeg.shutil.which", return_value="C:/path/ffmpeg.exe")
def test_repo_local_binary_wins_before_path(
    mock_which, tmp_path, monkeypatch: pytest.MonkeyPatch
) -> None:
    local_binary = tmp_path / ".venv" / "Scripts" / "ffmpeg.exe"
    local_binary.parent.mkdir(parents=True, exist_ok=True)
    local_binary.write_text("stub", encoding="utf-8")

    monkeypatch.setattr(
        "scripts.utilities.ffmpeg._repo_local_ffmpeg_candidates",
        lambda _root: (local_binary,),
    )

    assert resolve_ffmpeg_binary() == str(local_binary)
    mock_which.assert_not_called()


@patch("scripts.utilities.ffmpeg.shutil.which", return_value=None)
def test_imageio_fallback_used_when_path_missing(mock_which) -> None:
    fake_module = types.SimpleNamespace(get_ffmpeg_exe=lambda: "C:/venv/ffmpeg.exe")
    with patch.dict("sys.modules", {"imageio_ffmpeg": fake_module}):
        assert resolve_ffmpeg_binary() == "C:/venv/ffmpeg.exe"
    mock_which.assert_called_once_with("ffmpeg")


@patch("scripts.utilities.ffmpeg.shutil.which", return_value=None)
def test_resolver_raises_when_no_sources_available(mock_which) -> None:
    with patch.dict("sys.modules", {"imageio_ffmpeg": None}), pytest.raises(
        RuntimeError, match="ffmpeg is not available"
    ):
        resolve_ffmpeg_binary()
    mock_which.assert_called_once_with("ffmpeg")
