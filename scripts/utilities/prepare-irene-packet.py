#!/usr/bin/env python3
"""
Prepare Irene Packet Generator

Canonical generator for irene-packet.md used by Marcus in Prompt 4.
Aggregates source bundle, operator directives, and ingestion quality into packet.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.utilities.file_helpers import project_root


def prepare_irene_packet(
    bundle_dir: Path,
    run_id: str,
    output_path: Path,
) -> dict[str, Any]:
    """Generate irene-packet.md from bundle artifacts."""
    # Read inputs
    extracted_md = bundle_dir / "extracted.md"
    metadata_json = bundle_dir / "metadata.json"
    operator_directives = bundle_dir / "operator-directives.md"
    ingestion_receipt = bundle_dir / "ingestion-quality-gate-receipt.md"

    if not extracted_md.exists():
        raise FileNotFoundError(f"extracted.md not found in {bundle_dir}")
    if not metadata_json.exists():
        raise FileNotFoundError(f"metadata.json not found in {bundle_dir}")
    if not operator_directives.exists():
        raise FileNotFoundError(f"operator-directives.md not found in {bundle_dir}")

    extracted_content = extracted_md.read_text(encoding="utf-8")
    metadata = json.loads(metadata_json.read_text(encoding="utf-8"))
    directives_content = operator_directives.read_text(encoding="utf-8")

    ingestion_content = ""
    if ingestion_receipt.exists():
        ingestion_content = ingestion_receipt.read_text(encoding="utf-8")

    # Build packet sections
    packet_sections = [
        f"# Irene Packet for {run_id}",
        "",
        "## Source Bundle Summary",
        f"- Primary source: {metadata.get('primary_source', 'unknown')}",
        f"- Total sections: {metadata.get('total_sections', 'unknown')}",
        f"- Extraction confidence: {metadata.get('overall_confidence', 'unknown')}",
        "",
        "## Operator Directives",
        directives_content,
        "",
        "## Ingestion Quality Receipt",
        ingestion_content,
        "",
        "## Extracted Content",
        extracted_content,
    ]

    packet_content = "\n".join(packet_sections)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(packet_content, encoding="utf-8")

    return {
        "packet_path": str(output_path),
        "sections": len(packet_sections),
        "has_directives": bool(directives_content.strip()),
        "has_ingestion_receipt": bool(ingestion_content.strip()),
    }


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