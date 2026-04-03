"""Build a source-wrangler bundle from a local image + JSON perception payload.

Loads ``sensory-bridges`` from the hyphenated skill directory (same pattern as
``skills/sensory-bridges/scripts/tests/conftest.py``), then calls:

- ``bridge_utils.perceive(..., modality=\"image\", ...)`` — official sensory-bridge entrypoint
- ``source_wrangler_operations.write_source_bundle(...)`` — official bundle writer

No alternate extraction logic: vision fields must be supplied in the JSON payload
(typically produced by an IDE agent with image access, per ``png_to_agent`` docs).

Usage (repo root)::

    python scripts/utilities/build_image_source_bundle.py \\
        --image course-content/courses/APC\\ Content\\ Roadmap.jpg \\
        --payload path/to/_perception_input.json \\
        --bundle-dir course-content/staging/ad-hoc/source-bundles/apc-content-roadmap-image \\
        --title \"APC Content Roadmap (local image)\"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scripts.utilities.skill_module_loader import (
    load_sensory_bridge_utils,
    load_source_wrangler_operations,
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def main() -> int:
    repo = _repo_root()
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--image", required=True, help="Path to source image (provenance ref)")
    p.add_argument("--payload", required=True, help="JSON file with perceive() kwargs (incl. vision fields)")
    p.add_argument("--bundle-dir", required=True, help="Output bundle directory")
    p.add_argument("--title", required=True, help="Bundle title")
    p.add_argument("--gate", default="G0", help="Perception gate id")
    p.add_argument(
        "--requesting-agent",
        default="bmad-agent-marcus",
        help="Requesting agent id for perceive()",
    )
    args = p.parse_args()

    img = Path(args.image).resolve()
    payload_path = Path(args.payload).resolve()
    if not img.is_file():
        print(f"Image not found: {img}", file=sys.stderr)
        return 1
    if not payload_path.is_file():
        print(f"Payload not found: {payload_path}", file=sys.stderr)
        return 1

    kw = json.loads(payload_path.read_text(encoding="utf-8"))
    purpose = kw.pop("purpose", "")

    bu = load_sensory_bridge_utils(repo)
    result = bu.perceive(
        str(img),
        modality="image",
        gate=args.gate,
        requesting_agent=args.requesting_agent,
        purpose=purpose,
        run_id=None,
        use_cache=False,
        **kw,
    )
    errs = bu.validate_response(result)
    if errs:
        print("validate_response errors:", errs, file=sys.stderr)
        return 2

    sw = load_source_wrangler_operations(repo)
    sections = [
        ("Extracted text (roadmap transcription)", result["extracted_text"]),
        ("Layout and structure", result["layout_description"]),
        ("Document title", result.get("slide_title") or ""),
        (
            "Text blocks",
            "\n".join(f"- {t}" for t in (result.get("text_blocks") or [])),
        ),
        (
            "Visual elements (structured)",
            json.dumps(result.get("visual_elements") or [], indent=2, ensure_ascii=False),
        ),
        (
            "Bridge confidence",
            f"{result['confidence']}: {result['confidence_rationale']}",
        ),
    ]
    md = sw.build_extracted_markdown(args.title, sections)
    rec = sw.SourceRecord(
        kind="local_image",
        ref=str(img),
        note=(
            f"sensory-bridges bridge_utils.perceive(modality=image, gate={args.gate}); "
            f"schema={result['schema_version']}; validate_response=ok"
        ),
    )
    raw = {
        "perception.json": json.dumps(result, indent=2, ensure_ascii=False),
        "_perception_input.json": payload_path.read_text(encoding="utf-8"),
    }
    summary = sw.write_source_bundle(
        args.bundle_dir,
        args.title,
        md,
        [rec],
        raw_files=raw,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
