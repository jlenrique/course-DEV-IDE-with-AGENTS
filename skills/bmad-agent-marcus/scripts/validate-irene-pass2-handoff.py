# /// script
# requires-python = ">=3.10"
# ///
"""Validate Irene Pass 2 completeness — post-Pass-2 check.

Story 11.3 gate (updated for inline perception):
- Require both gary_slide_output and perception_artifacts.
- Fail closed with explicit missing-field diagnostics.
- Preserve Gary card ordering as the source of truth for downstream narration.

Timing: Run AFTER Irene Pass 2 completes, not before delegation.
Perception artifacts are generated inline by Irene during Pass 2
(the LLM reads each slide PNG and emits a perception artifact as a
side-effect of writing narration). This validator confirms completeness.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]


REQUIRED_PASS2_FIELDS = ("gary_slide_output", "perception_artifacts")

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def _is_remote_http_ref(value: str) -> bool:
    parsed = urlparse(str(value).strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _resolve_existing_local_path(path_value: str, *, bundle_dir: Path | None) -> Path | None:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate if candidate.is_file() else None

    if bundle_dir is not None:
        bundle_candidate = (bundle_dir / candidate).resolve()
        if bundle_candidate.is_file():
            return bundle_candidate

    project_candidate = (PROJECT_ROOT / candidate).resolve()
    if project_candidate.is_file():
        return project_candidate

    return None


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
    envelope_path: Path | None = None,
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
    non_png_file_path_for: list[str] = []
    remote_file_path_for: list[str] = []
    missing_local_png_for: list[str] = []
    gary_slide_path_by_id: dict[str, str] = {}
    bundle_dir = envelope_path.parent if envelope_path is not None else None
    for item in gary:
        if not isinstance(item, dict):
            continue
        slide_label = str(item.get("slide_id") or item.get("card_number") or "unknown")
        file_path = item.get("file_path")
        source_ref = item.get("source_ref")
        if not isinstance(file_path, str) or not file_path.strip():
            missing_file_path_for.append(slide_label)
        else:
            normalized_path = file_path.strip()
            if _is_remote_http_ref(normalized_path):
                remote_file_path_for.append(slide_label)
            if Path(normalized_path).suffix.lower() != ".png":
                non_png_file_path_for.append(slide_label)
            if envelope_path is not None and _resolve_existing_local_path(
                normalized_path,
                bundle_dir=bundle_dir,
            ) is None:
                missing_local_png_for.append(slide_label)

            slide_id = item.get("slide_id")
            if isinstance(slide_id, str) and slide_id.strip():
                gary_slide_path_by_id[slide_id.strip()] = normalized_path
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
    if remote_file_path_for:
        errors.append(
            "gary_slide_output file_path must reference local downloaded PNGs; remote path found for: "
            + ", ".join(remote_file_path_for)
        )
    if non_png_file_path_for:
        errors.append(
            "gary_slide_output file_path must end with .png for: "
            + ", ".join(non_png_file_path_for)
        )
    if missing_local_png_for:
        errors.append(
            "gary_slide_output file_path does not exist on disk for: "
            + ", ".join(missing_local_png_for)
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

    missing_source_image_path_for: list[str] = []
    mismatched_source_image_path_for: list[str] = []
    for item in perception:
        if not isinstance(item, dict):
            continue
        slide_id = str(item.get("slide_id") or "").strip()
        if not slide_id:
            continue
        source_image_path = item.get("source_image_path")
        if not isinstance(source_image_path, str) or not source_image_path.strip():
            missing_source_image_path_for.append(slide_id)
            continue
        normalized_source_path = source_image_path.strip()
        expected_path = gary_slide_path_by_id.get(slide_id)
        if expected_path is not None and normalized_source_path != expected_path:
            mismatched_source_image_path_for.append(slide_id)

    if missing_source_image_path_for:
        errors.append(
            "perception_artifacts missing non-empty source_image_path for slide_id(s): "
            + ", ".join(sorted(set(missing_source_image_path_for)))
        )
    if mismatched_source_image_path_for:
        errors.append(
            "perception_artifacts source_image_path must match gary_slide_output.file_path for slide_id(s): "
            + ", ".join(sorted(set(mismatched_source_image_path_for)))
        )

    remediation_hint = (
        "Perception artifacts are emitted inline during Pass 2. "
        "If missing, re-run Irene on the affected slides to regenerate perception side-effects. "
        "Narration grounding must use local post-integration downloaded PNGs from gary_slide_output"
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
            "missing_source_image_path_for": sorted(set(missing_source_image_path_for)),
            "mismatched_source_image_path_for": sorted(set(mismatched_source_image_path_for)),
            "non_png_file_path_for": non_png_file_path_for,
            "remote_file_path_for": remote_file_path_for,
            "missing_local_png_for": missing_local_png_for,
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
            envelope_path=args.envelope,
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
