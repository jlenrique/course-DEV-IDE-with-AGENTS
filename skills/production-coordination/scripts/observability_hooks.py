# /// script
# requires-python = ">=3.10"
# ///
"""Observability hooks for production governance and quality reporting."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
from datetime import datetime
from pathlib import Path
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


def _db_path(db_path: str | None = None) -> Path:
    if db_path:
        return Path(db_path)
    return project_root() / "state" / "runtime" / "coordination.db"


def _transient_path(run_id: str) -> Path:
    path = project_root() / "state" / "runtime" / "ad-hoc-observability" / f"{run_id}.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _connect(db_path: str | None = None) -> sqlite3.Connection:
    path = _db_path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS observability_events (
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
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_observability_run
        ON observability_events(run_id)
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_observability_mode
        ON observability_events(run_mode)
        """
    )
    conn.commit()


def _persist_or_transient(event: dict[str, Any], db_path: str | None = None) -> dict[str, Any]:
    guard = enforce_ad_hoc_boundary("observability_db", event.get("run_mode"))
    if not guard["allowed"]:
        path = _transient_path(str(event["run_id"]))
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return {
            "logged": False,
            "transient_logged": True,
            "code": guard["code"],
            "reason": guard["reason"],
            "path": str(path),
            "event": event,
        }

    conn = _connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO observability_events (
                run_id, event_type, gate, run_mode,
                fidelity_o_count, fidelity_i_count, fidelity_a_count,
                quality_scores_json, agent_metrics_json, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["run_id"],
                event["event_type"],
                event.get("gate"),
                event["run_mode"],
                event.get("fidelity_o_count"),
                event.get("fidelity_i_count"),
                event.get("fidelity_a_count"),
                json.dumps(event.get("quality_scores", {})),
                json.dumps(event.get("agent_metrics", {})),
                json.dumps(event.get("payload", {})),
                event["created_at"],
            ),
        )
        conn.commit()
        event_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    finally:
        conn.close()

    return {
        "logged": True,
        "transient_logged": False,
        "event_id": event_id,
        "event": event,
    }


def record_gate_result(
    *,
    run_id: str,
    gate: str,
    fidelity_o_count: int,
    fidelity_i_count: int,
    fidelity_a_count: int,
    quality_scores: dict[str, float] | None = None,
    agent_metrics: dict[str, Any] | None = None,
    run_mode: str | None = None,
    payload: dict[str, Any] | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    event = {
        "run_id": run_id,
        "event_type": "gate_result",
        "gate": gate,
        "run_mode": resolve_run_mode(run_mode),
        "fidelity_o_count": int(fidelity_o_count),
        "fidelity_i_count": int(fidelity_i_count),
        "fidelity_a_count": int(fidelity_a_count),
        "quality_scores": quality_scores or {},
        "agent_metrics": agent_metrics or {},
        "payload": payload or {},
        "created_at": _now(),
    }
    return _persist_or_transient(event, db_path)


def record_lane_violation(
    *,
    run_id: str,
    agent: str,
    dimension: str,
    context: str,
    gate: str | None = None,
    run_mode: str | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    event = {
        "run_id": run_id,
        "event_type": "lane_violation",
        "gate": gate,
        "run_mode": resolve_run_mode(run_mode),
        "fidelity_o_count": 0,
        "fidelity_i_count": 0,
        "fidelity_a_count": 0,
        "quality_scores": {},
        "agent_metrics": {"agent": agent},
        "payload": {
            "agent": agent,
            "dimension": dimension,
            "context": context,
        },
        "created_at": _now(),
    }
    return _persist_or_transient(event, db_path)


def record_cache_event(
    *,
    run_id: str,
    artifact_path: str,
    modality: str,
    hit: bool,
    run_mode: str | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    event = {
        "run_id": run_id,
        "event_type": "cache_hit" if hit else "cache_miss",
        "gate": None,
        "run_mode": resolve_run_mode(run_mode),
        "fidelity_o_count": 0,
        "fidelity_i_count": 0,
        "fidelity_a_count": 0,
        "quality_scores": {},
        "agent_metrics": {},
        "payload": {
            "artifact_path": artifact_path,
            "modality": modality,
        },
        "created_at": _now(),
    }
    return _persist_or_transient(event, db_path)


def summarize_run(run_id: str, db_path: str | None = None) -> dict[str, Any]:
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            """
            SELECT * FROM observability_events
            WHERE run_id = ?
            ORDER BY created_at ASC
            """,
            (run_id,),
        ).fetchall()
    finally:
        conn.close()

    gate_events = [r for r in rows if r["event_type"] == "gate_result"]
    violations = [r for r in rows if r["event_type"] == "lane_violation"]
    cache_events = [r for r in rows if r["event_type"] in {"cache_hit", "cache_miss"}]

    pass_events = 0
    total_events = len(gate_events)
    o_count = 0
    i_count = 0
    a_count = 0
    quality_sums: dict[str, float] = {}
    quality_counts: dict[str, int] = {}

    for row in gate_events:
        o_count += int(row["fidelity_o_count"] or 0)
        i_count += int(row["fidelity_i_count"] or 0)
        a_count += int(row["fidelity_a_count"] or 0)

        payload = json.loads(row["payload_json"] or "{}")
        if payload.get("passed", True):
            pass_events += 1

        quality_scores = json.loads(row["quality_scores_json"] or "{}")
        for key, value in quality_scores.items():
            quality_sums[key] = quality_sums.get(key, 0.0) + float(value)
            quality_counts[key] = quality_counts.get(key, 0) + 1

    quality_averages = {
        key: round(quality_sums[key] / quality_counts[key], 4)
        for key in quality_sums
        if quality_counts[key] > 0
    }

    cache_hit_count = sum(1 for r in cache_events if r["event_type"] == "cache_hit")
    cache_miss_count = sum(1 for r in cache_events if r["event_type"] == "cache_miss")
    cache_total = cache_hit_count + cache_miss_count
    cache_hit_rate = round(cache_hit_count / cache_total, 4) if cache_total else None

    return {
        "run_id": run_id,
        "gate_pass_rate": round(pass_events / total_events, 4) if total_events else None,
        "fidelity_oia": {
            "omissions": o_count,
            "inventions": i_count,
            "alterations": a_count,
        },
        "quality_dimension_averages": quality_averages,
        "governance_findings": [
            {
                "agent": json.loads(r["payload_json"] or "{}").get("agent"),
                "dimension": json.loads(r["payload_json"] or "{}").get("dimension"),
                "context": json.loads(r["payload_json"] or "{}").get("context"),
                "gate": r["gate"],
                "run_mode": r["run_mode"],
                "created_at": r["created_at"],
            }
            for r in violations
        ],
        "cache_metrics": {
            "hits": cache_hit_count,
            "misses": cache_miss_count,
            "hit_rate": cache_hit_rate,
        },
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record and summarize observability events")
    parser.add_argument("--db", help="Override database path")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gate = sub.add_parser("gate", help="Record a gate result")
    p_gate.add_argument("--run-id", required=True)
    p_gate.add_argument("--gate", required=True)
    p_gate.add_argument("--o", type=int, default=0)
    p_gate.add_argument("--i", type=int, default=0)
    p_gate.add_argument("--a", type=int, default=0)
    p_gate.add_argument("--quality-scores", default="{}", help="JSON object")
    p_gate.add_argument("--agent-metrics", default="{}", help="JSON object")
    p_gate.add_argument("--payload", default="{}", help="JSON object")
    p_gate.add_argument("--run-mode", default=None)

    p_lane = sub.add_parser("lane-violation", help="Record a lane boundary violation")
    p_lane.add_argument("--run-id", required=True)
    p_lane.add_argument("--agent", required=True)
    p_lane.add_argument("--dimension", required=True)
    p_lane.add_argument("--context", required=True)
    p_lane.add_argument("--gate", default=None)
    p_lane.add_argument("--run-mode", default=None)

    p_cache = sub.add_parser("cache", help="Record cache hit/miss")
    p_cache.add_argument("--run-id", required=True)
    p_cache.add_argument("--artifact-path", required=True)
    p_cache.add_argument("--modality", required=True)
    p_cache.add_argument("--hit", action="store_true")
    p_cache.add_argument("--run-mode", default=None)

    p_summary = sub.add_parser("summary", help="Summarize run metrics")
    p_summary.add_argument("run_id")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "gate":
        result = record_gate_result(
            run_id=args.run_id,
            gate=args.gate,
            fidelity_o_count=args.o,
            fidelity_i_count=args.i,
            fidelity_a_count=args.a,
            quality_scores=json.loads(args.quality_scores),
            agent_metrics=json.loads(args.agent_metrics),
            run_mode=args.run_mode,
            payload=json.loads(args.payload),
            db_path=args.db,
        )
    elif args.command == "lane-violation":
        result = record_lane_violation(
            run_id=args.run_id,
            agent=args.agent,
            dimension=args.dimension,
            context=args.context,
            gate=args.gate,
            run_mode=args.run_mode,
            db_path=args.db,
        )
    elif args.command == "cache":
        result = record_cache_event(
            run_id=args.run_id,
            artifact_path=args.artifact_path,
            modality=args.modality,
            hit=args.hit,
            run_mode=args.run_mode,
            db_path=args.db,
        )
    else:
        result = summarize_run(args.run_id, db_path=args.db)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
