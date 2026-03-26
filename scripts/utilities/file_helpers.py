"""File system helpers for path resolution and safe I/O operations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def project_root() -> Path:
    """Return the repository root directory.

    Resolves by walking up from this file's location to find the directory
    containing `pyproject.toml`.
    """
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parent.parent.parent


def resolve_path(*parts: str) -> Path:
    """Resolve a path relative to the project root.

    Args:
        *parts: Path segments relative to project root.

    Returns:
        Resolved absolute Path.
    """
    return project_root() / Path(*parts)


def safe_read_json(path: str | Path) -> dict[str, Any] | list[Any]:
    """Read and parse a JSON file with clear error messages.

    Args:
        path: Path to the JSON file.

    Returns:
        Parsed JSON content.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the content is not valid JSON.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def safe_write_json(path: str | Path, data: Any, indent: int = 2) -> None:
    """Write data as formatted JSON, creating parent directories as needed.

    Args:
        path: Destination file path.
        data: Serializable data to write.
        indent: JSON indentation level.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")
