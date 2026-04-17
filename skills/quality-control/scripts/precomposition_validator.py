# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Deterministic pre-composition validation for assembly-bundle manifests."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml

DEFAULT_MIN_WPM = 130.0
DEFAULT_MAX_WPM = 170.0
DEFAULT_MOTION_TOLERANCE_SECONDS = 0.5
VTT_TIMESTAMP_RE = re.compile(r"^(\d{2}):(\d{2}):(\d{2})\.(\d{3})$")
WORD_RE = re.compile(r"\b\w+(?:[-']\w+)?\b")


def _parse_vtt_timestamp(value: str) -> float:
    # WebVTT cue timing may include trailing settings (e.g., "align:start").
    timestamp_token = value.strip().split()[0] if value.strip() else ""
    match = VTT_TIMESTAMP_RE.match(timestamp_token)
    if not match:
        raise ValueError(f"Invalid VTT timestamp: {value}")
    hours, minutes, seconds, milliseconds = (int(part) for part in match.groups())
    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0


def _iter_vtt_cues(vtt_text: str) -> list[tuple[float, float]]:
    cues: list[tuple[float, float]] = []
    for line in vtt_text.splitlines():
        if "-->" not in line:
            continue
        start_text, end_text = (part.strip() for part in line.split("-->", 1))
        cues.append((_parse_vtt_timestamp(start_text), _parse_vtt_timestamp(end_text)))
    return cues


def _word_count(text: str) -> int:
    return len(WORD_RE.findall(text or ""))


def _coerce_non_negative_float(value: Any) -> float | None:
    """Return parsed float for optional non-negative values, else None."""
    if value in (None, ""):
        return None
    parsed = float(value)
    if parsed < 0:
        raise ValueError("must be >= 0")
    return parsed


def _normalize_path(path_value: str | None, repo_root: Path) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    return path if path.is_absolute() else (repo_root / path)


def _severity_for_dimension(dimension: str) -> str:
    return "high" if dimension in {"AQ", "CI"} else "medium"


def _make_finding(
    *,
    severity: str,
    dimension: str,
    location: str,
    description: str,
    fix_suggestion: str,
    remediation_target: str | None = None,
    blocking: bool = True,
) -> dict[str, Any]:
    payload = {
        "severity": severity,
        "dimension": dimension,
        "location": location,
        "description": description,
        "fix_suggestion": fix_suggestion,
        "blocking": blocking,
    }
    if remediation_target:
        payload["remediation_target"] = remediation_target
    return payload


def _validate_vtt_monotonicity(vtt_path: Path) -> list[str]:
    cues = _iter_vtt_cues(vtt_path.read_text(encoding="utf-8"))
    issues: list[str] = []
    previous_end = -1.0
    for index, (start, end) in enumerate(cues, start=1):
        if end < start:
            issues.append(
                f"Cue {index} has end before start ({start:.3f}s -> {end:.3f}s)."
            )
        if previous_end > start:
            issues.append(
                f"Cue {index} starts before prior cue ends ({start:.3f}s < {previous_end:.3f}s)."
            )
        previous_end = max(previous_end, end)
    if not cues:
        issues.append("No caption cues found.")
    return issues


def validate_precomposition(
    manifest_path: str | Path,
    *,
    repo_root: str | Path | None = None,
    min_wpm: float = DEFAULT_MIN_WPM,
    max_wpm: float = DEFAULT_MAX_WPM,
    motion_tolerance_seconds: float = DEFAULT_MOTION_TOLERANCE_SECONDS,
) -> dict[str, Any]:
    manifest_path = Path(manifest_path).resolve()
    root = Path(repo_root).resolve() if repo_root else Path.cwd().resolve()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    segments = manifest.get("segments") or []
    findings: list[dict[str, Any]] = []
    notes: list[str] = []
    segment_metrics: list[dict[str, Any]] = []

    if not segments:
        findings.append(
            _make_finding(
                severity="high",
                dimension="AQ",
                location=str(manifest_path),
                description="Manifest has no segments for pre-composition review.",
                fix_suggestion="Rebuild the assembly-bundle manifest before Quinn-R pre-composition review.",
                remediation_target="ElevenLabs",
            )
        )

    for segment in segments:
        segment_id = str(segment.get("id") or "<unknown>")
        narration_text = str(segment.get("narration_text") or "")
        narration_duration = segment.get("narration_duration")
        narration_file = _normalize_path(segment.get("narration_file"), root)
        narration_vtt = _normalize_path(segment.get("narration_vtt"), root)
        visual_file = _normalize_path(segment.get("visual_file"), root)
        sfx_file = _normalize_path(segment.get("sfx_file"), root)
        motion_type = str(segment.get("motion_type") or "static").strip().lower()
        motion_asset_path = _normalize_path(segment.get("motion_asset_path"), root)
        motion_duration = segment.get("motion_duration_seconds")
        duration_estimate = segment.get("duration_estimate_seconds")
        bridge_type = str(segment.get("bridge_type") or "none").strip().lower()
        onset_delay = segment.get("onset_delay")
        dwell = segment.get("dwell")
        cluster_gap = segment.get("cluster_gap")
        transition_buffer = segment.get("transition_buffer")

        timing_values: dict[str, float | None] = {}
        for field_name, raw_value in (
            ("onset_delay", onset_delay),
            ("dwell", dwell),
            ("cluster_gap", cluster_gap),
            ("transition_buffer", transition_buffer),
        ):
            try:
                timing_values[field_name] = _coerce_non_negative_float(raw_value)
            except (TypeError, ValueError):
                findings.append(
                    _make_finding(
                        severity=_severity_for_dimension("CI"),
                        dimension="CI",
                        location=segment_id,
                        description=f"{field_name} must be a non-negative number when present.",
                        fix_suggestion=f"Set `{field_name}` to a numeric value >= 0 or remove it.",
                        remediation_target="motion/editing decision",
                    )
                )
                timing_values[field_name] = None

        if timing_values["cluster_gap"] not in (None, 0.0) and bridge_type != "cluster_boundary":
            findings.append(
                _make_finding(
                    severity=_severity_for_dimension("CI"),
                    dimension="CI",
                    location=segment_id,
                    description=(
                        "cluster_gap is only valid on cluster-boundary segments "
                        "(bridge_type must be cluster_boundary)."
                    ),
                    fix_suggestion="Set bridge_type to cluster_boundary or reset cluster_gap to 0.",
                    remediation_target="motion/editing decision",
                )
            )

        if narration_duration in (None, ""):
            findings.append(
                _make_finding(
                    severity=_severity_for_dimension("AQ"),
                    dimension="AQ",
                    location=segment_id,
                    description="Missing narration_duration in assembly manifest.",
                    fix_suggestion="Re-run ElevenLabs manifest synthesis so the downstream manifest is fully populated.",
                    remediation_target="ElevenLabs",
                )
            )
            continue

        try:
            narration_duration = float(narration_duration)
        except (TypeError, ValueError):
            findings.append(
                _make_finding(
                    severity=_severity_for_dimension("AQ"),
                    dimension="AQ",
                    location=segment_id,
                    description="narration_duration must be numeric.",
                    fix_suggestion="Populate narration_duration with a numeric seconds value from ElevenLabs output.",
                    remediation_target="ElevenLabs",
                )
            )
            continue
        if narration_duration <= 0:
            findings.append(
                _make_finding(
                    severity=_severity_for_dimension("AQ"),
                    dimension="AQ",
                    location=segment_id,
                    description="narration_duration must be greater than 0 seconds.",
                    fix_suggestion="Re-run narration generation and write back a positive narration_duration.",
                    remediation_target="ElevenLabs",
                )
            )
            continue
        words = _word_count(narration_text)
        wpm = round(words / (narration_duration / 60.0), 2) if narration_duration > 0 else 0.0
        estimated_wpm = None
        if duration_estimate not in (None, ""):
            try:
                duration_estimate = float(duration_estimate)
            except (TypeError, ValueError):
                findings.append(
                    _make_finding(
                        severity="medium",
                        dimension="AQ",
                        location=segment_id,
                        description="duration_estimate_seconds must be numeric when present.",
                        fix_suggestion="Set duration_estimate_seconds to a numeric seconds value or remove it.",
                        remediation_target="Irene",
                        blocking=False,
                    )
                )
                duration_estimate = None
            if duration_estimate and duration_estimate > 0:
                estimated_wpm = round(words / (duration_estimate / 60.0), 2)

        if not narration_file or not narration_file.is_file():
            findings.append(
                _make_finding(
                    severity=_severity_for_dimension("AQ"),
                    dimension="AQ",
                    location=segment_id,
                    description="Narration file is missing or unreadable.",
                    fix_suggestion="Regenerate the missing narration asset from the approved assembly-bundle manifest.",
                    remediation_target="ElevenLabs",
                )
            )
        if not narration_vtt or not narration_vtt.is_file():
            findings.append(
                _make_finding(
                    severity=_severity_for_dimension("AQ"),
                    dimension="AQ",
                    location=segment_id,
                    description="Caption file is missing or unreadable.",
                    fix_suggestion="Re-run ElevenLabs caption generation for this segment from the approved manifest.",
                    remediation_target="ElevenLabs",
                )
            )
        if not visual_file or not visual_file.is_file():
            findings.append(
                _make_finding(
                    severity=_severity_for_dimension("CI"),
                    dimension="CI",
                    location=segment_id,
                    description="Approved still reference is missing or unreadable.",
                    fix_suggestion="Restore the approved still PNG before compositor packaging.",
                    remediation_target="motion/editing decision",
                )
            )
        if sfx_file and not sfx_file.is_file():
            findings.append(
                _make_finding(
                    severity=_severity_for_dimension("CI"),
                    dimension="CI",
                    location=segment_id,
                    description="Referenced SFX file is missing or unreadable.",
                    fix_suggestion="Regenerate or remove the missing SFX reference before compositor packaging.",
                    remediation_target="ElevenLabs",
                )
            )

        if narration_vtt and narration_vtt.is_file():
            monotonicity_issues = _validate_vtt_monotonicity(narration_vtt)
            for issue in monotonicity_issues:
                findings.append(
                    _make_finding(
                        severity=_severity_for_dimension("AQ"),
                        dimension="AQ",
                        location=segment_id,
                        description=f"VTT monotonicity failure: {issue}",
                        fix_suggestion="Regenerate the VTT from the approved narration output; do not hand-edit timestamps silently.",
                        remediation_target="ElevenLabs",
                    )
                )

        if words > 0 and (wpm < min_wpm or wpm > max_wpm):
            if estimated_wpm is not None and (estimated_wpm < min_wpm or estimated_wpm > max_wpm):
                notes.append(
                    f"{segment_id}: actual pace is {wpm:.2f} WPM, but the locked script and "
                    f"duration estimate already imply {estimated_wpm:.2f} WPM. Review Irene runtime "
                    "planning against the approved script before blaming ElevenLabs pacing."
                )
            else:
                findings.append(
                    _make_finding(
                        severity=_severity_for_dimension("AQ"),
                        dimension="AQ",
                        location=segment_id,
                        description=f"Narration pace is {wpm:.2f} WPM (target {min_wpm:.0f}-{max_wpm:.0f}).",
                        fix_suggestion="Adjust narration pacing and re-run ElevenLabs for this segment from the approved text.",
                        remediation_target="ElevenLabs",
                    )
                )

        if motion_type != "static":
            if not motion_asset_path or not motion_asset_path.is_file():
                findings.append(
                    _make_finding(
                        severity=_severity_for_dimension("CI"),
                        dimension="CI",
                        location=segment_id,
                        description="Non-static segment has unreadable motion_asset_path.",
                        fix_suggestion="Restore the approved motion clip or make an explicit motion/editing decision before compositor.",
                        remediation_target="motion/editing decision",
                    )
                )
            if motion_duration in (None, ""):
                findings.append(
                    _make_finding(
                        severity=_severity_for_dimension("CI"),
                        dimension="CI",
                        location=segment_id,
                        description="Non-static segment is missing motion_duration_seconds.",
                        fix_suggestion="Record the approved motion clip duration before compositor packaging.",
                        remediation_target="motion/editing decision",
                    )
                )
            else:
                try:
                    motion_duration = float(motion_duration)
                except (TypeError, ValueError):
                    findings.append(
                        _make_finding(
                            severity=_severity_for_dimension("CI"),
                            dimension="CI",
                            location=segment_id,
                            description="motion_duration_seconds must be numeric for non-static segments.",
                            fix_suggestion="Write motion_duration_seconds as a numeric seconds value.",
                            remediation_target="motion/editing decision",
                        )
                    )
                    motion_duration = None
                if motion_duration is None:
                    continue
                if motion_duration <= 0:
                    findings.append(
                        _make_finding(
                            severity=_severity_for_dimension("CI"),
                            dimension="CI",
                            location=segment_id,
                            description="motion_duration_seconds must be greater than 0 for non-static segments.",
                            fix_suggestion="Provide a positive motion_duration_seconds value.",
                            remediation_target="motion/editing decision",
                        )
                    )
                    continue
                delta = round(motion_duration - narration_duration, 3)
                if abs(delta) > motion_tolerance_seconds:
                    findings.append(
                        _make_finding(
                            severity=_severity_for_dimension("CI"),
                            dimension="CI",
                            location=segment_id,
                            description=(
                                f"Motion duration mismatch: clip={motion_duration:.3f}s "
                                f"vs narration={narration_duration:.3f}s (delta {delta:+.3f}s)."
                            ),
                            fix_suggestion=(
                                "Do not retime the approved clip silently. Decide whether to trim narration, "
                                "extend the visual treatment in editing, or regenerate motion explicitly."
                            ),
                            remediation_target="motion/editing decision",
                        )
                    )
                else:
                    notes.append(
                        f"{segment_id}: motion duration within tolerance ({delta:+.3f}s)."
                    )

        segment_metrics.append(
            {
                "segment_id": segment_id,
                "words": words,
                "narration_duration": narration_duration,
                "wpm": wpm,
                "estimated_wpm": estimated_wpm,
                "motion_type": motion_type,
                "motion_duration_seconds": motion_duration,
                "onset_delay": timing_values["onset_delay"],
                "dwell": timing_values["dwell"],
                "cluster_gap": timing_values["cluster_gap"],
                "transition_buffer": timing_values["transition_buffer"],
            }
        )

    aq_findings = [f for f in findings if f["dimension"] == "AQ"]
    ci_findings = [f for f in findings if f["dimension"] == "CI"]
    status = "fail" if findings else ("pass_with_notes" if notes else "pass")

    return {
        "review_pass": "pre-composition",
        "status": status,
        "verdict": {
            "result": "pass" if status in {"pass", "pass_with_notes"} else "fail",
            "confidence": 1.0,
        },
        "dimension_scores": {
            "audio_quality": {
                "status": "pass" if not aq_findings else "fail",
                "confidence": 1.0,
                "finding_count": len(aq_findings),
            },
            "composition_integrity": {
                "status": "pass" if not ci_findings else "fail",
                "confidence": 1.0,
                "finding_count": len(ci_findings),
            },
        },
        "critical_summary": [
            f"{finding['location']}: {finding['description']}" for finding in findings
        ],
        "findings": findings,
        "notes": notes,
        "segment_metrics": segment_metrics,
        "manifest_path": str(manifest_path),
        "segment_count": len(segments),
        "covered_segments": sum(
            1
            for segment in segments
            if segment.get("narration_file") and segment.get("narration_vtt")
        ),
    }


def write_json_output(payload: dict[str, Any], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deterministic Quinn-R pre-composition validation."
    )
    parser.add_argument("manifest_path")
    parser.add_argument("--repo-root")
    parser.add_argument("--min-wpm", type=float, default=DEFAULT_MIN_WPM)
    parser.add_argument("--max-wpm", type=float, default=DEFAULT_MAX_WPM)
    parser.add_argument(
        "--motion-tolerance-seconds",
        type=float,
        default=DEFAULT_MOTION_TOLERANCE_SECONDS,
    )
    parser.add_argument("--output-path")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = validate_precomposition(
            args.manifest_path,
            repo_root=args.repo_root,
            min_wpm=args.min_wpm,
            max_wpm=args.max_wpm,
            motion_tolerance_seconds=args.motion_tolerance_seconds,
        )
        if args.output_path:
            write_json_output(result, args.output_path)
            result["output_path"] = str(Path(args.output_path))
        print(json.dumps(result, indent=2))
        return 0 if result["status"] in {"pass", "pass_with_notes"} else 1
    except Exception as exc:  # pragma: no cover - CLI guard
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
