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


def _selection_pairs_from_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    data = manifest.get("double_dispatch")
    if not isinstance(data, dict):
        return []
    pairs = data.get("variant_pairs")
    if not isinstance(pairs, list):
        return []
    return [p for p in pairs if isinstance(p, dict)]


def _normalize_selections(path: Path) -> dict[str, str]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    if isinstance(raw, dict):
        for key, value in raw.items():
            if str(value).strip().upper() in {"A", "B"}:
                out[str(key)] = str(value).strip().upper()
        return out
    if isinstance(raw, list):
        for item in raw:
            if not isinstance(item, dict):
                continue
            key = str(item.get("card_number") or item.get("slide_id") or "").strip()
            selected = str(item.get("selected_variant") or "").strip().upper()
            if key and selected in {"A", "B"}:
                out[key] = selected
        return out
    raise ValueError("selection JSON must be an object or list of selection records")


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
    parser.add_argument(
        "--selections",
        type=Path,
        default=None,
        help=(
            "Optional JSON with explicit winners for double-dispatch pairs. "
            "Format: {\"<card_number|slide_id>\": \"A|B\"} or list of records."
        ),
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

        selection_pairs = _selection_pairs_from_manifest(manifest)
        selection_map: dict[str, str] = {}
        if args.selections is not None:
            if not args.selections.is_file():
                print(f"error: selections file not found: {args.selections}", file=sys.stderr)
                return 2
            selection_map = _normalize_selections(args.selections)

        selection_metadata: list[dict[str, Any]] = []
        if selection_pairs:
            for pair in selection_pairs:
                key = str(pair.get("card_number") or pair.get("slide_id") or "").strip()
                if not key:
                    continue
                selected_variant = selection_map.get(key) or str(pair.get("selected_variant") or "").strip().upper()
                if selected_variant not in {"A", "B"}:
                    print(
                        "error: all double-dispatch positions require exactly one selected variant "
                        f"(missing for key={key})",
                        file=sys.stderr,
                    )
                    return 2
                rejected_variant = "B" if selected_variant == "A" else "A"
                selection_metadata.append(
                    {
                        "slide_id": pair.get("slide_id"),
                        "card_number": pair.get("card_number"),
                        "selected_variant": selected_variant,
                        "rejected_variant": rejected_variant,
                        "selection_timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        record = {
            "authorized_storyboard_version": 1,
            "run_id": args.run_id,
            "authorized_at_utc": datetime.now(timezone.utc).isoformat(),
            "slide_ids": slide_ids,
            "source_manifest": args.manifest.resolve().as_posix(),
        }
        if selection_metadata:
            record["selection_metadata"] = selection_metadata
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(f"Wrote {args.output}")
        return 0
    except Exception as exc:
        print(f"error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
