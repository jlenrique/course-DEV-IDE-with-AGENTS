"""Restore the coordination database from a backup.

Usage:
    python state/runtime/backup/restore_db.py <backup_file>
    python state/runtime/backup/restore_db.py --latest
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path


def restore(
    backup_path: str | Path,
    db_path: str | Path | None = None,
) -> Path:
    """Restore the coordination database from a backup file.

    Args:
        backup_path: Path to the backup file to restore.
        db_path: Target database path. Defaults to ``state/runtime/coordination.db``.

    Returns:
        Path to the restored database.

    Raises:
        FileNotFoundError: If the backup file does not exist.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    backup_path = Path(backup_path)

    if not backup_path.exists():
        raise FileNotFoundError(f"Backup not found: {backup_path}")

    if db_path is None:
        db_path = repo_root / "state" / "runtime" / "coordination.db"
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    shutil.copy2(str(backup_path), str(db_path))
    return db_path


def find_latest_backup(backup_dir: str | Path | None = None) -> Path:
    """Find the most recent backup file by filename timestamp.

    Args:
        backup_dir: Directory to search. Defaults to ``state/runtime/backup/``.

    Returns:
        Path to the latest backup.

    Raises:
        FileNotFoundError: If no backups exist.
    """
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    if backup_dir is None:
        backup_dir = repo_root / "state" / "runtime" / "backup"
    backup_dir = Path(backup_dir)

    backups = sorted(backup_dir.glob("coordination_*.db"), reverse=True)
    if not backups:
        raise FileNotFoundError(f"No backups found in {backup_dir}")
    return backups[0]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: restore_db.py <backup_file> | --latest", file=sys.stderr)
        sys.exit(1)

    try:
        if sys.argv[1] == "--latest":
            source = find_latest_backup()
            print(f"Restoring from latest backup: {source.name}")
        else:
            source = Path(sys.argv[1])

        result = restore(source)
        print(f"Database restored to: {result}")
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
