# /// script
# requires-python = ">=3.10"
# ///
"""Persist an authorized slide snapshot after operator confirms in chat.

Reads ``storyboard.json`` (from :mod:`generate-storyboard`), writes a new JSON
file with run id, UTC timestamp, and ordered ``slide_ids``. Refuses to
overwrite an existing output path (fail closed).
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Manifest must be a JSON object")
    slides = data.get("slides")
    if not isinstance(slides, list):
        raise ValueError("Manifest missing slides array")
    return data


def ordered_slide_ids(manifest: dict[str, Any]) -> list[str]:
    slides = manifest.get("slides", [])
    out: list[str] = []
    for item in slides:
        if not isinstance(item, dict):
            continue
        sid = item.get("slide_id")
        if isinstance(sid, str) and sid.strip():
            out.append(sid.strip())
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Write authorized storyboard snapshot JSON")
    parser.add_argument(
        "--manifest",
        type=Path,
        required=True,
        help="Path to storyboard/storyboard.json",
    )
    parser.add_argument(
        "--run-id",
        required=True,
        dest="run_id",
        help="Production run identifier",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Destination JSON path (must not exist)",
    )
    args = parser.parse_args()

    try:
        if not args.manifest.is_file():
            print(f"error: manifest not found: {args.manifest}", file=sys.stderr)
            return 2
        if args.output.exists():
            print(
                f"error: refusing to overwrite existing file: {args.output}",
                file=sys.stderr,
            )
            return 1

        manifest = load_manifest(args.manifest)
        slide_ids = ordered_slide_ids(manifest)
        if not slide_ids:
            print("error: manifest contains no slide_id entries", file=sys.stderr)
            return 2

        record = {
            "authorized_storyboard_version": 1,
            "run_id": args.run_id,
            "authorized_at_utc": datetime.now(timezone.utc).isoformat(),
            "slide_ids": slide_ids,
            "source_manifest": args.manifest.resolve().as_posix(),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(f"Wrote {args.output}")
        return 0
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
