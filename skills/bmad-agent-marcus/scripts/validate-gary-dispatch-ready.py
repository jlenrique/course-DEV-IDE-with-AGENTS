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


def _card_sequence(slides: list[dict[str, Any]]) -> list[int]:
    return [item.get("card_number") for item in slides if isinstance(item, dict)]


def validate_gary_dispatch_ready(payload: dict[str, Any]) -> dict[str, Any]:
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
        result = validate_gary_dispatch_ready(payload)
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
