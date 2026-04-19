#!/usr/bin/env python3
"""Emit the canonical ``ingestion-quality-gate-receipt.md`` artifact.

Step 04 of the v4.2 prompt pack requires Marcus to evaluate the extracted
source bundle against six quality dimensions (completeness, readability,
anchorability, provenance quality, planning usability, fidelity usability)
and record a gate receipt before ``prepare-irene-packet.py`` generates
``irene-packet.md`` for Irene.

Prior to this module, the receipt was hand-written by the operator (or
silently omitted). ``prepare_irene_packet`` in ``marcus.intake.pre_packet``
tolerates the absence as a no-op fallback (pinned by AC-T.4 of story
30-2a), which meant an operator who forgot to write the receipt would
hand Irene a packet with an empty ``## Ingestion Quality Receipt``
section — the exact "silent quality gap" the 2026-04-19 trial caught.

This writer closes that gap deterministically. It consumes a structured
spec (operator- or Marcus-supplied via YAML/JSON) describing the per-
source verdicts, Vera G0 outcome, and gate decision, and renders the
receipt in the canonical shape pinned by the golden-trace fixture
``tests/fixtures/golden_trace/marcus_pre_30-1/step-04-ingestion-quality-gate-envelope.json``.

Usage
-----

Emit from a spec file::

    python -m scripts.utilities.emit_ingestion_quality_receipt \\
        --bundle-dir <bundle> \\
        --spec <receipt-spec.yaml>

Emit a template scaffold (``[FILL IN: ...]`` placeholders for the
judgment fields; mechanical fields pre-populated from bundle metadata)::

    python -m scripts.utilities.emit_ingestion_quality_receipt \\
        --bundle-dir <bundle> \\
        --template

The companion CLI shim ``scripts/utilities/prepare-irene-packet.py`` now
defaults to ``--require-receipt`` and refuses to build the packet when
the receipt is missing, empty, or still carries ``[FILL IN:`` markers,
so the template-then-fill workflow lands on a fail-hard guard if the
placeholders are not resolved.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# Ordered six-dimension key list. The YAML spec uses snake_case keys for
# valid YAML; the rendered markdown uses the space-separated labels from
# the golden-trace fixture so the output is byte-parity with historical
# receipts.
_SIX_DIMENSIONS: tuple[tuple[str, str], ...] = (
    ("completeness", "completeness"),
    ("readability", "readability"),
    ("anchorability", "anchorability"),
    ("provenance_quality", "provenance quality"),
    ("planning_usability", "planning usability"),
    ("fidelity_usability", "fidelity usability"),
)

_TEMPLATE_PLACEHOLDER = "[FILL IN:"

_VALID_VERDICTS: frozenset[str] = frozenset({"pass", "fail", "warn"})
_VALID_GATE_DECISIONS: frozenset[str] = frozenset({"proceed", "halt"})


class ReceiptSpecError(ValueError):
    """Raised when the receipt spec is malformed or internally inconsistent."""


@dataclass
class PerSourceEvaluation:
    """One source's per-dimension verdicts plus provenance context."""

    source_ref: str
    kind: str
    verdicts: dict[str, str]
    confidence_basis: str
    source_anchor_set: list[str]
    notes: str

    def validate(self) -> None:
        for key, _label in _SIX_DIMENSIONS:
            if key not in self.verdicts:
                raise ReceiptSpecError(
                    f"per_source[{self.source_ref!r}].verdicts missing key {key!r}"
                )
            v = self.verdicts[key]
            if v not in _VALID_VERDICTS:
                raise ReceiptSpecError(
                    f"per_source[{self.source_ref!r}].verdicts[{key!r}]={v!r}; "
                    f"must be one of {sorted(_VALID_VERDICTS)}"
                )


@dataclass
class VeraG0Receipt:
    verdict: str
    critical_findings: str = "none"
    remediation_target: str = "none"
    interpretation_notes: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.verdict not in _VALID_VERDICTS:
            raise ReceiptSpecError(
                f"vera_g0.verdict={self.verdict!r}; "
                f"must be one of {sorted(_VALID_VERDICTS)}"
            )


@dataclass
class ReceiptSpec:
    run_id: str
    bundle_path: str
    per_source: list[PerSourceEvaluation]
    vera_g0: VeraG0Receipt
    gate_decision: str
    artifacts_written: list[str] = field(default_factory=list)
    next_action: str = ""

    def validate(self) -> None:
        if not self.run_id:
            raise ReceiptSpecError("run_id is required and must be non-empty")
        if not self.bundle_path:
            raise ReceiptSpecError("bundle_path is required and must be non-empty")
        if not self.per_source:
            raise ReceiptSpecError("per_source must list at least one evaluated source")
        if self.gate_decision not in _VALID_GATE_DECISIONS:
            raise ReceiptSpecError(
                f"gate_decision={self.gate_decision!r}; "
                f"must be one of {sorted(_VALID_GATE_DECISIONS)}"
            )
        for entry in self.per_source:
            entry.validate()
        self.vera_g0.validate()
        # Internal consistency: proceed forbids any dim-fail or vera fail.
        if self.gate_decision == "proceed":
            for entry in self.per_source:
                for key, label in _SIX_DIMENSIONS:
                    if entry.verdicts[key] == "fail":
                        raise ReceiptSpecError(
                            f"gate_decision='proceed' but "
                            f"per_source[{entry.source_ref!r}].{label}=fail; "
                            f"use gate_decision='halt' or fix the verdict"
                        )
            if self.vera_g0.verdict == "fail":
                raise ReceiptSpecError(
                    "gate_decision='proceed' but vera_g0.verdict='fail'; "
                    "use gate_decision='halt' or fix the Vera verdict"
                )


# ---------------------------------------------------------------------------
# Spec loading
# ---------------------------------------------------------------------------


def _load_spec_mapping(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Receipt spec file not found: {path}")
    raw = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise ReceiptSpecError(f"Spec file is not valid YAML/JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ReceiptSpecError("Spec root must be a mapping")
    return data


def build_spec(mapping: dict[str, Any]) -> ReceiptSpec:
    """Construct + validate a :class:`ReceiptSpec` from a raw mapping."""
    per_source_raw = mapping.get("per_source") or []
    if not isinstance(per_source_raw, list):
        raise ReceiptSpecError("per_source must be a list")
    per_source: list[PerSourceEvaluation] = []
    for idx, entry in enumerate(per_source_raw):
        if not isinstance(entry, dict):
            raise ReceiptSpecError(f"per_source[{idx}] must be a mapping")
        verdicts = entry.get("verdicts") or {}
        if not isinstance(verdicts, dict):
            raise ReceiptSpecError(f"per_source[{idx}].verdicts must be a mapping")
        anchors = entry.get("source_anchor_set") or []
        if not isinstance(anchors, list):
            raise ReceiptSpecError(
                f"per_source[{idx}].source_anchor_set must be a list"
            )
        per_source.append(
            PerSourceEvaluation(
                source_ref=str(entry.get("source_ref", "")),
                kind=str(entry.get("kind", "unknown")),
                verdicts={str(k): str(v) for k, v in verdicts.items()},
                confidence_basis=str(entry.get("confidence_basis", "medium")),
                source_anchor_set=[str(a) for a in anchors],
                notes=str(entry.get("notes", "")),
            )
        )
    vera_raw = mapping.get("vera_g0") or {}
    if not isinstance(vera_raw, dict):
        raise ReceiptSpecError("vera_g0 must be a mapping")
    interp_notes = vera_raw.get("interpretation_notes") or []
    if not isinstance(interp_notes, list):
        raise ReceiptSpecError("vera_g0.interpretation_notes must be a list")
    vera = VeraG0Receipt(
        verdict=str(vera_raw.get("verdict", "pass")),
        critical_findings=str(vera_raw.get("critical_findings", "none")),
        remediation_target=str(vera_raw.get("remediation_target", "none")),
        interpretation_notes=[str(n) for n in interp_notes],
    )
    artifacts_raw = mapping.get("artifacts_written") or [
        "irene-packet.md",
        "ingestion-quality-gate-receipt.md",
    ]
    spec = ReceiptSpec(
        run_id=str(mapping.get("run_id", "")),
        bundle_path=str(mapping.get("bundle_path", "")),
        per_source=per_source,
        vera_g0=vera,
        gate_decision=str(mapping.get("gate_decision", "proceed")),
        artifacts_written=[str(a) for a in artifacts_raw],
        next_action=str(
            mapping.get(
                "next_action",
                "Prompt 5 (Irene Pass 1 Structure + Gate 1 Fidelity)",
            )
        ),
    )
    spec.validate()
    return spec


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def _render_anchor_list(anchors: list[str]) -> str:
    if not anchors:
        return "  - (none recorded)"
    return "\n".join(f"  - {a}" for a in anchors)


def _render_interpretation_notes(notes: list[str]) -> str:
    if not notes:
        return "  - (none recorded)"
    return "\n".join(f"  - {note}" for note in notes)


def _render_artifacts(artifacts: list[str]) -> str:
    if not artifacts:
        return "  - (none recorded)"
    return "\n".join(f"  - {a}" for a in artifacts)


def render_receipt_markdown(
    spec: ReceiptSpec,
    *,
    generated_at: datetime | None = None,
) -> str:
    """Render the canonical ``ingestion-quality-gate-receipt.md`` body.

    The output shape mirrors the golden-trace fixture at
    ``tests/fixtures/golden_trace/marcus_pre_30-1/step-04-ingestion-quality-gate-envelope.json``
    so historical trials' receipts and freshly-emitted ones share one
    contract the ``marcus_prompt_harness._check_step_4`` inspector can
    reason about uniformly (``gate_decision: proceed`` key-value line).
    """
    ts = (generated_at or datetime.now(tz=UTC)).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = [
        "# Ingestion Quality Gate Receipt",
        "",
        f"- run_id: {spec.run_id}",
        "- stage: Prompt 4 - Ingestion Quality Gate + Irene Packet",
        f"- bundle_path: {spec.bundle_path}",
        f"- generated_at_utc: {ts}",
        "",
        "## Per-source quality evaluation",
        "",
    ]
    for entry in spec.per_source:
        lines.append(f"### {entry.source_ref} ({entry.kind})")
        for key, label in _SIX_DIMENSIONS:
            lines.append(f"- {label}: {entry.verdicts[key]}")
        lines.append(f"- confidence_basis: {entry.confidence_basis}")
        lines.append("- source_anchor_set:")
        lines.append(_render_anchor_list(entry.source_anchor_set))
        lines.append(f"- notes: {entry.notes}")
        lines.append("")
    lines.extend([
        "## Vera G0 receipt (internal)",
        f"- verdict: {spec.vera_g0.verdict}",
        f"- critical_findings: {spec.vera_g0.critical_findings}",
        f"- remediation_target: {spec.vera_g0.remediation_target}",
        "- interpretation_notes:",
        _render_interpretation_notes(spec.vera_g0.interpretation_notes),
        "",
        "## Gate decision",
        f"- gate_decision: {spec.gate_decision}",
        "- artifacts_written:",
        _render_artifacts(spec.artifacts_written),
        f"- next_action: {spec.next_action}",
        "",
    ])
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Template scaffold
# ---------------------------------------------------------------------------


def build_template_spec(
    run_id: str,
    bundle_path: str,
    *,
    source_refs: list[tuple[str, str]] | None = None,
) -> ReceiptSpec:
    """Return a :class:`ReceiptSpec` whose judgment fields are placeholders.

    ``source_refs`` is a list of ``(source_ref, kind)`` tuples. When
    omitted, a single ``SRC-PRIMARY-01 (unknown)`` entry is emitted so
    operators have a starting row to edit.

    The resulting spec defaults to ``gate_decision='proceed'`` with all
    six dimensions pre-filled as ``pass`` so :meth:`ReceiptSpec.validate`
    succeeds. Operators are expected to edit the ``[FILL IN: ...]``
    markers before the shim guard on ``prepare-irene-packet.py`` will
    accept the receipt downstream.
    """
    refs = source_refs or [("SRC-PRIMARY-01", "unknown")]
    per_source = [
        PerSourceEvaluation(
            source_ref=ref,
            kind=kind,
            verdicts={k: "pass" for k, _ in _SIX_DIMENSIONS},
            confidence_basis="[FILL IN: high | medium | low]",
            source_anchor_set=[
                "[FILL IN: extracted.md#<anchor>]",
                "[FILL IN: ingestion-evidence.md row: <source_ref>]",
            ],
            notes=(
                "[FILL IN: one-sentence rationale citing specific "
                "extracted content]"
            ),
        )
        for ref, kind in refs
    ]
    vera = VeraG0Receipt(
        verdict="pass",
        critical_findings="none",
        remediation_target="none",
        interpretation_notes=[
            "[FILL IN: G0-01 section coverage note]",
            "[FILL IN: G0-02 media capture notation note]",
            "[FILL IN: G0-03 metadata completeness note]",
            "[FILL IN: G0-04 no content invention note]",
            "[FILL IN: G0-05 degraded source detection note]",
        ],
    )
    return ReceiptSpec(
        run_id=run_id,
        bundle_path=bundle_path,
        per_source=per_source,
        vera_g0=vera,
        gate_decision="proceed",
        artifacts_written=["irene-packet.md", "ingestion-quality-gate-receipt.md"],
        next_action="Prompt 5 (Irene Pass 1 Structure + Gate 1 Fidelity)",
    )


# ---------------------------------------------------------------------------
# Receipt-state inspection (used by the prepare-irene-packet shim guard)
# ---------------------------------------------------------------------------


def inspect_receipt_state(path: Path) -> tuple[bool, str]:
    """Return ``(ok, reason)`` describing whether ``path`` is a valid receipt.

    The shim guard on ``prepare-irene-packet.py`` uses this to decide
    whether packet generation should proceed. ``ok`` is True only when:

    * the file exists,
    * the file is non-empty after whitespace stripping,
    * the content does not contain ``[FILL IN:`` markers from an unfinished
      template scaffold,
    * the content contains the ``gate_decision:`` key expected by
      ``marcus_prompt_harness._check_step_4`` evidence parsing.
    """
    if not path.exists():
        return False, (
            f"{path.name} is missing. Run "
            "`python -m scripts.utilities.emit_ingestion_quality_receipt "
            "--bundle-dir <bundle> --spec <receipt-spec.yaml>` first."
        )
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, f"{path.name} could not be read: {exc}"
    if not text.strip():
        return False, f"{path.name} exists but is empty."
    if _TEMPLATE_PLACEHOLDER in text:
        return False, (
            f"{path.name} still contains '{_TEMPLATE_PLACEHOLDER}' markers "
            "from a template scaffold. Fill in every placeholder before "
            "regenerating the Irene packet."
        )
    if "gate_decision:" not in text:
        return False, (
            f"{path.name} does not declare a 'gate_decision:' line. The "
            "canonical shape from the 30-1 golden-trace fixture includes "
            "that key; without it the downstream evidence check cannot "
            "classify the gate outcome."
        )
    return True, "ok"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit the canonical ingestion-quality-gate-receipt.md "
            "artifact for Step 04 of the v4.2 prompt pack."
        )
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Bundle directory to write the receipt into.",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--spec",
        type=Path,
        help=(
            "Path to a YAML or JSON spec file describing per-source "
            "verdicts, Vera G0 receipt, and gate decision."
        ),
    )
    mode.add_argument(
        "--template",
        action="store_true",
        help=(
            "Emit a scaffold receipt with '[FILL IN: ...]' placeholders "
            "for the judgment fields. The operator must edit the file "
            "before prepare-irene-packet.py --require-receipt will accept it."
        ),
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help=(
            "Run ID for template mode. Required when --template is used "
            "and --spec is not provided."
        ),
    )
    parser.add_argument(
        "--source-ref",
        action="append",
        dest="source_refs",
        default=None,
        help=(
            "Template mode: add a per-source entry formatted as "
            "<source_ref>:<kind>. Repeatable. Defaults to one "
            "'SRC-PRIMARY-01:unknown' row."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Override the default output path "
            "(<bundle-dir>/ingestion-quality-gate-receipt.md)."
        ),
    )
    return parser


def _resolve_output_path(bundle_dir: Path, override: Path | None) -> Path:
    if override is not None:
        return override
    return bundle_dir / "ingestion-quality-gate-receipt.md"


def _parse_source_refs(raw: list[str] | None) -> list[tuple[str, str]] | None:
    if not raw:
        return None
    parsed: list[tuple[str, str]] = []
    for item in raw:
        if ":" not in item:
            raise ReceiptSpecError(
                f"--source-ref {item!r} must be formatted as "
                "<source_ref>:<kind>"
            )
        ref, kind = item.split(":", 1)
        parsed.append((ref.strip(), kind.strip()))
    return parsed


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(argv)
    bundle_dir: Path = args.bundle_dir
    output_path = _resolve_output_path(bundle_dir, args.output)

    try:
        if args.template:
            if not args.run_id:
                raise ReceiptSpecError("--template mode requires --run-id")
            source_refs = _parse_source_refs(args.source_refs)
            spec = build_template_spec(
                run_id=args.run_id,
                bundle_path=str(bundle_dir),
                source_refs=source_refs,
            )
        else:
            mapping = _load_spec_mapping(args.spec)
            # Allow the spec to elide run_id/bundle_path and derive them
            # from CLI / bundle layout for convenience.
            mapping.setdefault("bundle_path", str(bundle_dir))
            if args.run_id and "run_id" not in mapping:
                mapping["run_id"] = args.run_id
            spec = build_spec(mapping)

        markdown = render_receipt_markdown(spec)
    except (FileNotFoundError, ReceiptSpecError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")
    mode_label = "template scaffold" if args.template else "populated receipt"
    print(f"Wrote {mode_label} to {output_path}")
    if args.template:
        print(
            f"NOTE: replace every '{_TEMPLATE_PLACEHOLDER}' marker before "
            "re-running prepare-irene-packet.py --require-receipt.",
            file=sys.stderr,
        )
    return 0


# Convenience helpers for programmatic callers (tests, orchestrators).

def dump_spec_to_yaml(spec: ReceiptSpec) -> str:
    """Serialize a spec back to YAML for audit / round-trip tests."""
    payload = {
        "run_id": spec.run_id,
        "bundle_path": spec.bundle_path,
        "per_source": [
            {
                "source_ref": e.source_ref,
                "kind": e.kind,
                "verdicts": dict(e.verdicts),
                "confidence_basis": e.confidence_basis,
                "source_anchor_set": list(e.source_anchor_set),
                "notes": e.notes,
            }
            for e in spec.per_source
        ],
        "vera_g0": {
            "verdict": spec.vera_g0.verdict,
            "critical_findings": spec.vera_g0.critical_findings,
            "remediation_target": spec.vera_g0.remediation_target,
            "interpretation_notes": list(spec.vera_g0.interpretation_notes),
        },
        "gate_decision": spec.gate_decision,
        "artifacts_written": list(spec.artifacts_written),
        "next_action": spec.next_action,
    }
    return yaml.safe_dump(payload, sort_keys=False)


def dump_spec_to_json(spec: ReceiptSpec) -> str:
    """Serialize a spec to JSON for machine consumption."""
    return json.dumps(
        yaml.safe_load(dump_spec_to_yaml(spec)),
        indent=2,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    raise SystemExit(main())
