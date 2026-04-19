"""Cora pre-closure hook with manifest-driven block-mode classification."""

from __future__ import annotations

import fnmatch
import re
import subprocess
import sys
from typing import Literal

from pydantic import BaseModel, ConfigDict

from scripts.utilities.file_helpers import project_root
from scripts.utilities.pipeline_manifest import load_manifest


class PreClosureResult(BaseModel):
    """Structured outcome for pre-closure gate checks."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    story_id: str
    classification: Literal["warn", "block"]
    l1_exit_code: int | None
    l1_trace_path: str | None
    permit_closure: bool
    operator_message: str


PreClosureResult.model_rebuild()


def _normalize(path: str) -> str:
    return path.replace("\\", "/")


def classify_change_window(
    diff_paths: list[str],
    manifest_path: str = "state/config/pipeline-manifest.yaml",
) -> Literal["warn", "block"]:
    """Classify a diff window using manifest-declared trigger paths."""
    manifest = load_manifest(project_root() / manifest_path)
    for changed_path in diff_paths:
        normalized = _normalize(changed_path)
        for pattern in manifest.block_mode_trigger_paths:
            if fnmatch.fnmatch(normalized, pattern):
                return "block"
    return "warn"


def _extract_trace_path(output: str) -> str | None:
    match = re.search(r"trace=([^\s]+)", output)
    return match.group(1) if match else None


def run_preclosure_check(
    story_id: str,
    diff_paths: list[str],
    *,
    skip_l1: bool = False,
) -> PreClosureResult:
    """Run pre-closure check and enforce block-mode semantics."""
    classification = classify_change_window(diff_paths)
    if classification == "warn":
        return PreClosureResult(
            story_id=story_id,
            classification="warn",
            l1_exit_code=None,
            l1_trace_path=None,
            permit_closure=True,
            operator_message=(
                "Pre-closure check ran in warn mode; closure remains "
                "operator-controlled."
            ),
        )

    if skip_l1:
        return PreClosureResult(
            story_id=story_id,
            classification="block",
            l1_exit_code=None,
            l1_trace_path=None,
            permit_closure=False,
            operator_message=(
                "Story close-out blocked: lockstep check is required for "
                "workflow-stage changes."
            ),
        )

    result = subprocess.run(
        [sys.executable, "-m", "scripts.utilities.check_pipeline_manifest_lockstep"],
        capture_output=True,
        text=True,
        check=False,
        cwd=project_root(),
    )
    combined_output = "\n".join(filter(None, [result.stdout, result.stderr]))
    trace_path = _extract_trace_path(combined_output)
    if result.returncode == 0:
        return PreClosureResult(
            story_id=story_id,
            classification="block",
            l1_exit_code=0,
            l1_trace_path=trace_path,
            permit_closure=True,
            operator_message=(
                "Workflow-stage change validated by lockstep check; closure "
                "may proceed."
            ),
        )

    return PreClosureResult(
        story_id=story_id,
        classification="block",
        l1_exit_code=result.returncode,
        l1_trace_path=trace_path,
        permit_closure=False,
        operator_message=(
            "Story close-out blocked: lockstep check flagged divergence. "
            f"See {trace_path or 'reports/dev-coherence/<timestamp>/'} for the specific finding."
        ),
    )


__all__ = ("classify_change_window", "run_preclosure_check", "PreClosureResult")
