"""Generate a Marcus prompt harness and Quinn watcher report."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - pyyaml is a declared dependency
    yaml = None  # type: ignore[assignment]

from scripts.utilities.file_helpers import project_root
from scripts.utilities.run_constants import RunConstantsError, load_run_constants
from scripts.utilities.validate_source_directory_scan_gate import (
    validate_source_directory_scan_gate,
)


STANDARD_PROMPT_PACK = Path("docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md")
MOTION_PROMPT_PACK = Path("docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md")
SESSION_LAUNCHER = Path("docs/workflow/production-session-launcher.md")
DEFAULT_OUTPUT_DIR = Path("reports/prompt-harness/standard-v4.1")
MOTION_OUTPUT_DIR = Path("reports/prompt-harness/motion-v4.2")
STANDARD_STEP_HEADINGS = (
    "1) Activation + Preflight Contract Gate",
    "2) Source Authority Map Before Ingestion",
    "2A) Operator Directives (Custom Source Instructions)",
    "3) Ingestion Execution + Evidence Log",
    "4) Ingestion Quality Gate + Irene Packet",
    "5) Irene Pass 1 Structure + Gate 1 Fidelity",
    "6) Gate 1 Approved -> Pre-Dispatch Package Build (No Send)",
    "6B) Literal-Visual Operator Build + Confirmation (Mandatory Before Dispatch)",
    "7) Dispatch + Export + Sort Verification (Single Operation)",
    "7B) Variant Selection Gate (Double-Dispatch Only)",
    "8) Irene Pass 2 — Dual-Channel Narration with Inline Perception",
)
# Step 5B is a conditional cluster-only operator gate. It is documented in the
# prompt packs and the CLUSTER_GATE_STEP_HEADING constant below, but excluded
# from STANDARD/MOTION_STEP_HEADINGS because those tuples use positional indexing
# to map headings to StepReport objects — inserting a conditional step would shift
# all subsequent indices and break the mapping.
CLUSTER_GATE_STEP_HEADING = "5B) Cluster Plan G1.5 Gate + Operator Review"
MOTION_STEP_HEADINGS = (
    "1) Activation + Preflight Contract Gate",
    "2) Source Authority Map Before Ingestion",
    "2A) Operator Directives (Mandatory)",
    "3) Ingestion Execution + Evidence Log",
    "4) Ingestion Quality Gate + Irene Packet",
    "5) Irene Pass 1 Structure + Gate 1 Fidelity",
    "6) Gate 1 Approved -> Pre-Dispatch Package Build (No Send)",
    "6B) Literal-Visual Operator Build + Confirmation",
    "7) Gary Dispatch + Export + Sort Verification",
    "7B) Variant Selection Gate (Double-Dispatch Only)",
    "7C) Storyboard A + Gate 2 Approval + Winner Authorization",
    "7D) Gate 2M Motion Designation",
    "7E) Motion Generation / Import",
    "7F) Motion Gate",
    "8) Irene Pass 2 - Motion-Aware Narration + Segment Manifest",
)


@dataclass(frozen=True)
class HarnessContext:
    run_id: str
    lesson_slug: str
    bundle_dir: Path
    bundle_path: str
    primary_source_file: str
    optional_context_assets: tuple[str, ...]
    theme_selection: str
    theme_paramset_key: str
    execution_mode: str
    quality_preset: str
    double_dispatch: bool
    motion_enabled: bool
    cluster_density: str | None
    experience_profile: str | None
    field_sources: dict[str, str]


@dataclass(frozen=True)
class StepReport:
    step: str
    heading: str
    status: str
    summary: str
    evidence: tuple[str, ...]
    gaps: tuple[str, ...]


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_text(value: str) -> str:
    return value.replace("\r\n", "\n")


def _extract_sections(path: Path) -> dict[str, str]:
    text = _normalize_text(path.read_text(encoding="utf-8"))
    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines).strip()
            current_heading = line[3:].strip()
            current_lines = []
            continue
        if current_heading is not None:
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines).strip()
    return sections


def _bundle_candidates(root: Path) -> list[Path]:
    base = root / "course-content" / "staging" / "tracked" / "source-bundles"
    if not base.is_dir():
        return []
    candidates = [p for p in base.iterdir() if p.is_dir()]
    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates


def _repo_relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _slug_from_bundle_name(bundle_dir: Path) -> str:
    match = re.match(r"(?P<slug>.+)-\d{8}$", bundle_dir.name)
    if match:
        return match.group("slug")
    return bundle_dir.name or "apc-c1m1-tejal"


def _first_match(root: Path, patterns: tuple[str, ...]) -> str | None:
    for pattern in patterns:
        matches = sorted(root.glob(pattern))
        if matches:
            return str(matches[0].resolve())
    return None


def infer_context(*, root: Path, bundle_dir: Path | None = None) -> HarnessContext:
    resolved_bundle = bundle_dir.resolve() if bundle_dir is not None else None
    if resolved_bundle is None:
        candidates = _bundle_candidates(root)
        resolved_bundle = (
            candidates[0].resolve()
            if candidates
            else (root / "course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260403").resolve()
        )

    field_sources: dict[str, str] = {}
    run_constants = None
    run_constants_path = resolved_bundle / "run-constants.yaml"

    if resolved_bundle.is_dir() and run_constants_path.is_file():
        run_constants = load_run_constants(resolved_bundle, root=root)

    def choose(field: str, value: str, source: str) -> str:
        field_sources[field] = source
        return value

    cluster_density = None
    experience_profile = None
    if run_constants is not None:
        run_id = choose("run_id", run_constants.run_id, "run-constants.yaml")
        lesson_slug = choose("lesson_slug", run_constants.lesson_slug, "run-constants.yaml")
        bundle_path = choose("bundle_path", run_constants.bundle_path, "run-constants.yaml")
        primary_source_file = choose("primary_source_file", run_constants.primary_source_file, "run-constants.yaml")
        optional_context_assets = tuple(run_constants.optional_context_assets)
        field_sources["optional_context_assets"] = "run-constants.yaml"
        theme_selection = choose("theme_selection", run_constants.theme_selection, "run-constants.yaml")
        theme_paramset_key = choose("theme_paramset_key", run_constants.theme_paramset_key, "run-constants.yaml")
        execution_mode = choose("execution_mode", run_constants.execution_mode, "run-constants.yaml")
        quality_preset = choose("quality_preset", run_constants.quality_preset, "run-constants.yaml")
        double_dispatch = run_constants.double_dispatch
        field_sources["double_dispatch"] = "run-constants.yaml"
        motion_enabled = run_constants.motion_enabled
        field_sources["motion_enabled"] = "run-constants.yaml"
        cluster_density = run_constants.cluster_density
        field_sources["cluster_density"] = "run-constants.yaml"
        experience_profile = run_constants.experience_profile
        field_sources["experience_profile"] = "run-constants.yaml"
    else:
        run_id = choose("run_id", f"C1-M1-PRES-{_now_utc().strftime('%Y%m%d')}", "plausible fallback")
        lesson_slug = choose("lesson_slug", _slug_from_bundle_name(resolved_bundle), "bundle-dir name")
        bundle_path = choose("bundle_path", _repo_relative(resolved_bundle, root), "bundle-dir path")
        primary_source_file = choose(
            "primary_source_file",
            _first_match(root, ("course-content/courses/*.pdf",)) or "[PRIMARY_SOURCE_FILE]",
            "filesystem fallback",
        )
        optional_asset = _first_match(root, ("course-content/courses/*Roadmap*.jpg", "course-content/courses/*.jpg"))
        optional_context_assets = (optional_asset,) if optional_asset else ()
        field_sources["optional_context_assets"] = "filesystem fallback" if optional_asset else "plausible fallback"
        theme_selection = choose("theme_selection", "hil-2026-apc-nejal-A", "plausible fallback")
        theme_paramset_key = choose("theme_paramset_key", "hil-2026-apc-nejal-A", "plausible fallback")
        execution_mode = choose("execution_mode", "tracked/default", "plausible fallback")
        quality_preset = choose("quality_preset", "production", "plausible fallback")
        double_dispatch = False
        field_sources["double_dispatch"] = "plausible fallback"
        motion_enabled = (resolved_bundle / "motion_plan.yaml").is_file()
        field_sources["motion_enabled"] = "bundle filesystem" if motion_enabled else "plausible fallback"
        cluster_density = None
        field_sources["cluster_density"] = "plausible fallback"
        experience_profile = None
        field_sources["experience_profile"] = "plausible fallback"

    return HarnessContext(
        run_id=run_id,
        lesson_slug=lesson_slug,
        bundle_dir=resolved_bundle,
        bundle_path=bundle_path,
        primary_source_file=primary_source_file,
        optional_context_assets=optional_context_assets,
        theme_selection=theme_selection,
        theme_paramset_key=theme_paramset_key,
        execution_mode=execution_mode,
        quality_preset=quality_preset,
        double_dispatch=double_dispatch,
        motion_enabled=motion_enabled,
        cluster_density=cluster_density,
        experience_profile=experience_profile,
        field_sources=field_sources,
    )


def _replace_placeholders(text: str, context: HarnessContext) -> str:
    replacements = {
        "[RUN_ID]": context.run_id,
        "[LESSON_SLUG]": context.lesson_slug,
        "[BUNDLE_PATH]": context.bundle_path,
        "[PRIMARY_SOURCE_FILE]": context.primary_source_file,
        "[OPTIONAL_CONTEXT_ASSETS]": ", ".join(context.optional_context_assets) if context.optional_context_assets else "none",
        "[THEME_SELECTION]": context.theme_selection,
        "[THEME_PARAMSET_KEY]": context.theme_paramset_key,
    }
    rendered = text
    for needle, value in replacements.items():
        rendered = rendered.replace(needle, value)
    return rendered


def _read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return _normalize_text(path.read_text(encoding="utf-8"))


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _read_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file() or yaml is None:
        return None
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else None


def _extract_markdown_key_values(path: Path) -> dict[str, str]:
    text = _read_text(path)
    if text is None:
        return {}
    values: dict[str, str] = {}
    pattern = re.compile(r"^\s*(?:-\s+)?([A-Za-z0-9_ -]+):\s*(.+?)\s*$")
    for line in text.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        key = match.group(1).strip().lower().replace(" ", "_")
        values[key] = match.group(2).strip()
    return values


def _prompt_pack_path(context: HarnessContext) -> Path:
    return MOTION_PROMPT_PACK if context.motion_enabled else STANDARD_PROMPT_PACK


def _step_headings(context: HarnessContext) -> tuple[str, ...]:
    base = MOTION_STEP_HEADINGS if context.motion_enabled else STANDARD_STEP_HEADINGS
    if context.cluster_density not in (None, "none"):
        # Insert 5B after 5
        index = next(i for i, h in enumerate(base) if h.startswith("5) "))
        base = base[:index+1] + (CLUSTER_GATE_STEP_HEADING,) + base[index+1:]
    return base


def _artifact_run_id(path: Path) -> str | None:
    if not path.exists():
        return None
    if path.suffix.lower() == ".json":
        payload = _read_json(path)
        value = payload.get("run_id") if isinstance(payload, dict) else None
        return value if isinstance(value, str) else None
    key_values = _extract_markdown_key_values(path)
    return key_values.get("run_id")


def _authorized_slide_ids(bundle_dir: Path) -> tuple[str, ...]:
    payload = _read_json(bundle_dir / "authorized-storyboard.json") or {}
    slide_ids = payload.get("slide_ids")
    if isinstance(slide_ids, list):
        return tuple(item for item in slide_ids if isinstance(item, str) and item.strip())
    slides = payload.get("authorized_slides")
    if not isinstance(slides, list):
        return tuple()
    out: list[str] = []
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        slide_id = slide.get("slide_id")
        if isinstance(slide_id, str) and slide_id.strip():
            out.append(slide_id)
    return tuple(out)


def _motion_rows(bundle_dir: Path) -> list[dict[str, Any]]:
    payload = _read_yaml(bundle_dir / "motion_plan.yaml") or {}
    rows = payload.get("slides")
    return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []


def _step_status(*, direct_ok: bool, inferred_ok: bool, inconsistent: bool, gaps: list[str]) -> str:
    if inconsistent:
        return "INCONSISTENT"
    if direct_ok and not gaps:
        return "PASS"
    if direct_ok and gaps:
        return "PARTIAL"
    if inferred_ok:
        return "INFERRED"
    return "MISSING"


def _check_step_1(bundle_dir: Path) -> StepReport:
    preflight_path = bundle_dir / "preflight-results.json"
    payload = _read_json(preflight_path)
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False
    if payload is None:
        gaps.append("preflight-results.json missing")
    else:
        evidence.append("preflight-results.json present")
        gate = payload.get("gate", {})
        overall = gate.get("overall_status")
        if overall == "pass":
            evidence.append("preflight gate overall_status=pass")
        else:
            inconsistent = True
            gaps.append(f"preflight gate overall_status={overall!r}")
    status = _step_status(direct_ok=payload is not None, inferred_ok=False, inconsistent=inconsistent, gaps=gaps)
    summary = "Preflight evidence present and passing." if status == "PASS" else "Prompt 1 evidence is incomplete or failing."
    return StepReport("1", STANDARD_STEP_HEADINGS[0], status, summary, tuple(evidence), tuple(gaps))


def _check_step_2(bundle_dir: Path) -> StepReport:
    source_map = bundle_dir / "source-authority-map.md"
    source_scan = bundle_dir / "source-directory-scan.md"
    ingestion_evidence = bundle_dir / "ingestion-evidence.md"
    metadata = bundle_dir / "metadata.json"
    evidence: list[str] = []
    gaps: list[str] = []
    direct_ok = source_map.is_file()
    inferred_ok = False
    inconsistent = False
    if source_map.is_file():
        evidence.append("source-authority-map.md present")
    else:
        gaps.append("source-authority-map.md missing")
    if source_scan.is_file():
        evidence.append("source-directory-scan.md present")
        gate_result = validate_source_directory_scan_gate(source_scan)
        if gate_result["valid"]:
            evidence.append("source-directory scan gate valid")
        else:
            inconsistent = True
            gaps.extend(str(item) for item in gate_result["issues"])
    elif source_map.is_file():
        gaps.append("source-directory-scan.md missing")

    if not direct_ok and not source_map.is_file():
        if ingestion_evidence.is_file():
            evidence.append("ingestion-evidence.md present")
            inferred_ok = True
        if metadata.is_file():
            evidence.append("metadata.json present")
            inferred_ok = True
        if not inferred_ok:
            gaps.append("No source authority map or downstream ingestion evidence found")
    status = _step_status(direct_ok=direct_ok, inferred_ok=inferred_ok, inconsistent=inconsistent, gaps=gaps)
    summary = {
        "PASS": "Direct source scan and source authority map artifacts found.",
        "INFERRED": "Prompt 2 is only indirectly evidenced by downstream ingestion artifacts.",
        "MISSING": "No evidence that Prompt 2 output was persisted.",
        "PARTIAL": "Prompt 2 map exists but the scan-first gate artifact is missing.",
        "INCONSISTENT": "Prompt 2 artifacts exist but the scan-first gate validator failed.",
    }.get(status, "Prompt 2 evidence is incomplete.")
    return StepReport("2", STANDARD_STEP_HEADINGS[1], status, summary, tuple(evidence), tuple(gaps))


def _check_step_2a(bundle_dir: Path) -> StepReport:
    path = bundle_dir / "operator-directives.md"
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False
    values = _extract_markdown_key_values(path)
    if not path.is_file():
        gaps.append("operator-directives.md missing")
    else:
        evidence.append("operator-directives.md present")
        poll_status = values.get("poll_status")
        if poll_status in {"submitted", "open", "closed-timeout"}:
            evidence.append(f"poll_status={poll_status}")
        else:
            inconsistent = True
            gaps.append(f"Unexpected poll_status={poll_status!r}")
    status = _step_status(direct_ok=path.is_file(), inferred_ok=False, inconsistent=inconsistent, gaps=gaps)
    summary = "Operator directives artifact found." if status == "PASS" else "Prompt 2A evidence is incomplete or inconsistent."
    return StepReport("2A", STANDARD_STEP_HEADINGS[2], status, summary, tuple(evidence), tuple(gaps))


def _check_step_3(bundle_dir: Path) -> StepReport:
    required = ("extracted.md", "metadata.json", "ingestion-evidence.md")
    evidence = [name for name in required if (bundle_dir / name).exists()]
    gaps = [f"{name} missing" for name in required if not (bundle_dir / name).exists()]
    status = _step_status(
        direct_ok=len(evidence) == len(required),
        inferred_ok=False,
        inconsistent=False,
        gaps=gaps,
    )
    summary = "Ingestion artifacts are present." if status == "PASS" else "Prompt 3 did not leave the full ingestion artifact set."
    return StepReport("3", STANDARD_STEP_HEADINGS[3], status, summary, tuple(evidence), tuple(gaps))


def _check_step_4(bundle_dir: Path) -> StepReport:
    packet = bundle_dir / "irene-packet.md"
    receipt = bundle_dir / "ingestion-quality-gate-receipt.md"
    values = _extract_markdown_key_values(receipt)
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False
    if packet.is_file():
        evidence.append("irene-packet.md present")
    else:
        gaps.append("irene-packet.md missing")
    if receipt.is_file():
        evidence.append("ingestion-quality-gate-receipt.md present")
        decision = values.get("gate_decision")
        if decision == "proceed":
            evidence.append("gate_decision=proceed")
        else:
            inconsistent = True
            gaps.append(f"gate_decision={decision!r}")
    else:
        gaps.append("ingestion-quality-gate-receipt.md missing")
    status = _step_status(
        direct_ok=packet.is_file() and receipt.is_file(),
        inferred_ok=False,
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = "Irene packet and Prompt 4 gate receipt are present." if status == "PASS" else "Prompt 4 evidence is incomplete or inconsistent."
    return StepReport("4", STANDARD_STEP_HEADINGS[4], status, summary, tuple(evidence), tuple(gaps))


def _check_step_5(bundle_dir: Path) -> StepReport:
    packet = bundle_dir / "irene-pass1.md"
    receipt = bundle_dir / "irene-pass1-fidelity-receipt.md"
    values = _extract_markdown_key_values(receipt)
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False
    if packet.is_file():
        evidence.append("irene-pass1.md present")
    else:
        gaps.append("irene-pass1.md missing")
    if receipt.is_file():
        evidence.append("irene-pass1-fidelity-receipt.md present")
        status_value = values.get("status")
        if status_value == "pass":
            evidence.append("receipt status=pass")
        else:
            inconsistent = True
            gaps.append(f"receipt status={status_value!r}")
    else:
        gaps.append("irene-pass1-fidelity-receipt.md missing")
    status = _step_status(
        direct_ok=packet.is_file() and receipt.is_file(),
        inferred_ok=False,
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = "Prompt 5 artifacts and fidelity receipt are present." if status == "PASS" else "Prompt 5 evidence is incomplete or inconsistent."
    return StepReport("5", STANDARD_STEP_HEADINGS[5], status, summary, tuple(evidence), tuple(gaps))


def _check_step_5b(bundle_dir: Path) -> StepReport:
    receipt = bundle_dir / "g1.5-cluster-gate-receipt.json"
    if receipt.is_file():
        payload = _read_json(receipt) or {}
        status = "PASS" if payload.get("status") == "pass" else "FAIL"
        evidence = ("g1.5-cluster-gate-receipt.json present",)
        gaps = () if status == "PASS" else ("gate status != pass",)
    else:
        status = "MISSING"
        evidence = ()
        gaps = ("g1.5-cluster-gate-receipt.json missing",)
    summary = "G1.5 cluster gate receipt is present and passing." if status == "PASS" else "G1.5 cluster gate evidence is incomplete or failing."
    return StepReport("5B", CLUSTER_GATE_STEP_HEADING, status, summary, evidence, gaps)


def _check_step_6(bundle_dir: Path, *, double_dispatch: bool) -> StepReport:
    required = (
        "g2-slide-brief.md",
        "gary-slide-content.json",
        "gary-fidelity-slides.json",
        "gary-diagram-cards.json",
        "gary-theme-resolution.json",
        "gary-outbound-envelope.yaml",
        "pre-dispatch-package-gary.md",
    )
    evidence = [name for name in required if (bundle_dir / name).exists()]
    gaps = [f"{name} missing" for name in required if not (bundle_dir / name).exists()]
    envelope = _read_text(bundle_dir / "gary-outbound-envelope.yaml") or ""
    inconsistent = False
    if double_dispatch and "dispatch_count: 2" not in envelope:
        inconsistent = True
        gaps.append("gary-outbound-envelope.yaml missing dispatch_count: 2 for double-dispatch run")
    status = _step_status(
        direct_ok=len(evidence) == len(required),
        inferred_ok=False,
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = "Prompt 6 machine artifacts are present." if status == "PASS" else "Prompt 6 artifact set is incomplete or inconsistent."
    return StepReport("6", STANDARD_STEP_HEADINGS[6], status, summary, tuple(evidence), tuple(gaps))


def _check_step_6b(bundle_dir: Path) -> StepReport:
    packet = bundle_dir / "literal-visual-operator-packet.md"
    receipt = bundle_dir / "literal-visual-operator-receipt.md"
    values = _extract_markdown_key_values(receipt)
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False
    if packet.is_file():
        evidence.append("literal-visual-operator-packet.md present")
    else:
        gaps.append("literal-visual-operator-packet.md missing")
    if receipt.is_file():
        evidence.append("literal-visual-operator-receipt.md present")
        decision = values.get("gate_decision")
        if decision in {"unblocked", "proceed"}:
            evidence.append(f"gate_decision={decision}")
        else:
            inconsistent = True
            gaps.append(f"gate_decision={decision!r}")
    else:
        gaps.append("literal-visual-operator-receipt.md missing")
    status = _step_status(
        direct_ok=packet.is_file() and receipt.is_file(),
        inferred_ok=False,
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = "Prompt 6B operator checkpoint is evidenced." if status == "PASS" else "Prompt 6B evidence is incomplete or inconsistent."
    return StepReport("6B", STANDARD_STEP_HEADINGS[7], status, summary, tuple(evidence), tuple(gaps))


def _check_step_7(bundle_dir: Path) -> StepReport:
    dispatch_result = bundle_dir / "gary-dispatch-result.json"
    run_log = bundle_dir / "gary-dispatch-run-log.json"
    validation = bundle_dir / "gary-dispatch-validation-result.json"
    export_dir = bundle_dir / "gamma-export"
    storyboard = bundle_dir / "storyboard" / "storyboard.json"
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False

    for name, path in (
        ("gary-dispatch-result.json", dispatch_result),
        ("gary-dispatch-run-log.json", run_log),
        ("gary-dispatch-validation-result.json", validation),
        ("gamma-export/", export_dir),
        ("storyboard/storyboard.json", storyboard),
    ):
        if path.exists():
            evidence.append(f"{name} present")
        else:
            gaps.append(f"{name} missing")

    if validation.is_file():
        payload = _read_json(validation) or {}
        if payload.get("status") == "pass":
            evidence.append("dispatch validation status=pass")
        else:
            inconsistent = True
            gaps.append(f"dispatch validation status={payload.get('status')!r}")

    status = _step_status(
        direct_ok=dispatch_result.is_file() and run_log.is_file() and validation.is_file(),
        inferred_ok=storyboard.is_file(),
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = {
        "PASS": "Prompt 7 dispatch and validation outputs are evidenced.",
        "PARTIAL": "Dispatch outputs exist, but one or more Prompt 7 receipts are incomplete.",
        "INCONSISTENT": "Prompt 7 has dispatch evidence but a failing validator or inconsistent receipt.",
        "MISSING": "Prompt 7 evidence is missing.",
    }.get(status, "Prompt 7 is only partially evidenced.")
    return StepReport("7", STANDARD_STEP_HEADINGS[8], status, summary, tuple(evidence), tuple(gaps))


def _check_step_7b(bundle_dir: Path, *, double_dispatch: bool) -> StepReport:
    if not double_dispatch:
        return StepReport(
            "7B",
            STANDARD_STEP_HEADINGS[9],
            "SKIPPED",
            "Prompt 7B is skipped because DOUBLE_DISPATCH is false.",
            tuple(),
            tuple(),
        )
    selection = bundle_dir / "variant-selection.json"
    if selection.is_file():
        return StepReport(
            "7B",
            STANDARD_STEP_HEADINGS[9],
            "PASS",
            "Variant selection artifact is present.",
            ("variant-selection.json present",),
            tuple(),
        )
    return StepReport(
        "7B",
        STANDARD_STEP_HEADINGS[9],
        "MISSING",
        "Variant selection artifact missing for a double-dispatch run.",
        tuple(),
        ("variant-selection.json missing",),
    )


def _check_step_7c(bundle_dir: Path, *, double_dispatch: bool) -> StepReport:
    authorized = bundle_dir / "authorized-storyboard.json"
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False

    if authorized.is_file():
        evidence.append("authorized-storyboard.json present")
        slide_ids = _authorized_slide_ids(bundle_dir)
        if slide_ids:
            evidence.append(f"authorized slide count={len(slide_ids)}")
        else:
            inconsistent = True
            gaps.append("authorized-storyboard.json does not expose any authorized slide IDs")
    else:
        gaps.append("authorized-storyboard.json missing")

    if double_dispatch:
        selection = bundle_dir / "variant-selection.json"
        if selection.is_file():
            evidence.append("variant-selection.json present")
        else:
            inconsistent = True
            gaps.append("variant-selection.json missing for double-dispatch winner authorization")

    status = _step_status(
        direct_ok=authorized.is_file(),
        inferred_ok=False,
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = "Winner authorization artifact is present." if status == "PASS" else "Prompt 7C evidence is incomplete or inconsistent."
    return StepReport("7C", MOTION_STEP_HEADINGS[10], status, summary, tuple(evidence), tuple(gaps))


def _check_step_7d(bundle_dir: Path, *, motion_enabled: bool) -> StepReport:
    if not motion_enabled:
        return StepReport(
            "7D",
            MOTION_STEP_HEADINGS[11],
            "SKIPPED",
            "Prompt 7D is skipped because MOTION_ENABLED is false.",
            tuple(),
            tuple(),
        )

    designations = bundle_dir / "motion-designations.json"
    plan = bundle_dir / "motion_plan.yaml"
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False

    if designations.is_file():
        evidence.append("motion-designations.json present")
    else:
        gaps.append("motion-designations.json missing")
    rows = _motion_rows(bundle_dir)
    if plan.is_file():
        evidence.append("motion_plan.yaml present")
        if rows:
            evidence.append(f"motion plan slide count={len(rows)}")
        else:
            inconsistent = True
            gaps.append("motion_plan.yaml contains no slide rows")
    else:
        gaps.append("motion_plan.yaml missing")

    authorized_ids = _authorized_slide_ids(bundle_dir)
    if authorized_ids and rows:
        row_ids = {row.get('slide_id') for row in rows if isinstance(row.get('slide_id'), str)}
        missing = [slide_id for slide_id in authorized_ids if slide_id not in row_ids]
        if missing:
            inconsistent = True
            gaps.append(f"motion_plan.yaml missing authorized slide coverage for {len(missing)} slides")

    status = _step_status(
        direct_ok=designations.is_file() and plan.is_file(),
        inferred_ok=False,
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = "Motion designation artifacts are present." if status == "PASS" else "Prompt 7D evidence is incomplete or inconsistent."
    return StepReport("7D", MOTION_STEP_HEADINGS[11], status, summary, tuple(evidence), tuple(gaps))


def _check_step_7e(bundle_dir: Path, *, motion_enabled: bool) -> StepReport:
    if not motion_enabled:
        return StepReport(
            "7E",
            MOTION_STEP_HEADINGS[12],
            "SKIPPED",
            "Prompt 7E is skipped because MOTION_ENABLED is false.",
            tuple(),
            tuple(),
        )

    rows = _motion_rows(bundle_dir)
    progress_receipts = sorted(bundle_dir.glob("motion-generation-*.progress.json"))
    terminal_receipts = sorted((bundle_dir / "motion").glob("motion-generation-*.json"))
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False

    if progress_receipts:
        evidence.append(f"motion progress receipts={len(progress_receipts)}")
    if terminal_receipts:
        evidence.append(f"motion terminal receipts={len(terminal_receipts)}")

    non_static = [row for row in rows if row.get("motion_type") in {"video", "animation"}]
    unresolved = [
        row.get("slide_id")
        for row in non_static
        if not isinstance(row.get("motion_asset_path"), str) or not str(row.get("motion_asset_path")).strip()
    ]
    if non_static:
        evidence.append(f"non-static rows={len(non_static)}")
    if unresolved:
        inconsistent = True
        gaps.append(f"non-static rows without concrete assets={len(unresolved)}")
    elif non_static:
        evidence.append("all non-static rows have concrete asset paths")

    status = _step_status(
        direct_ok=bool(rows) and not unresolved,
        inferred_ok=False,
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = "Motion generation/import state is evidenced." if status == "PASS" else "Prompt 7E evidence is incomplete or inconsistent."
    return StepReport("7E", MOTION_STEP_HEADINGS[12], status, summary, tuple(evidence), tuple(gaps))


def _check_step_7f(bundle_dir: Path, *, motion_enabled: bool) -> StepReport:
    if not motion_enabled:
        return StepReport(
            "7F",
            MOTION_STEP_HEADINGS[13],
            "SKIPPED",
            "Prompt 7F is skipped because MOTION_ENABLED is false.",
            tuple(),
            tuple(),
        )

    rows = _motion_rows(bundle_dir)
    receipt = bundle_dir / "motion-gate-receipt.json"
    evidence: list[str] = []
    gaps: list[str] = []
    inconsistent = False

    if receipt.is_file():
        evidence.append("motion-gate-receipt.json present")
        payload = _read_json(receipt) or {}
        decision = payload.get("decision")
        if decision == "go":
            evidence.append("motion gate decision=go")
        else:
            inconsistent = True
            gaps.append(f"motion gate decision={decision!r}")
    else:
        gaps.append("motion-gate-receipt.json missing")

    non_static = [row for row in rows if row.get("motion_type") in {"video", "animation"}]
    non_approved = [
        row.get("slide_id")
        for row in non_static
        if row.get("motion_status") != "approved"
    ]
    if non_static:
        evidence.append(f"approved non-static targets={len(non_static)}")
    if non_approved:
        inconsistent = True
        gaps.append(f"non-static rows not approved={len(non_approved)}")

    status = _step_status(
        direct_ok=receipt.is_file() and not non_approved,
        inferred_ok=False,
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = "Motion Gate is cleanly closed." if status == "PASS" else "Prompt 7F evidence is incomplete or inconsistent."
    return StepReport("7F", MOTION_STEP_HEADINGS[13], status, summary, tuple(evidence), tuple(gaps))


def _check_step_8(bundle_dir: Path, *, motion_enabled: bool) -> StepReport:
    required = ("pass2-envelope.json", "narration-script.md", "segment-manifest.yaml", "perception-artifacts.json")
    evidence = [name for name in required if (bundle_dir / name).exists()]
    gaps = [f"{name} missing" for name in required if not (bundle_dir / name).exists()]
    inconsistent = False
    direct_ok = len(gaps) == 0

    if (bundle_dir / "pass2-prep-receipt.json").is_file():
        evidence.append("pass2-prep-receipt.json present")

    if motion_enabled:
        envelope = _read_json(bundle_dir / "pass2-envelope.json") or {}
        motion_artifacts = envelope.get("motion_perception_artifacts")
        non_static_rows = [row for row in _motion_rows(bundle_dir) if row.get("motion_type") in {"video", "animation"}]
        motion_artifact_count: int | None = None
        if isinstance(motion_artifacts, dict):
            motion_artifact_count = len(motion_artifacts)
        elif isinstance(motion_artifacts, list):
            motion_artifact_count = len(motion_artifacts)

        if motion_artifact_count is not None and (motion_artifact_count > 0 or not non_static_rows):
            evidence.append(f"motion_perception_artifacts={motion_artifact_count}")
        else:
            inconsistent = True
            gaps.append("pass2-envelope.json missing motion_perception_artifacts for motion-enabled run")

    status = _step_status(
        direct_ok=direct_ok,
        inferred_ok=False,
        inconsistent=inconsistent,
        gaps=gaps,
    )
    summary = "Prompt 8 outputs are present." if status == "PASS" else "Prompt 8 outputs are not fully evidenced in this bundle."
    heading = MOTION_STEP_HEADINGS[14] if motion_enabled else STANDARD_STEP_HEADINGS[10]
    return StepReport("8", heading, status, summary, tuple(evidence), tuple(gaps))


def build_step_reports(context: HarnessContext) -> list[StepReport]:
    bundle_dir = context.bundle_dir
    reports = [
        _check_step_1(bundle_dir),
        _check_step_2(bundle_dir),
        _check_step_2a(bundle_dir),
        _check_step_3(bundle_dir),
        _check_step_4(bundle_dir),
        _check_step_5(bundle_dir),
        _check_step_6(bundle_dir, double_dispatch=context.double_dispatch),
        _check_step_6b(bundle_dir),
        _check_step_7(bundle_dir),
        _check_step_7b(bundle_dir, double_dispatch=context.double_dispatch),
    ]
    if context.cluster_density not in (None, "none"):
        reports.insert(5, _check_step_5b(bundle_dir))
    if context.motion_enabled:
        reports.extend(
            [
                _check_step_7c(bundle_dir, double_dispatch=context.double_dispatch),
                _check_step_7d(bundle_dir, motion_enabled=context.motion_enabled),
                _check_step_7e(bundle_dir, motion_enabled=context.motion_enabled),
                _check_step_7f(bundle_dir, motion_enabled=context.motion_enabled),
            ]
        )
    reports.append(_check_step_8(bundle_dir, motion_enabled=context.motion_enabled))
    headings = _step_headings(context)
    heading_by_step = {report.step: headings[index] for index, report in enumerate(reports) if index < len(headings)}
    return [replace(report, heading=heading_by_step.get(report.step, report.heading)) for report in reports]


def build_consistency_findings(context: HarnessContext) -> list[str]:
    artifacts = (
        "preflight-results.json",
        "operator-directives.md",
        "ingestion-quality-gate-receipt.md",
        "irene-pass1-fidelity-receipt.md",
        "literal-visual-operator-receipt.md",
        "gary-dispatch-validation-result.json",
        "gary-dispatch-result.json",
        "motion-gate-receipt.json",
        "pass2-prep-receipt.json",
        "pass2-envelope.json",
    )
    findings: list[str] = []
    for relative in artifacts:
        path = context.bundle_dir / relative
        artifact_run_id = _artifact_run_id(path)
        if artifact_run_id is None:
            continue
        if artifact_run_id != context.run_id:
            findings.append(
                f"{relative} run_id={artifact_run_id} does not match canonical run_id={context.run_id}"
            )
    return findings


def render_transcript(*, launcher_text: str, step_sections: dict[str, str], context: HarnessContext) -> str:
    prompt_pack_path = _prompt_pack_path(context)
    step_headings = _step_headings(context)
    lines = [
        "# Simulated Marcus Prompt Harness",
        "",
        f"This is a deterministic operator-side transcript template for `{prompt_pack_path.as_posix()}`.",
        "Filled values come from bundle evidence when available and plausible fallbacks otherwise.",
        "",
        "## Session Launcher",
        "",
        "### User",
        "",
        "```md",
        launcher_text.strip(),
        "```",
    ]

    directive_reply = "No operator directives - process all source content at default authority levels."
    operator_directives_text = _read_text(context.bundle_dir / "operator-directives.md")
    if operator_directives_text:
        focus_lines = [line for line in operator_directives_text.splitlines() if line.startswith("- ")]
        if focus_lines:
            directive_reply = "\n".join(focus_lines[:4])

    approvals = {
        "1) Activation + Preflight Contract Gate": "GO.",
        "2) Source Authority Map Before Ingestion": "Approved. Proceed with ingestion.",
        "2A) Operator Directives (Custom Source Instructions)": directive_reply,
        "5) Irene Pass 1 Structure + Gate 1 Fidelity": "Gate 1 approved. Proceed to Prompt 6.",
        "6B) Literal-Visual Operator Build + Confirmation (Mandatory Before Dispatch)": "All required literal-visual assets are operator-ready. Proceed to Prompt 7.",
        "6B) Literal-Visual Operator Build + Confirmation": "All required literal-visual assets are operator-ready. Proceed to Prompt 7.",
        "7) Dispatch + Export + Sort Verification (Single Operation)": (
            "Gate 2 approved. Proceed to Prompt 8."
            if not context.double_dispatch
            else "Gate 2 approved. Proceed to Prompt 7B."
        ),
        "7) Gary Dispatch + Export + Sort Verification": (
            "Dispatch and Storyboard A review are complete. Proceed to Prompt 7C."
            if not context.double_dispatch
            else "Dispatch is complete. Proceed to Prompt 7B."
        ),
        "7B) Variant Selection Gate (Double-Dispatch Only)": (
            "Variant selections recorded. Proceed to Prompt 7C."
            if context.motion_enabled
            else "Variant selections recorded. Proceed to Prompt 8."
        ),
        "7C) Storyboard A + Gate 2 Approval + Winner Authorization": (
            "Gate 2 approved. Winner deck authorized. Proceed to Prompt 7D."
            if context.motion_enabled
            else "Gate 2 approved. Winner deck authorized."
        ),
        "7D) Gate 2M Motion Designation": "Motion designation approved. Proceed to Prompt 7E.",
        "7F) Motion Gate": "Motion Gate closed cleanly. Proceed to Prompt 8.",
    }

    for heading in step_headings:
        section = step_sections.get(heading)
        if section is None:
            continue
        if heading.startswith("7B") and not context.double_dispatch:
            continue
        lines.extend(
            [
                "",
                f"## {heading}",
                "",
                "### User To Marcus",
                "",
                "```md",
                _replace_placeholders(section, context).strip(),
                "```",
            ]
        )
        reply = approvals.get(heading)
        if reply:
            lines.extend(
                [
                    "",
                    "### Simulated Operator Reply",
                    "",
                    "```md",
                    reply,
                    "```",
                ]
            )
    return "\n".join(lines).strip() + "\n"


def render_quinn_report(
    *,
    context: HarnessContext,
    step_reports: list[StepReport],
    consistency_findings: list[str],
) -> str:
    prompt_pack_path = _prompt_pack_path(context)
    status_counts: dict[str, int] = {}
    for report in step_reports:
        status_counts[report.status] = status_counts.get(report.status, 0) + 1
    overall_status = "PASS"
    if any(report.status in {"MISSING", "INCONSISTENT", "PARTIAL"} for report in step_reports):
        overall_status = "PARTIAL"

    lines = [
        "# Quinn Watcher Report",
        "",
        f"**Prompt pack:** `{prompt_pack_path.as_posix()}`",
        f"**Bundle:** `{context.bundle_path}`",
        f"**Canonical RUN_ID:** `{context.run_id}`",
        f"**Overall watcher status:** `{overall_status}`",
        "",
        "## Resolved Context",
        "",
        "| Field | Value | Source |",
        "| --- | --- | --- |",
    ]
    for field in (
        "run_id",
        "lesson_slug",
        "bundle_path",
        "primary_source_file",
        "optional_context_assets",
        "theme_selection",
        "theme_paramset_key",
        "execution_mode",
        "quality_preset",
        "double_dispatch",
        "motion_enabled",
        "experience_profile",
    ):
        value: Any = getattr(context, field)
        if isinstance(value, tuple):
            value = ", ".join(value) if value else "none"
        lines.append(f"| `{field}` | `{value}` | `{context.field_sources.get(field, 'derived')}` |")

    lines.extend(
        [
            "",
            "## Step Results",
            "",
            "| Step | Status | Summary |",
            "| --- | --- | --- |",
        ]
    )
    for report in step_reports:
        lines.append(f"| `{report.step}` | `{report.status}` | {report.summary} |")

    for report in step_reports:
        if not report.evidence and not report.gaps:
            continue
        lines.extend(
            [
                "",
                f"### Prompt {report.step} - {report.heading}",
                "",
                f"- Status: `{report.status}`",
            ]
        )
        for item in report.evidence:
            lines.append(f"- Evidence: {item}")
        for item in report.gaps:
            lines.append(f"- Gap: {item}")

    lines.extend(["", "## Bundle Consistency Findings", ""])
    if consistency_findings:
        for finding in consistency_findings:
            lines.append(f"- {finding}")
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- PASS: {status_counts.get('PASS', 0)}",
            f"- INFERRED: {status_counts.get('INFERRED', 0)}",
            f"- PARTIAL: {status_counts.get('PARTIAL', 0)}",
            f"- MISSING: {status_counts.get('MISSING', 0)}",
            f"- INCONSISTENT: {status_counts.get('INCONSISTENT', 0)}",
            f"- SKIPPED: {status_counts.get('SKIPPED', 0)}",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def write_harness_outputs(
    *,
    root: Path,
    output_dir: Path,
    context: HarnessContext,
    transcript: str,
    quinn_report: str,
    step_reports: list[StepReport],
    consistency_findings: list[str],
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = output_dir / "simulated-transcript.md"
    quinn_path = output_dir / "quinn-watcher-report.md"
    summary_path = output_dir / "summary.json"

    transcript_path.write_text(transcript, encoding="utf-8")
    quinn_path.write_text(quinn_report, encoding="utf-8")
    summary_payload = {
        "generated_at": _now_utc().isoformat(),
        "prompt_pack": _prompt_pack_path(context).as_posix(),
        "bundle_path": context.bundle_path,
        "context": {
            **asdict(context),
            "bundle_dir": _repo_relative(context.bundle_dir, root),
        },
        "step_reports": [asdict(item) for item in step_reports],
        "consistency_findings": consistency_findings,
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    return {
        "transcript": str(transcript_path),
        "quinn_report": str(quinn_path),
        "summary": str(summary_path),
    }


def build_output_dir(root: Path, base: Path | None = None) -> Path:
    base_dir = base if base is not None else (root / DEFAULT_OUTPUT_DIR)
    stamp = _now_utc().strftime("%Y%m%d-%H%M%S")
    return base_dir / f"run-{stamp}"


def run_harness(
    *,
    root: Path | None = None,
    bundle_dir: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    repo_root = root or project_root()
    context = infer_context(root=repo_root, bundle_dir=bundle_dir)
    sections = _extract_sections(repo_root / _prompt_pack_path(context))
    launcher_text = _read_text(repo_root / SESSION_LAUNCHER) or ""
    transcript = render_transcript(launcher_text=launcher_text, step_sections=sections, context=context)
    step_reports = build_step_reports(context)
    consistency_findings = build_consistency_findings(context)
    quinn_report = render_quinn_report(
        context=context,
        step_reports=step_reports,
        consistency_findings=consistency_findings,
    )
    target_base = output_dir
    if target_base is None:
        target_base = repo_root / (MOTION_OUTPUT_DIR if context.motion_enabled else DEFAULT_OUTPUT_DIR)
    target_dir = build_output_dir(repo_root, target_base)
    files = write_harness_outputs(
        root=repo_root,
        output_dir=target_dir,
        context=context,
        transcript=transcript,
        quinn_report=quinn_report,
        step_reports=step_reports,
        consistency_findings=consistency_findings,
    )
    return {
        "output_dir": str(target_dir),
        "files": files,
        "context": context,
        "step_reports": step_reports,
        "consistency_findings": consistency_findings,
    }


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a Marcus prompt harness and Quinn watcher report.")
    parser.add_argument(
        "--bundle-dir",
        type=Path,
        help="Bundle directory to audit. Defaults to the newest tracked source bundle when available.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Optional explicit output directory root. A timestamped run directory is created beneath it.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    result = run_harness(bundle_dir=args.bundle_dir, output_dir=args.output_dir)
    print(f"Wrote prompt harness artifacts to {result['output_dir']}")
    print(f"Transcript: {result['files']['transcript']}")
    print(f"Quinn report: {result['files']['quinn_report']}")
    print(f"Summary JSON: {result['files']['summary']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
