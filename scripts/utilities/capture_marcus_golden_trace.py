#!/usr/bin/env python3
"""
Marcus Golden-Trace Baseline Capture — Story 30-1 Pre-Work

Captures pre-refactor Marcus envelope I/O on the trial corpus as committed
fixtures. Required by R1 ruling amendment 12 (Lesson Planner MVP) / Murat RED
binding PDG before Story 30-1 (Marcus-duality split) opens.

Plan authority: ``_bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md``.

--------------------------------------------------------------------------------
HOW THIS SCRIPT EXECUTES
--------------------------------------------------------------------------------

1. Run this script with a single named 7-page SME source file (§6-A1 of
   ``_bmad-output/planning-artifacts/lesson-planner-mvp-plan.md`` — named SME
   input floor). Commit that source file under ``tests/fixtures/trial_corpus/``
   first.

2. The script runs Marcus's current (pre-30-1) pipeline through:
     - Step 01 (ingestion envelope)
     - Step 02 (source-quality envelope)
     - Step 03 (audience-profile envelope)
     - Step 04 (ingestion quality gate envelope)
     - Step 04 → 05 pre-packet handoff envelope

3. For each emitted envelope, applies the four locked normalization rules in
   order (timestamps → UUIDs → SHA-256 → repo-absolute paths), then writes one
   JSON file per envelope to the output fixture directory.

4. Writes a ``golden-trace-manifest.yaml`` manifest with source SHA-256, capture
   timestamp, module versions, and repo commit SHA.

5. 30-1's post-refactor test will re-run this SAME script against the
   refactored Marcus and diff against the committed fixtures. Script + fixtures
   commit together in one PR before 30-1 opens.

--------------------------------------------------------------------------------
NORMALIZATION DISCIPLINE
--------------------------------------------------------------------------------

Four locked rules (R1 amendment 12; no other normalization permitted):

1. Timestamps — ISO-8601 with optional fractional seconds and tz → ``{{TIMESTAMP}}``
2. UUIDs — standard UUID4 shape → ``{{UUID4}}``
3. SHA-256 digests — 64 hex chars → ``{{SHA256}}``
4. Absolute path prefixes containing the repo root → repo-relative

Critical: normalization is applied symmetrically to pre- and post-refactor
output. Never apply normalization to only one side.

--------------------------------------------------------------------------------
PIPELINE INTEGRATION — OWNED BY THE CURSOR-SIDE CAPTURE AGENT
--------------------------------------------------------------------------------

The ``_run_marcus_pipeline()`` function below is a stub. The Cursor-side agent
running this capture on ``dev/30-1-baseline-capture`` is responsible for
wiring in the real Marcus pipeline calls, which are currently entangled across
``scripts/utilities/prepare-irene-packet.py`` and the Marcus skill invocations
Marcus runs via ``bmad-agent-marcus``. See the TODO markers in
``_run_marcus_pipeline()`` for the five envelope capture points.

This stub is deliberate: authoring the real pipeline wiring requires Marcus
module knowledge that is cleaner to resolve from a Cursor/Claude-Code session
running under real Marcus (which can inspect his sanctum and run the real 01-04
sequence). The stub here locks the I/O shape, normalization logic, manifest
format, and CLI contract so the capture agent has only the pipeline glue to
write.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from scripts.utilities.file_helpers import project_root

# ============================================================================
# NORMALIZATION RULES (LOCKED — R1 amendment 12; do not add more)
# ============================================================================

# Rule 1: ISO-8601 timestamps with optional fractional seconds and timezone.
TIMESTAMP_RE = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})"
)
TIMESTAMP_TOKEN = "{{TIMESTAMP}}"

# Rule 2: Standard UUID4 regex (8-4-4-4-12 hex).
UUID4_RE = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}"
)
UUID4_TOKEN = "{{UUID4}}"

# Rule 3: SHA-256 digests (64 hex chars).
SHA256_RE = re.compile(r"\b[a-f0-9]{64}\b")
SHA256_TOKEN = "{{SHA256}}"


def normalize_trace(payload: str, repo_root: Path) -> str:
    """Apply the four locked normalization rules to a serialized envelope.

    Rules are applied in order: timestamps → UUIDs → SHA-256 → repo-absolute
    paths. Any other string substitution is OUT OF SCOPE per R1 amendment 12 —
    a diff in any un-normalized field is a real behavioral diff.

    Args:
        payload: JSON-serialized envelope as a string.
        repo_root: Absolute path of the repository root (for rule 4 stripping).

    Returns:
        Normalized payload string suitable for byte-identical comparison.
    """
    # Rule 1: Timestamps
    payload = TIMESTAMP_RE.sub(TIMESTAMP_TOKEN, payload)

    # Rule 2: UUID4
    payload = UUID4_RE.sub(UUID4_TOKEN, payload)

    # Rule 3: SHA-256
    payload = SHA256_RE.sub(SHA256_TOKEN, payload)

    # Rule 4: Repo-absolute paths → repo-relative.
    # Match both POSIX and Windows path variants for cross-platform capture parity.
    repo_root_str = str(repo_root)
    payload = payload.replace(repo_root_str, "{{REPO_ROOT}}")
    # Also the Windows backslash variant (escaped in JSON as \\).
    repo_root_windows = repo_root_str.replace("/", "\\\\")
    if repo_root_windows != repo_root_str:
        payload = payload.replace(repo_root_windows, "{{REPO_ROOT}}")

    return payload


# ============================================================================
# CAPTURE POINTS — the five envelopes 30-1 must preserve byte-identical
# ============================================================================

CAPTURE_POINTS: list[dict[str, str]] = [
    {
        "step": "01",
        "name": "ingestion",
        "filename": "step-01-ingestion-envelope.json",
        "description": "Ingestion envelope emitted after source intake.",
    },
    {
        "step": "02",
        "name": "source-quality",
        "filename": "step-02-source-quality-envelope.json",
        "description": "Source-quality envelope with quality-band classification.",
    },
    {
        "step": "03",
        "name": "audience-profile",
        "filename": "step-03-audience-profile-envelope.json",
        "description": "Audience-profile envelope (Maya-facing audience targeting).",
    },
    {
        "step": "04",
        "name": "ingestion-quality-gate",
        "filename": "step-04-ingestion-quality-gate-envelope.json",
        "description": "Ingestion quality gate envelope (pass/fail with evidence).",
    },
    {
        "step": "04-05",
        "name": "pre-packet-handoff",
        "filename": "step-04-05-pre-packet-handoff-envelope.json",
        "description": "Pre-packet handoff envelope (Marcus → Irene at 4A entry).",
    },
]


# ============================================================================
# PIPELINE STUB — to be wired by the Cursor-side capture agent
# ============================================================================


def _run_marcus_pipeline(source: Path) -> list[dict[str, Any]]:
    """Run the current (pre-30-1) Marcus pipeline and collect envelopes.

    TODO (Cursor-side capture agent on dev/30-1-baseline-capture):
    Wire in the real Marcus pipeline calls to produce a list of envelope dicts
    in the same order as CAPTURE_POINTS. Each dict must:

    1. Serialize cleanly via json.dumps (no datetime / UUID / Path objects —
       coerce to strings before returning).
    2. Include an ``_internal_emitter`` audit field naming which internal
       Marcus identity (``marcus-intake`` vs ``marcus-orchestrator``) emits
       the envelope. This is a DEBUG AIDE ONLY — the field is stripped from
       the byte-identical comparison post-30-1, but preserved in the fixture
       JSON for human diff inspection.
    3. Match the CAPTURE_POINTS order exactly — step 01, 02, 03, 04, 04-05.

    Marcus pipeline entry points to consult (pre-30-1):
      - ``scripts/utilities/prepare-irene-packet.py`` (step 04 → 05 handoff)
      - Marcus sanctum invocations for steps 01-04 (see the Marcus BMM skill)
      - ``_bmad/memory/marcus-sidecar/`` for persisted envelope shapes
      - ``marcus/`` package (currently just ``marcus/lesson_plan/`` post-31-1;
        Marcus's 01-04 pipeline code is distributed across the skill layer)

    Args:
        source: Path to the trial corpus SME source file.

    Returns:
        List of envelope dicts in CAPTURE_POINTS order. MUST have exactly
        ``len(CAPTURE_POINTS)`` entries.
    """
    raise NotImplementedError(
        "Marcus pipeline wiring is owned by the Cursor-side capture agent on "
        "dev/30-1-baseline-capture. See the TODO in _run_marcus_pipeline for "
        "the five envelope capture points and required output shape."
    )


# ============================================================================
# MANIFEST + FIXTURE WRITING
# ============================================================================


def _compute_source_sha256(source: Path) -> str:
    """Compute SHA-256 of the trial corpus source file."""
    hasher = hashlib.sha256()
    with source.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _get_repo_commit_sha(repo_root: Path) -> str:
    """Return current HEAD commit SHA, or '{{UNKNOWN_COMMIT}}' if unavailable."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "{{UNKNOWN_COMMIT}}"


def _get_module_versions() -> dict[str, str]:
    """Collect versions of modules that affect envelope emission.

    Pinned to the modules whose drift would plausibly cause envelope diffs at
    post-refactor test time. Update this list if new Marcus-adjacent modules
    enter the emission path.
    """
    versions: dict[str, str] = {}
    try:
        import pydantic

        versions["pydantic"] = pydantic.VERSION
    except ImportError:  # pragma: no cover — pydantic is a hard dep
        versions["pydantic"] = "not-installed"
    versions["python"] = sys.version.split()[0]
    return versions


def _write_manifest(
    output_dir: Path,
    source: Path,
    source_sha256: str,
    repo_root: Path,
) -> None:
    """Write ``golden-trace-manifest.yaml`` recording capture provenance."""
    manifest_lines = [
        "# Marcus Golden-Trace Baseline — Capture Manifest",
        "# Story 30-1 pre-work (R1 amendment 12 / Murat RED binding PDG)",
        "# Authored 2026-04-18; see _bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md",
        "",
        f"captured_at: {datetime.now(UTC).isoformat()}",
        f"source_path: {source.relative_to(repo_root).as_posix()}",
        f"source_sha256: {source_sha256}",
        f"repo_commit_sha: {_get_repo_commit_sha(repo_root)}",
        "",
        "module_versions:",
    ]
    for module, version in _get_module_versions().items():
        manifest_lines.append(f"  {module}: {version}")
    manifest_lines.append("")
    manifest_lines.append("capture_points:")
    for point in CAPTURE_POINTS:
        manifest_lines.append(f"  - step: \"{point['step']}\"")
        manifest_lines.append(f"    name: {point['name']}")
        manifest_lines.append(f"    filename: {point['filename']}")
        manifest_lines.append(f"    description: {point['description']}")
    manifest_lines.append("")
    manifest_lines.append("normalization_rules_applied:")
    manifest_lines.append("  - timestamps → {{TIMESTAMP}}")
    manifest_lines.append("  - uuid4 → {{UUID4}}")
    manifest_lines.append("  - sha256 → {{SHA256}}")
    manifest_lines.append("  - repo_root_abs → {{REPO_ROOT}}")
    manifest_lines.append("")

    (output_dir / "golden-trace-manifest.yaml").write_text(
        "\n".join(manifest_lines), encoding="utf-8"
    )


def _write_envelopes(
    output_dir: Path, envelopes: list[dict[str, Any]], repo_root: Path
) -> None:
    """Serialize, normalize, and write each captured envelope to disk."""
    if len(envelopes) != len(CAPTURE_POINTS):
        raise ValueError(
            f"Expected {len(CAPTURE_POINTS)} envelopes "
            f"(one per capture point), got {len(envelopes)}."
        )
    for envelope, point in zip(envelopes, CAPTURE_POINTS, strict=True):
        raw = json.dumps(envelope, indent=2, sort_keys=True, ensure_ascii=False)
        normalized = normalize_trace(raw, repo_root)
        (output_dir / point["filename"]).write_text(
            normalized + "\n", encoding="utf-8"
        )


# ============================================================================
# CLI
# ============================================================================


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Capture pre-refactor Marcus envelope I/O as the 30-1 golden-trace "
            "baseline fixture. R1 amendment 12 (Lesson Planner MVP) / Murat "
            "RED binding PDG. See "
            "_bmad-output/specs/30-1-golden-trace-baseline-capture-plan.md for "
            "the full plan."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help=(
            "Path to the trial corpus SME source file (§6-A1 named-SME-input "
            "floor). Should live under tests/fixtures/trial_corpus/."
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help=(
            "Output fixture directory. Canonical path: "
            "tests/fixtures/golden_trace/marcus_pre_30-1/"
        ),
    )
    args = parser.parse_args(argv)

    repo_root = project_root()

    # Validate source path.
    source: Path = args.source.resolve()
    if not source.is_file():
        print(
            f"ERROR: --source must point to an existing file; got {source}",
            file=sys.stderr,
        )
        return 2
    try:
        source.relative_to(repo_root)
    except ValueError:
        print(
            "ERROR: --source must be inside the repository (so the committed "
            f"fixture path is portable); got {source}",
            file=sys.stderr,
        )
        return 2

    # Prepare output directory.
    output_dir: Path = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Compute source SHA-256 up front — manifest and reproducibility anchor.
    source_sha256 = _compute_source_sha256(source)
    print(f"Source SHA-256: {source_sha256}")

    # Run the pipeline. The pipeline stub raises NotImplementedError; the
    # Cursor-side capture agent on dev/30-1-baseline-capture is responsible
    # for wiring in the five envelope emission points.
    envelopes = _run_marcus_pipeline(source)

    # Write normalized envelopes + manifest.
    _write_envelopes(output_dir, envelopes, repo_root)
    _write_manifest(output_dir, source, source_sha256, repo_root)

    print(f"Wrote {len(envelopes)} envelopes + manifest to {output_dir}")
    print(
        "Sanity: re-run this script on the same source; output must be "
        "identical modulo normalization. If it drifts, a capture-side "
        "non-determinism exists and must be fixed before committing."
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
