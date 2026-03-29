# /// script
# requires-python = ">=3.10"
# ///
"""Tests for manage_baton.py — run baton lifecycle and authority checks."""
from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import manage_baton


class TempRuntime:
    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.path = self._tmp.name

    def __enter__(self) -> TempRuntime:
        return self

    def __exit__(self, *args: object) -> None:
        self._tmp.cleanup()


class TestBatonLifecycle(unittest.TestCase):
    def test_init_persists_required_fields(self) -> None:
        with TempRuntime() as rt:
            args = manage_baton.build_parser().parse_args(
                [
                    "--runtime-dir", rt.path,
                    "init", "RUN-001",
                    "--current-gate", "G2",
                    "--allowed-delegate", "gamma-specialist",
                    "--allowed-delegate", "quality-reviewer",
                ]
            )
            result = manage_baton.cmd_init(args)

            self.assertEqual(result["status"], "initialized")
            baton = result["baton"]
            self.assertEqual(baton["run_id"], "RUN-001")
            self.assertIn("orchestrator", baton)
            self.assertIn("current_gate", baton)
            self.assertIn("invocation_mode", baton)
            self.assertIn("allowed_delegates", baton)
            self.assertIn("escalation_target", baton)
            self.assertIn("blocking_authority", baton)
            self.assertTrue(Path(result["baton_file"]).exists())

    def test_init_rejects_existing_active_baton_without_force(self) -> None:
        with TempRuntime() as rt:
            manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "init", "RUN-INIT-GUARD"]
                )
            )

            result = manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "init", "RUN-INIT-GUARD"]
                )
            )
            self.assertIn("error", result)
            self.assertIn("Active baton already exists", result["error"])

    def test_init_rejects_second_active_run_without_force(self) -> None:
        with TempRuntime() as rt:
            manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "init", "RUN-PRIMARY"]
                )
            )
            result = manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "init", "RUN-SECONDARY"]
                )
            )
            self.assertIn("error", result)
            self.assertIn("another run", result["error"])

    def test_get_latest_active(self) -> None:
        with TempRuntime() as rt:
            manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "init", "RUN-001"]
                )
            )
            get_result = manage_baton.cmd_get(
                manage_baton.build_parser().parse_args(["--runtime-dir", rt.path, "get"])
            )
            self.assertEqual(get_result["status"], "ok")
            self.assertEqual(get_result["run_id"], "RUN-001")

    def test_update_gate(self) -> None:
        with TempRuntime() as rt:
            manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    [
                        "--runtime-dir", rt.path, "init", "RUN-002", "--current-gate", "G1"
                    ]
                )
            )
            result = manage_baton.cmd_update_gate(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "update-gate", "RUN-002", "G3"]
                )
            )
            self.assertEqual(result["status"], "updated")
            self.assertEqual(result["previous_gate"], "G1")
            self.assertEqual(result["current_gate"], "G3")

    def test_update_gate_concurrent_is_consistent(self) -> None:
        with TempRuntime() as rt:
            manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "init", "RUN-CONCURRENT", "--current-gate", "G1"]
                )
            )

            def worker(next_gate: str) -> None:
                manage_baton.cmd_update_gate(
                    manage_baton.build_parser().parse_args(
                        ["--runtime-dir", rt.path, "update-gate", "RUN-CONCURRENT", next_gate]
                    )
                )

            threads = [
                threading.Thread(target=worker, args=(f"G{i}",))
                for i in range(2, 8)
            ]
            for t in threads:
                t.start()
            for t in threads:
                t.join()

            baton_file = Path(rt.path) / "run_baton.RUN-CONCURRENT.json"
            baton = json.loads(baton_file.read_text(encoding="utf-8"))
            self.assertIn(baton["current_gate"], {f"G{i}" for i in range(2, 8)})

    def test_close_deletes_file(self) -> None:
        with TempRuntime() as rt:
            init_result = manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "init", "RUN-003"]
                )
            )
            baton_path = Path(init_result["baton_file"])
            self.assertTrue(baton_path.exists())

            result = manage_baton.cmd_close(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "close", "--run-id", "RUN-003"]
                )
            )
            self.assertEqual(result["status"], "closed")
            self.assertTrue(result["was_active"])
            self.assertFalse(baton_path.exists())

    def test_close_idempotent_with_run_id(self) -> None:
        with TempRuntime() as rt:
            result = manage_baton.cmd_close(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "close", "--run-id", "RUN-NO-BATON"]
                )
            )
            self.assertEqual(result["status"], "closed")
            self.assertFalse(result["was_active"])


class TestSpecialistChecks(unittest.TestCase):
    def test_check_no_baton_redirects(self) -> None:
        with TempRuntime() as rt:
            result = manage_baton.cmd_check_specialist(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "check-specialist", "gamma-specialist"]
                )
            )
            self.assertEqual(result["action"], "redirect")
            self.assertEqual(result["reason"], "no_active_baton")

    def test_delegated_check_requires_run_id(self) -> None:
        with TempRuntime() as rt:
            result = manage_baton.cmd_check_specialist(
                manage_baton.build_parser().parse_args(
                    [
                        "--runtime-dir", rt.path,
                        "check-specialist", "gamma-specialist",
                        "--delegated-call",
                    ]
                )
            )
            self.assertEqual(result["action"], "redirect")
            self.assertEqual(result["reason"], "run_id_required_for_delegated_check")

    def test_direct_invocation_redirects(self) -> None:
        with TempRuntime() as rt:
            manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    [
                        "--runtime-dir", rt.path,
                        "init", "RUN-004",
                        "--current-gate", "G2",
                        "--allowed-delegate", "gamma-specialist",
                    ]
                )
            )
            result = manage_baton.cmd_check_specialist(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "check-specialist", "gamma-specialist"]
                )
            )
            self.assertEqual(result["action"], "redirect")
            self.assertIn("Marcus is running RUN-004", result["message"])

    def test_delegated_allowed_proceeds(self) -> None:
        with TempRuntime() as rt:
            manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    [
                        "--runtime-dir", rt.path,
                        "init", "RUN-005",
                        "--current-gate", "G3",
                        "--allowed-delegate", "quality-reviewer",
                    ]
                )
            )
            result = manage_baton.cmd_check_specialist(
                manage_baton.build_parser().parse_args(
                    [
                        "--runtime-dir", rt.path,
                        "check-specialist", "quality-reviewer",
                        "--run-id", "RUN-005",
                        "--delegated-call",
                    ]
                )
            )
            self.assertEqual(result["action"], "proceed")
            self.assertEqual(result["mode"], "delegated")
            self.assertEqual(result["current_gate"], "G3")

    def test_explicit_standalone_bypass(self) -> None:
        with TempRuntime() as rt:
            manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    [
                        "--runtime-dir", rt.path,
                        "init", "RUN-006",
                        "--allowed-delegate", "gamma-specialist",
                    ]
                )
            )
            result = manage_baton.cmd_check_specialist(
                manage_baton.build_parser().parse_args(
                    [
                        "--runtime-dir", rt.path,
                        "check-specialist", "gamma-specialist",
                        "--standalone-mode",
                    ]
                )
            )
            self.assertEqual(result["action"], "proceed")
            self.assertEqual(result["mode"], "standalone-consult")
            self.assertIn("Do not mutate active production run state", result["note"])

    def test_baton_standalone_mode_proceeds_without_redirect(self) -> None:
        with TempRuntime() as rt:
            manage_baton.cmd_init(
                manage_baton.build_parser().parse_args(
                    [
                        "--runtime-dir", rt.path,
                        "init", "RUN-007",
                        "--invocation-mode", "standalone",
                        "--allowed-delegate", "gamma-specialist",
                    ]
                )
            )
            result = manage_baton.cmd_check_specialist(
                manage_baton.build_parser().parse_args(
                    ["--runtime-dir", rt.path, "check-specialist", "gamma-specialist"]
                )
            )
            self.assertEqual(result["action"], "proceed")
            self.assertEqual(result["mode"], "standalone")


if __name__ == "__main__":
    unittest.main()
