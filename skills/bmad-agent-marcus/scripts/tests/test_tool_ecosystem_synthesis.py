"""Tests for tool_ecosystem_synthesis.py (Story G.2)."""

from __future__ import annotations

import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "tool_ecosystem_synthesis.py"
SPEC = importlib.util.spec_from_file_location("tool_ecosystem_synthesis", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class TestToolEcosystemSynthesis(unittest.TestCase):
    def test_generate_synthesis_report_aggregates_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            gamma_doc = root / "skills" / "gamma-api-mastery" / "references" / "doc-sources.yaml"
            gamma_doc.parent.mkdir(parents=True, exist_ok=True)
            gamma_doc.write_text(
                """
                tool: gamma
                agent: bmad-agent-gamma
                doc_sources:
                  - name: Gamma docs
                    url: https://example.com/gamma
                last_refreshed: null
                refresh_notes: null
                """,
                encoding="utf-8",
            )

            eleven_doc = root / "skills" / "elevenlabs-audio" / "references" / "doc-sources.yaml"
            eleven_doc.parent.mkdir(parents=True, exist_ok=True)
            eleven_doc.write_text(
                """
                tool: elevenlabs
                agent: bmad-agent-elevenlabs
                doc_sources:
                  - name: ElevenLabs docs
                    url: https://example.com/elevenlabs
                last_refreshed: "2026-03-29T00:00:00+00:00"
                refresh_notes: validated
                """,
                encoding="utf-8",
            )

            patterns = root / "_bmad" / "memory" / "gary-sidecar" / "patterns.md"
            patterns.parent.mkdir(parents=True, exist_ok=True)
            patterns.write_text(
                "# Patterns\n\n"
                "- recurring issue: slide drift\n"
                "- effective recommendation: use preserve mode\n",
                encoding="utf-8",
            )

            empty_patterns = root / "_bmad" / "memory" / "quinn-r-sidecar" / "patterns.md"
            empty_patterns.parent.mkdir(parents=True, exist_ok=True)
            empty_patterns.write_text("# Patterns\n", encoding="utf-8")

            db_path = root / "state" / "runtime" / "coordination.db"
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(str(db_path))
            conn.executescript(
                """
                CREATE TABLE observability_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    gate TEXT,
                    run_mode TEXT NOT NULL,
                    fidelity_o_count INTEGER,
                    fidelity_i_count INTEGER,
                    fidelity_a_count INTEGER,
                    quality_scores_json TEXT,
                    agent_metrics_json TEXT,
                    payload_json TEXT,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE agent_coordination (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    action TEXT NOT NULL,
                    payload_json TEXT,
                    timestamp TEXT
                );
                """
            )
            conn.execute(
                """
                INSERT INTO observability_events
                (run_id, event_type, gate, run_mode, payload_json, created_at)
                VALUES ('R1', 'lane_violation', 'g2', 'default', '{}', '2026-03-30T00:00:00')
                """
            )
            conn.execute(
                """
                INSERT INTO observability_events
                (run_id, event_type, gate, run_mode, payload_json, created_at)
                VALUES ('R1', 'cache_hit', null, 'default', '{}', '2026-03-30T00:01:00')
                """
            )
            conn.execute(
                """
                INSERT INTO observability_events
                (run_id, event_type, gate, run_mode, payload_json, created_at)
                VALUES ('R1', 'cache_miss', null, 'default', '{}', '2026-03-30T00:02:00')
                """
            )
            conn.execute(
                """
                INSERT INTO agent_coordination (run_id, agent_name, action, payload_json, timestamp)
                VALUES (
                    'R1',
                    'gamma-specialist',
                    'redirect',
                    '{"reason": "active_baton_redirect"}',
                    '2026-03-30T00:03:00'
                )
                """
            )
            conn.commit()
            conn.close()

            with patch.object(MODULE, "project_root", return_value=root):
                report = MODULE.generate_synthesis_report(
                    db_path=db_path,
                    write_report=False,
                )

            self.assertEqual(len(report["tool_capability_changes"]), 2)
            self.assertEqual(report["governance_health_metrics"]["lane_violations"], 1)
            self.assertEqual(report["governance_health_metrics"]["baton_redirects"], 1)
            self.assertEqual(report["governance_health_metrics"]["cache_metrics"]["hit_rate"], 0.5)
            self.assertGreaterEqual(report["sidecar_pattern_synthesis"]["total_sidecars"], 2)
            self.assertTrue(
                any(
                    rec["category"] == "doc-updates"
                    for rec in report["prioritized_recommendations"]
                )
            )

    def test_generate_synthesis_report_writes_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            doc = root / "skills" / "compositor" / "references" / "doc-sources.yaml"
            doc.parent.mkdir(parents=True, exist_ok=True)
            doc.write_text(
                "tool: compositor\nagent: compositor\ndoc_sources: []\nlast_refreshed: null\n",
                encoding="utf-8",
            )

            with patch.object(MODULE, "project_root", return_value=root):
                report = MODULE.generate_synthesis_report(write_report=True)

            target = (
                root
                / "_bmad-output"
                / "implementation-artifacts"
                / "reports"
                / "tool-ecosystem-synthesis-report.json"
            )
            self.assertTrue(target.exists())
            self.assertEqual(report["report_path"], str(target))


if __name__ == "__main__":
    unittest.main()
