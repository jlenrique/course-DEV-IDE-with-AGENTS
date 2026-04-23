#!/usr/bin/env python3
"""
Emit Preflight Receipt Generator

Canonical generator for preflight-results.json used by Marcus in Prompt 1.
Aggregates app_session_readiness checks into JSON receipt.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.utilities.app_session_readiness import (
    has_evidence_bolster_key_failure,
    run_readiness,
)
from scripts.utilities.file_helpers import project_root
from scripts.utilities.workflow_policy import load_workflow_policy

_REQUIRED_RECEIPT_FIELDS = frozenset({"overall_status", "checks", "root", "timestamp"})


def emit_preflight_receipt(
    root: Path | None = None,
    bundle_dir: Path | None = None,
    with_preflight: bool = False,
    motion_enabled: bool = False,
    session_receipt: Path | None = None,
) -> dict[str, Any]:
    """Emit canonical preflight receipt for Marcus Prompt 1."""
    effective_root = root or project_root()
    policy = load_workflow_policy(root)
    max_age_minutes = policy["session_receipt_max_age_minutes"]

    if session_receipt is not None:
        cached = _load_session_receipt_if_fresh(
            session_receipt,
            max_age_minutes=max_age_minutes,
            required_root=effective_root,
        )
        if cached is not None:
            print(
                "Using cached session receipt "
                f"{session_receipt} (max age {max_age_minutes} minutes)."
            )
            return cached
        print("Session receipt cache missing, unreadable, or stale; running live readiness.")

    report = run_readiness(
        root=root,
        with_preflight=with_preflight,
        motion_enabled=motion_enabled,
        bundle_dir=bundle_dir,
    )
    return report


def _load_session_receipt_if_fresh(
    path: Path,
    *,
    max_age_minutes: int,
    required_root: Path | None = None,
) -> dict[str, Any] | None:
    """Return cached receipt when present, parseable, and within age window."""
    if not path.is_file():
        return None

    age_seconds = datetime.now(tz=UTC).timestamp() - path.stat().st_mtime
    if age_seconds > max_age_minutes * 60:
        return None

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    if not _REQUIRED_RECEIPT_FIELDS.issubset(payload):
        return None
    if required_root is None:
        return payload

    cached_root = payload.get("root")
    if not isinstance(cached_root, str):
        return None
    if Path(cached_root).resolve() != required_root.resolve():
        return None
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit canonical preflight receipt for Marcus Prompt 1."
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Repository root override.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        help="Bundle directory for run constants validation.",
    )
    parser.add_argument(
        "--with-preflight",
        action="store_true",
        help="Include tool pre-flight checks.",
    )
    parser.add_argument(
        "--motion-enabled",
        action="store_true",
        help="Motion-enabled run.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for preflight-results.json",
    )
    parser.add_argument(
        "--session-receipt",
        type=Path,
        default=None,
        help=(
            "Optional session-scoped readiness receipt to reuse when it exists "
            "and is still fresh under workflow policy."
        ),
    )

    args = parser.parse_args(argv)

    receipt = emit_preflight_receipt(
        root=args.root,
        bundle_dir=args.bundle_dir,
        with_preflight=args.with_preflight,
        motion_enabled=args.motion_enabled,
        session_receipt=args.session_receipt,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"Preflight receipt written to {args.output}")
    if has_evidence_bolster_key_failure(receipt):
        return 30
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
