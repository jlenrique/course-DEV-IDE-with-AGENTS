"""Shared workflow-policy loading for generated packs and runtime helpers.

Canonical home for prompt-pack timing and cache-window knobs that need
deterministic defaults even when ``state/config/workflow-policy.yaml`` has
not been authored yet.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - declared project dependency
    yaml = None  # type: ignore[assignment]

from scripts.utilities.file_helpers import project_root

DEFAULT_WORKFLOW_POLICY = {
    "poll_min_open_minutes": 3,
    "poll_auto_close_minutes": 15,
    "session_receipt_max_age_minutes": 60,
}
WORKFLOW_POLICY_PATH = Path("state/config/workflow-policy.yaml")


def _coerce_positive_int(
    payload: dict[str, Any],
    key: str,
    *,
    fallback: int,
) -> int:
    value = payload.get(key, fallback)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return fallback
    return value


def load_workflow_policy(root: Path | None = None) -> dict[str, int]:
    """Return workflow policy with defaults filled for missing/invalid values."""
    repo_root = root or project_root()
    path = repo_root / WORKFLOW_POLICY_PATH

    raw: dict[str, Any] = {}
    if path.is_file() and yaml is not None:
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            loaded = None
        if isinstance(loaded, dict):
            raw = loaded

    return {
        key: _coerce_positive_int(raw, key, fallback=value)
        for key, value in DEFAULT_WORKFLOW_POLICY.items()
    }
