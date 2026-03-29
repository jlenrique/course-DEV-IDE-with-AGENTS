# /// script
# requires-python = ">=3.10"
# ///
"""Archive agent quality scan reports to canonical skills/reports paths."""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

REQUIRED_DIMENSIONS = (
    "structure_compliance",
    "prompt_craft_quality",
    "cohesion",
    "execution_efficiency",
    "script_opportunity_analysis",
)

AGENT_NAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


@dataclass(frozen=True)
class ScanOutcome:
    status: str
    blocking: bool
    failed_dimensions: list[str]


def project_root() -> Path:
    """Resolve repository root from this file location via pyproject marker."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "pyproject.toml").exists():
            return parent
    return current.parent.parent.parent


def validate_agent_name(agent_name: str) -> str:
    """Validate and normalize agent short name for safe filesystem usage."""
    normalized = str(agent_name).strip()
    if not AGENT_NAME_PATTERN.fullmatch(normalized):
        raise ValueError(
            "Invalid agent name. Use lowercase letters, numbers, underscore, or hyphen."
        )
    return normalized


def validate_timestamp(timestamp: str | None) -> str:
    """Validate optional timestamp format or generate current timestamp."""
    if timestamp is None:
        return datetime.now().strftime("%Y%m%dT%H%M%S")
    value = str(timestamp).strip()
    try:
        datetime.strptime(value, "%Y%m%dT%H%M%S")
    except ValueError as exc:
        raise ValueError(
            "Invalid timestamp. Expected format: YYYYmmddTHHMMSS"
        ) from exc
    return value


def evaluate_dimensions(dimensions: dict[str, float], threshold: float) -> ScanOutcome:
    """Evaluate dimension scores against a minimum threshold."""
    threshold_value = float(threshold)
    if threshold_value < 0.0 or threshold_value > 1.0:
        raise ValueError("Threshold must be between 0.0 and 1.0")

    missing = [k for k in REQUIRED_DIMENSIONS if k not in dimensions]
    if missing:
        raise ValueError(f"Missing required dimensions: {missing}")

    normalized: dict[str, float] = {}
    for key in REQUIRED_DIMENSIONS:
        value = float(dimensions[key])
        if value < 0.0 or value > 1.0:
            raise ValueError(f"Dimension '{key}' must be between 0.0 and 1.0")
        normalized[key] = value

    failed = [k for k in REQUIRED_DIMENSIONS if normalized[k] < threshold_value]
    if failed:
        return ScanOutcome(status="fail", blocking=True, failed_dimensions=failed)
    return ScanOutcome(status="pass", blocking=False, failed_dimensions=[])


def build_report(
    *,
    agent_name: str,
    dimensions: dict[str, float],
    threshold: float,
    scanner: str,
    notes: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Build normalized quality-scan report payload."""
    normalized_agent_name = validate_agent_name(agent_name)
    ts = validate_timestamp(timestamp)
    outcome = evaluate_dimensions(dimensions, threshold)

    return {
        "timestamp": ts,
        "agent_name": normalized_agent_name,
        "scanner": scanner,
        "threshold": float(threshold),
        "dimensions": {k: float(dimensions[k]) for k in REQUIRED_DIMENSIONS},
        "failed_dimensions": outcome.failed_dimensions,
        "status": outcome.status,
        "blocking": outcome.blocking,
        "notes": notes,
    }


def archive_report(root: Path, report: dict[str, Any]) -> Path:
    """Persist report under canonical archive path and return file path."""
    agent_name = validate_agent_name(str(report["agent_name"]))
    ts = str(report["timestamp"]).strip()

    out_dir = root / "skills" / "reports" / f"bmad-agent-{agent_name}" / "quality-scan"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / f"{ts}.json"
    out_file.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return out_file


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Archive agent quality scan report")
    parser.add_argument("--agent-name", required=True, help="Agent short name (e.g., marcus)")
    parser.add_argument("--threshold", type=float, default=0.80, help="Minimum pass threshold")
    parser.add_argument(
        "--scanner",
        default="bmad-agent-builder-quality-optimizer",
        help="Scanner identifier",
    )
    parser.add_argument("--notes", default="", help="Optional notes")
    parser.add_argument(
        "--timestamp",
        default=None,
        help="Optional timestamp override (YYYYmmddTHHMMSS)",
    )

    parser.add_argument("--structure-compliance", type=float, required=True)
    parser.add_argument("--prompt-craft-quality", type=float, required=True)
    parser.add_argument("--cohesion", type=float, required=True)
    parser.add_argument("--execution-efficiency", type=float, required=True)
    parser.add_argument("--script-opportunity-analysis", type=float, required=True)

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    root = project_root()
    dimensions = {
        "structure_compliance": args.structure_compliance,
        "prompt_craft_quality": args.prompt_craft_quality,
        "cohesion": args.cohesion,
        "execution_efficiency": args.execution_efficiency,
        "script_opportunity_analysis": args.script_opportunity_analysis,
    }

    try:
        report = build_report(
            agent_name=args.agent_name,
            dimensions=dimensions,
            threshold=args.threshold,
            scanner=args.scanner,
            notes=args.notes,
            timestamp=args.timestamp,
        )
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 2

    out_file = archive_report(root, report)

    print(
        json.dumps(
            {
                "status": report["status"],
                "blocking": report["blocking"],
                "report_path": str(out_file),
            },
            indent=2,
        )
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
