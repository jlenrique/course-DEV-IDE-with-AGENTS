"""Run HUD — Heads-Up Display for production runs and dev cycle tracking.

Generates a self-refreshing HTML dashboard that shows:
- Production run pipeline position and gate results
- Dev cycle progress (epics/stories from sprint-status.yaml)
- Critical constants, artifact status, and risk flags

Usage:
    .venv/Scripts/python -m scripts.utilities.run_hud
    .venv/Scripts/python -m scripts.utilities.run_hud --bundle-dir path/to/bundle
    .venv/Scripts/python -m scripts.utilities.run_hud --open

The output HTML auto-refreshes every 10 seconds with scroll-position
and expand/collapse state preserved via sessionStorage.
"""

from __future__ import annotations

import argparse
import html as html_mod
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.file_helpers import project_root
from scripts.utilities.progress_map import build_report as build_progress_report

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = project_root()
HUD_OUTPUT = ROOT / "reports" / "run-hud.html"
BUNDLES_DIR = ROOT / "course-content" / "staging" / "tracked" / "source-bundles"
SPRINT_STATUS = ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"

# ---------------------------------------------------------------------------
# Pipeline step definitions (from prompt pack v4.2)
# SYNC-WITH: docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md
# TODO: Extract to shared pipeline-manifest.yaml for single-source-of-truth
# ---------------------------------------------------------------------------

PIPELINE_STEPS: list[dict[str, str]] = [
    {"id": "01", "name": "Activation + Preflight", "gate": "yes"},
    {"id": "02", "name": "Source Authority Map", "gate": "no"},
    {"id": "02A", "name": "Operator Directives", "gate": "no"},
    {"id": "03", "name": "Ingestion + Evidence Log", "gate": "no"},
    {"id": "04", "name": "Ingestion Quality Gate + Irene Packet", "gate": "yes"},
    {"id": "04.5", "name": "Estimator + Run Constants Lock", "gate": "no"},
    {"id": "05", "name": "Irene Pass 1 + Gate 1 Fidelity", "gate": "yes"},
    {"id": "05B", "name": "Cluster Plan G1.5 Gate", "gate": "yes"},
    {"id": "06", "name": "Pre-Dispatch Package Build", "gate": "no"},
    {"id": "06B", "name": "Literal-Visual Operator Build", "gate": "no"},
    {"id": "07", "name": "Gary Dispatch + Export", "gate": "no"},
    {"id": "07B", "name": "Variant Selection Gate", "gate": "yes"},
    {"id": "07C", "name": "Storyboard A + Gate 2 Approval", "gate": "yes"},
    {"id": "07D", "name": "Gate 2M Motion Designation", "gate": "yes"},
    {"id": "07E", "name": "Motion Generation / Import", "gate": "no"},
    {"id": "07F", "name": "Motion Gate", "gate": "yes"},
    {"id": "08", "name": "Irene Pass 2 + Segment Manifest", "gate": "no"},
    {"id": "08B", "name": "Storyboard B + HIL Review", "gate": "yes"},
    {"id": "09", "name": "Gate 3 - Lock Pass 2 Package", "gate": "yes"},
    {"id": "10", "name": "Fidelity + Quality Pre-Spend", "gate": "yes"},
    {"id": "11", "name": "ElevenLabs Voice Selection HIL", "gate": "yes"},
    {"id": "11B", "name": "ElevenLabs Input Package HIL", "gate": "yes"},
    {"id": "12", "name": "ElevenLabs Audio Generation", "gate": "no"},
    {"id": "13", "name": "Quinn-R Pre-Composition QA", "gate": "yes"},
    {"id": "14", "name": "Compositor Assembly Bundle", "gate": "no"},
    {"id": "15", "name": "Operator Handoff - Descript Ready", "gate": "no"},
]


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------


def _find_latest_bundle(bundles_dir: Path) -> Path | None:
    """Find the most recently modified bundle directory."""
    if not bundles_dir.exists():
        return None
    bundles = sorted(
        [d for d in bundles_dir.iterdir() if d.is_dir()],
        key=lambda d: d.stat().st_mtime,
        reverse=True,
    )
    return bundles[0] if bundles else None


def _load_run_constants(bundle_dir: Path) -> dict[str, Any]:
    """Load run-constants.yaml from a bundle directory."""
    rc_path = bundle_dir / "run-constants.yaml"
    if not rc_path.exists():
        return {}
    with rc_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data if isinstance(data, dict) else {}


def _load_gate_results(bundle_dir: Path) -> list[dict[str, Any]]:
    """Load all gate result sidecars from a bundle's gates/ directory."""
    gates_dir = bundle_dir / "gates"
    if not gates_dir.exists():
        return []
    results = []
    for gate_file in sorted(gates_dir.glob("gate-*-result.yaml")):
        try:
            with gate_file.open(encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                results.append(data)
        except (yaml.YAMLError, OSError):
            continue
    return results


_MAX_ARTIFACTS = 200


def _scan_bundle_artifacts(bundle_dir: Path) -> list[dict[str, str]]:
    """List files in the bundle directory with sizes (capped at _MAX_ARTIFACTS)."""
    artifacts = []
    if not bundle_dir.exists():
        return artifacts
    count = 0
    for f in sorted(bundle_dir.rglob("*")):
        if f.is_file():
            count += 1
            if count > _MAX_ARTIFACTS:
                artifacts.append({
                    "path": f"(+{count - _MAX_ARTIFACTS} more files not shown)",
                    "size": "",
                })
                break
            rel = f.relative_to(bundle_dir)
            size = f.stat().st_size
            if size < 1024:
                size_str = f"{size} B"
            elif size < 1024 * 1024:
                size_str = f"{size / 1024:.1f} KB"
            else:
                size_str = f"{size / (1024 * 1024):.1f} MB"
            artifacts.append({"path": str(rel), "size": size_str})
    return artifacts


def _build_pipeline_state(
    gate_results: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Merge gate results into pipeline step definitions."""
    gate_by_id = {str(g.get("step_id", "")).upper(): g for g in gate_results}

    steps = []
    for step in PIPELINE_STEPS:
        sid = step["id"].upper()
        gate_data = gate_by_id.get(sid)
        merged = {
            "id": step["id"],
            "name": step["name"],
            "is_gate": step["gate"] == "yes",
            "result": gate_data.get("result", "not-started") if gate_data else "not-started",
            "summary": gate_data.get("summary", "") if gate_data else "",
            "timestamp": gate_data.get("timestamp", "") if gate_data else "",
            "duration": gate_data.get("duration_seconds", 0) if gate_data else 0,
            "metrics": gate_data.get("metrics", {}) if gate_data else {},
            "conditions": gate_data.get("conditions", []) if gate_data else [],
            "blockers": gate_data.get("blockers", []) if gate_data else [],
            "evidence": gate_data.get("evidence", "") if gate_data else "",
            "inputs": gate_data.get("inputs", []) if gate_data else [],
            "outputs": gate_data.get("outputs", []) if gate_data else [],
        }
        steps.append(merged)
    return steps


def collect_hud_data(
    bundle_dir: Path | None = None,
    bundles_dir: Path | None = None,
) -> dict[str, Any]:
    """Collect all data needed for the HUD rendering."""
    bdir = bundles_dir or BUNDLES_DIR

    if bundle_dir is None:
        bundle_dir = _find_latest_bundle(bdir)

    run_constants: dict[str, Any] = {}
    gate_results: list[dict[str, Any]] = []
    artifacts: list[dict[str, str]] = []
    bundle_path = ""

    if bundle_dir and bundle_dir.exists():
        run_constants = _load_run_constants(bundle_dir)
        gate_results = _load_gate_results(bundle_dir)
        artifacts = _scan_bundle_artifacts(bundle_dir)
        bundle_path = str(bundle_dir)

    pipeline = _build_pipeline_state(gate_results)

    # Compute pipeline position
    current_step = 0
    for i, step in enumerate(pipeline):
        if step["result"] not in ("not-started",):
            current_step = i + 1

    # Count results
    passed = sum(1 for s in pipeline if s["result"] in ("pass", "conditional-pass"))
    failed = sum(1 for s in pipeline if s["result"] == "fail")
    pending = sum(1 for s in pipeline if s["result"] == "pending")
    warnings = sum(1 for s in pipeline if s["conditions"])

    # Dev cycle data from progress_map
    try:
        dev_report = build_progress_report()
    except Exception:  # noqa: BLE001 — dev panel is supplementary; never crash the HUD
        dev_report = None

    # Source freshness tracking
    now = datetime.now(tz=timezone.utc).replace(microsecond=0)
    source_freshness: dict[str, str] = {}

    def _file_ts(p: Path, label: str) -> None:
        if p.exists():
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).replace(microsecond=0)
            source_freshness[label] = mtime.isoformat()

    _file_ts(SPRINT_STATUS, "sprint-status")
    if bundle_dir and bundle_dir.exists():
        _file_ts(bundle_dir / "run-constants.yaml", "run-constants")
        gates_dir = bundle_dir / "gates"
        if gates_dir.exists():
            gate_files = list(gates_dir.glob("gate-*-result.yaml"))
            if gate_files:
                newest = max(gate_files, key=lambda f: f.stat().st_mtime)
                _file_ts(newest, "gate-sidecars")

    return {
        "generated": now.isoformat(),
        "bundle_path": bundle_path,
        "run_constants": run_constants,
        "pipeline": pipeline,
        "pipeline_summary": {
            "total_steps": len(pipeline),
            "current_step": current_step,
            "passed": passed,
            "failed": failed,
            "pending": pending,
            "warnings": warnings,
        },
        "artifacts": artifacts,
        "dev_report": dev_report,
        "source_freshness": source_freshness,
    }


# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

_STATUS_ICONS = {
    "pass": "&#x2705;",       # green check
    "conditional-pass": "&#x26A0;&#xFE0F;",  # warning
    "fail": "&#x274C;",       # red X
    "skip": "&#x23ED;&#xFE0F;",  # skip
    "pending": "&#x23F3;",    # hourglass
    "not-started": "&#x25CB;",  # open circle
}

_STATUS_CLASSES = {
    "pass": "status-pass",
    "conditional-pass": "status-warn",
    "fail": "status-fail",
    "skip": "status-skip",
    "pending": "status-pending",
    "not-started": "status-idle",
}


def _render_pipeline_step(step: dict[str, Any], is_current: bool) -> str:
    """Render a single pipeline step as HTML."""
    icon = _STATUS_ICONS.get(step["result"], "&#x25CB;")
    css = _STATUS_CLASSES.get(step["result"], "status-idle")
    current_cls = " step-current" if is_current else ""
    gate_badge = ' <span class="gate-badge">GATE</span>' if step["is_gate"] else ""

    detail_html = ""
    if step["summary"]:
        detail_html += f'<div class="step-summary">{_esc(step["summary"])}</div>'
    if step["metrics"]:
        metrics_items = "".join(
            f"<li><strong>{_esc(k)}:</strong> {_esc(str(v))}</li>"
            for k, v in step["metrics"].items()
        )
        detail_html += f'<details><summary>Metrics</summary><ul>{metrics_items}</ul></details>'
    if step["conditions"]:
        cond_items = "".join(f"<li>{_esc(c)}</li>" for c in step["conditions"])
        detail_html += f'<details><summary>Conditions ({len(step["conditions"])})</summary><ul class="warn-list">{cond_items}</ul></details>'
    if step["blockers"]:
        block_items = "".join(f"<li>{_esc(b)}</li>" for b in step["blockers"])
        detail_html += f'<details open><summary>Blockers ({len(step["blockers"])})</summary><ul class="fail-list">{block_items}</ul></details>'
    if step["evidence"]:
        detail_html += f'<details><summary>Evidence</summary><pre class="evidence">{_esc(step["evidence"])}</pre></details>'
    if step["outputs"]:
        out_items = "".join(
            f"<li>{_esc(o['path'] if isinstance(o, dict) else str(o))}</li>"
            for o in step["outputs"]
        )
        detail_html += f'<details><summary>Outputs ({len(step["outputs"])})</summary><ul>{out_items}</ul></details>'

    dur = ""
    if step["duration"]:
        dur = f' <span class="duration">{step["duration"]}s</span>'

    return (
        f'<div class="step {css}{current_cls}">'
        f'<div class="step-header">'
        f'<span class="step-icon">{icon}</span>'
        f'<span class="step-id">{_esc(step["id"])}</span>'
        f'<span class="step-name">{_esc(step["name"])}{gate_badge}{dur}</span>'
        f'</div>'
        f'{detail_html}'
        f'</div>'
    )


def _render_dev_panel(dev_report: dict[str, Any] | None) -> str:
    """Render the dev cycle panel from progress_map data."""
    if not dev_report:
        return '<div class="panel-empty">Dev cycle data unavailable (sprint-status.yaml not found)</div>'

    s = dev_report.get("summary", {})
    pct = s.get("completion_pct", 0)
    bar_w = int(pct * 2)  # 200px max

    # Completed epics
    done_rows = ""
    for e in dev_report.get("completed_epics", []):
        done_rows += (
            f'<tr><td>&#x2705;</td><td>{_esc(e["id"])}</td>'
            f'<td>{_esc(e["label"])}</td><td>{e["stories"]}</td></tr>'
        )

    # Active epics
    active_html = ""
    for ad in dev_report.get("you_are_here", {}).get("active_epics", []):
        c = ad.get("counts", {})
        total = sum(c.values())
        done = c.get("done", 0)
        epic_pct = round(done / total * 100) if total else 0
        bar = int(epic_pct * 1.5)  # 150px max

        details = ""
        if ad.get("in_progress"):
            details += f'<div class="epic-detail">In progress: {", ".join(ad["in_progress"])}</div>'
        if ad.get("ready_for_dev"):
            details += f'<div class="epic-detail">Ready: {", ".join(ad["ready_for_dev"])}</div>'
        if ad.get("deferred"):
            details += f'<div class="epic-detail dim">Deferred: {", ".join(ad["deferred"])}</div>'

        active_html += (
            f'<div class="active-epic">'
            f'<div class="epic-name">Epic {_esc(ad["epic_id"])}: {_esc(ad["label"])}</div>'
            f'<div class="progress-bar-container">'
            f'<div class="progress-bar-fill" style="width:{bar}px"></div>'
            f'<span class="progress-text">{done}/{total} ({epic_pct}%)</span>'
            f'</div>'
            f'{details}'
            f'</div>'
        )

    # Backlog epics
    backlog_rows = ""
    for e in dev_report.get("backlog_epics", []):
        backlog_rows += (
            f'<tr><td>&#x25CB;</td><td>{_esc(e["id"])}</td>'
            f'<td>{_esc(e["label"])}</td><td>{e["stories"]}</td></tr>'
        )

    # Source health
    sh = dev_report.get("source_health", {})
    health_cls = "health-clean" if sh.get("verdict") == "CLEAN" else (
        "health-warn" if sh.get("verdict") == "DEGRADED" else "health-fail"
    )
    health_items = ""
    for f in sh.get("findings", []):
        if f.get("level") != "ok":
            icon = "&#x26A0;&#xFE0F;" if f["level"] == "warn" else "&#x274C;"
            health_items += f'<div class="health-item">{icon} {_esc(f.get("message", ""))}</div>'

    # Risks
    risks_html = ""
    risks = dev_report.get("risks", "")
    if risks:
        risks_html = f'<div class="risks-content">{_esc(risks)}</div>'

    return f"""
    <div class="dev-overview">
      <div class="dev-bar">
        <div class="progress-bar-container wide">
          <div class="progress-bar-fill" style="width:{bar_w}px"></div>
          <span class="progress-text">{pct}% &mdash; {s.get('done_stories',0)}/{s.get('total_stories',0)} stories</span>
        </div>
        <div class="dev-counts">
          {s.get('done_epics',0)} done / {s.get('active_epics',0)} active / {s.get('backlog_epics',0)} backlog epics
        </div>
      </div>
    </div>
    <div class="dev-section">
      <h3>Active Work</h3>
      {active_html or '<div class="dim">No active epics</div>'}
    </div>
    <details>
      <summary>Completed ({len(dev_report.get('completed_epics',[]))} epics)</summary>
      <table class="epic-table"><thead><tr><th></th><th>ID</th><th>Epic</th><th>Stories</th></tr></thead>
      <tbody>{done_rows}</tbody></table>
    </details>
    <details>
      <summary>Backlog ({len(dev_report.get('backlog_epics',[]))} epics)</summary>
      <table class="epic-table"><thead><tr><th></th><th>ID</th><th>Epic</th><th>Stories</th></tr></thead>
      <tbody>{backlog_rows}</tbody></table>
    </details>
    <details class="{health_cls}">
      <summary>Source Health: {sh.get('verdict','UNKNOWN')}</summary>
      {health_items}
    </details>
    {"<details><summary>Risks / Unresolved</summary>" + risks_html + "</details>" if risks_html else ""}
    """


def _render_health_panel(
    pipeline: list[dict[str, Any]],
    dev_report: dict[str, Any] | None,
) -> str:
    """Render the System Health tab content."""
    sections = []

    # Preflight (step 01) — pulled from pipeline
    step_01 = next((s for s in pipeline if s["id"] == "01"), None)
    if step_01 and step_01["result"] != "not-started":
        icon = _STATUS_ICONS.get(step_01["result"], "&#x25CB;")
        css = _STATUS_CLASSES.get(step_01["result"], "status-idle")
        metrics_html = ""
        if step_01["metrics"]:
            for k, v in step_01["metrics"].items():
                val_str = _esc(str(v))
                check_icon = "&#x2705;" if str(v).lower() in ("true", "connected", "pass", "ok") else "&#x26A0;&#xFE0F;"
                metrics_html += f'<div class="health-row">{check_icon} <strong>{_esc(k)}:</strong> {val_str}</div>'
        summary = step_01.get("summary", "")
        sections.append(
            f'<div class="health-section {css}">'
            f'<h4>{icon} Preflight</h4>'
            f'{"<div class=\"step-summary\">" + _esc(summary) + "</div>" if summary else ""}'
            f'{metrics_html}'
            f'{"<div class=\"dim\">Ran: " + _esc(step_01.get("timestamp", "")) + "</div>" if step_01.get("timestamp") else ""}'
            f'</div>'
        )
    else:
        sections.append(
            '<div class="health-section status-idle">'
            '<h4>&#x25CB; Preflight</h4>'
            '<div class="dim">Not yet run</div>'
            '</div>'
        )

    # Source health from dev report
    if dev_report:
        sh = dev_report.get("source_health", {})
        verdict = sh.get("verdict", "UNKNOWN")
        v_icon = {"CLEAN": "&#x2705;", "DEGRADED": "&#x26A0;&#xFE0F;", "FAIL": "&#x274C;"}.get(verdict, "&#x2753;")
        v_cls = {"CLEAN": "status-pass", "DEGRADED": "status-warn", "FAIL": "status-fail"}.get(verdict, "")
        items = ""
        for f in sh.get("findings", []):
            if f.get("level") == "ok":
                items += f'<div class="health-row">&#x2705; {_esc(f.get("check", ""))}: {_esc(f.get("message", ""))}</div>'
            elif f.get("level") == "warn":
                items += f'<div class="health-row">&#x26A0;&#xFE0F; {_esc(f.get("check", ""))}: {_esc(f.get("message", ""))}</div>'
            elif f.get("level") == "error":
                items += f'<div class="health-row">&#x274C; {_esc(f.get("check", ""))}: {_esc(f.get("message", ""))}</div>'
        sections.append(
            f'<div class="health-section {v_cls}">'
            f'<h4>{v_icon} Source Health: {_esc(verdict)}</h4>'
            f'<details><summary>Details ({sh.get("error_count", 0)} errors, {sh.get("warning_count", 0)} warnings)</summary>'
            f'{items}'
            f'</details>'
            f'</div>'
        )

    if not sections:
        return '<div class="panel-empty">No health data available</div>'

    # Overall readiness badge
    has_fail = any("status-fail" in s for s in sections)
    has_warn = any("status-warn" in s for s in sections)
    if has_fail:
        badge = '<span class="badge badge-fail">BLOCKED</span>'
    elif has_warn:
        badge = '<span class="badge badge-warn">DEGRADED</span>'
    else:
        badge = '<span class="badge badge-pass">READY</span>'

    return f'<div class="readiness-badge">{badge}</div>' + "\n".join(sections)


def _esc(text: str) -> str:
    """Escape HTML special characters using stdlib html.escape."""
    return html_mod.escape(text, quote=True)


def render_html(data: dict[str, Any]) -> str:
    """Render the full HUD HTML page."""
    rc = data["run_constants"]
    ps = data["pipeline_summary"]
    pipeline = data["pipeline"]

    run_id = rc.get("RUN_ID", "No active run")
    profile = rc.get("EXPERIENCE_PROFILE", "—")
    source = rc.get("PRIMARY_SOURCE_FILE", "—")
    bundle = data["bundle_path"] or "—"
    pct = round(ps["current_step"] / ps["total_steps"] * 100) if ps["total_steps"] else 0
    bar_w = int(pct * 2)

    # Header status badges
    header_cls = ""
    if ps["failed"] > 0:
        header_cls = "header-fail"
    elif ps["warnings"] > 0:
        header_cls = "header-warn"

    # Pipeline steps HTML
    steps_html = ""
    for i, step in enumerate(pipeline):
        is_current = (i + 1) == ps["current_step"]
        steps_html += _render_pipeline_step(step, is_current)

    # Artifacts
    artifacts_html = ""
    for a in data["artifacts"]:
        artifacts_html += f'<tr><td>{_esc(a["path"])}</td><td>{_esc(a["size"])}</td></tr>'

    # Run constants display
    rc_html = ""
    for k, v in rc.items():
        rc_html += f'<tr><td>{_esc(str(k))}</td><td>{_esc(str(v))}</td></tr>'

    # Dev panel
    dev_html = _render_dev_panel(data.get("dev_report"))

    # System health panel — preflight step + source health
    health_html = _render_health_panel(pipeline, data.get("dev_report"))

    # Freshness bar
    freshness = data.get("source_freshness", {})
    freshness_items = ""
    max_age = 0
    for src_name, ts in freshness.items():
        if ts:
            try:
                age = (datetime.now(tz=timezone.utc) - datetime.fromisoformat(ts)).total_seconds()
            except (ValueError, TypeError):
                age = 9999
            age_str = f"{int(age)}s ago" if age < 120 else f"{int(age / 60)}m ago"
            age_cls = "fresh" if age < 60 else ("stale-warn" if age < 300 else "stale-bad")
            freshness_items += f'<span class="freshness-src {age_cls}">{_esc(src_name)}: {age_str}</span>'
            max_age = max(max_age, age)
    freshness_cls = "fresh" if max_age < 60 else ("stale-warn" if max_age < 300 else "stale-bad")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>HUD &mdash; {_esc(run_id)}</title>
<style>
{_CSS}
</style>
</head>
<body>

<div class="refresh-bar" id="refreshBar"></div>

<div class="freshness-meter {freshness_cls}">
  <span class="freshness-label">Data freshness:</span>
  {freshness_items or '<span class="freshness-src dim">no sources tracked</span>'}
  <span class="freshness-countdown dim">Next refresh: <span id="countdown">10</span>s</span>
</div>

<header class="{header_cls}">
  <div class="header-top">
    <h1>HUD</h1>
    <div class="tab-bar">
      <button class="tab active" data-tab="health" onclick="switchTab('health')">System Health</button>
      <button class="tab" data-tab="production" onclick="switchTab('production')">Production Run</button>
      <button class="tab" data-tab="dev" onclick="switchTab('dev')">Dev Cycle</button>
    </div>
    <button class="panel-show" id="panelShow" onclick="togglePanel()" title="Show Run Context">&#x25C0; Context</button>
  </div>
  <div class="header-meta">
    <span class="meta-item"><strong>Run:</strong> {_esc(run_id)}</span>
    <span class="meta-item"><strong>Profile:</strong> {_esc(profile)}</span>
    <span class="meta-item"><strong>Source:</strong> {_esc(str(source).split('/')[-1] if source != '—' else '—')}</span>
  </div>
</header>

<div class="hud-body">
  <div class="main-content">

    <div id="tab-health" class="tab-content active">
      {health_html}
    </div>

    <div id="tab-production" class="tab-content">
      <div class="pipeline-overview">
        <div class="progress-bar-container wide">
          <div class="progress-bar-fill" style="width:{pct}%"></div>
          <span class="progress-text">Step {ps['current_step']} / {ps['total_steps']} ({pct}%)</span>
        </div>
        <div class="status-badges">
          <span class="badge badge-pass">{ps['passed']} passed</span>
          {"<span class='badge badge-fail'>" + str(ps['failed']) + " FAILED</span>" if ps['failed'] else ""}
          {"<span class='badge badge-warn'>" + str(ps['warnings']) + " warnings</span>" if ps['warnings'] else ""}
          <span class="badge badge-idle">{ps['total_steps'] - ps['current_step']} remaining</span>
        </div>
      </div>

      <div class="pipeline-steps">
        {steps_html}
      </div>
    </div>

    <div id="tab-dev" class="tab-content">
      {dev_html}
    </div>

  </div>

  <aside class="run-context" id="runContext">
    <h3>Run Context <button class="panel-toggle" onclick="togglePanel()" title="Hide panel">&#x2715;</button></h3>
    <div class="context-section">
      <h4>Constants ({len(rc)})</h4>
      <table class="kv-table">
      <tbody>{rc_html}</tbody></table>
    </div>
    <div class="context-section">
      <h4>Bundle</h4>
      <div class="bundle-path">{_esc(bundle)}</div>
    </div>
    <details>
      <summary>Artifacts ({len(data['artifacts'])} files)</summary>
      <table class="kv-table">
      <tbody>{artifacts_html}</tbody></table>
    </details>
  </aside>
</div>

<script>
{_JS}
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
  background: #0f172a; color: #e2e8f0; line-height: 1.5;
  max-width: 1200px; margin: 0 auto; padding: 8px 16px;
}
.hud-body {
  display: grid; grid-template-columns: 1fr 280px; gap: 16px;
}
@media (max-width: 900px) {
  .hud-body { grid-template-columns: 1fr; }
  .run-context { order: -1; }
}
.main-content { min-width: 0; overflow: hidden; }
aside.run-context {
  background: #1a2332; border-radius: 6px; padding: 10px;
  position: sticky; top: 8px; max-height: calc(100vh - 16px);
  overflow-y: auto; overflow-x: hidden; font-size: 0.78rem;
  border: 1px solid #1e293b;
  width: 280px; min-width: 280px; max-width: 280px;
}
aside.run-context table { table-layout: fixed; width: 100%; }
aside.run-context td { word-break: break-all; overflow: hidden; text-overflow: ellipsis; }
aside.run-context h3 { color: #38bdf8; font-size: 0.85rem; margin-bottom: 8px; display: flex; align-items: center; justify-content: space-between; }
.panel-toggle {
  background: none; border: none; color: #64748b; cursor: pointer;
  font-size: 0.8rem; padding: 2px 6px; border-radius: 3px;
}
.panel-toggle:hover { background: #334155; color: #e2e8f0; }
.panel-show {
  display: none; background: #1e293b; border: 1px solid #334155;
  color: #94a3b8; cursor: pointer; font-size: 0.7rem;
  padding: 3px 8px; border-radius: 4px; margin-left: auto;
}
.panel-show:hover { background: #334155; color: #e2e8f0; }
.hud-body.panel-hidden { grid-template-columns: 1fr; }
.hud-body.panel-hidden .run-context { display: none; }
.hud-body.panel-hidden ~ .panel-show,
body:has(.panel-hidden) .panel-show { display: inline-block; }
aside.run-context h4 { color: #94a3b8; font-size: 0.75rem; margin: 8px 0 4px; }
.context-section { margin-bottom: 8px; }
h1 { font-size: 1.1rem; font-weight: 700; color: #38bdf8; }
h3 { font-size: 0.95rem; margin: 12px 0 6px; color: #94a3b8; }

.refresh-bar {
  position: fixed; top: 0; left: 0; height: 2px;
  background: #38bdf8; width: 0; z-index: 999;
  transition: width linear;
}

.freshness-meter {
  display: flex; align-items: center; gap: 12px;
  padding: 4px 8px; font-size: 0.7rem; color: #64748b;
  background: #0c1322; border-bottom: 1px solid #1e293b; margin-bottom: 4px;
}
.freshness-meter.stale-warn { border-bottom-color: #eab308; }
.freshness-meter.stale-bad { border-bottom-color: #ef4444; }
.freshness-label { font-weight: 600; color: #94a3b8; }
.freshness-src { padding: 1px 6px; border-radius: 3px; background: #1e293b; }
.freshness-src.fresh { color: #4ade80; }
.freshness-src.stale-warn { color: #fde047; background: #422006; }
.freshness-src.stale-bad { color: #fca5a5; background: #450a0a; }
.freshness-countdown { margin-left: auto; }

.health-section {
  padding: 8px 10px; margin: 4px 0; border-radius: 4px;
  background: #1e293b; border-left: 3px solid transparent;
}
.health-section h4 { font-size: 0.85rem; margin-bottom: 4px; }
.health-row { font-size: 0.78rem; padding: 2px 0 2px 4px; }
.readiness-badge { margin-bottom: 8px; }

header {
  padding: 8px 0; border-bottom: 1px solid #1e293b; margin-bottom: 12px;
}
header.header-fail { border-bottom: 2px solid #ef4444; }
header.header-warn { border-bottom: 2px solid #eab308; }
.header-top { display: flex; align-items: center; gap: 16px; }
.header-meta { display: flex; gap: 16px; margin-top: 6px; font-size: 0.8rem; }
.meta-item { color: #94a3b8; }
.meta-item strong { color: #cbd5e1; }
.refresh-info { margin-left: auto; font-size: 0.7rem; color: #64748b; text-align: right; }

.tab-bar { display: flex; gap: 4px; }
.tab {
  background: #1e293b; border: 1px solid #334155; color: #94a3b8;
  padding: 4px 12px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;
}
.tab.active { background: #334155; color: #e2e8f0; border-color: #475569; }
.tab:hover { background: #334155; }
.tab-content { display: none; }
.tab-content.active { display: block; }

.pipeline-overview { margin-bottom: 12px; }
.progress-bar-container {
  background: #1e293b; border-radius: 4px; height: 20px;
  position: relative; overflow: hidden;
}
.progress-bar-container.wide { width: 200px; display: inline-block; vertical-align: middle; }
.progress-bar-fill {
  background: linear-gradient(90deg, #22c55e, #38bdf8);
  height: 100%; border-radius: 4px; transition: width 0.3s;
}
.progress-text {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-size: 0.7rem; font-weight: 600; color: #f1f5f9; white-space: nowrap;
}

.status-badges { margin-top: 6px; display: flex; gap: 6px; }
.badge {
  font-size: 0.7rem; padding: 2px 8px; border-radius: 10px; font-weight: 600;
}
.badge-pass { background: #14532d; color: #4ade80; }
.badge-fail { background: #7f1d1d; color: #fca5a5; }
.badge-warn { background: #713f12; color: #fde047; }
.badge-idle { background: #1e293b; color: #64748b; }

.pipeline-steps { display: flex; flex-direction: column; gap: 2px; }
.step {
  padding: 6px 10px; border-radius: 4px; border-left: 3px solid transparent;
  background: #1e293b; font-size: 0.82rem;
}
.step-header { display: flex; align-items: center; gap: 8px; }
.step-icon { font-size: 0.9rem; min-width: 20px; text-align: center; }
.step-id { font-weight: 700; color: #64748b; min-width: 32px; font-size: 0.75rem; }
.step-name { flex: 1; }
.gate-badge {
  font-size: 0.6rem; background: #312e81; color: #a5b4fc; padding: 1px 4px;
  border-radius: 3px; margin-left: 6px; font-weight: 700;
}
.duration { font-size: 0.7rem; color: #64748b; }

.step-current { border-left-color: #38bdf8; background: #172554; }
.status-pass { border-left-color: #22c55e; }
.status-warn { border-left-color: #eab308; }
.status-fail { border-left-color: #ef4444; background: #1c1917; }
.status-pending { border-left-color: #3b82f6; }

.step-summary { font-size: 0.75rem; color: #94a3b8; margin: 4px 0 2px 28px; }

details { margin: 4px 0; font-size: 0.8rem; }
details summary {
  cursor: pointer; padding: 4px 8px; background: #1e293b;
  border-radius: 4px; color: #94a3b8; font-weight: 600;
}
details summary:hover { background: #334155; }
details > ul, details > pre, details > table, details > div {
  padding: 6px 12px; background: #0f172a;
}
ul { list-style: none; padding-left: 12px; }
li::before { content: "\\2022"; color: #475569; margin-right: 6px; }
.warn-list li::before { content: "\\26A0"; color: #eab308; }
.fail-list li::before { content: "\\274C"; color: #ef4444; }

.evidence { white-space: pre-wrap; font-size: 0.75rem; color: #94a3b8; max-height: 200px; overflow-y: auto; }

table { width: 100%; border-collapse: collapse; margin: 4px 0; }
th, td { text-align: left; padding: 3px 8px; font-size: 0.75rem; }
th { color: #64748b; border-bottom: 1px solid #334155; }
td { color: #cbd5e1; border-bottom: 1px solid #1e293b; }
.kv-table td:first-child { color: #94a3b8; font-weight: 600; white-space: nowrap; }
.epic-table td:first-child { width: 24px; text-align: center; }

.bundle-path { font-size: 0.7rem; color: #64748b; padding: 4px 8px; font-family: monospace; }

.dev-overview { margin-bottom: 8px; }
.dev-bar { display: flex; align-items: center; gap: 12px; }
.dev-counts { font-size: 0.75rem; color: #64748b; }
.active-epic { padding: 6px 10px; margin: 4px 0; background: #1e293b; border-radius: 4px; }
.epic-name { font-weight: 600; font-size: 0.82rem; }
.epic-detail { font-size: 0.75rem; color: #94a3b8; margin-left: 8px; }
.dim { color: #475569; }
.panel-empty { padding: 20px; text-align: center; color: #475569; }

.health-clean summary { color: #22c55e; }
.health-warn summary { color: #eab308; }
.health-fail summary { color: #ef4444; }
.health-item { padding: 2px 8px; font-size: 0.75rem; }

.risks-content { white-space: pre-wrap; font-size: 0.75rem; color: #94a3b8; padding: 6px 8px; }
"""

# ---------------------------------------------------------------------------
# JavaScript (scroll preservation + tab switching + refresh bar)
# ---------------------------------------------------------------------------

_JS = """
function togglePanel() {
  var body = document.querySelector('.hud-body');
  var btn = document.getElementById('panelShow');
  if (body.classList.contains('panel-hidden')) {
    body.classList.remove('panel-hidden');
    if (btn) btn.style.display = 'none';
    sessionStorage.setItem('hud_panel', 'visible');
  } else {
    body.classList.add('panel-hidden');
    if (btn) btn.style.display = 'inline-block';
    sessionStorage.setItem('hud_panel', 'hidden');
  }
}

function switchTab(name, noSave) {
  document.querySelectorAll('.tab-content').forEach(function(el) {
    el.classList.remove('active');
  });
  document.querySelectorAll('.tab').forEach(function(el) {
    el.classList.remove('active');
  });
  var target = document.getElementById('tab-' + name);
  if (target) target.classList.add('active');
  document.querySelectorAll('.tab').forEach(function(el) {
    if (el.getAttribute('data-tab') === name) el.classList.add('active');
  });
  if (!noSave) sessionStorage.setItem('hud_tab', name);
}

document.addEventListener('DOMContentLoaded', function() {
  var REFRESH_SECONDS = 10;

  // Restore scroll position
  var savedScroll = sessionStorage.getItem('hud_scroll');
  if (savedScroll) window.scrollTo(0, parseInt(savedScroll));

  // Restore active tab
  var savedTab = sessionStorage.getItem('hud_tab');
  if (savedTab) switchTab(savedTab, true);

  // Restore panel visibility
  var savedPanel = sessionStorage.getItem('hud_panel');
  if (savedPanel === 'hidden') togglePanel();

  // Restore expanded details
  var savedDetails = JSON.parse(sessionStorage.getItem('hud_details') || '{}');
  document.querySelectorAll('details').forEach(function(el, i) {
    if (savedDetails[i] !== undefined) el.open = savedDetails[i];
  });

  // Animate refresh bar
  var bar = document.getElementById('refreshBar');
  if (bar) {
    bar.style.transition = 'width ' + REFRESH_SECONDS + 's linear';
    setTimeout(function() { bar.style.width = '100vw'; }, 50);
  }

  // Countdown timer
  var remaining = REFRESH_SECONDS;
  var cdEl = document.getElementById('countdown');
  if (cdEl) {
    var cdInterval = setInterval(function() {
      remaining--;
      if (cdEl) cdEl.textContent = remaining;
      if (remaining <= 0) clearInterval(cdInterval);
    }, 1000);
  }

  // Schedule refresh with state save
  setTimeout(function() {
    sessionStorage.setItem('hud_scroll', window.scrollY);
    var activeTab = document.querySelector('.tab-content.active');
    if (activeTab) sessionStorage.setItem('hud_tab', activeTab.id.replace('tab-',''));
    var details = {};
    document.querySelectorAll('details').forEach(function(el, i) {
      details[i] = el.open;
    });
    sessionStorage.setItem('hud_details', JSON.stringify(details));
    location.reload();
  }, REFRESH_SECONDS * 1000);
});
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Run HUD: Heads-Up Display for production runs and dev tracking."
    )
    parser.add_argument(
        "--bundle-dir", type=str, default=None,
        help="Path to a specific source bundle directory. Auto-detects latest if omitted.",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Output HTML file path. Defaults to reports/run-hud.html.",
    )
    parser.add_argument(
        "--open", action="store_true",
        help="Open the generated HTML in the default browser.",
    )
    args = parser.parse_args(argv)

    bundle_dir = Path(args.bundle_dir) if args.bundle_dir else None
    output_path = Path(args.output) if args.output else HUD_OUTPUT

    data = collect_hud_data(bundle_dir=bundle_dir)
    html = render_html(data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
    print(f"HUD written to {output_path}")

    if args.open:
        import webbrowser
        webbrowser.open(str(output_path.resolve()))


if __name__ == "__main__":
    main()
