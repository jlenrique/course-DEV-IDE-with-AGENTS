"""Fail if known UTF-8/CP1252 mojibake sequences appear in high-churn spec artifacts."""
from __future__ import annotations

from pathlib import Path

from scripts.utilities.normalize_mojibake import KNOWN_MOJIBAKE_SEQUENCES

_ROOT = Path(__file__).resolve().parents[2]
_ARTIFACTS = _ROOT / "_bmad-output" / "implementation-artifacts"
_BAD = tuple(bad for bad, _ in KNOWN_MOJIBAKE_SEQUENCES)


def _iter_artifact_text_files() -> list[Path]:
    if not _ARTIFACTS.is_dir():
        return []
    return [
        p
        for p in _ARTIFACTS.rglob("*")
        if p.is_file() and p.suffix in {".md", ".yaml", ".yml", ".txt"}
    ]


def test_artifact_tree_has_no_known_mojibake_sequences() -> None:
    for path in _iter_artifact_text_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        for bad in _BAD:
            assert bad not in text, (
                f"Mojibake sequence {bad!r} in {path} — run scripts/utilities/normalize_mojibake.py"
            )
