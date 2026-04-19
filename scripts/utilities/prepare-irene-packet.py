#!/usr/bin/env python3
# ruff: noqa: N999 -- pre-existing hyphenated filename; lift is refactor-only
# (Story 30-2a) and preserves the script's public CLI path byte-identical.
"""
Prepare Irene Packet Generator — thin CLI shim

Thin CLI wrapper around :func:`marcus.intake.pre_packet.prepare_irene_packet`.
The function body lives in the ``marcus.intake.pre_packet`` module as of
Story 30-2a (refactor-only lift). This script preserves the pre-30-2a
CLI interface (argparse flags, exit codes, stdout format) byte-identical.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from marcus.intake.pre_packet import prepare_irene_packet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate canonical irene-packet.md for Prompt 4."
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Bundle directory containing extracted.md, metadata.json, operator-directives.md",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        help="Run ID for packet header",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output path for irene-packet.md",
    )

    args = parser.parse_args(argv)

    try:
        result = prepare_irene_packet(args.bundle_dir, args.run_id, args.output)
        print(f"Irene packet written to {result['packet_path']}")
        print(f"Sections: {result['sections']}")
        print(f"Has directives: {result['has_directives']}")
        print(f"Has ingestion receipt: {result['has_ingestion_receipt']}")
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
