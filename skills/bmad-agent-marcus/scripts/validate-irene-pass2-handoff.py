# /// script
# requires-python = ">=3.10"
# ///
"""Validate Irene Pass 2 completeness - post-Pass-2 check.

Story 11.3 gate (extended for stricter Pass 2 semantics):
- Require both gary_slide_output and perception_artifacts.
- Fail closed with explicit missing-field diagnostics.
- Preserve Gary card ordering as the source of truth for downstream narration.
- When bundle-root Pass 2 outputs are present, also validate:
  - every authorized slide has at least one manifest segment
  - every manifest segment has non-empty narration_text
  - every manifest segment has at least one non-empty visual narration cue
    traceable to perception and present in narration_text
  - every non-static motion segment is tied to the approved motion asset and
    has matching motion perception confirmation

Timing: Run AFTER Irene Pass 2 completes, not before delegation.
Perception artifacts are generated inline during Pass 2
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
NARRATION_SCRIPT_FILENAME = "narration-script.md"
SEGMENT_MANIFEST_FILENAME = "segment-manifest.yaml"
PERCEPTION_ARTIFACTS_FILENAME = "perception-artifacts.json"
PROJECT_ROOT = Path(__file__).resolve().parents[3]
NARRATION_PARAMS_PATH = PROJECT_ROOT / "state" / "config" / "narration-script-parameters.yaml"


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


def _resolve_local_path(path_value: str, *, bundle_dir: Path | None) -> Path:
    candidate = Path(path_value)
    if candidate.is_absolute():
        return candidate.resolve(strict=False)
    if bundle_dir is not None:
        return (bundle_dir / candidate).resolve(strict=False)
    return (PROJECT_ROOT / candidate).resolve(strict=False)


def _normalize_path_string(path_value: str, *, bundle_dir: Path | None) -> str:
    return str(_resolve_local_path(path_value, bundle_dir=bundle_dir))


def _load_payload(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
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


def _bundle_dir_from_inputs(
    payload: dict[str, Any],
    *,
    envelope_path: Path | None,
) -> Path | None:
    if envelope_path is not None:
        return envelope_path.parent
    bundle_path = payload.get("bundle_path")
    if isinstance(bundle_path, str) and bundle_path.strip():
        return _resolve_local_path(bundle_path.strip(), bundle_dir=None)
    return None


def _resolve_bundle_output_path(
    payload: dict[str, Any],
    *,
    bundle_dir: Path | None,
    filename: str,
) -> Path | None:
    expected_outputs = payload.get("expected_outputs", [])
    if isinstance(expected_outputs, list):
        for entry in expected_outputs:
            if not isinstance(entry, str):
                continue
            candidate = Path(entry)
            if candidate.name.lower() == filename.lower():
                return _resolve_local_path(entry, bundle_dir=bundle_dir)

    if bundle_dir is None:
        return None
    return bundle_dir / filename


def _load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object at the top level")
    return data


def _load_yaml_object(path: Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required for segment-manifest validation")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a YAML mapping at the top level")
    return data


def _load_json_array(path: Path) -> list[Any]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, list):
        raise ValueError(f"{path.name} must contain a JSON array at the top level")
    return data


def _load_meta_slide_language_guardrails() -> dict[str, Any]:
    """Load narration anti-meta guardrails from narration-script-parameters.yaml."""
    if yaml is None or not NARRATION_PARAMS_PATH.is_file():
        return {"policy": "allowed", "forbidden_phrases": []}

    try:
        data = yaml.safe_load(NARRATION_PARAMS_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {"policy": "allowed", "forbidden_phrases": []}

    visual = data.get("visual_narration", {})
    if not isinstance(visual, dict):
        return {"policy": "allowed", "forbidden_phrases": []}

    policy = str(visual.get("meta_slide_language") or "allowed").strip().lower()
    phrases_raw = visual.get("forbidden_meta_phrases", [])
    if not isinstance(phrases_raw, list):
        phrases_raw = []

    forbidden_phrases = [
        str(item).strip().lower()
        for item in phrases_raw
        if isinstance(item, str) and str(item).strip()
    ]
    return {"policy": policy, "forbidden_phrases": forbidden_phrases}


def _find_forbidden_meta_segments_in_script(
    narration_path: Path,
    *,
    forbidden_phrases: list[str],
) -> list[str]:
    """Return segment IDs in narration-script.md containing forbidden phrases."""
    if not forbidden_phrases:
        return []

    text = narration_path.read_text(encoding="utf-8")
    flagged: list[str] = []
    current_segment: str | None = None
    current_lines: list[str] = []

    def flush_segment() -> None:
        if current_segment is None:
            return
        lowered = "\n".join(current_lines).lower()
        if any(phrase in lowered for phrase in forbidden_phrases):
            flagged.append(current_segment)

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("[SEGMENT:") and line.endswith("]"):
            flush_segment()
            current_segment = line[len("[SEGMENT:") : -1].strip()
            current_lines = []
            continue
        if current_segment is not None:
            current_lines.append(raw_line)

    flush_segment()
    return sorted(set(flagged))


def _extract_behavioral_intents_from_script(narration_path: Path) -> dict[str, str]:
    """Parse `[SEGMENT: ...]` blocks and extract stage-direction behavioral intents."""
    intents: dict[str, str] = {}
    current_segment: str | None = None

    for raw_line in narration_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("[SEGMENT:") and line.endswith("]"):
            current_segment = line[len("[SEGMENT:") : -1].strip()
            continue
        if current_segment is None:
            continue
        if line.lower().startswith("- behavioral intent:"):
            intent = line.split(":", 1)[1].strip()
            if intent:
                intents[current_segment] = intent
    return intents


def _artifact_identity_key(artifact: dict[str, Any]) -> str:
    slide_id = str(artifact.get("slide_id") or "").strip()
    if slide_id:
        return slide_id
    artifact_path = str(artifact.get("artifact_path") or "").strip()
    if artifact_path:
        return artifact_path
    return json.dumps(artifact, sort_keys=True)


def _normalize_artifact_for_compare(artifact: dict[str, Any]) -> str:
    return json.dumps(artifact, sort_keys=True)


def _load_authorized_slide_ids(
    payload: dict[str, Any],
    *,
    bundle_dir: Path | None,
    gary_slide_ids: list[str],
) -> list[str]:
    authorized_path_value = payload.get("authorized_storyboard_path")
    if isinstance(authorized_path_value, str) and authorized_path_value.strip():
        authorized_path = _resolve_existing_local_path(authorized_path_value, bundle_dir=bundle_dir)
        if authorized_path is not None:
            data = _load_json_object(authorized_path)
            slide_ids = data.get("slide_ids", [])
            if isinstance(slide_ids, list):
                normalized = [str(item).strip() for item in slide_ids if str(item).strip()]
                if normalized:
                    return normalized
    return gary_slide_ids


def _load_motion_plan_assignments(
    payload: dict[str, Any],
    *,
    bundle_dir: Path | None,
) -> dict[str, dict[str, Any]]:
    motion_path_value = payload.get("motion_plan_path")
    if not isinstance(motion_path_value, str) or not motion_path_value.strip():
        return {}

    motion_plan_path = _resolve_existing_local_path(motion_path_value, bundle_dir=bundle_dir)
    if motion_plan_path is None:
        return {}

    motion_plan = _load_yaml_object(motion_plan_path)
    slides = motion_plan.get("slides", [])
    if not isinstance(slides, list):
        return {}

    by_slide_id: dict[str, dict[str, Any]] = {}
    for row in slides:
        if not isinstance(row, dict):
            continue
        slide_id = str(row.get("slide_id") or "").strip()
        if slide_id:
            by_slide_id[slide_id] = row
    return by_slide_id


def _build_perception_element_lookup(
    perception_artifacts: list[dict[str, Any]],
) -> dict[str, set[str]]:
    lookup: dict[str, set[str]] = {}
    for artifact in perception_artifacts:
        if not isinstance(artifact, dict):
            continue
        slide_id = str(artifact.get("slide_id") or "").strip()
        if not slide_id:
            continue
        elements = artifact.get("visual_elements", [])
        descriptions: set[str] = set()
        if isinstance(elements, list):
            for element in elements:
                if not isinstance(element, dict):
                    continue
                description = str(element.get("description") or "").strip()
                if description:
                    descriptions.add(description)
        lookup[slide_id] = descriptions
    return lookup


def _validate_bundle_pass2_outputs(
    payload: dict[str, Any],
    *,
    bundle_dir: Path | None,
    gary_slide_ids: list[str],
    gary_slide_path_by_id: dict[str, str],
    perception_artifacts: list[dict[str, Any]],
) -> dict[str, Any]:
    details: dict[str, Any] = {
        "narration_script_path": None,
        "segment_manifest_path": None,
        "perception_artifacts_path": None,
        "authorized_slide_count": 0,
        "manifest_segment_count": 0,
        "narration_script_missing": False,
        "narration_script_empty": False,
        "segment_manifest_missing": False,
        "segment_manifest_invalid": False,
        "perception_artifacts_missing": False,
        "perception_artifacts_invalid": False,
        "missing_manifest_for_slide_ids": [],
        "unknown_manifest_slide_ids": [],
        "segments_missing_narration_text": [],
        "segments_missing_visual_narration_cue": [],
        "segments_with_untraceable_visual_cues": [],
        "segments_with_forbidden_meta_slide_language": [],
        "script_segments_with_forbidden_meta_slide_language": [],
        "segments_with_behavioral_intent_mismatch": [],
        "perception_artifact_mismatches": [],
        "motion_segments_missing_perception_confirmation": [],
        "motion_segments_with_unapproved_asset_binding": [],
    }

    if bundle_dir is None:
        return {"errors": [], "details": details}

    errors: list[str] = []
    meta_guardrails = _load_meta_slide_language_guardrails()

    narration_path = _resolve_bundle_output_path(
        payload,
        bundle_dir=bundle_dir,
        filename=NARRATION_SCRIPT_FILENAME,
    )
    manifest_path = _resolve_bundle_output_path(
        payload,
        bundle_dir=bundle_dir,
        filename=SEGMENT_MANIFEST_FILENAME,
    )
    perception_path = _resolve_bundle_output_path(
        payload,
        bundle_dir=bundle_dir,
        filename=PERCEPTION_ARTIFACTS_FILENAME,
    )

    if narration_path is not None:
        details["narration_script_path"] = str(narration_path)
    if manifest_path is not None:
        details["segment_manifest_path"] = str(manifest_path)
    if perception_path is not None:
        details["perception_artifacts_path"] = str(perception_path)

    if narration_path is None or not narration_path.is_file():
        details["narration_script_missing"] = True
        errors.append(f"Missing required Pass 2 artifact: {NARRATION_SCRIPT_FILENAME}")
    else:
        narration_text = narration_path.read_text(encoding="utf-8").strip()
        if not narration_text:
            details["narration_script_empty"] = True
            errors.append(f"{NARRATION_SCRIPT_FILENAME} exists but is empty")
        elif meta_guardrails["policy"] == "forbidden":
            details["script_segments_with_forbidden_meta_slide_language"] = (
                _find_forbidden_meta_segments_in_script(
                    narration_path,
                    forbidden_phrases=meta_guardrails["forbidden_phrases"],
                )
            )
    script_behavioral_intents = (
        _extract_behavioral_intents_from_script(narration_path)
        if narration_path is not None and narration_path.is_file()
        else {}
    )

    if perception_path is None or not perception_path.is_file():
        details["perception_artifacts_missing"] = True
        errors.append(f"Missing required Pass 2 artifact: {PERCEPTION_ARTIFACTS_FILENAME}")
        standalone_perception_artifacts: list[dict[str, Any]] = []
    else:
        try:
            standalone_raw = _load_json_array(perception_path)
            standalone_perception_artifacts = [
                item for item in standalone_raw if isinstance(item, dict)
            ]
        except Exception as exc:
            details["perception_artifacts_invalid"] = True
            errors.append(f"{PERCEPTION_ARTIFACTS_FILENAME} is invalid: {type(exc).__name__}: {exc}")
            standalone_perception_artifacts = []

    if manifest_path is None or not manifest_path.is_file():
        details["segment_manifest_missing"] = True
        errors.append(f"Missing required Pass 2 artifact: {SEGMENT_MANIFEST_FILENAME}")
        return {"errors": errors, "details": details}

    try:
        manifest = _load_yaml_object(manifest_path)
    except Exception as exc:
        details["segment_manifest_invalid"] = True
        errors.append(f"{SEGMENT_MANIFEST_FILENAME} is invalid: {type(exc).__name__}: {exc}")
        return {"errors": errors, "details": details}

    segments = manifest.get("segments", [])
    if not isinstance(segments, list):
        details["segment_manifest_invalid"] = True
        errors.append(f"{SEGMENT_MANIFEST_FILENAME} segments must be a list")
        return {"errors": errors, "details": details}

    details["manifest_segment_count"] = len(segments)

    authorized_slide_ids = _load_authorized_slide_ids(
        payload,
        bundle_dir=bundle_dir,
        gary_slide_ids=gary_slide_ids,
    )
    details["authorized_slide_count"] = len(authorized_slide_ids)

    manifest_slide_ids: list[str] = []
    manifest_slide_id_set: set[str] = set()
    motion_segments: list[dict[str, Any]] = []
    perception_elements_by_slide = _build_perception_element_lookup(perception_artifacts)
    perception_slide_ids = {
        str(item.get("slide_id") or "").strip()
        for item in perception_artifacts
        if isinstance(item, dict)
    }
    motion_plan_by_slide_id = _load_motion_plan_assignments(payload, bundle_dir=bundle_dir)
    motion_perception_artifacts = payload.get("motion_perception_artifacts", [])
    if motion_perception_artifacts is not None and not isinstance(motion_perception_artifacts, list):
        motion_perception_artifacts = []

    motion_confirmations: dict[str, set[str]] = {}
    if isinstance(motion_perception_artifacts, list):
        for artifact in motion_perception_artifacts:
            if not isinstance(artifact, dict):
                continue
            slide_id = str(artifact.get("slide_id") or "").strip()
            if not slide_id:
                continue
            source_motion_path = str(
                artifact.get("source_motion_path")
                or artifact.get("artifact_path")
                or ""
            ).strip()
            if not source_motion_path:
                continue
            motion_confirmations.setdefault(slide_id, set()).add(
                _normalize_path_string(source_motion_path, bundle_dir=bundle_dir)
            )

    segments_missing_narration_text: list[str] = []
    segments_missing_visual_narration_cue: list[str] = []
    segments_with_untraceable_visual_cues: list[str] = []
    motion_segments_missing_perception_confirmation: list[str] = []
    motion_segments_with_unapproved_asset_binding: list[str] = []
    motion_segments_with_noncanonical_visual_file: list[str] = []
    segments_with_forbidden_meta_slide_language: list[str] = []
    segments_with_behavioral_intent_mismatch: list[str] = []
    for segment in segments:
        if not isinstance(segment, dict):
            continue
        seg_id = str(segment.get("id") or "<missing-id>").strip() or "<missing-id>"
        slide_id = str(segment.get("gary_slide_id") or segment.get("slide_id") or "").strip()
        if slide_id:
            manifest_slide_ids.append(slide_id)
            manifest_slide_id_set.add(slide_id)

        narration_text = str(segment.get("narration_text") or "").strip()
        if not narration_text:
            segments_missing_narration_text.append(seg_id)
        elif meta_guardrails["policy"] == "forbidden":
            lowered = narration_text.lower()
            if any(phrase in lowered for phrase in meta_guardrails["forbidden_phrases"]):
                segments_with_forbidden_meta_slide_language.append(seg_id)
        script_intent = str(script_behavioral_intents.get(seg_id) or "").strip()
        manifest_intent = str(segment.get("behavioral_intent") or "").strip()
        if script_intent and manifest_intent and script_intent != manifest_intent:
            segments_with_behavioral_intent_mismatch.append(seg_id)

        refs = segment.get("visual_references", [])
        valid_visual_cue_found = False
        if isinstance(refs, list):
            for ref in refs:
                if not isinstance(ref, dict):
                    continue
                cue = str(ref.get("narration_cue") or "").strip()
                source = str(ref.get("perception_source") or "").strip()
                element = str(ref.get("element") or "").strip()
                if not cue:
                    continue
                if cue not in narration_text:
                    continue
                if not source or source not in perception_slide_ids:
                    continue
                available_elements = perception_elements_by_slide.get(source, set())
                if available_elements and element and element not in available_elements:
                    continue
                valid_visual_cue_found = True
                break
        if not isinstance(refs, list) or not refs or not valid_visual_cue_found:
            segments_missing_visual_narration_cue.append(seg_id)
        elif slide_id:
            # Only classify as traceable once a cue exists and the slide identity is known.
            trace_sources = {
                str(ref.get("perception_source") or "").strip()
                for ref in refs
                if isinstance(ref, dict) and str(ref.get("narration_cue") or "").strip()
            }
            if not trace_sources:
                segments_with_untraceable_visual_cues.append(seg_id)

        motion_type = str(segment.get("motion_type") or "static").strip().lower() or "static"
        if motion_type != "static":
            motion_segments.append(segment)
            approved_assignment = motion_plan_by_slide_id.get(slide_id, {})
            approved_asset = str(approved_assignment.get("motion_asset_path") or "").strip()
            segment_asset = str(segment.get("motion_asset_path") or "").strip()
            segment_status = str(segment.get("motion_status") or "").strip().lower()
            approved_status = str(approved_assignment.get("motion_status") or "").strip().lower()
            segment_visual_file = str(segment.get("visual_file") or "").strip()
            approved_slide_png = str(gary_slide_path_by_id.get(slide_id) or "").strip()

            canonical_visual_ok = bool(
                approved_slide_png
                and segment_visual_file
                and _normalize_path_string(segment_visual_file, bundle_dir=bundle_dir)
                == _normalize_path_string(approved_slide_png, bundle_dir=bundle_dir)
            )
            if not canonical_visual_ok:
                motion_segments_with_noncanonical_visual_file.append(seg_id)

            approved_ok = bool(
                approved_asset
                and segment_asset
                and segment_status == "approved"
                and approved_status == "approved"
                and _normalize_path_string(segment_asset, bundle_dir=bundle_dir)
                == _normalize_path_string(approved_asset, bundle_dir=bundle_dir)
            )
            if not approved_ok:
                motion_segments_with_unapproved_asset_binding.append(seg_id)
                continue

            confirmed_paths = motion_confirmations.get(slide_id, set())
            expected_path = _normalize_path_string(approved_asset, bundle_dir=bundle_dir)
            if expected_path not in confirmed_paths:
                motion_segments_missing_perception_confirmation.append(seg_id)

    missing_manifest_for_slide_ids = [
        slide_id for slide_id in authorized_slide_ids if slide_id not in manifest_slide_id_set
    ]
    unknown_manifest_slide_ids = sorted(manifest_slide_id_set - set(authorized_slide_ids))

    details["missing_manifest_for_slide_ids"] = missing_manifest_for_slide_ids
    details["unknown_manifest_slide_ids"] = unknown_manifest_slide_ids
    details["segments_missing_narration_text"] = sorted(set(segments_missing_narration_text))
    details["segments_missing_visual_narration_cue"] = sorted(set(segments_missing_visual_narration_cue))
    details["segments_with_untraceable_visual_cues"] = sorted(set(segments_with_untraceable_visual_cues))
    details["segments_with_forbidden_meta_slide_language"] = sorted(
        set(segments_with_forbidden_meta_slide_language)
    )
    details["segments_with_behavioral_intent_mismatch"] = sorted(
        set(segments_with_behavioral_intent_mismatch)
    )
    details["motion_segments_missing_perception_confirmation"] = sorted(
        set(motion_segments_missing_perception_confirmation)
    )
    details["motion_segments_with_unapproved_asset_binding"] = sorted(
        set(motion_segments_with_unapproved_asset_binding)
    )
    details["motion_segments_with_noncanonical_visual_file"] = sorted(
        set(motion_segments_with_noncanonical_visual_file)
    )
    envelope_artifacts_by_key = {
        _artifact_identity_key(item): _normalize_artifact_for_compare(item)
        for item in perception_artifacts
        if isinstance(item, dict)
    }
    standalone_artifacts_by_key = {
        _artifact_identity_key(item): _normalize_artifact_for_compare(item)
        for item in standalone_perception_artifacts
        if isinstance(item, dict)
    }
    mismatch_keys = sorted(
        key
        for key in set(envelope_artifacts_by_key) | set(standalone_artifacts_by_key)
        if envelope_artifacts_by_key.get(key) != standalone_artifacts_by_key.get(key)
    )
    details["perception_artifact_mismatches"] = mismatch_keys

    if missing_manifest_for_slide_ids:
        errors.append(
            "segment-manifest.yaml missing at least one segment for slide_id(s): "
            + ", ".join(missing_manifest_for_slide_ids)
        )
    if unknown_manifest_slide_ids:
        errors.append(
            "segment-manifest.yaml references unknown slide_id(s): "
            + ", ".join(unknown_manifest_slide_ids)
        )
    if segments_missing_narration_text:
        errors.append(
            "segment-manifest.yaml has segment(s) with empty narration_text: "
            + ", ".join(sorted(set(segments_missing_narration_text)))
        )
    if segments_missing_visual_narration_cue:
        errors.append(
            "segment-manifest.yaml has segment(s) without a non-empty visual narration_cue tied to perception and present in narration_text: "
            + ", ".join(sorted(set(segments_missing_visual_narration_cue)))
        )
    if segments_with_forbidden_meta_slide_language:
        errors.append(
            "segment-manifest.yaml has segment(s) using forbidden meta slide-language while audience-directed narration is required: "
            + ", ".join(sorted(set(segments_with_forbidden_meta_slide_language)))
        )
    if details["script_segments_with_forbidden_meta_slide_language"]:
        errors.append(
            "narration-script.md has segment(s) using forbidden meta slide-language while audience-directed narration is required: "
            + ", ".join(details["script_segments_with_forbidden_meta_slide_language"])
        )
    if details["segments_with_behavioral_intent_mismatch"]:
        errors.append(
            "narration-script.md and segment-manifest.yaml disagree on behavioral_intent for segment(s): "
            + ", ".join(details["segments_with_behavioral_intent_mismatch"])
        )
    if mismatch_keys:
        errors.append(
            "perception-artifacts.json must match the envelope perception_artifacts for artifact key(s): "
            + ", ".join(mismatch_keys)
        )
    if motion_segments and not isinstance(payload.get("motion_perception_artifacts"), list):
        errors.append(
            "motion-enabled Pass 2 requires motion_perception_artifacts aligned to non-static segments"
        )
    if motion_segments_with_unapproved_asset_binding:
        errors.append(
            "motion segment(s) are not bound to the approved motion asset from motion_plan.yaml: "
            + ", ".join(sorted(set(motion_segments_with_unapproved_asset_binding)))
        )
    if motion_segments_with_noncanonical_visual_file:
        errors.append(
            "motion segment(s) must keep visual_file bound to the approved Gary/Gamma still instead of the motion clip: "
            + ", ".join(sorted(set(motion_segments_with_noncanonical_visual_file)))
        )
    if motion_segments_missing_perception_confirmation:
        errors.append(
            "motion segment(s) are missing motion perception confirmation for the approved asset: "
            + ", ".join(sorted(set(motion_segments_missing_perception_confirmation)))
        )

    return {"errors": errors, "details": details}


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
    png_card_mismatch_for: list[str] = []
    gary_slide_path_by_id: dict[str, str] = {}
    bundle_dir = _bundle_dir_from_inputs(payload, envelope_path=envelope_path)
    for item in gary:
        if not isinstance(item, dict):
            continue
        slide_label = str(item.get("slide_id") or item.get("card_number") or "unknown")
        file_path = item.get("file_path")
        source_ref = item.get("source_ref")
        card_number = item.get("card_number")
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

            # Check PNG filename number matches card_number
            if isinstance(card_number, int) and card_number > 0:
                filename = Path(normalized_path).name
                if filename.startswith("slide_") and filename.endswith(".png"):
                    num_str = filename[6:-4]  # Remove "slide_" and ".png"
                    try:
                        filename_number = int(num_str)
                        if filename_number != card_number:
                            png_card_mismatch_for.append(slide_label)
                    except ValueError:
                        pass  # Non-numeric, skip check

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

    gary_slide_ids = [
        str(item.get("slide_id")).strip()
        for item in gary
        if isinstance(item, dict) and item.get("slide_id")
    ]
    perception_slide_ids = {
        str(item.get("slide_id"))
        for item in perception
        if isinstance(item, dict) and item.get("slide_id")
    }

    missing_perception_for = sorted(set(gary_slide_ids) - perception_slide_ids)
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

    bundle_checks = _validate_bundle_pass2_outputs(
        payload,
        bundle_dir=bundle_dir,
        gary_slide_ids=gary_slide_ids,
        gary_slide_path_by_id=gary_slide_path_by_id,
        perception_artifacts=[item for item in perception if isinstance(item, dict)],
    )
    errors.extend(bundle_checks["errors"])

    remediation_hint = (
        "Perception artifacts are emitted inline during Pass 2. "
        "If missing, re-run Irene on the affected slides to regenerate perception side-effects. "
        "Narration grounding must use local post-integration downloaded PNGs from gary_slide_output. "
        "Pass 2 must also produce a complete segment-manifest.yaml with non-empty narration_text "
        "and traceable visual narration cues for every authorized slide."
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
        "pass2_outputs": bundle_checks["details"],
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
