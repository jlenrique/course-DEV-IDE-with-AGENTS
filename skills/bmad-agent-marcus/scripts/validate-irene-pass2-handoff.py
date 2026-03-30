# /// script
# requires-python = ">=3.10"
# ///
"""Validate Irene Pass 2 handoff envelope requirements.

Story 11.3 gate:
- Require both gary_slide_output and perception_artifacts.
- Fail closed with explicit missing-field diagnostics.
- Preserve Gary card ordering as the source of truth for downstream narration.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]


REQUIRED_PASS2_FIELDS = ("gary_slide_output", "perception_artifacts")


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
        raise ValueError("Pass 2 envelope payload must be an object at the top level")
    return data


def validate_irene_pass2_handoff(
    payload: dict[str, Any],
    *,
    expected_artifact_hint: str | None = None,
) -> dict[str, Any]:
    """Validate required Pass 2 inputs and sequencing integrity."""
    missing_fields = [key for key in REQUIRED_PASS2_FIELDS if key not in payload]
    errors: list[str] = []

    if missing_fields:
        errors.append(
            "Missing required Pass 2 field(s): " + ", ".join(missing_fields)
        )

    gary = payload.get("gary_slide_output", [])
    perception = payload.get("perception_artifacts", [])

    if gary is not None and not isinstance(gary, list):
        errors.append("gary_slide_output must be an array")
        gary = []
    if perception is not None and not isinstance(perception, list):
        errors.append("perception_artifacts must be an array")
        perception = []

    card_sequence = [item.get("card_number") for item in gary if isinstance(item, dict)]
    strictly_ascending = all(
        isinstance(n, int) and isinstance(m, int) and n < m
        for n, m in zip(card_sequence, card_sequence[1:], strict=False)
    )
    contiguous_from_one = (
        bool(card_sequence)
        and all(isinstance(n, int) for n in card_sequence)
        and card_sequence == list(range(1, len(card_sequence) + 1))
    )

    missing_file_path_for: list[str] = []
    missing_source_ref_for: list[str] = []
    for item in gary:
        if not isinstance(item, dict):
            continue
        slide_label = str(item.get("slide_id") or item.get("card_number") or "unknown")
        file_path = item.get("file_path")
        source_ref = item.get("source_ref")
        if not isinstance(file_path, str) or not file_path.strip():
            missing_file_path_for.append(slide_label)
        if not isinstance(source_ref, str) or not source_ref.strip():
            missing_source_ref_for.append(slide_label)

    if not contiguous_from_one:
        errors.append(
            "gary_slide_output card_number sequence must be contiguous and start at 1 (1..N)"
        )
    if missing_file_path_for:
        errors.append(
            "gary_slide_output missing non-empty file_path for: " + ", ".join(missing_file_path_for)
        )
    if missing_source_ref_for:
        errors.append(
            "gary_slide_output missing non-empty source_ref for: "
            + ", ".join(missing_source_ref_for)
        )

    gary_slide_ids = {
        str(item.get("slide_id"))
        for item in gary
        if isinstance(item, dict) and item.get("slide_id")
    }
    perception_slide_ids = {
        str(item.get("slide_id"))
        for item in perception
        if isinstance(item, dict) and item.get("slide_id")
    }

    missing_perception_for = sorted(gary_slide_ids - perception_slide_ids)
    if missing_perception_for:
        errors.append(
            "perception_artifacts missing slide_id(s): " + ", ".join(missing_perception_for)
        )

    remediation_hint = (
        "Generate perception_artifacts via sensory bridges and attach to the Pass 2 envelope"
    )
    if expected_artifact_hint:
        remediation_hint += f" (expected location hint: {expected_artifact_hint})"

    status = "pass" if not errors else "fail"
    return {
        "status": status,
        "required_fields": list(REQUIRED_PASS2_FIELDS),
        "missing_fields": missing_fields,
        "errors": errors,
        "card_sequence": card_sequence,
        "order_check": {
            "strictly_ascending": strictly_ascending,
            "contiguous_from_one": contiguous_from_one,
        },
        "consistency": {
            "gary_slide_count": len(gary),
            "perception_count": len(perception),
            "missing_perception_for": missing_perception_for,
            "missing_file_path_for": missing_file_path_for,
            "missing_source_ref_for": missing_source_ref_for,
        },
        "remediation_hint": remediation_hint,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Irene Pass 2 handoff envelope")
    parser.add_argument(
        "--envelope",
        type=Path,
        required=True,
        help="Path to pass2 envelope JSON/YAML",
    )
    parser.add_argument(
        "--expected-artifact-hint",
        type=str,
        default=None,
        help="Optional path hint shown in remediation guidance",
    )
    args = parser.parse_args()

    try:
        payload = _load_payload(args.envelope)
        result = validate_irene_pass2_handoff(
            payload,
            expected_artifact_hint=args.expected_artifact_hint,
        )
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
