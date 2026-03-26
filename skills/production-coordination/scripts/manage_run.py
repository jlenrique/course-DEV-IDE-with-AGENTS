# /// script
# requires-python = ">=3.10"
# ///
"""Production run lifecycle management.

CLI tool for creating, advancing, and querying production runs in the
coordination database. Outputs JSON for agent consumption.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


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


# ── Commands ──────────────────────────────────────────────────────────


def cmd_create(args: argparse.Namespace) -> dict[str, Any]:
    """Create a new production run."""
    conn = connect_db(args.db)
    now = _now()

    stages = []
    if args.stages_json:
        stages = json.loads(args.stages_json)
    for s in stages:
        s.setdefault("status", "pending")

    context = {
        "content_type": args.content_type or "unknown",
        "module": args.module or "",
        "lesson": args.lesson or "",
        "learning_objectives": [],
        "mode": args.mode or "default",
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

    try:
        conn.execute(
            """INSERT INTO production_runs
               (run_id, purpose, status, preset, context_json,
                course_code, module_id, started_at, created_at, updated_at)
               VALUES (?, ?, 'planning', ?, ?, ?, ?, ?, ?, ?)""",
            (
                run_id,
                args.purpose or f"Production run for {args.content_type}",
                args.preset or "draft",
                json.dumps(context),
                args.course or "",
                args.module or "",
                now, now, now,
            ),
        )
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
    }


def cmd_advance(args: argparse.Namespace) -> dict[str, Any]:
    """Advance a run to the next stage."""
    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    ctx = _parse_context(row)
    stages = ctx.get("stages", [])
    idx = ctx.get("current_stage_index", 0)

    if idx < len(stages):
        stages[idx]["status"] = "approved"

    next_idx = idx + 1
    if next_idx >= len(stages):
        conn.close()
        return {"error": "Already at final stage — use 'complete' to finalize the run"}

    stages[next_idx]["status"] = "working"
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

    return {
        "run_id": args.run_id,
        "status": run_status,
        "advanced_to": stages[next_idx],
        "stage_index": next_idx,
        "stages_total": len(stages),
    }


def cmd_checkpoint(args: argparse.Namespace) -> dict[str, Any]:
    """Mark the current stage as awaiting human review."""
    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    ctx = _parse_context(row)
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
    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    ctx = _parse_context(row)
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
    conn = connect_db(args.db)
    row = conn.execute(
        "SELECT * FROM production_runs WHERE run_id = ?", (args.run_id,)
    ).fetchone()
    if not row:
        conn.close()
        return {"error": f"Run not found: {args.run_id}"}

    ctx = _parse_context(row)
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

    return {
        "run_id": args.run_id,
        "status": "completed",
        "completed_at": now,
        "stages_count": len(stages),
    }


def cmd_status(args: argparse.Namespace) -> dict[str, Any]:
    """Query current state of a production run."""
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
        ctx = json.loads(r["context_json"]) if r["context_json"] else {}
        runs.append({
            "run_id": r["run_id"],
            "purpose": r["purpose"],
            "status": r["status"],
            "content_type": ctx.get("content_type", ""),
            "updated_at": r["updated_at"],
        })

    return {"runs": runs, "count": len(runs)}


# ── CLI ───────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Production run lifecycle management",
    )
    parser.add_argument("--db", help="Override database path")
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

    # status
    p_status = sub.add_parser("status", help="Query run state")
    p_status.add_argument("run_id", help="Production run ID")

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
    "status": cmd_status,
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
