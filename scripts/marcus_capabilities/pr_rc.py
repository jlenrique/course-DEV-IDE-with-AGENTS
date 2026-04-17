"""PR-RC — Run-Constants author + validate (full implementation).

Direct fix for the 2026-04-17 APC C1-M1 Tejal trial halt at Prompt 1. Marcus
now authors ``run-constants.yaml`` in the canonical lowercase-nested form the
validator expects; operators no longer hand-transcribe from the prompt pack's
UPPERCASE display, eliminating the schema-drift vector.

See ``skills/bmad-agent-marcus/capabilities/pr-rc.md`` for doctrine.

Sub-modes under the execute mode are controlled by ``args.mode_sub``:

- ``author`` (default): write ``run-constants.yaml`` to ``target_path``.
- ``validate``: read existing file and run it through parse_run_constants.

Invocation::

    python -m scripts.marcus_capabilities.pr_rc --mode summarize \\
        --args '{"values": {...}}'
    python -m scripts.marcus_capabilities.pr_rc --mode execute \\
        --args '{"values": {...}, "mode_sub": "author"}'
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Any

import yaml

from scripts.marcus_capabilities._shared import (
    CapabilityError,
    Invocation,
    LandingPoint,
    ReturnEnvelope,
    run_cli,
)
from scripts.utilities import run_constants as rc

CAPABILITY_CODE = "PR-RC"

# Field ordering for the canonical output — matches RunConstants dataclass order.
CANONICAL_REQUIRED_FIELDS = [
    "run_id",
    "lesson_slug",
    "bundle_path",
    "primary_source_file",
    "theme_selection",
    "theme_paramset_key",
    "execution_mode",
    "quality_preset",
]
CANONICAL_OPTIONAL_FIELDS = [
    "optional_context_assets",
    "requested_content_type",
    "double_dispatch",
    "motion_enabled",
    "motion_budget",
    "cluster_density",
    "experience_profile",
    "slide_mode_proportions",
    "schema_version",
    "frozen_at_utc",
    "frozen_note",
]

_UPPERCASE_TO_SNAKE = {
    "RUN_ID": "run_id",
    "LESSON_SLUG": "lesson_slug",
    "BUNDLE_PATH": "bundle_path",
    "PRIMARY_SOURCE_FILE": "primary_source_file",
    "OPTIONAL_CONTEXT_ASSETS": "optional_context_assets",
    "THEME_SELECTION": "theme_selection",
    "THEME_PARAMSET_KEY": "theme_paramset_key",
    "EXECUTION_MODE": "execution_mode",
    "QUALITY_PRESET": "quality_preset",
    "REQUESTED_CONTENT_TYPE": "requested_content_type",
    "MOTION_ENABLED": "motion_enabled",
    "DOUBLE_DISPATCH": "double_dispatch",
    "CLUSTER_DENSITY": "cluster_density",
    "EXPERIENCE_PROFILE": "experience_profile",
    "SCHEMA_VERSION": "schema_version",
    "FROZEN_AT_UTC": "frozen_at_utc",
    "FROZEN_NOTE": "frozen_note",
}


def _normalize_values(raw: dict[str, Any]) -> dict[str, Any]:
    """Accept UPPERCASE pack-style keys; produce canonical lowercase-nested form.

    This is the core of the drift fix: no matter what form the operator
    dictates, Marcus lands on the validator's expected shape.
    """
    normalized: dict[str, Any] = {}
    motion_budget: dict[str, Any] = {}

    for key, value in raw.items():
        snake = _UPPERCASE_TO_SNAKE.get(key, key).lower() if key.isupper() else key
        if snake == "motion_budget_max_credits":
            motion_budget["max_credits"] = value
            continue
        if snake == "motion_budget_model_preference":
            motion_budget["model_preference"] = value
            continue
        normalized[snake] = value

    if motion_budget:
        # Merge flat MOTION_BUDGET_* into nested motion_budget block.
        existing = normalized.get("motion_budget")
        if isinstance(existing, dict):
            motion_budget = {**existing, **motion_budget}
        normalized["motion_budget"] = motion_budget

    return normalized


def _canonical_ordered(values: dict[str, Any]) -> dict[str, Any]:
    """Emit in stable field order for byte-identical re-author (AC-T.7)."""
    ordered: dict[str, Any] = {}
    for f in CANONICAL_REQUIRED_FIELDS + CANONICAL_OPTIONAL_FIELDS:
        if f in values:
            ordered[f] = values[f]
    # Preserve any unknown extra keys at the end (sorted for stability)
    for f in sorted(k for k in values if k not in ordered):
        ordered[f] = values[f]
    return ordered


def _render_yaml(values: dict[str, Any]) -> str:
    """Stable YAML rendering; byte-identical on re-author for same input."""
    return yaml.safe_dump(_canonical_ordered(values), sort_keys=False, default_flow_style=False)


def summarize(invocation: Invocation) -> ReturnEnvelope:
    """Preview the canonical YAML that would be written/validated.

    If values are missing or the proposed document fails validation, the
    envelope surfaces the issue so Marcus can report it in the verbose turn
    BEFORE asking the operator to proceed.
    """
    ctx = invocation.context
    args = invocation.args
    values_raw = args.get("values") or {}
    mode_sub = str(args.get("mode_sub", "author")).lower()

    if not isinstance(values_raw, dict):
        return ReturnEnvelope(
            status="error",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            errors=[
                CapabilityError(
                    code="PR_RC_BAD_ARGS",
                    message="args.values must be a mapping of run-constants fields.",
                    remediation=(
                        "Pass a dict of canonical lowercase fields "
                        "(or pack UPPERCASE; Marcus normalizes)."
                    ),
                )
            ],
            telemetry={"mode": "summarize"},
        )

    if not values_raw:
        return ReturnEnvelope(
            status="partial",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            result={
                "mode": "summarize",
                "mode_sub": mode_sub,
                "preview": "",
                "notice": "No values provided; summarize has nothing to preview.",
            },
            errors=[],
            telemetry={"mode": "summarize", "empty_values": True},
        )

    normalized = _normalize_values(values_raw)
    preview = _render_yaml(normalized)

    # Dry-run the validator to confirm shape BEFORE authoring.
    validation_err: str | None = None
    try:
        rc.parse_run_constants(normalized)
    except rc.RunConstantsError as exc:
        validation_err = str(exc)

    status = "ok" if validation_err is None else "error"
    errors: list[CapabilityError] = []
    if validation_err:
        errors.append(
            CapabilityError(
                code="RUN_CONSTANTS_INVALID",
                message=validation_err,
                remediation="Fix the offending field and re-invoke PR-RC summarize.",
            )
        )

    return ReturnEnvelope(
        status=status,
        capability_code=CAPABILITY_CODE,
        run_id=ctx.run_id if ctx else None,
        result={
            "mode": "summarize",
            "mode_sub": mode_sub,
            "preview": preview,
            "normalized_values": normalized,
            "validation_ok": validation_err is None,
        },
        landing_point=LandingPoint(bundle_path=ctx.bundle_path if ctx else None),
        errors=errors,
        telemetry={"mode": "summarize"},
    )


def _target_path(args: dict[str, Any], ctx) -> Path:
    override = args.get("target_path")
    if override:
        return Path(str(override))
    if ctx and ctx.bundle_path:
        return Path(ctx.bundle_path) / "run-constants.yaml"
    raise ValueError("target_path not provided and no bundle_path in context")


def _author(invocation: Invocation, normalized: dict[str, Any]) -> ReturnEnvelope:
    """Execute sub-mode ``author``: write run-constants.yaml then re-parse."""
    ctx = invocation.context
    try:
        target = _target_path(invocation.args, ctx)
    except ValueError as exc:
        return ReturnEnvelope(
            status="error",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            errors=[
                CapabilityError(
                    code="PR_RC_TARGET_MISSING",
                    message=str(exc),
                    remediation="Pass args.target_path or set context.bundle_path.",
                )
            ],
            telemetry={"mode": "execute", "mode_sub": "author"},
        )

    target.parent.mkdir(parents=True, exist_ok=True)
    document = _render_yaml(normalized)
    target.write_text(document, encoding="utf-8")

    sha256 = hashlib.sha256(document.encode("utf-8")).hexdigest()

    # Round-trip through the validator to confirm on-disk validity.
    try:
        parsed = rc.parse_run_constants(normalized)
    except rc.RunConstantsError as exc:
        return ReturnEnvelope(
            status="error",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            errors=[
                CapabilityError(
                    code="RUN_CONSTANTS_INVALID",
                    message=str(exc),
                    remediation="Correct args.values and re-author.",
                )
            ],
            result={"mode": "execute", "mode_sub": "author", "written_path": str(target)},
            landing_point=LandingPoint(bundle_path=ctx.bundle_path if ctx else None, sha256=sha256),
            telemetry={"mode": "execute", "mode_sub": "author"},
        )

    return ReturnEnvelope(
        status="ok",
        capability_code=CAPABILITY_CODE,
        run_id=ctx.run_id if ctx else None,
        result={
            "mode": "execute",
            "mode_sub": "author",
            "written_path": str(target),
            "run_id_written": parsed.run_id,
            "bytes_written": len(document.encode("utf-8")),
        },
        landing_point=LandingPoint(
            bundle_path=ctx.bundle_path if ctx else None,
            manifest={"written_path": str(target)},
            sha256=sha256,
        ),
        errors=[],
        telemetry={"mode": "execute", "mode_sub": "author"},
    )


def _validate(invocation: Invocation) -> ReturnEnvelope:
    """Execute sub-mode ``validate``: read existing file and parse."""
    ctx = invocation.context
    try:
        target = _target_path(invocation.args, ctx)
    except ValueError as exc:
        return ReturnEnvelope(
            status="error",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            errors=[
                CapabilityError(
                    code="PR_RC_TARGET_MISSING",
                    message=str(exc),
                    remediation="Pass args.target_path or set context.bundle_path.",
                )
            ],
            telemetry={"mode": "execute", "mode_sub": "validate"},
        )

    try:
        data = rc.load_run_constants_dict(target)
        parsed = rc.parse_run_constants(data)
    except rc.RunConstantsError as exc:
        return ReturnEnvelope(
            status="error",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            errors=[
                CapabilityError(
                    code="RUN_CONSTANTS_INVALID",
                    message=str(exc),
                    remediation=(
                        "Inspect the failing field. Consider re-authoring via PR-RC "
                        "execute/author to restore canonical shape."
                    ),
                )
            ],
            result={"mode": "execute", "mode_sub": "validate", "target_path": str(target)},
            telemetry={"mode": "execute", "mode_sub": "validate"},
        )

    return ReturnEnvelope(
        status="ok",
        capability_code=CAPABILITY_CODE,
        run_id=ctx.run_id if ctx else None,
        result={
            "mode": "execute",
            "mode_sub": "validate",
            "target_path": str(target),
            "run_id_validated": parsed.run_id,
        },
        landing_point=LandingPoint(bundle_path=ctx.bundle_path if ctx else None),
        errors=[],
        telemetry={"mode": "execute", "mode_sub": "validate"},
    )


def execute(invocation: Invocation) -> ReturnEnvelope:
    """Dispatch by ``args.mode_sub`` (``author`` or ``validate``)."""
    args = invocation.args
    mode_sub = str(args.get("mode_sub", "author")).lower()

    if mode_sub == "validate":
        return _validate(invocation)

    # Default to author mode.
    values_raw = args.get("values") or {}
    if not isinstance(values_raw, dict) or not values_raw:
        ctx = invocation.context
        return ReturnEnvelope(
            status="error",
            capability_code=CAPABILITY_CODE,
            run_id=ctx.run_id if ctx else None,
            errors=[
                CapabilityError(
                    code="PR_RC_BAD_ARGS",
                    message="args.values (non-empty dict) is required for author mode.",
                    remediation="Pass the canonical run-constants fields under args.values.",
                )
            ],
            telemetry={"mode": "execute", "mode_sub": mode_sub},
        )
    normalized = _normalize_values(values_raw)
    return _author(invocation, normalized)


def main(argv: list[str] | None = None) -> int:
    return run_cli(CAPABILITY_CODE, summarize, execute, argv)


if __name__ == "__main__":
    sys.exit(main())
