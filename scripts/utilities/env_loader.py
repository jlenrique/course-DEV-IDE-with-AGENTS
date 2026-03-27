"""Environment variable loading from .env files.

Provides Python-native .env loading complementing the Node.js
load_env.cjs used by MCP wrapper scripts.
"""

from __future__ import annotations

import os
from pathlib import Path

from scripts.utilities.file_helpers import project_root


def load_env(env_path: str | Path | None = None) -> dict[str, str]:
    """Load environment variables from a .env file.

    Variables are set in ``os.environ`` only if not already present,
    matching the behavior of ``python-dotenv`` and the Node.js
    ``scripts/lib/load_env.cjs``.

    Args:
        env_path: Path to .env file. Defaults to ``{project_root}/.env``.

    Returns:
        Dict of key-value pairs that were loaded.

    Raises:
        FileNotFoundError: If the .env file does not exist.
    """
    if env_path is None:
        env_path = project_root() / ".env"
    env_path = Path(env_path)

    if not env_path.exists():
        raise FileNotFoundError(
            f"Missing .env file at {env_path}. "
            "Create `.env` at the project root and add your API keys "
            "(see docs/admin-guide.md — API Keys and Credentials)."
        )

    loaded: dict[str, str] = {}
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        eq_idx = line.find("=")
        if eq_idx == -1:
            continue
        key = line[:eq_idx].strip()
        value = line[eq_idx + 1 :].strip()
        if value and key not in os.environ:
            os.environ[key] = value
            loaded[key] = value

    return loaded
