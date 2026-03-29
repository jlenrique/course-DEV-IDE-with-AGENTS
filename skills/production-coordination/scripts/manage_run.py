# /// script
# requires-python = ">=3.10"
# ///
"""Production run lifecycle management.

CLI tool for creating, advancing, and querying production runs in the
coordination database. Outputs JSON for agent consumption.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sqlite3
import sys
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

try:
    from scripts.utilities.ad_hoc_persistence_guard import enforce_ad_hoc_boundary
except ModuleNotFoundError:
    def _load_guard_module() -> Any:
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "scripts" / "utilities" / "ad_hoc_persistence_guard.py"
            if candidate.exists():
                spec = importlib.util.spec_from_file_location("ad_hoc_persistence_guard_local", candidate)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
        raise

    enforce_ad_hoc_boundary = _load_guard_module().enforce_ad_hoc_boundary


def find_project_root() -> Path:
    """Walk up from script location to find the project root (contains state/)."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "state").is_dir():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def get_db_path(root: Path | None = None) -> Path:
    """Return the coordination database path."""
    root = root or find_project_root()
    return root / "state" / "runtime" / "coordination.db"


def connect_db(db_path: Path | str | None = None) -> sqlite3.Connection:
    """Open a connection to the coordination database.

    Args:
        db_path: Override path. Uses default project path if None.

    Returns:
        sqlite3.Connection with row_factory set to sqlite3.Row.
    """
    path = Path(db_path) if db_path else get_db_path()
    if not path.exists():
        print(json.dumps({"error": f"Database not found: {path}"}), file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _parse_context(row: sqlite3.Row) -> dict[str, Any]:
    """Parse the context_json field from a production_runs row."""
    raw = row["context_json"]
    if raw:
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            pass
    return {}


def _current_stage(ctx: dict[str, Any]) -> dict[str, Any] | None:
    """Extract the current stage from context."""
    stages = ctx.get("stages", [])
    idx = ctx.get("current_stage_index", 0)
    if 0 <= idx < len(stages):
        stage = dict(stages[idx])
        stage["index"] = idx
        return stage
    return None


def _runtime_dir(runtime_dir: str | None = None) -> Path:
    """Resolve runtime directory for transient baton files."""
    if runtime_dir:
        return Path(runtime_dir)
    return find_project_root() / "state" / "runtime"


@contextmanager
def _file_lock(lock_path: Path, timeout_seconds: float = 3.0):
    """Acquire an exclusive file lock via lock-file creation."""
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    while True:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            try:
                yield
            finally:
                os.close(fd)
                lock_path.unlink(missing_ok=True)
            return
        except FileExistsError:
            if time.monotonic() - start >= timeout_seconds:
                raise TimeoutError(f"Timed out waiting for lock: {lock_path}")
            time.sleep(0.05)


def _load_run_preset_policy(preset: str | None) -> dict[str, Any]:
    """Load run preset policy from state/config/tool_policies.yaml."""
    policy_path = find_project_root() / "state" / "config" / "tool_policies.yaml"
    default_policy = {
        "description": "Draft baseline",
        "quality_threshold": 0.7,
        "human_review": True,
        "accessibility_check": True,
        "brand_consistency_check": False,
    }

    if not policy_path.exists():
        return default_policy

    try:
        data = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return default_policy

    run_presets = data.get("run_presets", {}) if isinstance(data, dict) else {}
    selected = str(preset or data.get("default_preset") or "draft")
    candidate = run_presets.get(selected)
    if isinstance(candidate, dict):
        return candidate
    return default_policy


def _ad_hoc_runs_dir(runtime_dir: str | None = None) -> Path:
    """Resolve ad-hoc transient run store directory."""
    path = _runtime_dir(runtime_dir) / "ad-hoc-runs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _ad_hoc_run_path(run_id: str, runtime_dir: str | None = None) -> Path:
    return _ad_hoc_runs_dir(runtime_dir) / f"{run_id}.json"


def _perception_cache_path(run_id: str, runtime_dir: str | None = None) -> Path:
    return _runtime_dir(runtime_dir) / "perception-cache" / f"{run_id}.json"


def _load_ad_hoc_run(run_id: str, runtime_dir: str | None = None) -> dict[str, Any] | None:
    path = _ad_hoc_run_path(run_id, runtime_dir)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _save_ad_hoc_run(data: dict[str, Any], runtime_dir: str | None = None) -> None:
    run_id = str(data["run_id"])
    path = _ad_hoc_run_path(run_id, runtime_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    tmp.replace(path)


def _write_run_context_yaml(
    *,
    run_id: str,
    course: str,
    module: str,
    lesson: str,
    content_type: str,
    preset: str,
    base_dir: Path | None = None,
) -> dict[str, str]:
    """Create run-scoped context YAML entities under state/config/."""
    from run_context_builder import build_run_context

    paths = build_run_context(
        run_id=run_id,
        course=course,
        module=module,
        lesson=lesson,
        content_type=content_type,
        preset=preset,
        base_dir=str(base_dir) if base_dir else None,
    )
    return {k: str(v) for k, v in paths.items()}


def _persist_cross_run_links(
    conn: sqlite3.Connection,
    *,
    run_id: str,
    linked_runs: list[str],
) -> None:
    """Persist cross-run relationships when schema supports it."""
    if not linked_runs:
        return
    for linked_run_id in linked_runs:
        try:
            conn.execute(
                """
                INSERT INTO run_context_links (run_id, linked_run_id, link_type)
                VALUES (?, ?, ?)
                """,
                (run_id, linked_run_id, "same-course-module"),
            )
        except sqlite3.OperationalError:
            # Older test schemas may not include run_context_links yet.
            return


def _baton_path(run_id: str, runtime_dir: str | None = None) -> Path:
    """Return baton file path for a run id."""
    return _runtime_dir(runtime_dir) / f"run_baton.{run_id}.json"


def _close_baton(run_id: str, runtime_dir: str | None = None) -> dict[str, Any]:
    """Close baton for a run by deleting transient baton file."""
    path = _baton_path(run_id, runtime_dir)
    if not path.exists():
        return {
            "status": "not-found",
            "closed": False,
            "message": "No active baton found",
        }
    try:
        path.unlink(missing_ok=True)
        return {
            "status": "closed",
            "closed": True,
            "baton_file": str(path),
        }
    except OSError as exc:
        return {
            "status": "error",
            "closed": False,
            "error": str(exc),
            "baton_file": str(path),
        }


def _clear_run_cache(run_id: str, runtime_dir: str | None = None) -> dict[str, Any]:
    """Clear run-scoped perception cache file if present."""
    path = _perception_cache_path(run_id, runtime_dir)
    if not path.exists():
        return {
            "status": "not-found",
            "cleared": False,
            "cache_file": str(path),
        }
    try:
        path.unlink(missing_ok=True)
        return {
            "status": "cleared",
            "cleared": True,
            "cache_file": str(path),
        }
    except OSError as exc:
        return {
            "status": "error",
            "cleared": False,
            "error": str(exc),
            "cache_file": str(path),
        }


def _update_baton_gate(run_id: str, gate: str, runtime_dir: str | None = None) -> dict[str, Any]:
    """Update baton gate if an active baton exists for this run."""
    path = _baton_path(run_id, runtime_dir)
    if not path.exists():
        return {
            "status": "not-found",
            "updated": False,
            "message": "No active baton found",
        }

    lock_path = path.with_suffix(path.suffix + ".lock")
    try:
        with _file_lock(lock_path):
            try:
                with open(path, encoding="utf-8") as f:
                    baton = json.load(f)
            except (json.JSONDecodeError, OSError) as exc:
                return {
                    "status": "error",
                    "updated": False,
                    "error": str(exc),
                }

            if not baton.get("active", True):
                return {
                    "status": "inactive",
                    "updated": False,
                    "message": "Baton exists but is inactive",
                }

            baton["current_gate"] = gate
            baton["updated_at"] = _now()
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix(path.suffix + ".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(baton, f, indent=2)
            tmp.replace(path)
    except (OSError, TimeoutError) as exc:
        return {
            "status": "error",
            "updated": False,
            "error": str(exc),
        }

    return {
        "status": "updated",
        "updated": True,
        "current_gate": gate,
    }


# ── Commands ──────────────────────────────────────────────────────────


def cmd_create(args: argparse.Namespace) -> dict[str, Any]:
    """Create a new production run."""
    now = _now()

    stages = []
    if args.stages_json:
        stages = json.loads(args.stages_json)
    for s in stages:
        s.setdefault("status", "pending")

    selected_preset = args.preset or "draft"
    preset_policy = _load_run_preset_policy(selected_preset)
    mode = args.mode or "default"

    context = {
        "content_type": args.content_type or "unknown",
        "module": args.module or "",
        "lesson": args.lesson or "",
        "learning_objectives": [],
        "mode": mode,
        "preset_policy": preset_policy,
        "stages": stages,
        "current_stage_index": 0,
        "revision_count": 0,
        "user_feedback": [],
    }

    run_id = args.run_id
    if not run_id:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        parts = [args.course or "RUN", args.module or "XX", args.content_type or "task", ts]
        run_id = "-".join(p for p in parts if p)

    guard = enforce_ad_hoc_boundary("production_run_db", mode)

    if guard["allowed"]:
        context_paths = _write_run_context_yaml(
            run_id=run_id,
            course=args.course or "",
            module=args.module or "",
            lesson=args.lesson or "",
            content_type=args.content_type or "unknown",
            preset=args.preset or "draft",
        )
        context["context_scope"] = "canonical"
    else:
        transient_guard = enforce_ad_hoc_boundary("transient_run_context", mode)
        if not transient_guard["allowed"]:
            return {
                "error": "Ad-hoc mode run context cannot be created",
                "run_id": run_id,
                "code": transient_guard["code"],
                "reason": transient_guard["reason"],
            }
        transient_context_base = _runtime_dir(args.runtime_dir) / "ad-hoc-runs" / run_id / "context"
        context_paths = _write_run_context_yaml(
            run_id=run_id,
            course=args.course or "",
            module=args.module or "",
            lesson=args.lesson or "",
            content_type=args.content_type or "unknown",
            preset=args.preset or "draft",
            base_dir=transient_context_base,
        )
        context["context_scope"] = "transient"

    context["context_paths"] = context_paths

    # Cross-run context linkage for same course/module history.
    cross_run_links: list[str] = []
    if (args.course or args.module) and guard["allowed"]:
        try:
            conn_link = connect_db(args.db)
            rows = conn_link.execute(
                """
                SELECT run_id FROM production_runs
                WHERE run_id != ? AND course_code = ? AND module_id = ?
                ORDER BY updated_at DESC LIMIT 5
                """,
                (run_id, args.course or "", args.module or ""),
            ).fetchall()
            conn_link.close()
            cross_run_links = [r["run_id"] for r in rows]
            context["cross_run_links"] = cross_run_links
        except Exception:
            context["cross_run_links"] = []

    if not guard["allowed"]:
        ad_hoc_record = {
            "run_id": run_id,
            "purpose": args.purpose or f"Ad-hoc run for {args.content_type}",
            "status": "planning",
            "preset": args.preset or "draft",
            "context_json": context,
            "created_at": now,
            "updated_at": now,
            "ad_hoc": True,
        }
        _save_ad_hoc_run(ad_hoc_record, args.runtime_dir)
        return {
            "run_id": run_id,
            "status": "planning",
            "stages_count": len(stages),
            "created_at": now,
            "persisted": False,
            "mode": mode,
            "code": guard["code"],
            "reason": guard["reason"],
            "ad_hoc_state": str(_ad_hoc_run_path(run_id, args.runtime_dir)),
            "context_paths": context_paths,
        }

    conn = connect_db(args.db)

    try:
        conn.execute(
            """INSERT INTO production_runs
               (run_id, purpose, status, preset, context_json,
                course_code, module_id, started_at, created_at, updated_at)
               VALUES (?, ?, 'planning', ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                args.purpose or f"Production run for {args.content_type}",
                selected_preset,
                json.dumps(context),
                args.course or "",
                args.module or "",
                now, now, now,
            ),
        )
        _persist_cross_run_links(conn, run_id=run_id, linked_runs=cross_run_links)
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return {"error": f"Run ID already exists: {run_id}"}
    finally:
        conn.close()

    return {
        "run_id": run_id,
        "status": "planning",
        "stages_count": len(stages),
        "created_at": now,
        "persisted": True,
        "mode": context.get("mode", "default"),
        "preset_policy": preset_policy,
        "cross_run_links": cross_run_links,
        "context_paths": context_paths,
    }


def cmd_advance(args: argparse.Namespace) -> dict[str, Any]:
    """Advance a run to the next stage."""
    ad_hoc_run = _load_ad_hoc_run(args.run_id, args.runtime_dir)
    if ad_hoc_run is not None:
        ctx = ad_hoc_run.get("context_json", {})
        stages = ctx.get("stages", [])
        idx = ctx.get("current_stage_index", 0)

        if idx < len(stages):
            stages[idx]["status"] = "approved"
            stages[idx]["stage_completed_at"] = _now()

        next_idx = idx + 1
        if next_idx >= len(stages):
            return {"error": "Already at final stage — use 'complete' to finalize the run"}

        stages[next_idx]["status"] = "working"
        stages[next_idx].setdefault("stage_started_at", _now())
        ctx["current_stage_index"] = next_idx
        ctx["stages"] = stages

        ad_hoc_run["context_json"] = ctx
        ad_hoc_run["status"] = "in-progress"
        ad_hoc_run["updated_at"] = _now()
        _save_ad_hoc_run(ad_hoc_run, args.runtime_dir)

        next_gate = str(stages[next_idx].get("stage", f"stage-{next_idx}"))
        baton_gate_sync = _update_baton_gate(args.run_id, next_gate, args.runtime_dir)

        return {
            "run_id": args.run_id,
            "status": "in-progress",
            "advanced_to": stages[next_idx],
            "stage_index": next_idx,
            "stages_total": len(stages),
            "baton_gate_updated": baton_gate_sync.get("updated", False),
            "baton_gate_sync": baton_gate_sync,
            "persisted": False,
            "mode": "ad-hoc",
        }

    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    ctx = _parse_context(row)
    guard = enforce_ad_hoc_boundary("production_run_db", ctx.get("mode"))
    if not guard["allowed"]:
        conn.close()
        return {
            "error": "Ad-hoc mode run cannot mutate production ledger",
            "code": guard["code"],
            "reason": guard["reason"],
            "run_id": args.run_id,
        }

    stages = ctx.get("stages", [])
    idx = ctx.get("current_stage_index", 0)

    if idx < len(stages):
        stages[idx]["status"] = "approved"
        stages[idx]["stage_completed_at"] = _now()

    next_idx = idx + 1
    if next_idx >= len(stages):
        conn.close()
        return {"error": "Already at final stage — use 'complete' to finalize the run"}

    stages[next_idx]["status"] = "working"
    stages[next_idx].setdefault("stage_started_at", _now())
    ctx["current_stage_index"] = next_idx
    ctx["stages"] = stages

    run_status = "in-progress" if row["status"] == "planning" else row["status"]
    now = _now()
    conn.execute(
        "UPDATE production_runs SET context_json = ?, status = ?, updated_at = ? WHERE run_id = ?",
        (json.dumps(ctx), run_status, now, args.run_id),
    )
    conn.commit()
    conn.close()

    next_gate = str(stages[next_idx].get("stage", f"stage-{next_idx}"))
    baton_gate_sync = _update_baton_gate(args.run_id, next_gate, args.runtime_dir)

    return {
        "run_id": args.run_id,
        "status": run_status,
        "advanced_to": stages[next_idx],
        "stage_index": next_idx,
        "stages_total": len(stages),
        "baton_gate_updated": baton_gate_sync.get("updated", False),
        "baton_gate_sync": baton_gate_sync,
    }


def cmd_checkpoint(args: argparse.Namespace) -> dict[str, Any]:
    """Mark the current stage as awaiting human review."""
    ad_hoc_run = _load_ad_hoc_run(args.run_id, args.runtime_dir)
    if ad_hoc_run is not None:
        ctx = ad_hoc_run.get("context_json", {})
        stages = ctx.get("stages", [])
        idx = ctx.get("current_stage_index", 0)

        if idx >= len(stages):
            return {"error": "No active stage to checkpoint"}

        stages[idx]["status"] = "awaiting-review"
        ctx["stages"] = stages
        quality_gates = ctx.setdefault("quality_gates", [])
        quality_gates.append(
            {
                "stage": stages[idx].get("stage", f"stage-{idx}"),
                "status": "pending",
                "created_at": _now(),
            }
        )
        ad_hoc_run["context_json"] = ctx
        ad_hoc_run["updated_at"] = _now()
        _save_ad_hoc_run(ad_hoc_run, args.runtime_dir)

        return {
            "run_id": args.run_id,
            "stage": stages[idx],
            "stage_index": idx,
            "status": "awaiting-review",
            "persisted": False,
            "mode": "ad-hoc",
        }

    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    ctx = _parse_context(row)
    guard = enforce_ad_hoc_boundary("quality_gate_db", ctx.get("mode"))
    if not guard["allowed"]:
        conn.close()
        return {
            "error": "Ad-hoc mode run cannot persist quality gates",
            "code": guard["code"],
            "reason": guard["reason"],
            "run_id": args.run_id,
        }

    stages = ctx.get("stages", [])
    idx = ctx.get("current_stage_index", 0)

    if idx >= len(stages):
        conn.close()
        return {"error": "No active stage to checkpoint"}

    stages[idx]["status"] = "awaiting-review"
    ctx["stages"] = stages
    now = _now()

    conn.execute(
        "UPDATE production_runs SET context_json = ?, updated_at = ? WHERE run_id = ?",
        (json.dumps(ctx), now, args.run_id),
    )

    conn.execute(
        """INSERT INTO quality_gates (run_id, stage, status, created_at)
           VALUES (?, ?, 'pending', ?)""",
        (args.run_id, stages[idx].get("stage", f"stage-{idx}"), now),
    )
    conn.commit()
    conn.close()

    return {
        "run_id": args.run_id,
        "stage": stages[idx],
        "stage_index": idx,
        "status": "awaiting-review",
    }


def cmd_approve(args: argparse.Namespace) -> dict[str, Any]:
    """Record user approval for the current checkpoint."""
    ad_hoc_run = _load_ad_hoc_run(args.run_id, args.runtime_dir)
    if ad_hoc_run is not None:
        ctx = ad_hoc_run.get("context_json", {})
        stages = ctx.get("stages", [])
        idx = ctx.get("current_stage_index", 0)

        if idx >= len(stages):
            return {"error": "No active stage to approve"}

        if stages[idx].get("status") != "awaiting-review":
            return {
                "error": f"Stage is '{stages[idx].get('status')}', not 'awaiting-review'"
            }

        stages[idx]["status"] = "approved"
        stages[idx]["stage_completed_at"] = _now()
        ctx["stages"] = stages

        for gate in reversed(ctx.get("quality_gates", [])):
            if gate.get("stage") == stages[idx].get("stage", f"stage-{idx}") and gate.get("status") == "pending":
                gate["status"] = "approved"
                gate["reviewer"] = "human"
                gate["score"] = args.score or 1.0
                gate["decided_at"] = _now()
                break

        ad_hoc_run["context_json"] = ctx
        ad_hoc_run["updated_at"] = _now()
        _save_ad_hoc_run(ad_hoc_run, args.runtime_dir)

        next_idx = idx + 1
        result: dict[str, Any] = {
            "run_id": args.run_id,
            "approved_stage": stages[idx],
            "stage_index": idx,
            "persisted": False,
            "mode": "ad-hoc",
        }
        if next_idx >= len(stages):
            result["next_action"] = "complete"
            result["message"] = "Final stage approved — call 'complete' to finalize the run"
        else:
            result["next_action"] = "advance"
            result["next_stage"] = stages[next_idx]
        return result

    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    ctx = _parse_context(row)
    guard = enforce_ad_hoc_boundary("quality_gate_db", ctx.get("mode"))
    if not guard["allowed"]:
        conn.close()
        return {
            "error": "Ad-hoc mode run cannot persist quality approvals",
            "code": guard["code"],
            "reason": guard["reason"],
            "run_id": args.run_id,
        }

    stages = ctx.get("stages", [])
    idx = ctx.get("current_stage_index", 0)

    if idx >= len(stages):
        conn.close()
        return {"error": "No active stage to approve"}

    if stages[idx].get("status") != "awaiting-review":
        conn.close()
        return {"error": f"Stage is '{stages[idx].get('status')}', not 'awaiting-review'"}

    stages[idx]["status"] = "approved"
    ctx["stages"] = stages
    now = _now()

    conn.execute(
        "UPDATE production_runs SET context_json = ?, updated_at = ? WHERE run_id = ?",
        (json.dumps(ctx), now, args.run_id),
    )

    stage_name = stages[idx].get("stage", f"stage-{idx}")
    conn.execute(
        """UPDATE quality_gates SET status = 'approved', reviewer = 'human',
           score = ?, decided_at = ? WHERE run_id = ? AND stage = ? AND status = 'pending'""",
        (args.score or 1.0, now, args.run_id, stage_name),
    )
    conn.commit()

    next_idx = idx + 1
    is_final = next_idx >= len(stages)

    conn.close()
    result: dict[str, Any] = {
        "run_id": args.run_id,
        "approved_stage": stages[idx],
        "stage_index": idx,
    }
    if is_final:
        result["next_action"] = "complete"
        result["message"] = "Final stage approved — call 'complete' to finalize the run"
    else:
        result["next_action"] = "advance"
        result["next_stage"] = stages[next_idx]
    return result


def cmd_complete(args: argparse.Namespace) -> dict[str, Any]:
    """Finalize a production run."""
    ad_hoc_run = _load_ad_hoc_run(args.run_id, args.runtime_dir)
    if ad_hoc_run is not None:
        ctx = ad_hoc_run.get("context_json", {})
        stages = ctx.get("stages", [])
        unapproved = [s for s in stages if s.get("status") != "approved"]
        if unapproved:
            return {
                "error": "Cannot complete — unapproved stages remain",
                "unapproved": unapproved,
            }

        now = _now()
        ad_hoc_run["status"] = "completed"
        ad_hoc_run["completed_at"] = now
        ad_hoc_run["updated_at"] = now
        _save_ad_hoc_run(ad_hoc_run, args.runtime_dir)

        baton_close = _close_baton(args.run_id, args.runtime_dir)
        cache_clear = _clear_run_cache(args.run_id, args.runtime_dir)
        return {
            "run_id": args.run_id,
            "status": "completed",
            "completed_at": now,
            "stages_count": len(stages),
            "baton_closed": baton_close.get("closed", False),
            "baton_close": baton_close,
            "cache_cleared": cache_clear.get("cleared", False),
            "cache_clear": cache_clear,
            "persisted": False,
            "mode": "ad-hoc",
        }

    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    ctx = _parse_context(row)
    guard = enforce_ad_hoc_boundary("production_run_db", ctx.get("mode"))
    if not guard["allowed"]:
        conn.close()
        return {
            "error": "Ad-hoc mode run cannot finalize production ledger",
            "code": guard["code"],
            "reason": guard["reason"],
            "run_id": args.run_id,
        }

    stages = ctx.get("stages", [])
    unapproved = [s for s in stages if s.get("status") != "approved"]
    if unapproved:
        conn.close()
        return {
            "error": "Cannot complete — unapproved stages remain",
            "unapproved": unapproved,
        }

    now = _now()
    conn.execute(
        """UPDATE production_runs SET status = 'completed',
           completed_at = ?, updated_at = ? WHERE run_id = ?""",
        (now, now, args.run_id),
    )
    conn.commit()
    conn.close()

    baton_close = _close_baton(args.run_id, args.runtime_dir)
    cache_clear = _clear_run_cache(args.run_id, args.runtime_dir)

    return {
        "run_id": args.run_id,
        "status": "completed",
        "completed_at": now,
        "stages_count": len(stages),
        "baton_closed": baton_close.get("closed", False),
        "baton_close": baton_close,
        "cache_cleared": cache_clear.get("cleared", False),
        "cache_clear": cache_clear,
    }


def cmd_cancel(args: argparse.Namespace) -> dict[str, Any]:
    """Cancel a production run and clear its baton."""
    ad_hoc_run = _load_ad_hoc_run(args.run_id, args.runtime_dir)
    if ad_hoc_run is not None:
        if ad_hoc_run.get("status") == "completed":
            return {"error": "Cannot cancel a completed run"}

        if ad_hoc_run.get("status") == "cancelled":
            baton_close = _close_baton(args.run_id, args.runtime_dir)
            cache_clear = _clear_run_cache(args.run_id, args.runtime_dir)
            return {
                "run_id": args.run_id,
                "status": "cancelled",
                "message": "Run already cancelled",
                "baton_closed": baton_close.get("closed", False),
                "baton_close": baton_close,
                "cache_cleared": cache_clear.get("cleared", False),
                "cache_clear": cache_clear,
                "persisted": False,
                "mode": "ad-hoc",
            }

        now = _now()
        ad_hoc_run["status"] = "cancelled"
        ad_hoc_run["updated_at"] = now
        ad_hoc_run["cancelled_at"] = now
        _save_ad_hoc_run(ad_hoc_run, args.runtime_dir)

        baton_close = _close_baton(args.run_id, args.runtime_dir)
        cache_clear = _clear_run_cache(args.run_id, args.runtime_dir)
        return {
            "run_id": args.run_id,
            "status": "cancelled",
            "cancelled_at": now,
            "baton_closed": baton_close.get("closed", False),
            "baton_close": baton_close,
            "cache_cleared": cache_clear.get("cleared", False),
            "cache_clear": cache_clear,
            "persisted": False,
            "mode": "ad-hoc",
        }

    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    if row["status"] == "completed":
        conn.close()
        return {"error": "Cannot cancel a completed run"}

    if row["status"] == "cancelled":
        conn.close()
        baton_close = _close_baton(args.run_id, args.runtime_dir)
        cache_clear = _clear_run_cache(args.run_id, args.runtime_dir)
        return {
            "run_id": args.run_id,
            "status": "cancelled",
            "message": "Run already cancelled",
            "baton_closed": baton_close.get("closed", False),
            "baton_close": baton_close,
            "cache_cleared": cache_clear.get("cleared", False),
            "cache_clear": cache_clear,
        }

    now = _now()
    conn.execute(
        """UPDATE production_runs SET status = 'cancelled',
           updated_at = ? WHERE run_id = ?""",
        (now, args.run_id),
    )
    conn.commit()
    conn.close()

    baton_close = _close_baton(args.run_id, args.runtime_dir)
    cache_clear = _clear_run_cache(args.run_id, args.runtime_dir)
    return {
        "run_id": args.run_id,
        "status": "cancelled",
        "cancelled_at": now,
        "baton_closed": baton_close.get("closed", False),
        "baton_close": baton_close,
        "cache_cleared": cache_clear.get("cleared", False),
        "cache_clear": cache_clear,
    }


def cmd_status(args: argparse.Namespace) -> dict[str, Any]:
    """Query current state of a production run."""
    ad_hoc_run = _load_ad_hoc_run(args.run_id, args.runtime_dir)
    if ad_hoc_run is not None:
        ctx = ad_hoc_run.get("context_json", {})
        current = _current_stage(ctx)
        stages = ctx.get("stages", [])
        completed_count = sum(1 for s in stages if s.get("status") == "approved")
        return {
            "run_id": ad_hoc_run["run_id"],
            "purpose": ad_hoc_run.get("purpose", ""),
            "status": ad_hoc_run.get("status", "planning"),
            "preset": ad_hoc_run.get("preset", "draft"),
            "mode": "ad-hoc",
            "content_type": ctx.get("content_type", ""),
            "current_stage": current,
            "stages_completed": completed_count,
            "stages_total": len(stages),
            "revision_count": ctx.get("revision_count", 0),
            "created_at": ad_hoc_run.get("created_at"),
            "updated_at": ad_hoc_run.get("updated_at"),
            "persisted": False,
        }

    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    ctx = _parse_context(row)
    current = _current_stage(ctx)
    stages = ctx.get("stages", [])
    completed_count = sum(1 for s in stages if s.get("status") == "approved")

    conn.close()
    return {
        "run_id": row["run_id"],
        "purpose": row["purpose"],
        "status": row["status"],
        "preset": row["preset"],
        "mode": ctx.get("mode", "default"),
        "content_type": ctx.get("content_type", ""),
        "current_stage": current,
        "stages_completed": completed_count,
        "stages_total": len(stages),
        "revision_count": ctx.get("revision_count", 0),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def cmd_resume(args: argparse.Namespace) -> dict[str, Any]:
    """Resume an interrupted run from the latest successful checkpoint."""
    ad_hoc_run = _load_ad_hoc_run(args.run_id, args.runtime_dir)
    if ad_hoc_run is not None:
        if ad_hoc_run.get("status") in {"completed", "cancelled"}:
            return {"error": f"Cannot resume run in status '{ad_hoc_run.get('status')}'"}

        ctx = ad_hoc_run.get("context_json", {})
        stages = ctx.get("stages", [])
        if not stages:
            return {"error": "Run has no stages to resume"}

        resume_idx = ctx.get("current_stage_index", 0)
        for idx, stage in enumerate(stages):
            if stage.get("status") in {"working", "awaiting-review"}:
                resume_idx = idx
                break
            if stage.get("status") == "approved" and idx + 1 < len(stages):
                resume_idx = idx + 1

        ctx["current_stage_index"] = resume_idx
        if stages[resume_idx].get("status") == "pending":
            stages[resume_idx]["status"] = "working"
            stages[resume_idx].setdefault("stage_started_at", _now())
        ctx["stages"] = stages

        ad_hoc_run["context_json"] = ctx
        ad_hoc_run["status"] = "in-progress"
        ad_hoc_run["updated_at"] = _now()
        _save_ad_hoc_run(ad_hoc_run, args.runtime_dir)

        return {
            "run_id": args.run_id,
            "status": "in-progress",
            "resumed_stage_index": resume_idx,
            "resumed_stage": stages[resume_idx],
            "persisted": False,
            "mode": "ad-hoc",
        }

    conn = connect_db(args.db)
    row = conn.execute("SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    if row["status"] in {"completed", "cancelled"}:
        conn.close()
        return {"error": f"Cannot resume run in status '{row['status']}'"}

    ctx = _parse_context(row)
    stages = ctx.get("stages", [])
    if not stages:
        conn.close()
        return {"error": "Run has no stages to resume"}

    resume_idx = ctx.get("current_stage_index", 0)
    for idx, stage in enumerate(stages):
        if stage.get("status") in {"working", "awaiting-review"}:
            resume_idx = idx
            break
        if stage.get("status") == "approved" and idx + 1 < len(stages):
            resume_idx = idx + 1

    ctx["current_stage_index"] = resume_idx
    if stages[resume_idx].get("status") == "pending":
        stages[resume_idx]["status"] = "working"
        stages[resume_idx].setdefault("stage_started_at", _now())
    ctx["stages"] = stages

    now = _now()
    conn.execute(
        "UPDATE production_runs SET context_json = ?, status = 'in-progress', updated_at = ? WHERE run_id = ?",
        (json.dumps(ctx), now, args.run_id),
    )
    conn.commit()
    conn.close()

    return {
        "run_id": args.run_id,
        "status": "in-progress",
        "resumed_stage_index": resume_idx,
        "resumed_stage": stages[resume_idx],
        "persisted": True,
        "mode": ctx.get("mode", "default"),
    }


def cmd_list(args: argparse.Namespace) -> dict[str, Any]:
    """List active or recent production runs."""
    conn = connect_db(args.db)
    if args.all:
        rows = conn.execute(
            "SELECT * FROM production_runs ORDER BY updated_at DESC LIMIT ?",
            (args.limit or 20,),
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT * FROM production_runs
               WHERE status NOT IN ('completed', 'cancelled')
               ORDER BY updated_at DESC LIMIT ?""",
            (args.limit or 20,),
        ).fetchall()
    conn.close()

    runs = []
    for r in rows:
        try:
            ctx = json.loads(r["context_json"]) if r["context_json"] else {}
        except (json.JSONDecodeError, TypeError):
            ctx = {}
        runs.append({
            "run_id": r["run_id"],
            "purpose": r["purpose"],
            "status": r["status"],
            "content_type": ctx.get("content_type", ""),
            "updated_at": r["updated_at"],
            "persisted": True,
        })

    # Include ad-hoc transient runs in list output.
    for path in sorted(_ad_hoc_runs_dir(args.runtime_dir).glob("*.json")):
        try:
            run = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue

        status = run.get("status", "planning")
        if not args.all and status in {"completed", "cancelled"}:
            continue

        ctx = run.get("context_json", {})
        runs.append(
            {
                "run_id": run.get("run_id", path.stem),
                "purpose": run.get("purpose", ""),
                "status": status,
                "content_type": ctx.get("content_type", ""),
                "updated_at": run.get("updated_at"),
                "persisted": False,
                "mode": "ad-hoc",
            }
        )

    runs.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    if args.limit:
        runs = runs[: args.limit]

    return {"runs": runs, "count": len(runs)}


# ── CLI ───────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Production run lifecycle management",
    )
    parser.add_argument("--db", help="Override database path")
    parser.add_argument("--runtime-dir", help="Override runtime dir for transient baton files")
    sub = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = sub.add_parser("create", help="Create a new production run")
    p_create.add_argument("--run-id", help="Explicit run ID (auto-generated if omitted)")
    p_create.add_argument("--purpose", help="Human-readable run purpose")
    p_create.add_argument("--content-type", help="Content type (lecture-slides, assessment, etc.)")
    p_create.add_argument("--course", help="Course code (e.g. C1)")
    p_create.add_argument("--module", help="Module ID (e.g. M2)")
    p_create.add_argument("--lesson", help="Lesson ID (e.g. L3)")
    p_create.add_argument(
        "--preset", default="draft",
        help="Run preset (explore/draft/production/regulated)",
    )
    p_create.add_argument("--mode", default="default", help="Run mode (default/ad-hoc)")
    p_create.add_argument("--stages-json", help="JSON array of stage objects")

    # advance
    p_advance = sub.add_parser("advance", help="Advance to next stage")
    p_advance.add_argument("run_id", help="Production run ID")

    # checkpoint
    p_cp = sub.add_parser("checkpoint", help="Mark current stage for human review")
    p_cp.add_argument("run_id", help="Production run ID")

    # approve
    p_approve = sub.add_parser("approve", help="Approve current checkpoint")
    p_approve.add_argument("run_id", help="Production run ID")
    p_approve.add_argument("--score", type=float, help="Quality score (0.0-1.0)")

    # complete
    p_complete = sub.add_parser("complete", help="Finalize a production run")
    p_complete.add_argument("run_id", help="Production run ID")

    # cancel
    p_cancel = sub.add_parser("cancel", help="Cancel a production run")
    p_cancel.add_argument("run_id", help="Production run ID")

    # status
    p_status = sub.add_parser("status", help="Query run state")
    p_status.add_argument("run_id", help="Production run ID")

    # resume
    p_resume = sub.add_parser("resume", help="Resume run from latest checkpoint")
    p_resume.add_argument("run_id", help="Production run ID")

    # list
    p_list = sub.add_parser("list", help="List production runs")
    p_list.add_argument("--all", action="store_true", help="Include completed/cancelled runs")
    p_list.add_argument("--limit", type=int, default=20, help="Max results")

    return parser


COMMANDS = {
    "create": cmd_create,
    "advance": cmd_advance,
    "checkpoint": cmd_checkpoint,
    "approve": cmd_approve,
    "complete": cmd_complete,
    "cancel": cmd_cancel,
    "status": cmd_status,
    "resume": cmd_resume,
    "list": cmd_list,
}


def main(argv: list[str] | None = None) -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler = COMMANDS[args.command]
    result = handler(args)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
