# /// script
# requires-python = ">=3.10"
# ///
"""Prepare a fresh Irene Pass 2 handoff envelope at bundle root.

This helper is the canonical Marcus-side Prompt 8 preflight. It:
- validates authoritative inputs for Irene Pass 2
- archives stale bundle-root Pass 2 outputs on rerun
- preserves exact Motion Gate-approved asset bindings
- reports non-authoritative motion leftovers without using them as inputs
- writes a fresh ``pass2-envelope.json`` plus ``pass2-prep-receipt.json``
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - optional for yaml input
    yaml = None  # type: ignore[assignment]


EXPECTED_PASS2_OUTPUTS = (
    "narration-script.md",
    "segment-manifest.yaml",
    "perception-artifacts.json",
)
STALE_PASS2_FILES = (
    "pass2-envelope.json",
    "pass2-prep-receipt.json",
    *EXPECTED_PASS2_OUTPUTS,
)
ARCHIVE_SUBDIR = Path("recovery") / "archive" / "pass2-reruns"
DEFAULT_ENVELOPE_FILENAME = "pass2-envelope.json"
DEFAULT_RECEIPT_FILENAME = "pass2-prep-receipt.json"
REPO_ROOT = Path(__file__).resolve().parents[3]
STATIC_MOTION_PATTERN = re.compile(r"slide[-_](\d{2})", re.IGNORECASE)
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUN_CONSTANTS_FILENAME = "run-constants.yaml"
STYLE_GUIDE_PATH = PROJECT_ROOT / "state" / "config" / "style_guide.yaml"
RUNTIME_ROW_RE = re.compile(
    r"^\|\s*(?P<slide>\d+)\s*\|\s*(?P<target>\d+(?:\.\d+)?)\s*\|\s*(?P<cumulative>\d+:\d{2})\s*\|$"
)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _timestamp_slug(now: datetime) -> str:
    return now.strftime("%Y%m%dT%H%M%SZ")


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object at the top level")
    return data


def _load_yaml_object(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for motion_plan.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping at the top level")
    return data


def _bundle_input(bundle_dir: Path, filename: str) -> Path:
    return bundle_dir / filename


def _parse_runtime_budget_rows(irene_pass1_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw_line in irene_pass1_path.read_text(encoding="utf-8").splitlines():
        match = RUNTIME_ROW_RE.match(raw_line.strip())
        if not match:
            continue
        slide = int(match.group("slide"))
        target_seconds = float(match.group("target"))
        cumulative_minutes, cumulative_seconds = match.group("cumulative").split(":")
        rows.append(
            {
                "card_number": slide,
                "target_runtime_seconds": target_seconds,
                "cumulative_runtime_seconds": int(cumulative_minutes) * 60 + int(cumulative_seconds),
            }
        )
    return rows


def _load_runtime_plan(bundle_dir: Path, irene_pass1_path: Path) -> dict[str, Any] | None:
    run_constants_path = _bundle_input(bundle_dir, RUN_CONSTANTS_FILENAME)
    if not run_constants_path.is_file() and not irene_pass1_path.is_file():
        return None

    run_constants: dict[str, Any] = {}
    if run_constants_path.is_file():
        run_constants = _load_yaml_object(run_constants_path)

    runtime_plan: dict[str, Any] = {
        "locked_slide_count": run_constants.get("locked_slide_count"),
        "target_total_runtime_minutes": run_constants.get("target_total_runtime_minutes"),
        "slide_runtime_average_seconds": run_constants.get("slide_runtime_average_seconds"),
        "slide_runtime_variability_scale": run_constants.get("slide_runtime_variability_scale"),
    }
    if irene_pass1_path.is_file():
        per_slide_targets = _parse_runtime_budget_rows(irene_pass1_path)
        if per_slide_targets:
            runtime_plan["per_slide_targets"] = per_slide_targets
    if not any(value not in (None, "", []) for value in runtime_plan.values()):
        return None
    return runtime_plan


def _load_voice_direction_defaults() -> dict[str, Any]:
    if yaml is None or not STYLE_GUIDE_PATH.is_file():
        return {}
    data = yaml.safe_load(STYLE_GUIDE_PATH.read_text(encoding="utf-8")) or {}
    elevenlabs = data.get("tool_parameters", {}).get("elevenlabs", {})
    if not isinstance(elevenlabs, dict):
        return {}
    defaults = {}
    for key in (
        "stability",
        "similarity_boost",
        "style",
        "speed",
        "use_speaker_boost",
        "emotional_variability",
        "pace_variability",
    ):
        value = elevenlabs.get(key)
        if value not in (None, ""):
            defaults[key] = value
    return defaults


def _slug_from_bundle_name(bundle_dir: Path) -> str:
    match = re.match(r"(?P<slug>.+)-\d{8}(?:-.+)?$", bundle_dir.name)
    if match:
        return match.group("slug")
    return bundle_dir.name


def _dispatch_row_lookup(dispatch_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = dispatch_payload.get("gary_slide_output", [])
    if not isinstance(rows, list):
        return {}
    lookup: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id:
            lookup[slide_id] = row
    return lookup


def _resolve_slide_asset_path(file_path: str, *, bundle_dir: Path) -> Path:
    """Resolve slide asset paths from either bundle-local or repo-root-relative inputs."""
    candidate = Path(file_path)
    if candidate.is_absolute():
        return candidate.resolve()

    bundle_relative = (bundle_dir / candidate).resolve()
    if bundle_relative.is_file():
        return bundle_relative

    repo_relative = (REPO_ROOT / candidate).resolve()
    if repo_relative.is_file():
        return repo_relative

    return bundle_relative


def _normalize_slide_row(
    row: dict[str, Any],
    *,
    dispatch_row: dict[str, Any] | None,
    bundle_dir: Path,
) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    slide_id = str(row.get("slide_id") or "").strip()
    if not slide_id:
        errors.append("authorized-storyboard.json contains a slide without slide_id")

    card_number = row.get("card_number")
    if not isinstance(card_number, int) or card_number <= 0:
        errors.append(f"{slide_id or '<missing-slide-id>'}: card_number must be a positive integer")

    file_path = str(row.get("file_path") or dispatch_row.get("file_path") if dispatch_row else row.get("file_path") or "").strip()
    if not file_path:
        errors.append(f"{slide_id or '<missing-slide-id>'}: file_path is required")
        resolved_file = None
    else:
        resolved_file = _resolve_slide_asset_path(file_path, bundle_dir=bundle_dir)
        if resolved_file.suffix.lower() != ".png":
            errors.append(f"{slide_id or '<missing-slide-id>'}: file_path must end with .png")
        if not resolved_file.is_file():
            errors.append(f"{slide_id or '<missing-slide-id>'}: file_path does not exist on disk")

    source_ref = str(row.get("source_ref") or dispatch_row.get("source_ref") if dispatch_row else row.get("source_ref") or "").strip()
    if not source_ref:
        errors.append(f"{slide_id or '<missing-slide-id>'}: source_ref is required")

    normalized = {
        "slide_id": slide_id,
        "card_number": card_number,
        "file_path": str(resolved_file) if resolved_file is not None else "",
        "source_ref": source_ref,
        "visual_description": str(
            row.get("visual_description")
            or (dispatch_row.get("visual_description") if dispatch_row else "")
            or ""
        ).strip(),
        "fidelity": str(
            row.get("fidelity")
            or (dispatch_row.get("fidelity") if dispatch_row else "")
            or ""
        ).strip()
        or None,
        "literal_visual_source": row.get("literal_visual_source")
        if row.get("literal_visual_source") is not None
        else (dispatch_row.get("literal_visual_source") if dispatch_row else None),
    }
    return normalized, errors


def _load_authorized_slide_output(
    authorized_storyboard: dict[str, Any],
    *,
    dispatch_payload: dict[str, Any],
    bundle_dir: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    rows = authorized_storyboard.get("authorized_slides", [])
    if not isinstance(rows, list) or not rows:
        return [], ["authorized-storyboard.json must contain a non-empty authorized_slides array"]

    dispatch_lookup = _dispatch_row_lookup(dispatch_payload)
    normalized_rows: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_slide_ids: set[str] = set()

    for row in rows:
        if not isinstance(row, dict):
            errors.append("authorized-storyboard.json authorized_slides entries must be objects")
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        dispatch_row = dispatch_lookup.get(slide_id, {})
        normalized, row_errors = _normalize_slide_row(
            row,
            dispatch_row=dispatch_row,
            bundle_dir=bundle_dir,
        )
        errors.extend(row_errors)
        if slide_id in seen_slide_ids:
            errors.append(f"{slide_id}: duplicate slide_id in authorized-storyboard.json")
        seen_slide_ids.add(slide_id)
        normalized_rows.append(normalized)

    normalized_rows.sort(key=lambda item: int(item["card_number"]))
    card_sequence = [int(item["card_number"]) for item in normalized_rows if isinstance(item.get("card_number"), int)]
    if card_sequence != list(range(1, len(card_sequence) + 1)):
        errors.append("authorized winner deck card_number sequence must be contiguous and start at 1 (1..N)")

    return normalized_rows, errors


def _motion_enabled(motion_plan: dict[str, Any]) -> bool:
    if bool(motion_plan.get("motion_enabled", False)):
        return True
    rows = motion_plan.get("slides", [])
    return isinstance(rows, list) and any(
        isinstance(row, dict) and str(row.get("motion_type") or "static").strip().lower() != "static"
        for row in rows
    )


def _validate_motion_plan(
    *,
    motion_plan: dict[str, Any] | None,
    authorized_rows: list[dict[str, Any]],
    bundle_dir: Path,
) -> tuple[bool, dict[str, str], list[str], list[str]]:
    if motion_plan is None:
        return False, {}, [], []

    rows = motion_plan.get("slides", [])
    if not isinstance(rows, list):
        return False, {}, [], ["motion_plan.yaml slides must be a list"]

    motion_enabled = _motion_enabled(motion_plan)
    rows_by_slide_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id:
            rows_by_slide_id[slide_id] = row

    errors: list[str] = []
    warnings: list[str] = []
    approved_assets: dict[str, str] = {}

    if motion_enabled:
        missing_slide_ids = [
            str(row["slide_id"])
            for row in authorized_rows
            if str(row["slide_id"]) not in rows_by_slide_id
        ]
        if missing_slide_ids:
            errors.append(
                "motion_plan.yaml is missing authorized slide coverage for: "
                + ", ".join(missing_slide_ids)
            )

    for row in authorized_rows:
        slide_id = str(row["slide_id"])
        assignment = rows_by_slide_id.get(slide_id)
        if assignment is None:
            continue
        motion_type = str(assignment.get("motion_type") or "static").strip().lower() or "static"
        motion_status = str(assignment.get("motion_status") or "").strip().lower()
        motion_asset_path = str(assignment.get("motion_asset_path") or "").strip()

        if motion_type == "static":
            if motion_asset_path or motion_status:
                warnings.append(
                    f"{slide_id}: static row still carries motion metadata; it will not be used for handoff"
                )
            continue

        if motion_status != "approved":
            errors.append(
                f"{slide_id}: non-static motion rows must be approved before Irene Pass 2"
            )
            continue
        if not motion_asset_path:
            errors.append(
                f"{slide_id}: non-static motion rows must have motion_asset_path before Irene Pass 2"
            )
            continue
        resolved_asset = Path(motion_asset_path)
        if not resolved_asset.is_absolute():
            resolved_asset = (bundle_dir / resolved_asset).resolve()
        if not resolved_asset.is_file():
            errors.append(
                f"{slide_id}: approved motion asset is not readable on disk: {motion_asset_path}"
            )
            continue
        approved_assets[slide_id] = str(resolved_asset)

    return motion_enabled, approved_assets, warnings, errors


def _detect_non_authoritative_motion_leftovers(
    *,
    bundle_dir: Path,
    authorized_rows: list[dict[str, Any]],
    approved_assets: dict[str, str],
) -> list[str]:
    motion_dir = bundle_dir / "motion"
    if not motion_dir.is_dir():
        return []

    static_card_numbers = {
        int(row["card_number"])
        for row in authorized_rows
        if str(row["slide_id"]) not in approved_assets
    }
    approved_resolved = {Path(path).resolve() for path in approved_assets.values()}
    leftovers: set[str] = set()

    candidate_files = list(motion_dir.rglob("*"))
    candidate_files.extend(bundle_dir.glob("motion-generation-slide-*.json"))
    candidate_files.extend(bundle_dir.glob("motion-generation-slide-*.progress.json"))

    for path in candidate_files:
        if not path.is_file():
            continue
        if path.resolve() in approved_resolved:
            continue
        match = STATIC_MOTION_PATTERN.search(path.name)
        if not match:
            continue
        if int(match.group(1)) in static_card_numbers:
            leftovers.add(str(path.resolve()))

    return sorted(leftovers)


def _archive_stale_outputs(
    *,
    bundle_dir: Path,
    now: datetime,
) -> tuple[Path | None, list[dict[str, str]]]:
    stale_paths = [bundle_dir / name for name in STALE_PASS2_FILES if (bundle_dir / name).exists()]
    if not stale_paths:
        return None, []

    archive_dir = bundle_dir / ARCHIVE_SUBDIR / _timestamp_slug(now)
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived: list[dict[str, str]] = []
    for source in stale_paths:
        target = archive_dir / source.name
        shutil.move(str(source), str(target))
        archived.append({"source": str(source), "archived_to": str(target)})

    return archive_dir, archived


def prepare_irene_pass2_handoff(
    bundle_dir: str | Path,
    *,
    archive_stale: bool = True,
    now: datetime | None = None,
) -> dict[str, Any]:
    bundle = Path(bundle_dir).resolve()
    if not bundle.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle}")

    ts = now or _utc_now()
    errors: list[str] = []
    warnings: list[str] = []

    authorized_path = _bundle_input(bundle, "authorized-storyboard.json")
    dispatch_path = _bundle_input(bundle, "gary-dispatch-result.json")
    motion_plan_path = _bundle_input(bundle, "motion_plan.yaml")
    variant_selection_path = _bundle_input(bundle, "variant-selection.json")
    operator_directives_path = _bundle_input(bundle, "operator-directives.md")
    irene_pass1_path = _bundle_input(bundle, "irene-pass1.md")
    envelope_path = _bundle_input(bundle, DEFAULT_ENVELOPE_FILENAME)
    receipt_path = _bundle_input(bundle, DEFAULT_RECEIPT_FILENAME)

    if not authorized_path.is_file():
        raise FileNotFoundError(f"authorized-storyboard.json not found in bundle: {bundle}")
    if not dispatch_path.is_file():
        raise FileNotFoundError(f"gary-dispatch-result.json not found in bundle: {bundle}")

    authorized_storyboard = _load_json_object(authorized_path)
    dispatch_payload = _load_json_object(dispatch_path)
    motion_plan = _load_yaml_object(motion_plan_path) if motion_plan_path.is_file() else None

    gary_slide_output, slide_errors = _load_authorized_slide_output(
        authorized_storyboard,
        dispatch_payload=dispatch_payload,
        bundle_dir=bundle,
    )
    errors.extend(slide_errors)

    double_dispatch = bool(
        dispatch_payload.get("generation_mode") == "double-dispatch"
        or (
            isinstance(dispatch_payload.get("double_dispatch"), dict)
            and dispatch_payload["double_dispatch"].get("enabled")
        )
    )
    if double_dispatch and not variant_selection_path.is_file():
        errors.append("variant-selection.json is required for double-dispatch Pass 2 handoff")

    if not irene_pass1_path.is_file():
        errors.append("irene-pass1.md is required before Irene Pass 2 handoff")
    if not operator_directives_path.is_file():
        warnings.append("operator-directives.md is missing; handoff will proceed without an operator directives path")

    motion_enabled, approved_assets, motion_warnings, motion_errors = _validate_motion_plan(
        motion_plan=motion_plan,
        authorized_rows=gary_slide_output,
        bundle_dir=bundle,
    )
    warnings.extend(motion_warnings)
    errors.extend(motion_errors)

    non_authoritative_motion_leftovers = _detect_non_authoritative_motion_leftovers(
        bundle_dir=bundle,
        authorized_rows=gary_slide_output,
        approved_assets=approved_assets,
    )
    if non_authoritative_motion_leftovers:
        warnings.append(
            "Detected non-authoritative motion leftovers for slide(s) currently treated as static"
        )

    if errors:
        receipt = {
            "status": "fail",
            "prepared_at_utc": ts.isoformat(),
            "bundle_path": str(bundle),
            "errors": errors,
            "warnings": warnings,
            "approved_motion_assets": approved_assets,
            "non_authoritative_motion_leftovers": non_authoritative_motion_leftovers,
        }
        receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        return receipt

    archive_dir = None
    archived_files: list[dict[str, str]] = []
    if archive_stale:
        archive_dir, archived_files = _archive_stale_outputs(bundle_dir=bundle, now=ts)

    expected_outputs = [str(bundle / name) for name in EXPECTED_PASS2_OUTPUTS]
    runtime_plan = (
        _load_runtime_plan(bundle, irene_pass1_path)
        if irene_pass1_path.is_file()
        else None
    )
    voice_direction_defaults = _load_voice_direction_defaults()
    envelope: dict[str, Any] = {
        "run_id": str(
            dispatch_payload.get("run_id")
            or authorized_storyboard.get("run_id")
            or f"pass2-{_timestamp_slug(ts)}"
        ).strip(),
        "lesson_slug": str(
            dispatch_payload.get("lesson_slug")
            or authorized_storyboard.get("lesson_slug")
            or _slug_from_bundle_name(bundle)
        ).strip(),
        "bundle_path": str(bundle),
        "handoff_status": "prepared-pending-irene-pass2",
        "double_dispatch": double_dispatch,
        "motion_enabled": motion_enabled,
        "authorized_storyboard_path": str(authorized_path),
        "motion_plan_path": str(motion_plan_path) if motion_plan_path.is_file() else None,
        "operator_directives_path": str(operator_directives_path) if operator_directives_path.is_file() else None,
        "irene_pass1_path": str(irene_pass1_path) if irene_pass1_path.is_file() else None,
        "variant_selection_path": str(variant_selection_path) if double_dispatch and variant_selection_path.is_file() else None,
        "approved_motion_assets": approved_assets,
        "expected_outputs": expected_outputs,
        "gary_slide_output": gary_slide_output,
        "perception_artifacts": [],
        "context_paths": {
            "motion_plan": str(motion_plan_path) if motion_plan_path.is_file() else None,
        },
    }
    if runtime_plan:
        envelope["runtime_plan"] = runtime_plan
    if voice_direction_defaults:
        envelope["voice_direction_defaults"] = voice_direction_defaults
    literal_visual_publish = dispatch_payload.get("literal_visual_publish")
    if isinstance(literal_visual_publish, dict):
        envelope["literal_visual_publish"] = literal_visual_publish
    if motion_enabled:
        envelope["motion_perception_artifacts"] = []

    envelope_path.write_text(json.dumps(envelope, indent=2), encoding="utf-8")

    receipt = {
        "status": "prepared",
        "prepared_at_utc": ts.isoformat(),
        "bundle_path": str(bundle),
        "envelope_path": str(envelope_path),
        "expected_outputs": expected_outputs,
        "archive_dir": str(archive_dir) if archive_dir is not None else None,
        "archived_stale_outputs": archived_files,
        "double_dispatch": double_dispatch,
        "motion_enabled": motion_enabled,
        "approved_motion_assets": approved_assets,
        "non_authoritative_motion_leftovers": non_authoritative_motion_leftovers,
        "warnings": warnings,
        "errors": [],
        "next_action": "delegate-irene-pass2",
    }
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a fresh Irene Pass 2 handoff envelope")
    parser.add_argument(
        "--bundle",
        type=Path,
        required=True,
        help="Tracked source-bundle directory containing authorized-storyboard.json",
    )
    parser.add_argument(
        "--no-archive-stale",
        action="store_true",
        help="Do not archive existing bundle-root Pass 2 outputs before writing the new envelope",
    )
    args = parser.parse_args()

    try:
        result = prepare_irene_pass2_handoff(
            args.bundle,
            archive_stale=not args.no_archive_stale,
        )
        print(json.dumps(result, indent=2))
        return 0 if result["status"] == "prepared" else 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "fail",
                    "errors": [f"prepare_exception: {type(exc).__name__}: {exc}"],
                },
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
