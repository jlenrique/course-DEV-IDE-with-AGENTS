#!/usr/bin/env python3
"""
Emit Preflight Receipt Generator

Canonical generator for preflight-results.json used by Marcus in Prompt 1.
Aggregates app_session_readiness checks into JSON receipt.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.utilities.app_session_readiness import run_readiness


def emit_preflight_receipt(
    root: Path | None = None,
    bundle_dir: Path | None = None,
    with_preflight: bool = False,
    motion_enabled: bool = False,
) -> dict[str, any]:
    """Emit canonical preflight receipt for Marcus Prompt 1."""
    report = run_readiness(
        root=root,
        with_preflight=with_preflight,
        motion_enabled=motion_enabled,
        bundle_dir=bundle_dir,
    )
    return report


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

    args = parser.parse_args(argv)

    receipt = emit_preflight_receipt(
        root=args.root,
        bundle_dir=args.bundle_dir,
        with_preflight=args.with_preflight,
        motion_enabled=args.motion_enabled,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"Preflight receipt written to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
