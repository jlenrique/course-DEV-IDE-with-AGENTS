# /// script
# requires-python = ">=3.10"
# ///
"""Export and platform deployment coordination.

Coordinates final accessibility verification, deployment event persistence,
and platform-specific confirmation payloads.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from types import ModuleType
from typing import Any

try:
    from scripts.utilities.ad_hoc_persistence_guard import enforce_ad_hoc_boundary, resolve_run_mode
    from scripts.utilities.file_helpers import project_root
except ModuleNotFoundError:
    def _load_util_module(file_name: str, module_name: str) -> Any:
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "scripts" / "utilities" / file_name
            if candidate.exists():
                spec = importlib.util.spec_from_file_location(module_name, candidate)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
        raise

    _guard_mod = _load_util_module("ad_hoc_persistence_guard.py", "ad_hoc_persistence_guard_local")
    _file_mod = _load_util_module("file_helpers.py", "file_helpers_local")
    enforce_ad_hoc_boundary = _guard_mod.enforce_ad_hoc_boundary
    resolve_run_mode = _guard_mod.resolve_run_mode
    project_root = _file_mod.project_root


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else project_root() / "state" / "runtime" / "coordination.db"
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _load_module(module_name: str, file_path: Path) -> ModuleType:
    if module_name in sys.modules:
        return sys.modules[module_name]
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not spec.loader:
        raise ImportError(f"Unable to load module {module_name} from {file_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _accessibility_checker() -> ModuleType:
    path = project_root() / "skills" / "quality-control" / "scripts" / "accessibility_checker.py"
    return _load_module("skills.quality_control.scripts.accessibility_checker", path)


def _platform_urls(platform: str, run_id: str, module_id: str) -> dict[str, str]:
    platform_l = platform.strip().lower()
    if platform_l == "canvas":
        return {
            "module_url": f"https://canvas.example/courses/demo/modules/{module_id or 'module'}",
            "run_verification_url": f"https://canvas.example/production/runs/{run_id}",
        }
    if platform_l == "coursearc":
        return {
            "module_url": f"https://coursearc.example/library/{module_id or 'module'}",
            "run_verification_url": f"https://coursearc.example/deployments/{run_id}",
        }
    return {
        "module_url": f"https://platform.example/modules/{module_id or 'module'}",
        "run_verification_url": f"https://platform.example/deployments/{run_id}",
    }


def _verify_accessibility(artifact_paths: list[str]) -> dict[str, Any]:
    checker = _accessibility_checker()
    results: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []

    for path_s in artifact_paths:
        path = Path(path_s)
        if not path.exists():
            skipped.append({"artifact_path": str(path), "reason": "missing_file"})
            continue
        if path.suffix.lower() not in {".md", ".txt", ".html"}:
            skipped.append({"artifact_path": str(path), "reason": "unsupported_extension"})
            continue
        text = path.read_text(encoding="utf-8")
        result = checker.run_accessibility_check(text)
        result["artifact_path"] = str(path)
        results.append(result)

    if not results:
        status = "skipped"
    else:
        status = "pass" if all(r.get("status") == "pass" for r in results) else "fail"
    return {
        "status": status,
        "results": results,
        "checked_count": len(results),
        "skipped_count": len(skipped),
        "skipped_artifacts": skipped,
    }


def deploy_content(
    *,
    run_id: str,
    platform: str,
    artifact_paths: list[str],
    run_mode: str | None = None,
    db_path: Path | str | None = None,
    enforce_accessibility: bool = True,
    module_structure: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deploy artifacts to target platform with final checks and logging."""
    mode = resolve_run_mode(run_mode)

    accessibility = _verify_accessibility(artifact_paths) if enforce_accessibility else {
        "status": "pass",
        "results": [],
        "checked_count": 0,
    }
    if enforce_accessibility and accessibility["checked_count"] == 0:
        return {
            "run_id": run_id,
            "platform": platform,
            "status": "blocked",
            "reason": "Final accessibility verification requires at least one checkable text artifact",
            "accessibility": accessibility,
            "run_mode": mode,
        }

    if accessibility["status"] != "pass":
        return {
            "run_id": run_id,
            "platform": platform,
            "status": "blocked",
            "reason": "Final accessibility verification failed",
            "accessibility": accessibility,
            "run_mode": mode,
        }

    guard = enforce_ad_hoc_boundary("production_run_db", mode)

    run_row: sqlite3.Row | None = None
    module_id = ""
    if guard["allowed"]:
        conn = _connect(db_path)
        try:
            run_row = conn.execute(
                "SELECT * FROM production_runs WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            module_id = str(run_row["module_id"]) if run_row else ""
        finally:
            conn.close()

        if run_row is None:
            return {
                "run_id": run_id,
                "platform": platform,
                "status": "blocked",
                "reason": "Run not found for durable deployment",
                "run_mode": mode,
            }

    urls = _platform_urls(platform, run_id, module_id)
    module_verification = {
        "expected_assets": len(artifact_paths),
        "resolved_assets": len([p for p in artifact_paths if Path(p).exists()]),
        "module_structure": module_structure or {"sections": len(artifact_paths)},
    }

    deployment_payload = {
        "platform": platform,
        "artifact_paths": artifact_paths,
        "urls": urls,
        "module_verification": module_verification,
        "accessibility": accessibility,
        "deployed_at": _now(),
    }

    if not guard["allowed"]:
        return {
            "run_id": run_id,
            "platform": platform,
            "status": "deployed-simulated",
            "persisted": False,
            "run_mode": mode,
            "code": guard["code"],
            "reason": guard["reason"],
            "deployment": deployment_payload,
            "confirmation": f"Module deployed to {platform} (sandbox). Here's the link to verify.",
        }

    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO deployment_events (run_id, platform, status, details_json, deployed_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                run_id,
                platform,
                "deployed",
                json.dumps(deployment_payload),
                deployment_payload["deployed_at"],
            ),
        )

        if run_row is not None:
            context = {}
            try:
                context = json.loads(run_row["context_json"] or "{}")
            except (json.JSONDecodeError, TypeError):
                context = {}
            deployments = context.setdefault("deployments", [])
            deployments.append(
                {
                    "platform": platform,
                    "urls": urls,
                    "deployed_at": deployment_payload["deployed_at"],
                }
            )
            conn.execute(
                """
                UPDATE production_runs
                SET status = 'deployed', context_json = ?, updated_at = ?
                WHERE run_id = ?
                """,
                (json.dumps(context), _now(), run_id),
            )

        conn.execute(
            """
            INSERT INTO agent_coordination (run_id, agent_name, action, payload_json, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                run_id,
                "deployment-coordinator",
                "deployment_completed",
                json.dumps(deployment_payload),
                _now(),
            ),
        )

        conn.commit()
        event_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    finally:
        conn.close()

    return {
        "run_id": run_id,
        "platform": platform,
        "status": "deployed",
        "persisted": True,
        "run_mode": mode,
        "deployment_event_id": event_id,
        "deployment": deployment_payload,
        "confirmation": f"Module deployed to {platform}. Here's the link to verify.",
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Coordinate export and deployment")
    parser.add_argument("--db", help="Override coordination database path")

    sub = parser.add_subparsers(dest="command", required=True)

    p_deploy = sub.add_parser("deploy", help="Deploy run artifacts")
    p_deploy.add_argument("--run-id", required=True)
    p_deploy.add_argument("--platform", required=True)
    p_deploy.add_argument("--artifact-paths", required=True, help="JSON array of file paths")
    p_deploy.add_argument("--run-mode", default=None)
    p_deploy.add_argument("--no-accessibility", action="store_true")
    p_deploy.add_argument("--module-structure", default="{}", help="JSON object")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "deploy":
        result = deploy_content(
            run_id=args.run_id,
            platform=args.platform,
            artifact_paths=json.loads(args.artifact_paths),
            run_mode=args.run_mode,
            db_path=args.db,
            enforce_accessibility=not args.no_accessibility,
            module_structure=json.loads(args.module_structure),
        )
    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
