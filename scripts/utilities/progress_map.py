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
BMM_WORKFLOW = ROOT / "_bmad-output" / "implementation-artifacts" / "bmm-workflow-status.yaml"
STORY_ARTIFACTS_DIR = ROOT / "_bmad-output" / "implementation-artifacts"
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

# ---------------------------------------------------------------------------
# Epic label extraction from sprint-status.yaml comments
# ---------------------------------------------------------------------------
# Sprint-status.yaml contains structured comments like:
#   # === EPIC 20C: Cluster Intelligence + Creative Control (Added ...) ===
# We parse these to derive labels dynamically, eliminating hardcoded dicts.

_EPIC_COMMENT_RE = re.compile(
    r"#\s*===\s*EPIC\s+([^:]+?):\s*(.+?)\s*(?:\([^)]*\)\s*)?===",
    re.IGNORECASE,
)


def _parse_epic_labels_from_comments(filepath: Path) -> dict[str, str]:
    """Parse epic labels from ``# === EPIC {ID}: {LABEL} ===`` comments.

    Returns a dict mapping normalised epic id (lowercase, no spaces) to label.
    """
    labels: dict[str, str] = {}
    if not filepath.exists():
        return labels
    text = filepath.read_text(encoding="utf-8")
    for match in _EPIC_COMMENT_RE.finditer(text):
        raw_id = match.group(1).strip().lower()
        label = match.group(2).strip()
        labels[raw_id] = label
    return labels

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


# Story-ID pattern: e.g. 23-2, 20c-15, 4a-6, sb-1
_STORY_ID_RE = re.compile(r"\b(\d+[a-z]?-\d+|[a-z]+-\d+)\b", re.IGNORECASE)


def _qualify_bmm_workflow(
    sprint_status_path: Path,
    bmm_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Cross-check bmm-workflow-status.yaml next_workflow_step against sprint status.

    If the next_workflow_step mentions story IDs that are already 'done' in
    sprint-status.yaml, flag the field as stale.

    *bmm_path* defaults to the module-level ``BMM_WORKFLOW`` constant when
    not provided explicitly.
    """
    bmm = bmm_path if bmm_path is not None else BMM_WORKFLOW
    findings: list[dict[str, Any]] = []
    src = str(bmm)

    if not bmm.exists():
        findings.append({"source": src, "level": "warn",
                         "check": "bmm_exists",
                         "message": "bmm-workflow-status.yaml not found"})
        return findings

    try:
        with bmm.open(encoding="utf-8") as f:
            bmm_data = yaml.safe_load(f)
    except yaml.YAMLError:
        findings.append({"source": src, "level": "warn",
                         "check": "bmm_parse",
                         "message": "bmm-workflow-status.yaml YAML parse error"})
        return findings

    if not isinstance(bmm_data, dict):
        return findings

    next_step = bmm_data.get("next_workflow_step", "")
    if not next_step:
        findings.append({"source": src, "level": "ok",
                         "check": "bmm_next_step",
                         "message": "No next_workflow_step field"})
        return findings

    # Load sprint status to check story statuses
    if not sprint_status_path.exists():
        return findings

    try:
        with sprint_status_path.open(encoding="utf-8") as f:
            sprint_data = yaml.safe_load(f)
    except yaml.YAMLError:
        return findings

    dev = sprint_data.get("development_status", {}) if isinstance(sprint_data, dict) else {}

    # Extract story IDs mentioned in next_workflow_step
    mentioned = _STORY_ID_RE.findall(str(next_step))
    stale_ids = []
    for sid in mentioned:
        # Normalise: sprint keys use hyphens and lowercase
        normalised = sid.lower()
        # Look for any key containing this story id
        for key, val in dev.items():
            if key.startswith(normalised) and str(val) in DONE_STATUSES:
                stale_ids.append(sid)
                break

    if stale_ids:
        findings.append({
            "source": src,
            "level": "warn",
            "check": "bmm_next_step_stale",
            "message": (
                f"next_workflow_step references completed story(s): "
                f"{', '.join(stale_ids)}. Field may be stale."
            ),
        })
    else:
        findings.append({"source": src, "level": "ok",
                         "check": "bmm_next_step",
                         "message": "next_workflow_step references are current"})

    return findings


# Statuses that should have a corresponding story artifact file
_ARTIFACT_EXPECTED_STATUSES = DONE_STATUSES | IN_PROGRESS_STATUSES | REVIEW_STATUSES


def _spot_check_story_artifacts(
    data: dict[str, Any],
    artifacts_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Check that non-backlog stories have corresponding artifact files.

    Looks for ``{story-key}*.md`` in the artifacts directory.
    Stories in backlog or deferred status are not expected to have artifacts.
    """
    adir = artifacts_dir if artifacts_dir is not None else STORY_ARTIFACTS_DIR
    findings: list[dict[str, Any]] = []

    if not adir.exists():
        findings.append({
            "source": str(adir),
            "level": "warn",
            "check": "artifacts_dir_exists",
            "message": "Story artifacts directory not found",
        })
        return findings

    dev = data.get("development_status", {})
    missing: list[str] = []

    for key, val in dev.items():
        # Skip epic-level keys and retrospectives
        if key.startswith("epic-") or key.endswith("-retrospective"):
            continue
        status = str(val)
        if status not in _ARTIFACT_EXPECTED_STATUSES:
            continue
        # Check for any .md file starting with the story key
        matches = list(adir.glob(f"{key}*.md"))
        if not matches:
            missing.append(key)

    if missing:
        sample = ", ".join(missing[:5])
        suffix = f" (+{len(missing) - 5} more)" if len(missing) > 5 else ""
        findings.append({
            "source": str(adir),
            "level": "warn",
            "check": "story_artifact_missing",
            "message": (
                f"{len(missing)} story(s) with status done/in-progress/review "
                f"have no artifact file: {sample}{suffix}"
            ),
        })
    else:
        findings.append({
            "source": str(adir),
            "level": "ok",
            "check": "story_artifacts",
            "message": "All non-backlog stories have artifact files",
        })

    return findings


def qualify_sources() -> dict[str, Any]:
    """Run all source qualification checks. Returns structured results."""
    all_findings: list[dict[str, Any]] = []

    all_findings.extend(_qualify_sprint_status())
    all_findings.extend(_qualify_markdown(
        SESSION_HANDOFF, ["What Is Next", "Unresolved Issues"]))
    all_findings.extend(_qualify_markdown(
        NEXT_SESSION, ["Immediate Next Action", "Key Risks / Unresolved Issues"]))

    all_findings.extend(_qualify_bmm_workflow(SPRINT_STATUS))

    # Story artifact spot-check (only if sprint-status loaded successfully)
    if SPRINT_STATUS.exists():
        try:
            with SPRINT_STATUS.open(encoding="utf-8") as _f:
                _sprint_data = yaml.safe_load(_f)
            if isinstance(_sprint_data, dict):
                all_findings.extend(_spot_check_story_artifacts(_sprint_data))
        except yaml.YAMLError:
            pass  # already flagged by _qualify_sprint_status

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


def _parse_epics(
    data: dict[str, Any],
    *,
    comment_labels: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Extract per-epic status summaries from development_status block.

    *comment_labels* is an optional dict of epic-id → label parsed from
    sprint-status.yaml comments.  When provided these take precedence over
    the generic ``"Epic {id}"`` fallback.
    """
    dev = data.get("development_status", {})
    if not dev:
        return []

    labels = comment_labels or {}

    epics: list[dict[str, Any]] = []
    current_epic: dict[str, Any] | None = None

    for key, val in dev.items():
        if key.startswith("epic-") and not key.endswith("-retrospective"):
            # Flush previous epic
            if current_epic:
                epics.append(current_epic)
            epic_id = key.removeprefix("epic-")
            label = labels.get(epic_id, f"Epic {epic_id}")
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
    """Extract the text under a markdown heading (## level).

    Uses prefix matching so ``"Unresolved Issues"`` matches both
    ``## Unresolved Issues`` and ``## Unresolved Issues / Risks``.

    Prefix match is safe because our target headings are semantically
    distinct.  If new headings are added, ensure they don't prefix-collide.
    """
    if not filepath.exists():
        return ""
    text = filepath.read_text(encoding="utf-8")
    pattern = rf"^##\s+{re.escape(heading)}[^\n]*(.*?)(?=^##\s|\Z)"
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
    comment_labels = _parse_epic_labels_from_comments(SPRINT_STATUS)
    epics = _parse_epics(data, comment_labels=comment_labels)
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
