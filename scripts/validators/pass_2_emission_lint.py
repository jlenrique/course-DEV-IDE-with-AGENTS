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
import math
import sys
from dataclasses import dataclass
from pathlib import Path

import jsonschema
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = _REPO_ROOT / "state" / "config" / "schemas" / "segment-manifest.schema.json"

# Absolute-tolerance for receipt↔manifest duration comparison. This is a
# BUSINESS tolerance (how precisely Motion Gate reports durations and how
# precisely Irene needs to carry them forward), not a round-trip-float
# slop allowance (actual IEEE-754 round-trip drift on typical durations is
# ~1e-15). 1 millisecond is well below human-perceptible audio-alignment
# thresholds while still catching meaningful value disagreements.
_DURATION_TOLERANCE_SECONDS = 0.001

# Supported finding kinds (closed set for AC-C.2 determinism).
_KIND_LEGACY_KEY = "§6.3"
_KIND_MISSING_VISUAL = "§6.4"
_KIND_MISSING_DURATION = "§6.5-null"
_KIND_DURATION_MISMATCH = "§6.5-mismatch"
_KIND_SCHEMA = "schema"
# Sprint 2 — reading-path repertoire shape checks. Warning-level for 6 of 7
# patterns (Murat rider); sequence_numbered is fail-closed because ordinal-
# marker absence on that classification is a structural contract violation.
_KIND_READING_PATH_WARN = "reading-path-warn"
_KIND_READING_PATH_FAIL = "reading-path-fail"


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


# Sprint 2 — reading-path pattern shape checks. Each returns a finding-kind
# when the narration does not show the expected cadence signal, else None.
# The pattern→check mapping below is the declarative surface; the checks are
# simple substring heuristics in v1, with room for smarter analysis in a
# follow-on (e.g., POS-tagged detection of compare/contrast connectives).


_COMPARE_CONTRAST_TOKENS = (
    "compared to",
    "contrast",
    "whereas",
    "whilst",
    "on the other hand",
    "vs",
    "versus",
    "by contrast",
    "different from",
    "in comparison",
)
_ORDINAL_TOKENS = (
    "first",
    "second",
    "third",
    "fourth",
    "next",
    "then",
    "finally",
    "step 1",
    "step 2",
    "step 3",
    "step a",
    "step b",
    "step c",
)
_COLUMN_BRIDGE_TOKENS = (
    "in the next column",
    "moving to the right",
    "the adjacent column",
    "the column beside",
    "moving rightward",
    "in the column to the right",
    "across the columns",
)
_ORBIT_RETURN_TOKENS = (
    "returning to the center",
    "back to the hero",
    "circling back",
    "center again",
    "back to the main",
    "returning to the heart",
)
_SPINE_CADENCE_TOKENS = (
    "next item",
    "continuing down",
    "further down",
    "proceeding through",
    "step by step",
    "in order",
)
_EVIDENCE_DRILL_TOKENS = (
    "evidence",
    "drill into",
    "as shown",
    "note the",
    "data shows",
    "marked on the",
    "callout",
)
_Z_SWEEP_TOKENS = (
    "headline",
    "body",
    "visual",
    "call to action",
    "cta",
    "top-left",
    "bottom-right",
)


def _narration_contains_any(narration: str, tokens: tuple[str, ...]) -> bool:
    if not narration:
        return False
    lower = narration.lower()
    return any(tok in lower for tok in tokens)


def _check_reading_path_pattern(
    segment_id: str,
    pattern: str,
    narration: str,
    evidence: dict | None,
) -> list[LintFinding]:
    """Return warning-or-fail findings per the pattern's narration-grammar rider.

    Narration-grammar riders (from pass-2-grammar-riders-examples.md):
      - z_pattern: four-beat sweep tokens (warning-level)
      - f_pattern: drill-down on evidence markers (warning-level)
      - center_out: orbit-return-to-hero (warning-level)
      - top_down: spine-item cadence (warning-level)
      - multi_column: column-boundary bridges (warning-level)
      - grid_quadrant: compare/contrast connectives (warning-level)
      - sequence_numbered: ordinal markers (FAIL-CLOSED per Murat rider)
    """
    findings: list[LintFinding] = []
    if not narration:
        return findings

    if pattern == "sequence_numbered":
        if not _narration_contains_any(narration, _ORDINAL_TOKENS):
            findings.append(
                LintFinding(
                    kind=_KIND_READING_PATH_FAIL,
                    segment_id=segment_id,
                    detail=(
                        "sequence_numbered classification requires ordinal "
                        "markers in narration (first/second/third/next/step N). "
                        "Fail-closed per Murat rider — ordinal-marker absence "
                        "is a contract violation, not a warning."
                    ),
                )
            )
        return findings

    # Warning-level patterns
    if pattern == "grid_quadrant" and not _narration_contains_any(
        narration, _COMPARE_CONTRAST_TOKENS
    ):
        findings.append(
            LintFinding(
                kind=_KIND_READING_PATH_WARN,
                segment_id=segment_id,
                detail=(
                    "grid_quadrant narration should contain compare/contrast "
                    "connectives (whereas / versus / in contrast / etc.)"
                ),
            )
        )
    elif pattern == "multi_column" and not _narration_contains_any(
        narration, _COLUMN_BRIDGE_TOKENS
    ):
        findings.append(
            LintFinding(
                kind=_KIND_READING_PATH_WARN,
                segment_id=segment_id,
                detail=(
                    "multi_column narration should contain column-boundary "
                    "bridges (in the next column / moving to the right / etc.)"
                ),
            )
        )
    elif pattern == "center_out" and not _narration_contains_any(
        narration, _ORBIT_RETURN_TOKENS
    ):
        findings.append(
            LintFinding(
                kind=_KIND_READING_PATH_WARN,
                segment_id=segment_id,
                detail=(
                    "center_out narration should return to the hero near the "
                    "end of the scan (returning to the center / back to the "
                    "hero / circling back)"
                ),
            )
        )
    elif pattern == "top_down" and not _narration_contains_any(
        narration, _SPINE_CADENCE_TOKENS
    ):
        findings.append(
            LintFinding(
                kind=_KIND_READING_PATH_WARN,
                segment_id=segment_id,
                detail=(
                    "top_down narration should show cadence at spine-item "
                    "boundaries (next item / continuing down / step by step)"
                ),
            )
        )
    elif pattern == "f_pattern" and not _narration_contains_any(
        narration, _EVIDENCE_DRILL_TOKENS
    ):
        findings.append(
            LintFinding(
                kind=_KIND_READING_PATH_WARN,
                segment_id=segment_id,
                detail=(
                    "f_pattern narration should drill down on evidence markers "
                    "(evidence / as shown / note the / data shows)"
                ),
            )
        )
    elif pattern == "z_pattern" and not _narration_contains_any(
        narration, _Z_SWEEP_TOKENS
    ):
        # Z-pattern is the default; token set is generous on purpose.
        findings.append(
            LintFinding(
                kind=_KIND_READING_PATH_WARN,
                segment_id=segment_id,
                detail=(
                    "z_pattern narration should trace the four-beat sweep "
                    "(headline / body / visual / CTA — or explicit spatial tokens)"
                ),
            )
        )
    return findings


def _resolve_segment_pattern(manifest: dict, segment: dict) -> tuple[str, str] | None:
    """Resolve the effective reading_path.pattern for a segment.

    Returns ``(pattern, source)`` or None. ``source`` is one of:
      - "segment" — segment-level structured reading_path
      - "envelope" — envelope-level structured reading_path
      - "legacy" — normalized from free-text narration_directive (Sprint-1)

    The lint uses ``source`` to decide whether to run the pattern-aware shape
    check. Legacy-resolved patterns skip the check so Sprint-1 fixtures remain
    lint-clean (AC-8 byte-identical regression). Structured patterns (either
    envelope or segment level) trigger the full check.
    """
    # Try segment-level structured block first.
    seg_rp = segment.get("reading_path")
    if isinstance(seg_rp, dict) and isinstance(seg_rp.get("pattern"), str):
        return seg_rp["pattern"], "segment"
    # Envelope structured block.
    env_rp = manifest.get("reading_path")
    if isinstance(env_rp, dict) and isinstance(env_rp.get("pattern"), str):
        return env_rp["pattern"], "envelope"
    # Legacy free-text normalization (Sprint 1 convention).
    directive = manifest.get("narration_directive")
    if isinstance(directive, str):
        normalized = directive.strip().lower()
        if normalized in ("z-pattern-literal-scan", "z_pattern_literal_scan", "z-pattern"):
            return "z_pattern", "legacy"
    return None


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

    if not isinstance(manifest, dict):
        findings.append(
            LintFinding(
                kind=_KIND_SCHEMA,
                segment_id="<manifest>",
                detail=(
                    f"manifest root must be a mapping, got "
                    f"{type(manifest).__name__}"
                ),
            )
        )
        return _sorted_findings(findings)

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

    if not segments:
        findings.append(
            LintFinding(
                kind=_KIND_SCHEMA,
                segment_id="<manifest>",
                detail="segments list is empty (manifest must carry >=1 segment)",
            )
        )
        return _sorted_findings(findings)

    for idx, segment in enumerate(segments):
        if not isinstance(segment, dict):
            findings.append(
                LintFinding(
                    kind=_KIND_SCHEMA,
                    segment_id=f"segments[{idx}]",
                    detail=(
                        f"segment must be a mapping, got "
                        f"{type(segment).__name__}"
                    ),
                )
            )
            continue

        seg_id = (
            segment.get("id")
            or segment.get("slide_id")
            or f"segments[{idx}]"
        )

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
            slide_id = segment.get("slide_id")
            # Track which key we matched on so the finding detail can name
            # the actual receipt-lookup key. segment_id remains stable (always
            # seg_id) so all findings for the same segment sort adjacently.
            receipt_lookup_key: str | None = None
            receipt_duration = receipt_durations.get(seg_id)
            if receipt_duration is not None:
                receipt_lookup_key = seg_id
            elif slide_id and slide_id != seg_id:
                receipt_duration = receipt_durations.get(slide_id)
                if receipt_duration is not None:
                    receipt_lookup_key = slide_id

            lookup_note = (
                ""
                if receipt_lookup_key is None or receipt_lookup_key == seg_id
                else f" (matched receipt via slide_id={receipt_lookup_key!r})"
            )

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
                            f"Motion Gate receipt carries {receipt_duration}s"
                            f"{lookup_note} — carry it forward at Pass 2 emission"
                        ),
                    )
                )
            elif not isinstance(duration, (int, float)) or isinstance(duration, bool):
                # String, bool, list, or any non-numeric type — cannot compare
                # against the numeric receipt value. Surfaces as §6.5-null
                # since the manifest's duration is functionally unusable.
                findings.append(
                    LintFinding(
                        kind=_KIND_MISSING_DURATION,
                        segment_id=seg_id,
                        detail=(
                            f"motion_duration_seconds has non-numeric type "
                            f"{type(duration).__name__} (value={duration!r}); "
                            f"receipt carries {receipt_duration}s{lookup_note}"
                        ),
                    )
                )
            elif math.isnan(duration) or math.isinf(duration):
                findings.append(
                    LintFinding(
                        kind=_KIND_DURATION_MISMATCH,
                        segment_id=seg_id,
                        detail=(
                            f"motion_duration_seconds is {duration!r} (not a "
                            f"finite number); receipt carries "
                            f"{receipt_duration}s{lookup_note}"
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
                            f"{lookup_note}"
                        ),
                    )
                )

        # Sprint 2 — reading-path pattern shape check. Resolves pattern via
        # (segment-level > envelope > legacy directive normalization) and
        # emits warning (or fail-closed for sequence_numbered) when narration
        # does not show the expected cadence tokens. Legacy-resolved patterns
        # (Sprint-1 free-text `narration_directive`) skip the check so
        # existing fixtures stay lint-clean (AC-8 byte-identical regression).
        resolved = _resolve_segment_pattern(manifest, segment)
        if resolved is not None:
            pattern, source = resolved
            if source != "legacy":
                narration = segment.get("narration_text") or ""
                findings.extend(
                    _check_reading_path_pattern(
                        segment_id=seg_id,
                        pattern=pattern,
                        narration=str(narration),
                        evidence=segment.get("reading_path", {}).get("evidence"),
                    )
                )

    return _sorted_findings(findings)


def _load_manifest(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"manifest not found: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        raise yaml.YAMLError(f"manifest is empty: {path}")
    if not isinstance(data, dict):
        raise yaml.YAMLError(
            f"manifest root must be a mapping, got {type(data).__name__}: {path}"
        )
    return data


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

    # Sprint 2: reading-path WARNINGS do not fail the gate; reading-path FAILs
    # and all §6.x / schema findings do. Partition for clarity in CLI output.
    warnings_only = {_KIND_READING_PATH_WARN}
    blockers = [f for f in findings if f.kind not in warnings_only]
    warns = [f for f in findings if f.kind in warnings_only]

    print(
        f"Pass 2 emission lint: {len(blockers)} blocker(s), {len(warns)} warning(s)"
    )
    for finding in _sorted_findings(blockers + warns):
        print("  " + finding.format_line())
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(run_cli())
