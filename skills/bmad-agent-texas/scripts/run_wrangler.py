"""Texas runtime wrangling runner.

Executes the Marcus -> Texas delegation contract end-to-end:
  1. Load a wrangling directive YAML
  2. For each source, dispatch to the appropriate fetch helper and extract text
  3. Run extraction_validator.validate_extraction per source
  4. Run cross_validator.cross_validate for each validation-role asset
  5. Write the full bundle: extracted.md, metadata.json, manifest.json,
     extraction-report.yaml, ingestion-evidence.md, result.yaml
  6. Emit a structured result to stdout and exit with a status-matched code.

Invocation (direct-path; skills/bmad-agent-texas uses hyphens so -m is unavailable):

    python skills/bmad-agent-texas/scripts/run_wrangler.py \\
        --directive <path-to-directive.yaml> \\
        --bundle-dir <bundle-directory> \\
        [--json]

Exit codes:
  0  complete                — all sources at tier 1
 10  complete_with_warnings  — one or more sources at tier 2 but all passed
 20  blocked                 — any source at tier 3/4 after fallbacks, OR
                               unsupported provider, OR fetch failure
 30  directive/IO error      — malformed directive, missing files, etc.

The runner embodies the "30-line-stub tripwire is non-negotiable" contract:
thin extractions (tier DEGRADED/FAILED) exit 20 and are surfaced as blocking
issues in result.yaml. See references/extraction-report-schema.md for the
canonical output shape and references/delegation-contract.md for the
envelope contract with Marcus.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

# Add the repo root to sys.path so we can import sibling scripts without
# requiring the tree to be packaged. Hyphenated directory names prevent
# standard -m invocation; this is the boring-technology workaround.
_THIS_DIR = Path(__file__).resolve().parent
# _THIS_DIR                 = .../skills/bmad-agent-texas/scripts/
# _THIS_DIR.parents[0]      = .../skills/bmad-agent-texas/
# _THIS_DIR.parents[1]      = .../skills/
# _THIS_DIR.parents[2]      = repo root
_REPO_ROOT = _THIS_DIR.parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

# Load Texas library modules by path (the hyphenated parent path blocks import).
from scripts.utilities.skill_module_loader import load_module_from_path  # noqa: E402

_extraction_validator = load_module_from_path(
    "texas_extraction_validator",
    _THIS_DIR / "extraction_validator.py",
)
_cross_validator = load_module_from_path(
    "texas_cross_validator",
    _THIS_DIR / "cross_validator.py",
)
_source_ops = load_module_from_path(
    "texas_source_wrangler_operations",
    _THIS_DIR / "source_wrangler_operations.py",
)
_cli_encoding = load_module_from_path(
    "texas_cli_encoding",
    _THIS_DIR / "_cli_encoding.py",
)

# Story 26-7 AC-C.2 + code-review finding: fire the guard at import time,
# not just in main(). If this module is `python -m`-loaded (or imported
# by another harness), any import-time print — from sibling modules,
# from tracebacks during load, from wrapper scripts — would hit stdout
# BEFORE main() runs. The guard must precede any possible stdout write.
_cli_encoding.ensure_utf8_stdout()


VALIDATOR_VERSION = "extraction_validator.py@2026-04-17"
RUNNER_VERSION = "run_wrangler.py@2026-04-17"
SCHEMA_VERSION = "1.0"


# ---------------------------------------------------------------------------
# Exit codes and status mapping
# ---------------------------------------------------------------------------

EXIT_COMPLETE = 0
EXIT_COMPLETE_WITH_WARNINGS = 10
EXIT_BLOCKED = 20
EXIT_DIRECTIVE_OR_IO_ERROR = 30

_STATUS_TO_EXIT = {
    "complete": EXIT_COMPLETE,
    "complete_with_warnings": EXIT_COMPLETE_WITH_WARNINGS,
    "blocked": EXIT_BLOCKED,
}

# extractor_used string per provider, for provenance clarity in the report.
# Used as the fallback when the SourceRecord.kind from _fetch_source does not
# match _EXTRACTOR_LABELS_BY_KIND (below).
_EXTRACTOR_LABELS: dict[str, str] = {
    "local_file": "local_text_read",
    "pdf": "pypdf",
    "url": "requests+html_to_text",
    "notion": "notion_client",
    "playwright_html": "playwright_file",
}

# extractor_used string per SourceRecord.kind — preferred lookup because it
# distinguishes extractors within a single provider (e.g., local_file splits
# into local_text_read / local_pdf / local_docx based on file suffix).
_EXTRACTOR_LABELS_BY_KIND: dict[str, str] = {
    "local_file": "local_text_read",
    "local_pdf": "pypdf",
    "local_docx": "python-docx",
    "notion_page": "notion_client",
    "playwright_saved_html": "playwright_file",
}

# Provider -> default source_type passed into the validator's expected-words heuristic.
_PROVIDER_SOURCE_TYPE: dict[str, str] = {
    "local_file": "default",
    "pdf": "pdf",
    "url": "html",
    "notion": "notion",
    "playwright_html": "html",
}


# ---------------------------------------------------------------------------
# Internal data classes
# ---------------------------------------------------------------------------


@dataclass
class SourceOutcome:
    """Collected per-source result used to build both extraction-report.yaml
    and the runner's return envelope."""

    ref_id: str
    provider: str
    locator: str
    role: str
    description: str
    extractor_used: str
    fetched_at: str
    content_text: str
    section_title: str
    report: Any  # extraction_validator.ExtractionReport
    error_kind: str | None = None
    error_detail: str | None = None


# ---------------------------------------------------------------------------
# Directive loading
# ---------------------------------------------------------------------------


class DirectiveError(Exception):
    """Raised when a directive is missing, malformed, or fails shape validation."""


_SUPPORTED_PROVIDERS: frozenset[str] = frozenset(
    {"local_file", "pdf", "url", "notion", "playwright_html"}
)


def _load_directive(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise DirectiveError(f"Directive file not found: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise DirectiveError(f"Directive file is not UTF-8: {exc}") from exc
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        raise DirectiveError(f"Directive YAML failed to parse: {exc}") from exc
    if not isinstance(data, dict):
        raise DirectiveError("Directive root must be a mapping")

    # Minimum-required shape validation — fail loudly at the door.
    for field in ("run_id", "sources"):
        if field not in data:
            raise DirectiveError(f"Directive missing required field: {field}")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise DirectiveError("Directive.sources must be a non-empty list")
    seen_ref_ids: set[str] = set()
    for i, src in enumerate(sources):
        if not isinstance(src, dict):
            raise DirectiveError(f"sources[{i}] must be a mapping")
        for required in ("ref_id", "provider", "locator", "role"):
            if required not in src:
                raise DirectiveError(
                    f"sources[{i}] missing required field: {required}"
                )
        if src["role"] not in ("primary", "validation", "supplementary"):
            raise DirectiveError(
                f"sources[{i}].role must be primary|validation|supplementary, "
                f"got {src['role']!r}"
            )
        if src["provider"] not in _SUPPORTED_PROVIDERS:
            raise DirectiveError(
                f"sources[{i}].provider must be one of "
                f"{sorted(_SUPPORTED_PROVIDERS)}, got {src['provider']!r}"
            )
        ref_id = src["ref_id"]
        if not isinstance(ref_id, str) or not ref_id.strip():
            raise DirectiveError(
                f"sources[{i}].ref_id must be a non-empty string"
            )
        if ref_id in seen_ref_ids:
            raise DirectiveError(
                f"sources[{i}].ref_id={ref_id!r} is a duplicate; ref_ids must be unique"
            )
        seen_ref_ids.add(ref_id)

    # Require at least one primary so downstream consumers always receive content.
    roles = [s["role"] for s in sources]
    if "primary" not in roles:
        raise DirectiveError(
            "Directive has no role: primary source; extraction cannot produce "
            "extracted.md without at least one primary"
        )

    return data


# ---------------------------------------------------------------------------
# Fetch dispatch
# ---------------------------------------------------------------------------


def _fetch_source(src: dict[str, Any]) -> tuple[str, str, Any]:
    """Dispatch to the Texas fetch helper matching the provider.

    Returns (section_title, extracted_text, provenance_record).
    Raises ValueError on unsupported provider or bad input.
    """
    provider = src["provider"]
    locator = src["locator"]

    if provider in ("local_file", "pdf"):
        path = Path(locator)
        if not path.is_file():
            raise ValueError(f"File not found: {locator}")
        suffix = path.suffix.lower()
        if suffix == ".pdf" or provider == "pdf":
            title, body, rec = _source_ops.wrangle_local_pdf(path)
            return title, body, rec
        # Story 27-1: DOCX wired via python-docx before the text-read fall-through.
        # Branch raises python-docx PackageNotFoundError on malformed DOCX; the
        # adapter (_wrangle_source → _classify_fetch_error) maps that to
        # error_kind="docx_extraction_failed" with known_losses=["docx_open_failed"]
        # so the text-read fall-through below is NOT re-entered after failure
        # (which would re-introduce the binary-garbage defect 27-1 exists to fix).
        if suffix == ".docx":
            title, body, rec = _source_ops.wrangle_local_docx(path)
            return title, body, rec
        # Local .md / .txt / other text — read directly.
        body = _source_ops.read_text_file(path)
        rec = _source_ops.SourceRecord(
            kind="local_file",
            ref=str(path.resolve()),
            note=f"local text read ({suffix or 'no-ext'})",
        )
        title = path.stem.replace("_", " ")
        return title, body, rec

    if provider == "url":
        title, body, rec = _source_ops.summarize_url_for_envelope(locator)
        return title, body, rec

    if provider == "notion":
        # wrangle_notion_page returns (title, markdown_body, page_id).
        title, body, page_id = _source_ops.wrangle_notion_page(locator)
        rec = _source_ops.SourceRecord(
            kind="notion_page",
            ref=locator,
            note=f"notion page_id={page_id}",
        )
        return title, body, rec

    if provider == "playwright_html":
        title, body, rec = _source_ops.wrangle_playwright_saved_html(
            locator,
            source_url=src.get("source_url"),
        )
        return title, body, rec

    raise ValueError(f"Unsupported provider: {provider!r}")


# ---------------------------------------------------------------------------
# Per-source wrangling
# ---------------------------------------------------------------------------


def _expected_pages_for_source(src: dict[str, Any], body: str) -> dict[str, Any]:
    """Build the source_meta dict consumed by extraction_validator."""
    meta: dict[str, Any] = {
        "source_type": _PROVIDER_SOURCE_TYPE.get(src["provider"], "default"),
        "filename": src.get("description") or src["locator"],
    }
    # If the operator declared a page count in the directive, respect it.
    if "pages_total" in src:
        meta["pages_total"] = src["pages_total"]
    if "expected_min_words" in src:
        meta["expected_min_words_override"] = src["expected_min_words"]
    return meta


def _wrangle_source(src: dict[str, Any], now: str) -> SourceOutcome:
    """Fetch + validate a single source.

    Captures runtime errors (network, decode, IO, unsupported-provider fallback)
    into a FAILED outcome rather than letting them propagate — the runner always
    produces a report for real-world fetch or parse failures. Programming errors
    still surface because we don't catch BaseException. `now` is the
    run-scoped timestamp (captured once in run() so all artifacts align).
    """
    ref_id = src["ref_id"]
    provider = src["provider"]
    locator = src["locator"]
    role = src["role"]
    description = src.get("description") or locator
    extractor_label = _EXTRACTOR_LABELS.get(provider, "unknown")

    try:
        title, body, rec = _fetch_source(src)
    except Exception as exc:
        # Fetch-layer failure (network, file not found, PDF parse error,
        # Notion auth, unicode decode, or unsupported-provider fallback).
        # Synthesize a FAILED outcome so the runner's "always produces a
        # report" contract holds end-to-end.
        exc_class = type(exc).__name__
        error_kind = _classify_fetch_error(exc)
        detail = f"{exc_class}: {exc}"
        empty_report = _extraction_validator.ExtractionReport(
            tier=_extraction_validator.QualityTier.FAILED,
            word_count=0,
            line_count=0,
            heading_count=0,
            expected_min_words=0,
            completeness_ratio=0.0,
            structural_fidelity="none",
            evidence=[f"Fetch failed for ref_id={ref_id}: {detail}"],
            known_losses=_fetch_error_known_losses(error_kind, detail),
            recommendations=_fetch_error_recommendations(error_kind, provider),
        )
        return SourceOutcome(
            ref_id=ref_id,
            provider=provider,
            locator=locator,
            role=role,
            description=description,
            extractor_used=extractor_label,
            fetched_at=now,
            content_text="",
            section_title=description,
            report=empty_report,
            error_kind=error_kind,
            error_detail=detail,
        )

    # Prefer per-kind extractor label (distinguishes local_text_read / local_pdf /
    # local_docx inside the shared "local_file" provider).
    kind_label = _EXTRACTOR_LABELS_BY_KIND.get(rec.kind) if rec else None
    if kind_label:
        extractor_label = kind_label

    meta = _expected_pages_for_source(src, body)
    report = _extraction_validator.validate_extraction(body, meta)
    # Override the expected_min_words if directive-supplied. Evidence strings
    # embedded by validate_extraction reflect the validator-estimated floor;
    # when the operator asserts an explicit floor via the directive, rewrite
    # those strings so the evidence trail doesn't lie about what was checked.
    if "expected_min_words_override" in meta:
        override = int(meta["expected_min_words_override"])
        original_min = report.expected_min_words
        report.expected_min_words = override
        report.completeness_ratio = (
            report.word_count / override if override > 0 else 0.0
        )
        # Re-derive the tier from the override-adjusted ratio — otherwise an
        # operator declaring `expected_min_words: 4800` against a 500-word
        # extraction would still show FULL_FIDELITY if the validator's
        # own heuristic estimated a 100-word floor. The tripwire depends
        # on the tier, not on completeness_ratio alone.
        report.tier = _rederive_tier_for_override(
            report.word_count,
            override,
            report.structural_fidelity,
            original_tier=report.tier,
        )
        ratio_pct = f"{report.completeness_ratio:.1%}"
        rewritten_evidence: list[str] = []
        for line in report.evidence:
            if line.startswith("Expected minimum:"):
                rewritten_evidence.append(
                    f"Expected minimum: {override} words "
                    f"(completeness ratio: {ratio_pct}; "
                    f"operator-declared floor overrode validator estimate of {original_min})"
                )
            else:
                rewritten_evidence.append(line)
        rewritten_evidence.append(
            f"Tier re-derived after operator-declared floor: {report.tier.name}"
        )
        report.evidence = rewritten_evidence

    return SourceOutcome(
        ref_id=ref_id,
        provider=provider,
        locator=locator,
        role=role,
        description=description,
        extractor_used=extractor_label,
        fetched_at=now,
        content_text=body,
        section_title=title or description,
        report=report,
    )


def _classify_fetch_error(exc: BaseException) -> str:
    """Map a fetch exception to the canonical error_kind vocabulary."""
    # Unsupported-provider fallback from _fetch_source — message-based because
    # it's the one programmer-authored ValueError with stable phrasing.
    message = str(exc)
    if isinstance(exc, ValueError) and "Unsupported provider" in message:
        return "unsupported_provider"
    # Story 27-1: python-docx PackageNotFoundError surfaces for malformed-ZIP /
    # non-DOCX input. Classify by exception class name + module prefix to avoid
    # a hard import of docx into run_wrangler's module-load path (docx is
    # imported by source_wrangler_operations). Module qualification guards
    # against foreign PackageNotFoundError classes (e.g., importlib.metadata,
    # pkg_resources) that share the name but signal unrelated failures —
    # code-review finding (Blind+Edge Hunter, 2026-04-17).
    if (
        type(exc).__name__ == "PackageNotFoundError"
        and type(exc).__module__.startswith("docx.")
    ):
        return "docx_extraction_failed"
    # Missing file is a common shape — surface cleanly.
    if isinstance(exc, FileNotFoundError):
        return "fetch_failed"
    # Decode failures fall under fetch_failed for operator-action purposes.
    if isinstance(exc, UnicodeDecodeError):
        return "fetch_failed"
    return "fetch_failed"


# Story 27-1 AC-B.3: error-kind → known_losses sentinel mapping for the
# FAILED outcome's ExtractionReport. DOCX gets a distinct "docx_open_failed"
# token so cross-validation and operator routing can tell "the file was
# there but unreadable as DOCX" apart from "generic fetch failed."
_ERROR_KIND_TO_KNOWN_LOSSES: dict[str, list[str]] = {
    "docx_extraction_failed": ["docx_open_failed"],
}


def _fetch_error_known_losses(error_kind: str, detail: str) -> list[str]:
    """Return the known_losses list for an error_kind, with per-kind overrides."""
    sentinel = _ERROR_KIND_TO_KNOWN_LOSSES.get(error_kind)
    if sentinel is not None:
        return list(sentinel)
    return [f"Source not fetchable: {detail}"]


def _fetch_error_recommendations(error_kind: str, provider: str) -> list[str]:
    if error_kind == "unsupported_provider":
        return [
            "Check the directive's provider field against the delegation contract",
            "Consult transform-registry.md for supported provider values",
        ]
    return [
        f"Verify the locator for provider={provider!r} is reachable and readable",
        "Check network / auth / file permissions as applicable to the provider",
        "Consult fallback-resolution.md for alternative paths",
    ]


def _rederive_tier_for_override(
    word_count: int,
    expected_min: int,
    structural_fidelity: str,
    original_tier: Any,
) -> Any:
    """Apply the same tier-threshold logic as extraction_validator to the
    override-adjusted ratio. Mirrors the validator's _TIER_THRESHOLDS so
    operator-declared floors drive tier assignment consistently."""
    quality_tier = _extraction_validator.QualityTier
    if expected_min <= 0:
        # Degenerate override: keep the validator's original tier rather than
        # picking a tier based on a meaningless ratio.
        return original_tier
    ratio = word_count / expected_min
    if ratio >= 0.80 and structural_fidelity in ("high", "medium"):
        return quality_tier.FULL_FIDELITY
    if ratio >= 0.50:
        return quality_tier.ADEQUATE_WITH_GAPS
    if ratio >= 0.20:
        return quality_tier.DEGRADED
    return quality_tier.FAILED


# ---------------------------------------------------------------------------
# Cross-validation
# ---------------------------------------------------------------------------


def _run_cross_validation(
    primaries: list[SourceOutcome],
    validators: list[SourceOutcome],
    directive_sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Run cross_validator for each (primary, validation) pair.

    Returns a list of dicts matching the extraction-report-schema
    cross_validation[] shape. Empty list when no validation assets present.
    """
    if not validators or not primaries:
        return []

    entries: list[dict[str, Any]] = []
    for primary in primaries:
        if not primary.content_text:
            continue
        for validator_src in validators:
            if not validator_src.content_text:
                continue
            directive_entry = next(
                (s for s in directive_sources if s["ref_id"] == validator_src.ref_id),
                {},
            )
            coverage_scope = directive_entry.get("coverage_scope", "unspecified")

            result = _cross_validator.cross_validate(
                extracted_text=primary.content_text,
                reference_text=validator_src.content_text,
                reference_meta={
                    "ref_id": validator_src.ref_id,
                    "description": validator_src.description,
                    "coverage_scope": coverage_scope,
                },
            )
            entry = {
                "primary_ref_id": primary.ref_id,
                "asset_ref_id": result.asset_ref_id,
                "asset_description": result.asset_description,
                "coverage_scope": result.coverage_scope,
                "sections_in_reference": result.sections_in_reference,
                "sections_matched": result.sections_matched,
                "key_terms_total": result.key_terms_total,
                "key_terms_found": result.key_terms_found,
                "key_terms_coverage": round(result.key_terms_coverage, 3),
                "word_count_ratio": round(result.word_count_ratio, 2),
                "verdict": result.verdict,
                "passed": bool(result.passed),
                "missing_sections": list(result.missing_sections[:10]),
                "missing_key_terms": list(result.missing_key_terms[:10]),
            }
            entries.append(entry)
    return entries


# ---------------------------------------------------------------------------
# Overall status derivation
# ---------------------------------------------------------------------------


def _derive_overall_status(
    outcomes: list[SourceOutcome],
    cross_entries: list[dict[str, Any]],
) -> tuple[str, list[dict[str, Any]]]:
    """Return (overall_status, blocking_issues[])."""
    quality_tier = _extraction_validator.QualityTier
    blocking: list[dict[str, Any]] = []

    any_failed = False
    any_degraded = False
    any_warnings = False

    for o in outcomes:
        if o.error_kind:
            blocking.append(
                {
                    "ref_id": o.ref_id,
                    "reason": o.error_kind,
                    "detail": o.error_detail or "fetch error",
                    "operator_question": "Provide a working locator or switch providers",
                }
            )
            any_failed = True
            continue
        tier = o.report.tier
        if tier == quality_tier.FAILED:
            any_failed = True
            blocking.append(
                {
                    "ref_id": o.ref_id,
                    "reason": "insufficient_content",
                    "detail": (
                        f"Extraction produced only {o.report.word_count} words "
                        f"({o.report.completeness_ratio:.0%} of expected "
                        f"{o.report.expected_min_words})"
                    ),
                    "operator_question": (
                        "Is the source scanned/image-only, or is a different "
                        "provider needed?"
                    ),
                }
            )
        elif tier == quality_tier.DEGRADED:
            any_degraded = True
            blocking.append(
                {
                    "ref_id": o.ref_id,
                    "reason": "insufficient_content",
                    "detail": (
                        f"Degraded extraction: {o.report.completeness_ratio:.0%} "
                        f"of expected volume — below the 50% adequacy floor"
                    ),
                    "operator_question": (
                        "Try the documented fallback chain for this provider "
                        "or supply a validation-role asset"
                    ),
                }
            )
        elif tier == quality_tier.ADEQUATE_WITH_GAPS:
            any_warnings = True

    if any_failed or any_degraded:
        return "blocked", blocking

    # Any failed cross-validation on a primary elevates to warnings.
    for entry in cross_entries:
        if not entry["passed"]:
            any_warnings = True
            break

    if any_warnings:
        return "complete_with_warnings", blocking

    return "complete", blocking


# ---------------------------------------------------------------------------
# Artifact writers
# ---------------------------------------------------------------------------


def _write_extracted_md(
    bundle_dir: Path,
    run_id: str,
    primaries: list[SourceOutcome],
) -> Path:
    """Build and write extracted.md from primary sources only."""
    sections = [(p.section_title, p.content_text) for p in primaries if p.content_text]
    title = f"Source bundle for {run_id}"
    extracted = _source_ops.build_extracted_markdown(title, sections)
    path = bundle_dir / "extracted.md"
    path.write_text(extracted, encoding="utf-8")
    return path


def _write_metadata_json(
    bundle_dir: Path,
    run_id: str,
    outcomes: list[SourceOutcome],
    run_timestamp: str,
) -> Path:
    """Write metadata.json with the provenance chain preserved."""
    provenance = [
        {
            "ref_id": o.ref_id,
            "kind": o.provider,
            "ref": o.locator,
            "role": o.role,
            "description": o.description,
            "extractor_used": o.extractor_used,
            "fetched_at": o.fetched_at,
        }
        for o in outcomes
    ]
    meta = {
        "run_id": run_id,
        "generated_at": run_timestamp,
        "provenance": provenance,
        "primary_consumption_path": "extracted.md",
    }
    path = bundle_dir / "metadata.json"
    path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return path


def _source_outcome_to_report_entry(o: SourceOutcome) -> dict[str, Any]:
    return {
        "ref_id": o.ref_id,
        "provider": o.provider,
        "locator": o.locator,
        "role": o.role,
        "tier": o.report.tier.name,
        "tier_value": o.report.tier.value,
        "passed": bool(o.report.passed),
        "counts": {
            "words": o.report.word_count,
            "lines": o.report.line_count,
            "headings": o.report.heading_count,
            "expected_min_words": o.report.expected_min_words,
        },
        "structural_fidelity": o.report.structural_fidelity,
        "completeness_ratio": round(o.report.completeness_ratio, 3),
        "extractor_used": o.extractor_used,
        "fetched_at": o.fetched_at,
        "content_path": "extracted.md" if o.role == "primary" else None,
        "evidence": list(o.report.evidence),
        "known_losses": list(o.report.known_losses),
        "recommendations": list(o.report.recommendations),
    }


def _write_extraction_report(
    bundle_dir: Path,
    run_id: str,
    overall_status: str,
    outcomes: list[SourceOutcome],
    cross_entries: list[dict[str, Any]],
    blocking_issues: list[dict[str, Any]],
    run_timestamp: str,
) -> Path:
    """Write extraction-report.yaml matching extraction-report-schema.md v1.0."""
    evidence_summary = _build_evidence_summary(overall_status, outcomes, cross_entries)
    report = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at": run_timestamp,
        "overall_status": overall_status,
        "validator_version": VALIDATOR_VERSION,
        "sources": [_source_outcome_to_report_entry(o) for o in outcomes],
        "cross_validation": cross_entries,
        "evidence_summary": evidence_summary,
        "recommendations": _collect_recommendations(outcomes),
    }
    if overall_status == "blocked" and blocking_issues:
        report["blocking_issues"] = blocking_issues
    path = bundle_dir / "extraction-report.yaml"
    path.write_text(
        yaml.safe_dump(report, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return path


def _build_evidence_summary(
    overall_status: str,
    outcomes: list[SourceOutcome],
    cross_entries: list[dict[str, Any]],
) -> list[str]:
    # Schema contract: always produce 2-5 sentences.
    primaries = [o for o in outcomes if o.role == "primary"]
    validators = [o for o in outcomes if o.role == "validation"]
    supplementaries = [o for o in outcomes if o.role == "supplementary"]
    lines: list[str] = []
    if primaries:
        tier_names = [o.report.tier.name for o in primaries]
        lines.append(
            f"{len(primaries)} primary source(s) processed; tiers: {', '.join(tier_names)}."
        )
    else:
        # Should be unreachable — directive validation rejects zero-primary
        # directives at load time — but we keep a defensive branch so the
        # evidence summary always explains why a report exists.
        lines.append(
            "No primary sources were processed (directive validation should "
            "have prevented this state)."
        )
    if cross_entries:
        passed = sum(1 for e in cross_entries if e["passed"])
        lines.append(
            f"Cross-validation: {passed}/{len(cross_entries)} validation pairs passed "
            f"across {len(validators)} validation-role asset(s)."
        )
    else:
        lines.append("No validation-role assets supplied; cross-validation skipped.")
    if supplementaries:
        lines.append(
            f"{len(supplementaries)} supplementary source(s) recorded in metadata "
            "provenance but not extracted into extracted.md."
        )
    lines.append(f"Overall status: {overall_status}.")
    return lines


def _collect_recommendations(outcomes: list[SourceOutcome]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for o in outcomes:
        for r in o.report.recommendations:
            if r not in seen:
                seen.add(r)
                out.append(r)
    return out


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _write_manifest_json(
    bundle_dir: Path,
    run_id: str,
    artifact_paths: list[Path],
    run_timestamp: str,
) -> Path:
    """Write manifest.json listing every artifact with sha256 + size.

    Intentionally includes itself-by-omission: manifest.json isn't listed
    because it's written after the content files. Its sha256 would change
    every run anyway. result.yaml is also written after manifest.json so
    it cannot self-hash either; that omission is documented in the delegation
    contract.
    """
    artifacts = []
    for p in artifact_paths:
        if p.is_file():
            artifacts.append(
                {
                    "path": p.relative_to(bundle_dir).as_posix(),
                    "sha256": _sha256_of_file(p),
                    "size_bytes": p.stat().st_size,
                }
            )
    manifest = {
        "schema_version": "1.0",
        "run_id": run_id,
        "bundle_dir": Path(bundle_dir).resolve().as_posix(),
        "generated_at": run_timestamp,
        "artifacts": artifacts,
    }
    path = bundle_dir / "manifest.json"
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def _write_ingestion_evidence(
    bundle_dir: Path,
    run_id: str,
    outcomes: list[SourceOutcome],
    cross_entries: list[dict[str, Any]],
    overall_status: str,
    run_timestamp: str,
) -> Path:
    """Human-readable markdown log of the session."""
    lines: list[str] = [
        "# Ingestion Evidence Log",
        "",
        f"**Run ID:** {run_id}",
        f"**Generated at:** {run_timestamp}",
        f"**Overall status:** {overall_status}",
        f"**Runner:** {RUNNER_VERSION}",
        "",
        "## Sources Processed",
        "",
    ]
    for o in outcomes:
        lines.append(f"### {o.ref_id} — {o.description}")
        lines.append("")
        lines.append(f"- Provider: `{o.provider}`")
        lines.append(f"- Role: `{o.role}`")
        lines.append(f"- Extractor: `{o.extractor_used}`")
        lines.append(f"- Fetched at: {o.fetched_at}")
        lines.append(f"- Tier: **{o.report.tier.name}** (tier_value {o.report.tier.value})")
        lines.append(
            f"- Counts: {o.report.word_count} words / "
            f"{o.report.line_count} lines / {o.report.heading_count} headings "
            f"(expected min {o.report.expected_min_words})"
        )
        lines.append(f"- Completeness ratio: {o.report.completeness_ratio:.1%}")
        lines.append(f"- Structural fidelity: {o.report.structural_fidelity}")
        if o.report.evidence:
            lines.append("- Evidence:")
            for e in o.report.evidence:
                lines.append(f"  - {e}")
        if o.report.known_losses:
            lines.append("- Known losses:")
            for loss in o.report.known_losses:
                lines.append(f"  - {loss}")
        if o.error_kind:
            lines.append(f"- **Error:** {o.error_kind} — {o.error_detail}")
        lines.append("")

    if cross_entries:
        lines.append("## Cross-Validation")
        lines.append("")
        for entry in cross_entries:
            verdict_word = "PASS" if entry["passed"] else "FAIL"
            lines.append(
                f"- **{verdict_word}** {entry['primary_ref_id']} ↔ "
                f"{entry['asset_ref_id']}: "
                f"sections {entry['sections_matched']}/{entry['sections_in_reference']}, "
                f"key-term coverage {entry['key_terms_coverage']:.1%}. "
                f"Verdict: {entry['verdict']}"
            )
        lines.append("")

    path = bundle_dir / "ingestion-evidence.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _write_result_envelope(
    bundle_dir: Path,
    run_id: str,
    overall_status: str,
    outcomes: list[SourceOutcome],
    cross_entries: list[dict[str, Any]],
    blocking_issues: list[dict[str, Any]],
    artifact_paths: list[Path],
) -> Path:
    """Write result.yaml matching the delegation-contract Texas -> Marcus return.

    This is the *envelope* Marcus consumes — it mirrors extraction-report.yaml
    but with additional pointers to artifacts and Marcus-facing status.
    """
    materials = []
    for o in outcomes:
        materials.append(
            {
                "ref_id": o.ref_id,
                "role": o.role,
                "quality_tier": o.report.tier.value,
                "extractor_used": o.extractor_used,
                "content_path": "extracted.md" if o.role == "primary" else None,
                "word_count": o.report.word_count,
                "line_count": o.report.line_count,
                "heading_count": o.report.heading_count,
                "quality_report": {
                    "completeness_ratio": round(o.report.completeness_ratio, 3),
                    "structural_fidelity": o.report.structural_fidelity,
                    "known_losses": list(o.report.known_losses),
                    "evidence": list(o.report.evidence),
                },
            }
        )

    envelope = {
        "status": overall_status,
        "run_id": run_id,
        "bundle_dir": Path(bundle_dir).resolve().as_posix(),
        "runner_version": RUNNER_VERSION,
        "materials": materials,
        "cross_validation": cross_entries,
        "blocking_issues": blocking_issues,
        "recommendations": _collect_recommendations(outcomes),
        "artifacts": [p.relative_to(bundle_dir).as_posix() for p in artifact_paths],
        "bundle_manifest_path": "manifest.json",
    }
    path = bundle_dir / "result.yaml"
    path.write_text(
        yaml.safe_dump(envelope, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def _utc_timestamp_z() -> str:
    """ISO-8601 UTC timestamp with trailing Z suffix (matches schema example)."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(directive_path: Path, bundle_dir: Path) -> dict[str, Any]:
    """Run the wrangler end-to-end; return the result envelope as a dict.

    Raises DirectiveError on malformed directive (caller maps to exit 30).
    Runtime errors inside source fetching are captured into FAILED outcomes
    per the "always produce a report" contract. Unexpected programming
    errors (TypeError, AttributeError, etc.) still propagate so bugs surface
    rather than being silently swallowed.
    """
    directive = _load_directive(directive_path)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    run_id = str(directive["run_id"])
    # Capture one run-scoped timestamp so every artifact agrees on "when".
    run_timestamp = _utc_timestamp_z()

    # Wrangle every source in directive order. Primary + validation both fetch
    # content; role drives downstream treatment. Supplementary sources are
    # fetched into metadata provenance but contribute no content to extracted.md
    # and are not cross-validated.
    outcomes: list[SourceOutcome] = []
    for src in directive["sources"]:
        outcomes.append(_wrangle_source(src, run_timestamp))

    primaries = [o for o in outcomes if o.role == "primary"]
    validators = [o for o in outcomes if o.role == "validation"]

    cross_entries = _run_cross_validation(primaries, validators, directive["sources"])
    overall_status, blocking_issues = _derive_overall_status(outcomes, cross_entries)

    # Write artifacts in a specific order so manifest.json indexes all the
    # content-bearing files.
    extracted_path = _write_extracted_md(bundle_dir, run_id, primaries)
    metadata_path = _write_metadata_json(bundle_dir, run_id, outcomes, run_timestamp)
    extraction_report_path = _write_extraction_report(
        bundle_dir,
        run_id,
        overall_status,
        outcomes,
        cross_entries,
        blocking_issues,
        run_timestamp,
    )
    ingestion_evidence_path = _write_ingestion_evidence(
        bundle_dir, run_id, outcomes, cross_entries, overall_status, run_timestamp
    )

    content_artifacts = [
        extracted_path,
        metadata_path,
        extraction_report_path,
        ingestion_evidence_path,
    ]
    manifest_path = _write_manifest_json(
        bundle_dir, run_id, content_artifacts, run_timestamp
    )

    all_artifacts = content_artifacts + [manifest_path]
    result_path = _write_result_envelope(
        bundle_dir,
        run_id,
        overall_status,
        outcomes,
        cross_entries,
        blocking_issues,
        all_artifacts,
    )

    # Re-read the written envelope so the in-memory return matches disk exactly.
    return yaml.safe_load(result_path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    # Story 26-7 AC-C.2: force UTF-8 stdout/stderr before any print so a
    # Windows cp1252 terminal does not crash on non-ASCII source titles.
    _cli_encoding.ensure_utf8_stdout()

    parser = argparse.ArgumentParser(
        description=(
            "Texas runtime wrangling runner — executes the Marcus ↔ Texas "
            "delegation contract end-to-end."
        )
    )
    parser.add_argument(
        "--directive",
        type=Path,
        required=True,
        help="Path to the wrangling directive YAML.",
    )
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        required=True,
        help="Bundle directory where artifacts are written.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the result envelope as JSON to stdout (default: YAML).",
    )

    args = parser.parse_args(argv)

    try:
        envelope = run(args.directive, args.bundle_dir)
    except DirectiveError as exc:
        sys.stderr.write(f"[run_wrangler] directive error: {exc}\n")
        return EXIT_DIRECTIVE_OR_IO_ERROR
    except OSError as exc:
        sys.stderr.write(f"[run_wrangler] IO error: {exc}\n")
        return EXIT_DIRECTIVE_OR_IO_ERROR
    except Exception as exc:  # noqa: BLE001 — deliberate runner-boundary catch
        # Any other exception (programming error, unexpected library fault)
        # is still a runner failure from Marcus's perspective. Report it
        # cleanly rather than letting Python print a traceback and return 1.
        sys.stderr.write(
            f"[run_wrangler] unexpected error ({type(exc).__name__}): {exc}\n"
            "[run_wrangler] this indicates a runner bug or unhandled fetch "
            "exception class — report to the maintainer\n"
        )
        return EXIT_DIRECTIVE_OR_IO_ERROR

    if args.json:
        sys.stdout.write(json.dumps(envelope, indent=2) + "\n")
    else:
        sys.stdout.write(yaml.safe_dump(envelope, sort_keys=False) + "\n")

    status = envelope.get("status", "blocked")
    return _STATUS_TO_EXIT.get(status, EXIT_BLOCKED)


if __name__ == "__main__":
    raise SystemExit(main())
