"""State management infrastructure for agent coordination.

Provides SQLite database initialization, YAML config helpers,
and backup/restore operations for the runtime coordination state.
"""

from scripts.state_management.db_init import DB_PATH, init_database

__all__ = ["DB_PATH", "init_database"]
