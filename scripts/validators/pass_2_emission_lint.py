"""Pass 2 emission lint — fail-closed gate blocking Storyboard B render on
structural or upstream-reference violations in an Irene Pass 2 manifest.

Satisfies Story §7.1 AC-B.3 (structural schema + upstream Motion Gate receipt
cross-validation). Invoked at end of Pack v4.2 §07 so a failing lint blocks
§08 Storyboard B render.

Exit codes:
- 0: clean
- 1: violations found
- 2: infrastructure error (missing file, malformed input)

Deterministic per AC-C.2 — pure function core, zero LLM/network/clock/random.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = _REPO_ROOT / "state" / "config" / "schemas" / "segment-manifest.schema.json"

# Absolute-tolerance for receipt↔manifest duration comparison. Motion Gate
# records durations to 3 decimal places; we allow 1ms slop for float round-trip.
_DURATION_TOLERANCE_SECONDS = 0.001

# Supported finding kinds (closed set for AC-C.2 determinism).
_KIND_LEGACY_KEY = "§6.3"
_KIND_MISSING_VISUAL = "§6.4"
_KIND_MISSING_DURATION = "§6.5-null"
_KIND_DURATION_MISMATCH = "§6.5-mismatch"
_KIND_SCHEMA = "schema"


@dataclass(frozen=True)
class LintFinding:
    kind: str
    segment_id: str
    detail: str

    def format_line(self) -> str:
        return f"[{self.kind}] {self.segment_id}: {self.detail}"


def _sorted_findings(findings: list[LintFinding]) -> list[LintFinding]:
    """Stable order: (segment_id, kind, detail)."""
    return sorted(findings, key=lambda f: (f.segment_id, f.kind, f.detail))


def lint_manifest(
    manifest: dict,
    receipt_durations: dict[str, float],
) -> list[LintFinding]:
    """Return findings (empty list = clean).

    Args:
        manifest: parsed segment-manifest.yaml payload.
        receipt_durations: {slide_id: duration_seconds} from Motion Gate
            receipt (via motion_gate_receipt_reader). Empty dict = static-only
            deck; any motion segment is then §6.5-null.

    Layer 1 — schema-level structural checks (§6.3 / §6.4 / §6.5-null).
    Layer 2 — upstream-reference cross-validation (§6.5-mismatch on
    value disagreement between manifest and receipt).
    """
    findings: list[LintFinding] = []

    segments = manifest.get("segments")
    if not isinstance(segments, list):
        findings.append(
            LintFinding(
                kind=_KIND_SCHEMA,
                segment_id="<manifest>",
                detail="segments key missing or not a list",
            )
        )
        return _sorted_findings(findings)

    for segment in segments:
        seg_id = segment.get("id") or segment.get("slide_id") or "<unknown>"

        # §6.3 — legacy motion_asset key forbidden.
        if "motion_asset" in segment:
            findings.append(
                LintFinding(
                    kind=_KIND_LEGACY_KEY,
                    segment_id=seg_id,
                    detail=(
                        "legacy 'motion_asset' key present (emit only "
                        "'motion_asset_path')"
                    ),
                )
            )

        visual_mode = segment.get("visual_mode")

        # §6.4 — non-null visual_mode requires visual_file.
        if (
            isinstance(visual_mode, str)
            and visual_mode
            and not segment.get("visual_file")
        ):
            findings.append(
                LintFinding(
                    kind=_KIND_MISSING_VISUAL,
                    segment_id=seg_id,
                    detail=(
                        f"segment has visual_mode={visual_mode!r} but no "
                        "visual_file (Pass 2 MUST populate visual_file at "
                        "emission, not at §14 Compositor back-fill)"
                    ),
                )
            )

        # §6.5-null + §6.5-mismatch — motion segments only.
        if visual_mode == "video":
            duration = segment.get("motion_duration_seconds")
            receipt_duration = receipt_durations.get(seg_id)
            slide_id = segment.get("slide_id")
            if slide_id and slide_id != seg_id and receipt_duration is None:
                receipt_duration = receipt_durations.get(slide_id)

            if receipt_duration is None:
                # Upstream Motion Gate receipt has no entry for this slide —
                # the manifest is claiming motion that wasn't approved. Fires
                # regardless of whether the manifest's duration is null or
                # populated; both cases are upstream-reference violations.
                findings.append(
                    LintFinding(
                        kind=_KIND_MISSING_DURATION,
                        segment_id=seg_id,
                        detail=(
                            "motion segment has no matching Motion Gate receipt "
                            "entry for this slide_id (is the slide actually "
                            "approved as motion in the receipt?)"
                        ),
                    )
                )
            elif duration is None:
                findings.append(
                    LintFinding(
                        kind=_KIND_MISSING_DURATION,
                        segment_id=seg_id,
                        detail=(
                            f"motion segment has null motion_duration_seconds; "
                            f"Motion Gate receipt carries {receipt_duration}s — "
                            "carry it forward at Pass 2 emission"
                        ),
                    )
                )
            elif (
                abs(duration - receipt_duration) > _DURATION_TOLERANCE_SECONDS
            ):
                findings.append(
                    LintFinding(
                        kind=_KIND_DURATION_MISMATCH,
                        segment_id=seg_id,
                        detail=(
                            f"motion_duration_seconds={duration} disagrees with "
                            f"Motion Gate receipt value {receipt_duration} "
                            f"(tolerance {_DURATION_TOLERANCE_SECONDS}s)"
                        ),
                    )
                )

    return _sorted_findings(findings)


def _load_manifest(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"manifest not found: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _schema_errors(manifest: dict) -> list[LintFinding]:
    """Return schema validation errors as LintFinding(schema, ...) entries.

    Treated as infrastructure / structural failures alongside the targeted
    §6.3 / §6.4 / §6.5 checks. This layer surfaces anything the schema
    rejects that lint_manifest() hasn't already named.
    """
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    findings: list[LintFinding] = []
    for err in validator.iter_errors(manifest):
        path = list(err.absolute_path)
        seg_id = "<manifest>"
        if len(path) >= 2 and path[0] == "segments":
            idx = path[1]
            try:
                seg_id = manifest["segments"][idx].get("id", f"segments[{idx}]")
            except (IndexError, TypeError, AttributeError):
                seg_id = f"segments[{idx}]"
        findings.append(
            LintFinding(
                kind=_KIND_SCHEMA,
                segment_id=seg_id,
                detail=f"{err.message} (at {list(err.absolute_path)})",
            )
        )
    return findings


def run_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--motion-gate-receipt", type=Path, required=True)
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="skip JSON Schema validation layer (use for targeted lint-only runs)",
    )
    args = parser.parse_args(argv)

    # Lazy import — reader is optional; cli needs it.
    try:
        from skills.bmad_agent_content_creator.scripts.motion_gate_receipt_reader import (
            MotionGateReceiptError,
            read_motion_durations,
        )
    except ImportError:
        # Fallback: load via spec from known path (running outside pytest conftest).
        import importlib.util

        reader_path = (
            _REPO_ROOT
            / "skills"
            / "bmad-agent-content-creator"
            / "scripts"
            / "motion_gate_receipt_reader.py"
        )
        spec = importlib.util.spec_from_file_location(
            "motion_gate_receipt_reader", reader_path
        )
        if spec is None or spec.loader is None:
            print(
                f"infrastructure error: cannot locate motion_gate_receipt_reader at {reader_path}",
                file=sys.stderr,
            )
            return 2
        reader_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reader_mod)
        MotionGateReceiptError = reader_mod.MotionGateReceiptError  # noqa: N806
        read_motion_durations = reader_mod.read_motion_durations  # noqa: N806

    try:
        manifest = _load_manifest(args.manifest)
    except FileNotFoundError as exc:
        print(f"infrastructure error: {exc}", file=sys.stderr)
        return 2
    except yaml.YAMLError as exc:
        print(
            f"infrastructure error: manifest is malformed YAML ({args.manifest}): {exc}",
            file=sys.stderr,
        )
        return 2

    try:
        durations = read_motion_durations(args.motion_gate_receipt)
    except MotionGateReceiptError as exc:
        print(f"infrastructure error: {exc}", file=sys.stderr)
        return 2

    findings: list[LintFinding] = []
    if not args.skip_schema:
        findings.extend(_schema_errors(manifest))
    findings.extend(lint_manifest(manifest, durations))

    if not findings:
        print("Pass 2 emission lint: CLEAN")
        return 0

    print(f"Pass 2 emission lint: {len(findings)} finding(s)")
    for finding in _sorted_findings(findings):
        print("  " + finding.format_line())
    return 1


if __name__ == "__main__":
    sys.exit(run_cli())
