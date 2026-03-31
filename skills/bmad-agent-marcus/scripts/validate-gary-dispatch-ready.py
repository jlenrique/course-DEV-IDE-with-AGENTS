# /// script
# requires-python = ">=3.10"
# ///
"""Validate Gary dispatch payload readiness for HIL Gate 2.

This gate is run after Gary dispatch/export and before Irene Pass 2 handoff.
It enforces strict dispatch contract requirements by calling
`gamma_operations.validate_dispatch_ready()` and adds sequencing checks.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

GAMMA_SCRIPTS_DIR = PROJECT_ROOT / "skills" / "gamma-api-mastery" / "scripts"
if str(GAMMA_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(GAMMA_SCRIPTS_DIR))

from gamma_operations import validate_dispatch_ready  # type: ignore[import-not-found]  # noqa: E402


def _load_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in {".yml", ".yaml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML input payloads")
        data = yaml.safe_load(text)
    else:
        data = json.loads(text)

    if not isinstance(data, dict):
        raise ValueError("Gary dispatch payload must be an object at the top level")
    return data


def _parse_literal_visual_specs(irene_pass1_path: Path) -> dict[int, dict[str, str]]:
    text = irene_pass1_path.read_text(encoding="utf-8")
    if "## literal-visual spec cards" not in text:
        return {}

    section = text.split("## literal-visual spec cards", 1)[1]
    next_heading = section.find("\n## ")
    if next_heading != -1:
        section = section[:next_heading]

    specs: dict[int, dict[str, str]] = {}
    blocks = re.split(r"\n###\s+", section)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.splitlines()
        fields: dict[str, str] = {}
        for line in lines[1:]:
            stripped = line.strip()
            if not stripped.startswith("- ") or ":" not in stripped:
                continue
            key, value = stripped[2:].split(":", 1)
            fields[key.strip()] = value.strip()
        slide_number = fields.get("slide_number")
        if slide_number and slide_number.isdigit():
            specs[int(slide_number)] = fields
    return specs


def _load_diagram_cards(bundle_dir: Path) -> list[dict[str, Any]]:
    path = bundle_dir / "gary-diagram-cards.json"
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        cards = data.get("cards", [])
        return cards if isinstance(cards, list) else []
    return []


def _infer_gamma_asset_family(url: str) -> str:
    normalized = url.lower()
    if "/generated-images/" in normalized:
        return "generated-images"
    if "/design-anything/" in normalized:
        return "design-anything"
    return "other"


def _validate_literal_visual_authority(bundle_dir: Path) -> list[str]:
    errors: list[str] = []
    irene_pass1_path = bundle_dir / "irene-pass1.md"
    if not irene_pass1_path.exists():
        return errors

    specs = _parse_literal_visual_specs(irene_pass1_path)
    if not specs:
        return errors

    diagram_cards = _load_diagram_cards(bundle_dir)
    card_map = {
        card.get("card_number"): card
        for card in diagram_cards
        if isinstance(card, dict) and isinstance(card.get("card_number"), int)
    }

    spec_card_numbers = sorted(specs)
    diagram_card_numbers = sorted(card_map)
    if diagram_card_numbers != spec_card_numbers:
        errors.append(
            "gary-diagram-cards.json card_number set must exactly match Irene Pass 1 "
            f"literal-visual cards. expected={spec_card_numbers} actual={diagram_card_numbers}"
        )

    for card_number, spec in specs.items():
        card = card_map.get(card_number)
        if card is None:
            continue

        expected_source_asset = spec.get("source_asset", "")
        expected_treatment = spec.get("image_treatment", "")
        layout_constraint = spec.get("layout_constraint", "")

        actual_source_asset = str(card.get("source_asset", "")).strip()
        derivation_type = str(card.get("derivation_type", "")).strip()
        image_url = str(card.get("image_url", "")).strip()
        asset_family = _infer_gamma_asset_family(image_url)

        if expected_source_asset and actual_source_asset != expected_source_asset:
            errors.append(
                f"literal-visual card {card_number} source_asset mismatch: "
                f"expected {expected_source_asset!r} but found {actual_source_asset!r}"
            )

        requires_source_derived = expected_treatment == "source-crop" or any(
            phrase in layout_constraint.lower()
            for phrase in ("no redrawn substitute", "do not fabricate")
        )
        if not requires_source_derived:
            continue

        if derivation_type not in {"source-crop", "rebranded-source", "user-provided-exact"}:
            errors.append(
                f"literal-visual card {card_number} must declare a source-derived derivation_type "
                f"for Irene image_treatment=source-crop; found {derivation_type!r}"
            )

        if asset_family == "generated-images":
            errors.append(
                f"literal-visual card {card_number} uses a Gamma generated-images asset for a "
                "source-crop slide; dispatch must fail closed until a source-derived image is staged"
            )

    return errors


def _card_sequence(slides: list[dict[str, Any]]) -> list[int]:
    return [item.get("card_number") for item in slides if isinstance(item, dict)]


def validate_gary_dispatch_ready(
    payload: dict[str, Any],
    *,
    payload_path: Path | None = None,
) -> dict[str, Any]:
    """Validate dispatch payload for Gate 2 readiness."""
    errors: list[str] = []

    slides = payload.get("gary_slide_output")
    if not isinstance(slides, list):
        errors.append("gary_slide_output must be an array")
        slides = []

    if isinstance(slides, list) and len(slides) == 0:
        errors.append("gary_slide_output must contain at least one slide for Gate 2 review")

    try:
        validate_dispatch_ready(payload)
    except ValueError as exc:
        errors.append(str(exc))

    card_sequence = _card_sequence(slides)
    contiguous_from_one = (
        bool(card_sequence)
        and all(isinstance(n, int) for n in card_sequence)
        and card_sequence == list(range(1, len(card_sequence) + 1))
    )
    if card_sequence and not contiguous_from_one:
        errors.append(
            "gary_slide_output card_number sequence must be contiguous and start at 1 (1..N)"
        )

    dispatch_metadata = payload.get("dispatch_metadata")
    if not isinstance(dispatch_metadata, dict):
        errors.append(
            "dispatch_metadata must be present — re-run dispatch with the current "
            "gamma_operations.py to embed content source provenance"
        )
    elif not str(dispatch_metadata.get("slides_content_json_path") or "").strip():
        errors.append(
            "dispatch_metadata.slides_content_json_path must be non-empty — "
            "dispatch must use --slides-content-json to prevent placeholder content"
        )

    if payload_path is not None:
        errors.extend(_validate_literal_visual_authority(payload_path.parent))

    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "checks": {
            "slide_count": len(slides),
            "card_sequence": card_sequence,
            "contiguous_from_one": contiguous_from_one,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Gary dispatch payload readiness")
    parser.add_argument(
        "--payload",
        type=Path,
        required=True,
        help="Path to Gary dispatch payload JSON/YAML",
    )
    args = parser.parse_args()

    try:
        payload = _load_payload(args.payload)
        result = validate_gary_dispatch_ready(payload, payload_path=args.payload)
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "pass" else 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "errors": [f"validator_exception: {type(exc).__name__}: {exc}"],
                },
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
