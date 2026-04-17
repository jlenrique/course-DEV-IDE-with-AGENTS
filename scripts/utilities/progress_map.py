"""Progress Map — 'You Are Here' report for HIL oversight.

Parses sprint-status.yaml, SESSION-HANDOFF.md, and next-session-start-here.md
to produce a compact orientation report showing completed work, active work,
and upcoming milestones relative to the full development plan.

Usage:
    .venv/Scripts/python -m scripts.utilities.progress_map
    .venv/Scripts/python -m scripts.utilities.progress_map --json

Text reports are also written to ``reports/progress-map-latest.txt`` (gitignored
``reports/`` folder) unless ``--no-latest-file`` is set.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.file_helpers import project_root

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ROOT = project_root()
LATEST_TEXT_REPORT = ROOT / "reports" / "progress-map-latest.txt"
SPRINT_STATUS = ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"
SESSION_HANDOFF = ROOT / "SESSION-HANDOFF.md"
NEXT_SESSION = ROOT / "next-session-start-here.md"

# ---------------------------------------------------------------------------
# Status classification
# ---------------------------------------------------------------------------

DONE_STATUSES = {"done"}
REVIEW_STATUSES = {"review"}
IN_PROGRESS_STATUSES = {"in-progress"}
READY_STATUSES = {"ready-for-dev"}
ACTIVE_STATUSES = IN_PROGRESS_STATUSES | READY_STATUSES | REVIEW_STATUSES
DEFERRED_STATUSES = {"deferred"}
BACKLOG_STATUSES = {"backlog"}

ALL_KNOWN_STATUSES = (
    DONE_STATUSES
    | REVIEW_STATUSES
    | ACTIVE_STATUSES
    | DEFERRED_STATUSES
    | BACKLOG_STATUSES
)

WAVE_LABELS: dict[str, str] = {
    "1": "Repository & Agent Infrastructure",
    "2": "Master Agent & Fidelity Assurance",
    "2a": "Fidelity Assurance & APP Intel",
    "3": "Tool Specialist Agents",
    "4a": "Governance & Quality",
    "4": "Workflow Coordination",
    "5": "Tool Expansion",
    "6": "LMS Integration",
    "g": "Governance Synthesis",
    "10": "Strategic Production",
    "11": "Trial Remediation",
    "sb": "Storyboard Run View",
    "12": "Double-Dispatch",
    "13": "Visual-Aware Irene Pass 2",
    "14": "Motion-Enhanced Workflow",
    "15": "Learning & Compound Intel",
    "16": "Autonomy Expansion",
    "17": "Research & Reference",
    "18": "Additional Asset Families",
    "19": "Cluster Schema & Manifest",
    "20a": "Cluster Decision & Planning",
    "20b": "Cluster Implementation",
    "20c": "Cluster Intel + Creative Control",
    "21": "Cluster Visual Design",
    "22": "Storyboard Phase 2",
    "23": "Cluster-Aware Narration",
    "24": "Assembly & Regression",
}

# ---------------------------------------------------------------------------
# Source qualification
# ---------------------------------------------------------------------------

_STALENESS_DAYS = 14
_MIN_MARKDOWN_CHARS = 50


def _qualify_sprint_status() -> list[dict[str, Any]]:
    """Qualify sprint-status.yaml — the critical data source."""
    findings: list[dict[str, Any]] = []
    src = str(SPRINT_STATUS)

    # 1. Existence
    if not SPRINT_STATUS.exists():
        findings.append({"source": src, "level": "error",
                         "check": "exists", "message": "File not found"})
        return findings  # nothing else to check
    findings.append({"source": src, "level": "ok",
                     "check": "exists", "message": "File found"})

    # 2. Valid YAML
    try:
        with SPRINT_STATUS.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        findings.append({"source": src, "level": "error",
                         "check": "yaml_parse", "message": f"YAML parse error: {exc}"})
        return findings
    if not isinstance(data, dict):
        findings.append({"source": src, "level": "error",
                         "check": "yaml_parse", "message": "Root is not a mapping"})
        return findings
    findings.append({"source": src, "level": "ok",
                     "check": "yaml_parse", "message": "Valid YAML"})

    # 3. development_status key present and populated
    dev = data.get("development_status")
    if not isinstance(dev, dict) or len(dev) == 0:
        findings.append({"source": src, "level": "error",
                         "check": "dev_status_key",
                         "message": "Missing or empty 'development_status' block"})
    else:
        findings.append({"source": src, "level": "ok",
                         "check": "dev_status_key",
                         "message": f"development_status contains {len(dev)} entries"})

        # 4. At least one epic
        epic_keys = [k for k in dev if k.startswith("epic-") and not k.endswith("-retrospective")]
        if not epic_keys:
            findings.append({"source": src, "level": "error",
                             "check": "epic_presence",
                             "message": "No epic-* keys found in development_status"})
        else:
            findings.append({"source": src, "level": "ok",
                             "check": "epic_presence",
                             "message": f"{len(epic_keys)} epics found"})

        # 5. Unknown status values
        known = ALL_KNOWN_STATUSES | {"optional"}  # retrospective uses 'optional'
        non_epic_keys = [k for k in dev if not k.startswith("epic-") and not k.endswith("-retrospective")]
        unknown_pairs = [(k, str(v)) for k, v in dev.items()
                         if not k.startswith("epic-")
                         and not k.endswith("-retrospective")
                         and str(v) not in known]
        if unknown_pairs:
            samples = ", ".join(f"{k}={v}" for k, v in unknown_pairs[:5])
            findings.append({"source": src, "level": "warn",
                             "check": "status_vocab",
                             "message": f"{len(unknown_pairs)} unknown status value(s): {samples}"})
        else:
            findings.append({"source": src, "level": "ok",
                             "check": "status_vocab",
                             "message": "All status values recognized"})

    # 6. last_updated freshness
    raw_date = str(data.get("last_updated", "")).split("#")[0].strip()
    if not raw_date:
        findings.append({"source": src, "level": "warn",
                         "check": "last_updated",
                         "message": "No last_updated field"})
    else:
        try:
            updated_date = datetime.strptime(raw_date[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            age_days = (datetime.now(tz=timezone.utc) - updated_date).days
            if age_days > _STALENESS_DAYS:
                findings.append({"source": src, "level": "warn",
                                 "check": "staleness",
                                 "message": f"last_updated is {age_days} days old (threshold: {_STALENESS_DAYS})"})
            else:
                findings.append({"source": src, "level": "ok",
                                 "check": "staleness",
                                 "message": f"Updated {age_days} day(s) ago"})
        except ValueError:
            findings.append({"source": src, "level": "warn",
                             "check": "last_updated",
                             "message": f"Cannot parse date from '{raw_date}'"})

    return findings


def _qualify_markdown(filepath: Path, expected_headings: list[str]) -> list[dict[str, Any]]:
    """Qualify a markdown context source."""
    findings: list[dict[str, Any]] = []
    src = str(filepath)

    # 1. Existence
    if not filepath.exists():
        findings.append({"source": src, "level": "warn",
                         "check": "exists", "message": "File not found"})
        return findings
    findings.append({"source": src, "level": "ok",
                     "check": "exists", "message": "File found"})

    # 2. Non-trivial content
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception as exc:
        findings.append({"source": src, "level": "warn",
                         "check": "readable", "message": f"Read error: {exc}"})
        return findings

    if len(text.strip()) < _MIN_MARKDOWN_CHARS:
        findings.append({"source": src, "level": "warn",
                         "check": "content_size",
                         "message": f"Content too small ({len(text.strip())} chars, min {_MIN_MARKDOWN_CHARS})"})
    else:
        findings.append({"source": src, "level": "ok",
                         "check": "content_size",
                         "message": f"{len(text.strip())} chars"})

    # 3. Expected headings
    found = [h for h in expected_headings if re.search(rf"^##\s+{re.escape(h)}", text, re.MULTILINE)]
    missing = [h for h in expected_headings if h not in found]
    if missing:
        findings.append({"source": src, "level": "warn",
                         "check": "headings",
                         "message": f"Missing expected heading(s): {', '.join(missing)}"})
    else:
        findings.append({"source": src, "level": "ok",
                         "check": "headings",
                         "message": f"All {len(expected_headings)} expected heading(s) found"})

    return findings


def qualify_sources() -> dict[str, Any]:
    """Run all source qualification checks. Returns structured results."""
    all_findings: list[dict[str, Any]] = []

    all_findings.extend(_qualify_sprint_status())
    all_findings.extend(_qualify_markdown(
        SESSION_HANDOFF, ["What Is Next", "Unresolved Issues"]))
    all_findings.extend(_qualify_markdown(
        NEXT_SESSION, ["Immediate Next Action", "Key Risks / Unresolved Issues"]))

    handoff_next = _extract_section(SESSION_HANDOFF, "What Is Next")
    next_action = _extract_section(NEXT_SESSION, "Immediate Next Action")
    if handoff_next and next_action:
        handoff_norm = " ".join(handoff_next.split())
        next_norm = " ".join(next_action.split())
        if handoff_norm != next_norm:
            all_findings.append({
                "source": f"{SESSION_HANDOFF.name} | {NEXT_SESSION.name}",
                "level": "warn",
                "check": "next_step_conflict",
                "message": (
                    "Next-step guidance differs across handoff files; "
                    "next-session-start-here.md should be treated as authoritative."
                ),
            })

    errors = [f for f in all_findings if f["level"] == "error"]
    warnings = [f for f in all_findings if f["level"] == "warn"]

    if errors:
        verdict = "FAIL"
    elif warnings:
        verdict = "DEGRADED"
    else:
        verdict = "CLEAN"

    return {
        "verdict": verdict,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": all_findings,
    }


# ---------------------------------------------------------------------------
# Parse sprint-status.yaml
# ---------------------------------------------------------------------------


def _load_sprint_status() -> dict[str, Any]:
    if not SPRINT_STATUS.exists():
        print(f"ERROR: {SPRINT_STATUS} not found", file=sys.stderr)
        sys.exit(1)
    with SPRINT_STATUS.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def _parse_epics(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract per-epic status summaries from development_status block."""
    dev = data.get("development_status", {})
    if not dev:
        return []

    epics: list[dict[str, Any]] = []
    current_epic: dict[str, Any] | None = None

    for key, val in dev.items():
        if key.startswith("epic-") and not key.endswith("-retrospective"):
            # Flush previous epic
            if current_epic:
                epics.append(current_epic)
            epic_id = key.removeprefix("epic-")
            label = WAVE_LABELS.get(epic_id, f"Epic {epic_id}")
            current_epic = {
                "id": epic_id,
                "label": label,
                "status": str(val),
                "stories": OrderedDict(),
            }
        elif current_epic and not key.endswith("-retrospective"):
            current_epic["stories"][key] = str(val)

    if current_epic:
        epics.append(current_epic)

    return epics


def _classify_epic(epic: dict[str, Any]) -> str:
    """Return a classification bucket: done / active / deferred / backlog."""
    status = epic["status"]
    stories = epic["stories"]
    if status in DONE_STATUSES and all(s in DONE_STATUSES for s in stories.values()):
        return "done"
    if all(s in DEFERRED_STATUSES | BACKLOG_STATUSES for s in stories.values()):
        if all(s in BACKLOG_STATUSES for s in stories.values()):
            return "backlog"
        return "deferred"
    return "active"


def _story_counts(epic: dict[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {
        "done": 0,
        "review": 0,
        "in_progress": 0,
        "ready": 0,
        "deferred": 0,
        "backlog": 0,
        "unknown": 0,
    }
    for val in epic["stories"].values():
        if val in DONE_STATUSES:
            counts["done"] += 1
        elif val in REVIEW_STATUSES:
            counts["review"] += 1
        elif val in IN_PROGRESS_STATUSES:
            counts["in_progress"] += 1
        elif val in READY_STATUSES:
            counts["ready"] += 1
        elif val in DEFERRED_STATUSES:
            counts["deferred"] += 1
        elif val in BACKLOG_STATUSES:
            counts["backlog"] += 1
        else:
            counts["unknown"] += 1
    return counts


# ---------------------------------------------------------------------------
# Parse markdown helpers
# ---------------------------------------------------------------------------


def _extract_section(filepath: Path, heading: str) -> str:
    """Extract the text under a markdown heading (## level)."""
    if not filepath.exists():
        return ""
    text = filepath.read_text(encoding="utf-8")
    pattern = rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_last_updated(data: dict[str, Any]) -> str:
    raw = data.get("last_updated", "")
    return str(raw).split("#")[0].strip() if raw else "unknown"


def _file_timestamp(filepath: Path) -> str | None:
    if not filepath.exists():
        return None
    return datetime.fromtimestamp(filepath.stat().st_mtime, tz=timezone.utc).replace(
        microsecond=0
    ).isoformat()


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------


def build_report(*, json_mode: bool = False) -> dict[str, Any]:
    # Qualify sources first
    source_health = qualify_sources()

    data = _load_sprint_status()
    epics = _parse_epics(data)
    last_updated = _extract_last_updated(data)

    # Buckets
    done_epics = [e for e in epics if _classify_epic(e) == "done"]
    active_epics = [e for e in epics if _classify_epic(e) == "active"]
    deferred_epics = [e for e in epics if _classify_epic(e) == "deferred"]
    backlog_epics = [e for e in epics if _classify_epic(e) == "backlog"]

    # Totals
    total_stories = sum(len(e["stories"]) for e in epics)
    done_stories = sum(_story_counts(e)["done"] for e in epics)
    review_stories = sum(_story_counts(e)["review"] for e in epics)
    in_progress_stories = sum(_story_counts(e)["in_progress"] for e in epics)
    ready_stories = sum(_story_counts(e)["ready"] for e in epics)
    deferred_stories = sum(_story_counts(e)["deferred"] for e in epics)
    backlog_stories = sum(_story_counts(e)["backlog"] for e in epics)

    # Active detail
    active_detail = []
    for e in active_epics:
        counts = _story_counts(e)
        stories_in_review = [
            k for k, v in e["stories"].items() if v == "review"
        ]
        stories_in_progress = [
            k for k, v in e["stories"].items() if v == "in-progress"
        ]
        stories_ready = [
            k for k, v in e["stories"].items() if v == "ready-for-dev"
        ]
        stories_deferred = [
            k for k, v in e["stories"].items() if v == "deferred"
        ]
        active_detail.append({
            "epic_id": e["id"],
            "label": e["label"],
            "status": e["status"],
            "counts": counts,
            "in_review": stories_in_review,
            "in_progress": stories_in_progress,
            "ready_for_dev": stories_ready,
            "deferred": stories_deferred,
        })

    # Context from markdown files
    what_is_next = _extract_section(SESSION_HANDOFF, "What Is Next")
    immediate_action = _extract_section(NEXT_SESSION, "Immediate Next Action")
    unresolved = _extract_section(SESSION_HANDOFF, "Unresolved Issues")
    risks = _extract_section(NEXT_SESSION, "Key Risks / Unresolved Issues")
    next_up = immediate_action or what_is_next

    report = {
        "generated": datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat(),
        "sprint_status_updated": last_updated,
        "source_files": {
            "sprint_status": {
                "path": str(SPRINT_STATUS),
                "file_modified": _file_timestamp(SPRINT_STATUS),
            },
            "session_handoff": {
                "path": str(SESSION_HANDOFF),
                "file_modified": _file_timestamp(SESSION_HANDOFF),
            },
            "next_session": {
                "path": str(NEXT_SESSION),
                "file_modified": _file_timestamp(NEXT_SESSION),
            },
        },
        "source_health": source_health,
        "summary": {
            "total_epics": len(epics),
            "done_epics": len(done_epics),
            "active_epics": len(active_epics),
            "deferred_epics": len(deferred_epics),
            "backlog_epics": len(backlog_epics),
            "total_stories": total_stories,
            "done_stories": done_stories,
            "review_stories": review_stories,
            "in_progress_stories": in_progress_stories,
            "ready_stories": ready_stories,
            "deferred_stories": deferred_stories,
            "backlog_stories": backlog_stories,
            "completion_pct": round(done_stories / total_stories * 100, 1) if total_stories else 0,
        },
        "you_are_here": {
            "active_epics": active_detail,
            "what_is_next": what_is_next,
            "immediate_action": immediate_action,
            "next_up": next_up,
            "next_up_source": "next-session-start-here.md" if immediate_action else (
                "SESSION-HANDOFF.md" if what_is_next else ""
            ),
        },
        "completed_epics": [
            {"id": e["id"], "label": e["label"], "stories": len(e["stories"])}
            for e in done_epics
        ],
        "deferred_epics": [
            {"id": e["id"], "label": e["label"], "stories": len(e["stories"])}
            for e in deferred_epics
        ],
        "backlog_epics": [
            {"id": e["id"], "label": e["label"], "stories": len(e["stories"])}
            for e in backlog_epics
        ],
        "risks": risks or unresolved,
    }
    return report


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def _bar(done: int, near_term: int, remaining: int, width: int = 40) -> str:
    total = done + near_term + remaining
    if total == 0:
        return "[" + " " * width + "]"
    d = round(done / total * width)
    a = round(near_term / total * width)
    r = width - d - a
    return "[" + "█" * d + "▓" * a + "░" * r + "]"


def render_text(report: dict[str, Any]) -> str:
    lines: list[str] = []
    s = report["summary"]
    sh = report["source_health"]

    lines.append("=" * 68)
    lines.append("  PROGRESS MAP — You Are Here")
    lines.append(f"  Generated: {report['generated']}")
    lines.append(f"  Sprint status last updated: {report['sprint_status_updated']}")

    # Source health badge
    verdict = sh["verdict"]
    if verdict == "CLEAN":
        lines.append("  Sources: ✓ STRUCTURALLY CLEAN")
    elif verdict == "DEGRADED":
        lines.append(f"  Sources: ⚠ DEGRADED ({sh['warning_count']} warning(s))")
    else:
        lines.append(f"  Sources: ✖ FAIL ({sh['error_count']} error(s), {sh['warning_count']} warning(s))")

    lines.append("=" * 68)

    # If errors or warnings, show detail block
    non_ok = [f for f in sh["findings"] if f["level"] != "ok"]
    if non_ok:
        lines.append("")
        lines.append("─" * 68)
        lines.append("  SOURCE HEALTH")
        lines.append("─" * 68)
        for f in non_ok:
            icon = "⚠" if f["level"] == "warn" else "✖"
            basename = Path(f["source"]).name
            lines.append(f"  {icon} {basename}: {f['message']}")
        lines.append("")
    lines.append("")

    # Overall bar
    near_term_stories = s["review_stories"] + s["in_progress_stories"] + s["ready_stories"]
    bar = _bar(
        s["done_stories"],
        near_term_stories,
        s["deferred_stories"] + s["backlog_stories"],
    )
    lines.append(f"  Overall: {bar} {s['completion_pct']}%")
    lines.append(
        f"  Stories: {s['done_stories']} done / {s['review_stories']} review / "
        f"{s['in_progress_stories']} in progress / {s['ready_stories']} ready / "
        f"{s['deferred_stories']} deferred / {s['backlog_stories']} backlog"
        f"  (total: {s['total_stories']})"
    )
    lines.append(f"  Epics:   {s['done_epics']} done / {s['active_epics']} active"
                 f" / {s['deferred_epics']} deferred / {s['backlog_epics']} backlog"
                 f"  (total: {s['total_epics']})")
    lines.append("")

    # Completed epics (compact)
    lines.append("─" * 68)
    lines.append("  COMPLETED")
    lines.append("─" * 68)
    for e in report["completed_epics"]:
        lines.append(f"  ✓ Epic {e['id']:>4s}  {e['label']:<45s} ({e['stories']} stories)")
    lines.append("")

    # Active epics (detailed)
    lines.append("─" * 68)
    lines.append("  ★ YOU ARE HERE — Active Work")
    lines.append("─" * 68)
    for ad in report["you_are_here"]["active_epics"]:
        c = ad["counts"]
        total = sum(c.values())
        near_term = c["review"] + c["in_progress"] + c["ready"]
        bar = _bar(c["done"], near_term, c["deferred"] + c["backlog"], width=20)
        lines.append(f"  Epic {ad['epic_id']:>4s}  {ad['label']}")
        lines.append(f"         {bar}  {c['done']}/{total} stories done")
        if ad["in_review"]:
            lines.append(f"         ▸ Review:      {', '.join(ad['in_review'])}")
        if ad["in_progress"]:
            lines.append(f"         ▸ In progress: {', '.join(ad['in_progress'])}")
        if ad["ready_for_dev"]:
            lines.append(f"         ▸ Ready:       {', '.join(ad['ready_for_dev'])}")
        if ad["deferred"]:
            lines.append(f"         ▸ Deferred:    {', '.join(ad['deferred'])}")
        lines.append("")

    # What is next
    next_up = report["you_are_here"].get("next_up", "")
    next_up_source = report["you_are_here"].get("next_up_source", "")
    if next_up:
        lines.append("─" * 68)
        lines.append("  NEXT UP")
        lines.append("─" * 68)
        if next_up_source:
            lines.append(f"  Source: {next_up_source}")
        for line in next_up.splitlines()[:12]:
            lines.append(f"  {line}")
        lines.append("")

    # Deferred / Backlog
    if report["deferred_epics"] or report["backlog_epics"]:
        lines.append("─" * 68)
        lines.append("  HORIZON — Backlog & Deferred")
        lines.append("─" * 68)
        for e in report["deferred_epics"]:
            lines.append(f"  ○ Epic {e['id']:>4s}  {e['label']:<45s} ({e['stories']} stories, deferred)")
        for e in report["backlog_epics"]:
            lines.append(f"  ○ Epic {e['id']:>4s}  {e['label']:<45s} ({e['stories']} stories)")
        lines.append("")

    # Risks
    risks = report.get("risks", "")
    if risks:
        lines.append("─" * 68)
        lines.append("  ⚠ RISKS / UNRESOLVED")
        lines.append("─" * 68)
        for line in risks.splitlines()[:10]:
            lines.append(f"  {line}")
        lines.append("")

    lines.append("=" * 68)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Progress Map: 'You Are Here' development orientation report."
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_mode",
        help="Output raw JSON instead of formatted text.",
    )
    parser.add_argument(
        "--output", "-o", type=str, default=None,
        help="Write report to this file instead of stdout.",
    )
    parser.add_argument(
        "--no-latest-file",
        action="store_true",
        help="Do not write reports/progress-map-latest.txt (text mode only).",
    )
    args = parser.parse_args(argv)

    report = build_report(json_mode=args.json_mode)

    if args.json_mode:
        text = json.dumps(report, indent=2, default=str)
    else:
        text = render_text(report)

    if not args.json_mode and not args.no_latest_file:
        LATEST_TEXT_REPORT.parent.mkdir(parents=True, exist_ok=True)
        LATEST_TEXT_REPORT.write_text(text, encoding="utf-8")

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"Report written to {out}")
    else:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        print(text)


if __name__ == "__main__":
    main()
