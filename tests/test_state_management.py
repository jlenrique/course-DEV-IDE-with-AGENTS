"""Validation tests for Story 1.3: State Management Infrastructure.

Verifies YAML config templates, SQLite schema, BMad memory sidecars,
and backup/restore operations.
"""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path

import pytest
import yaml

from scripts.utilities.file_helpers import project_root

ROOT = project_root()


# ---------------------------------------------------------------------------
# AC #1: Course Context YAML
# ---------------------------------------------------------------------------


class TestCourseContext:
    def test_file_exists(self):
        assert (ROOT / "state/config/course_context.yaml").exists()

    def test_parses_valid_yaml(self):
        data = yaml.safe_load(
            (ROOT / "state/config/course_context.yaml").read_text(encoding="utf-8")
        )
        assert isinstance(data, dict)

    def test_has_course_structure(self):
        data = yaml.safe_load(
            (ROOT / "state/config/course_context.yaml").read_text(encoding="utf-8")
        )
        course = data["course"]
        for key in ["name", "description", "learning_objectives", "modules"]:
            assert key in course, f"Missing key: course.{key}"


# ---------------------------------------------------------------------------
# AC #2: Style Guide YAML
# ---------------------------------------------------------------------------


class TestStyleGuide:
    def test_file_exists(self):
        assert (ROOT / "state/config/style_guide.yaml").exists()

    def test_parses_valid_yaml(self):
        data = yaml.safe_load(
            (ROOT / "state/config/style_guide.yaml").read_text(encoding="utf-8")
        )
        assert isinstance(data, dict)

    def test_has_brand_section(self):
        data = yaml.safe_load(
            (ROOT / "state/config/style_guide.yaml").read_text(encoding="utf-8")
        )
        assert "brand" in data
        assert "colors" in data["brand"]
        assert "fonts" in data["brand"]

    def test_has_tool_parameter_sections(self):
        data = yaml.safe_load(
            (ROOT / "state/config/style_guide.yaml").read_text(encoding="utf-8")
        )
        params = data["tool_parameters"]
        for tool in ["gamma", "elevenlabs", "canvas", "qualtrics"]:
            assert tool in params, f"Missing tool_parameters.{tool}"


# ---------------------------------------------------------------------------
# AC #3: Tool Policies YAML
# ---------------------------------------------------------------------------


class TestToolPolicies:
    def test_file_exists(self):
        assert (ROOT / "state/config/tool_policies.yaml").exists()

    def test_parses_valid_yaml(self):
        data = yaml.safe_load(
            (ROOT / "state/config/tool_policies.yaml").read_text(encoding="utf-8")
        )
        assert isinstance(data, dict)

    def test_has_run_presets(self):
        data = yaml.safe_load(
            (ROOT / "state/config/tool_policies.yaml").read_text(encoding="utf-8")
        )
        presets = data["run_presets"]
        for preset in ["explore", "draft", "production", "regulated"]:
            assert preset in presets, f"Missing run_presets.{preset}"

    def test_has_quality_gates(self):
        data = yaml.safe_load(
            (ROOT / "state/config/tool_policies.yaml").read_text(encoding="utf-8")
        )
        assert "quality_gates" in data

    def test_has_retry_policy(self):
        data = yaml.safe_load(
            (ROOT / "state/config/tool_policies.yaml").read_text(encoding="utf-8")
        )
        retry = data["retry_policy"]
        assert retry["max_attempts"] == 3
        assert retry["backoff_delays_seconds"] == [2, 4, 8]


# ---------------------------------------------------------------------------
# AC #4: SQLite Database
# ---------------------------------------------------------------------------


class TestSQLiteDatabase:
    def test_init_creates_database(self):
        from scripts.state_management.db_init import init_database

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test_coord.db"
            result = init_database(db_path)
            assert result.exists()

    def test_production_runs_table(self):
        from scripts.state_management.db_init import init_database

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            init_database(db_path)
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("PRAGMA table_info(production_runs)")
            columns = {row[1] for row in cursor.fetchall()}
            conn.close()

            for col in ["run_id", "purpose", "status", "preset", "context_json"]:
                assert col in columns, f"Missing column: production_runs.{col}"

    def test_agent_coordination_table(self):
        from scripts.state_management.db_init import init_database

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            init_database(db_path)
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("PRAGMA table_info(agent_coordination)")
            columns = {row[1] for row in cursor.fetchall()}
            conn.close()

            for col in ["event_id", "run_id", "agent_name", "action", "payload_json"]:
                assert col in columns, f"Missing column: agent_coordination.{col}"

    def test_quality_gates_table(self):
        from scripts.state_management.db_init import init_database

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            init_database(db_path)
            conn = sqlite3.connect(str(db_path))
            cursor = conn.execute("PRAGMA table_info(quality_gates)")
            columns = {row[1] for row in cursor.fetchall()}
            conn.close()

            for col in ["gate_id", "run_id", "stage", "status", "findings_json"]:
                assert col in columns, f"Missing column: quality_gates.{col}"

    def test_insert_and_query(self):
        from scripts.state_management.db_init import init_database

        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "test.db"
            init_database(db_path)
            conn = sqlite3.connect(str(db_path))
            conn.execute(
                "INSERT INTO production_runs (run_id, purpose, status) VALUES (?, ?, ?)",
                ("test-001", "Unit test run", "pending"),
            )
            conn.commit()
            row = conn.execute(
                "SELECT purpose FROM production_runs WHERE run_id = ?", ("test-001",)
            ).fetchone()
            conn.close()
            assert row[0] == "Unit test run"


# ---------------------------------------------------------------------------
# AC #5: BMad Memory Sidecar Directories
# ---------------------------------------------------------------------------


class TestBMadMemorySidecars:
    SIDECARS = [
        "master-orchestrator-sidecar",
        "gamma-specialist-sidecar",
        "elevenlabs-specialist-sidecar",
        "canvas-specialist-sidecar",
        "quality-reviewer-sidecar",
    ]

    def test_memory_directory_exists(self):
        assert (ROOT / "_bmad/memory").is_dir()

    @pytest.mark.parametrize("sidecar", SIDECARS)
    def test_sidecar_directory_exists(self, sidecar: str):
        assert (ROOT / "_bmad/memory" / sidecar).is_dir()

    @pytest.mark.parametrize("sidecar", SIDECARS)
    def test_sidecar_has_index_md(self, sidecar: str):
        index = ROOT / "_bmad/memory" / sidecar / "index.md"
        assert index.exists()
        content = index.read_text(encoding="utf-8")
        assert len(content) > 10, "index.md should have meaningful content"


# ---------------------------------------------------------------------------
# AC #6: Backup / Restore
# ---------------------------------------------------------------------------


class TestBackupRestore:
    def test_backup_creates_timestamped_copy(self):
        from scripts.state_management.db_init import init_database
        from state.runtime.backup.backup_db import backup

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            db_path = tmp_path / "coordination.db"
            backup_dir = tmp_path / "backups"

            init_database(db_path)
            result = backup(db_path=db_path, backup_dir=backup_dir)

            assert result.exists()
            assert result.name.startswith("coordination_")
            assert result.suffix == ".db"

    def test_backup_missing_db_raises(self):
        from state.runtime.backup.backup_db import backup

        with pytest.raises(FileNotFoundError):
            backup(db_path="/nonexistent/coordination.db")

    def test_restore_from_backup(self):
        from scripts.state_management.db_init import init_database
        from state.runtime.backup.backup_db import backup
        from state.runtime.backup.restore_db import restore

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            db_path = tmp_path / "coordination.db"
            backup_dir = tmp_path / "backups"
            restore_target = tmp_path / "restored.db"

            init_database(db_path)

            conn = sqlite3.connect(str(db_path))
            conn.execute(
                "INSERT INTO production_runs (run_id, purpose, status) VALUES (?, ?, ?)",
                ("backup-test", "Backup test", "pending"),
            )
            conn.commit()
            conn.close()

            backup_path = backup(db_path=db_path, backup_dir=backup_dir)
            restore(backup_path, db_path=restore_target)

            conn = sqlite3.connect(str(restore_target))
            row = conn.execute(
                "SELECT purpose FROM production_runs WHERE run_id = ?",
                ("backup-test",),
            ).fetchone()
            conn.close()
            assert row[0] == "Backup test"

    def test_find_latest_backup(self):
        from scripts.state_management.db_init import init_database
        from state.runtime.backup.backup_db import backup
        from state.runtime.backup.restore_db import find_latest_backup

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            db_path = tmp_path / "coordination.db"
            backup_dir = tmp_path / "backups"

            init_database(db_path)
            backup(db_path=db_path, backup_dir=backup_dir)

            latest = find_latest_backup(backup_dir=backup_dir)
            assert latest.exists()
            assert latest.name.startswith("coordination_")


# ---------------------------------------------------------------------------
# Gitignore verification
# ---------------------------------------------------------------------------


class TestGitignore:
    def test_gitignore_excludes_sqlite(self):
        content = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert "state/runtime/*.db" in content
