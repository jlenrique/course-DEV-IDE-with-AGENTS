# /// script
# requires-python = ">=3.10"
# ///
"""Quality gate coordination for production runs.

Coordinates automated checks, reviewer scoring, override handling,
and observability/audit logging for stage gates.
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

import yaml

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


def _quality_scripts() -> tuple[ModuleType, ModuleType, ModuleType]:
    root = project_root()
    base = root / "skills" / "quality-control" / "scripts"
    accessibility = _load_module(
        "skills.quality_control.scripts.accessibility_checker",
        base / "accessibility_checker.py",
    )
    brand = _load_module(
        "skills.quality_control.scripts.brand_validator",
        base / "brand_validator.py",
    )
    logger = _load_module(
        "skills.quality_control.scripts.quality_logger",
        base / "quality_logger.py",
    )
    return accessibility, brand, logger


def _load_policies(path: Path | None = None) -> tuple[dict[str, Any], str | None]:
    policy_path = path or (project_root() / "state" / "config" / "tool_policies.yaml")
    if not policy_path.exists():
        return {}, None
    try:
        return yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}, None
    except Exception as exc:
        error = f"Failed to load policy file '{policy_path}': {exc}"
        print(error, file=sys.stderr)
        return {}, error


def _connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path else project_root() / "state" / "runtime" / "coordination.db"
    if not path.exists():
        raise FileNotFoundError(f"Database not found: {path}")
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    return conn


def _get_run_preset(conn: sqlite3.Connection, run_id: str) -> str:
    row = conn.execute("SELECT preset FROM production_runs WHERE run_id = ?", (run_id,)).fetchone()
    if not row:
        return "draft"
    return str(row["preset"] or "draft")


def _is_human_checkpoint_stage(stage: str) -> bool:
    stage_l = stage.strip().lower()
    return stage_l in {
        "creative-direction",
        "creative_direction",
        "creative direction",
        "final-approval",
        "final_approval",
        "final approval",
        "checkpoint",
    }


def _log_decision_audit(
    *,
    run_id: str,
    stage: str,
    decision: str,
    reason: str,
    run_mode: str,
    payload: dict[str, Any],
    db_path: Path | str | None,
) -> dict[str, Any]:
    guard = enforce_ad_hoc_boundary("coordination_audit_db", run_mode)
    if not guard["allowed"]:
        return {
            "logged": False,
            "code": guard["code"],
            "reason": guard["reason"],
        }

    try:
        conn = _connect(db_path)
    except FileNotFoundError:
        return {"logged": False, "reason": "Database not found"}

    try:
        conn.execute(
            """
            INSERT INTO agent_coordination (run_id, agent_name, action, payload_json, timestamp)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                run_id,
                "quality-gate-coordinator",
                "quality_gate_decision",
                json.dumps(
                    {
                        "stage": stage,
                        "decision": decision,
                        "reason": reason,
                        "payload": payload,
                    }
                ),
                _now(),
            ),
        )
        conn.commit()
        event_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    finally:
        conn.close()

    return {"logged": True, "event_id": event_id}


def evaluate_quality_gate(
    *,
    run_id: str,
    stage: str,
    reviewer_score: float,
    content: str | None = None,
    content_path: str | Path | None = None,
    reviewer: str = "quality-reviewer",
    run_mode: str | None = None,
    override: bool = False,
    override_reason: str = "",
    decision_point: bool = False,
    db_path: Path | str | None = None,
    style_bible_path: Path | None = None,
    fidelity_counts: tuple[int, int, int] = (0, 0, 0),
    agent_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a stage quality gate with policy-aware checks."""
    mode = resolve_run_mode(run_mode)
    policy_data, policy_load_error = _load_policies()

    preset = "draft"
    try:
        conn = _connect(db_path)
        try:
            preset = _get_run_preset(conn, run_id)
        finally:
            conn.close()
    except FileNotFoundError:
        preset = "draft"

    run_presets = policy_data.get("run_presets", {}) if isinstance(policy_data, dict) else {}
    preset_policy = run_presets.get(preset, run_presets.get("draft", {}))
    threshold = float(preset_policy.get("quality_threshold", 0.7))

    content_text = content
    if content_text is None and content_path:
        path = Path(content_path)
        content_text = path.read_text(encoding="utf-8") if path.exists() else ""
    if content_text is None:
        content_text = ""

    accessibility_mod, brand_mod, quality_logger_mod = _quality_scripts()

    accessibility_result: dict[str, Any] | None = None
    if preset_policy.get("accessibility_check", False):
        accessibility_result = accessibility_mod.run_accessibility_check(content_text)

    brand_result: dict[str, Any] | None = None
    if preset_policy.get("brand_consistency_check", False):
        brand_result = brand_mod.run_brand_validation(
            content_text,
            style_bible_path=style_bible_path,
        )

    findings: list[dict[str, Any]] = []
    if accessibility_result:
        findings.extend(accessibility_result.get("findings", []))
    if brand_result:
        findings.extend(brand_result.get("findings", []))

    component_scores: dict[str, float] = {"reviewer": float(reviewer_score)}
    if accessibility_result:
        component_scores["accessibility"] = (
            1.0 if accessibility_result.get("status") == "pass" else 0.0
        )
    if brand_result:
        component_scores["brand"] = float(brand_result.get("compliance_score", 0.0))

    overall_score = round(sum(component_scores.values()) / len(component_scores), 4)
    has_critical = any(f.get("severity") == "critical" for f in findings)

    gate_pass = overall_score >= threshold and not has_critical
    decision = "pass" if gate_pass else "fail"
    reason = f"score={overall_score} threshold={threshold} critical={has_critical}"

    if not gate_pass and override:
        decision = "override-pass"
        gate_pass = True
        reason = override_reason or "human override applied"

    checkpoint_required = bool(preset_policy.get("human_review", False)) and (
        decision_point or _is_human_checkpoint_stage(stage)
    )

    if gate_pass and checkpoint_required:
        workflow_action = "human-checkpoint"
    elif gate_pass:
        workflow_action = "proceed"
    else:
        workflow_action = "revise"

    quality_status = "pass" if gate_pass else "fail"
    log_result = quality_logger_mod.log_quality_result(
        run_id=run_id,
        stage=stage,
        status=quality_status,
        reviewer=reviewer,
        findings=findings,
        score=overall_score,
        run_mode=mode,
        db_path=Path(db_path) if db_path else None,
    )

    audit_payload = {
        "decision": decision,
        "workflow_action": workflow_action,
        "overall_score": overall_score,
        "threshold": threshold,
        "override": bool(override),
        "findings_count": len(findings),
    }
    audit_result = _log_decision_audit(
        run_id=run_id,
        stage=stage,
        decision=decision,
        reason=reason,
        run_mode=mode,
        payload=audit_payload,
        db_path=db_path,
    )

    try:
        from observability_hooks import record_gate_result

        obs_result = record_gate_result(
            run_id=run_id,
            gate=stage,
            fidelity_o_count=fidelity_counts[0],
            fidelity_i_count=fidelity_counts[1],
            fidelity_a_count=fidelity_counts[2],
            quality_scores=component_scores,
            agent_metrics=agent_metrics or {},
            run_mode=mode,
            payload={
                "passed": gate_pass,
                "decision": decision,
                "workflow_action": workflow_action,
                "override_reason": override_reason if override else "",
            },
            db_path=str(db_path) if db_path else None,
        )
    except Exception:
        obs_result = {"logged": False, "reason": "observability hook unavailable"}

    return {
        "run_id": run_id,
        "stage": stage,
        "run_mode": mode,
        "preset": preset,
        "threshold": threshold,
        "decision": decision,
        "reason": reason,
        "workflow_action": workflow_action,
        "can_override": not gate_pass,
        "override_applied": bool(override and decision == "override-pass"),
        "human_checkpoint_required": checkpoint_required,
        "quality": {
            "reviewer": reviewer,
            "overall_score": overall_score,
            "component_scores": component_scores,
            "status": quality_status,
            "findings": findings,
            "accessibility": accessibility_result,
            "brand": brand_result,
        },
        "quality_log": log_result,
        "audit_log": audit_result,
        "observability": obs_result,
        "orchestrator_options": (
            ["proceed"]
            if gate_pass and not checkpoint_required
            else ["request-revision", "override-with-rationale", "adjust-plan"]
            if not gate_pass
            else ["present-for-human-approval", "override-with-rationale"]
        ),
        "policy_load_error": policy_load_error,
        "recorded_at": _now(),
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Coordinate quality gate decisions")
    parser.add_argument("--db", help="Override coordination database path")
    parser.add_argument("--style-bible", help="Optional style bible path")

    sub = parser.add_subparsers(dest="command", required=True)

    p_eval = sub.add_parser("evaluate", help="Evaluate a stage gate")
    p_eval.add_argument("--run-id", required=True)
    p_eval.add_argument("--stage", required=True)
    p_eval.add_argument("--reviewer-score", type=float, required=True)
    p_eval.add_argument("--reviewer", default="quality-reviewer")
    p_eval.add_argument("--content", help="Inline content string")
    p_eval.add_argument("--content-path", help="Content file path")
    p_eval.add_argument("--run-mode", default=None)
    p_eval.add_argument("--override", action="store_true")
    p_eval.add_argument("--override-reason", default="")
    p_eval.add_argument("--decision-point", action="store_true")
    p_eval.add_argument("--o", type=int, default=0, help="Fidelity omissions count")
    p_eval.add_argument("--i", type=int, default=0, help="Fidelity inventions count")
    p_eval.add_argument("--a", type=int, default=0, help="Fidelity alterations count")
    p_eval.add_argument("--agent-metrics", default="{}", help="JSON object")

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "evaluate":
        result = evaluate_quality_gate(
            run_id=args.run_id,
            stage=args.stage,
            reviewer_score=args.reviewer_score,
            content=args.content,
            content_path=args.content_path,
            reviewer=args.reviewer,
            run_mode=args.run_mode,
            override=args.override,
            override_reason=args.override_reason,
            decision_point=args.decision_point,
            db_path=args.db,
            style_bible_path=Path(args.style_bible) if args.style_bible else None,
            fidelity_counts=(args.o, args.i, args.a),
            agent_metrics=json.loads(args.agent_metrics),
        )
    else:
        result = {"error": f"Unknown command: {args.command}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
