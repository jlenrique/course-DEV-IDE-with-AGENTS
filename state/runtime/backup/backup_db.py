"""Backup the coordination database with a timestamped copy.

Usage:
    python -m state.runtime.backup.backup_db
    python state/runtime/backup/backup_db.py
"""

from __future__ import annotations

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


def backup(
    db_path: str | Path | None = None,
    backup_dir: str | Path | None = None,
) -> Path:
    """Create a timestamped backup of the coordination database.

    Args:
        db_path: Source database path. Defaults to ``state/runtime/coordination.db``.
        backup_dir: Target directory. Defaults to ``state/runtime/backup/``.

    Returns:
        Path to the created backup file.

    Raises:
        FileNotFoundError: If the source database does not exist.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    if db_path is None:
        db_path = repo_root / "state" / "runtime" / "coordination.db"
    db_path = Path(db_path)

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    if backup_dir is None:
        backup_dir = db_path.parent / "backup"
    backup_dir = Path(backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"coordination_{timestamp}.db"

    shutil.copy2(str(db_path), str(backup_path))
    return backup_path


if __name__ == "__main__":
    try:
        path = backup()
        print(f"Backup created: {path}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
