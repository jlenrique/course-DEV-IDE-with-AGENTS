"""Canonical structural walk generator.

Builds a workflow-specific readiness report for the narrated production
pipelines. The default walk is deterministic and local, but it uses
real checks wherever practical: contract validation, YAML parsing,
Python import sanity, and optional command probes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from scripts.utilities.file_helpers import project_root
from scripts.utilities.skill_module_loader import (
    load_module_from_path,
    load_sensory_bridge_utils,
    load_source_wrangler_operations,
)
from scripts.validate_fidelity_contracts import validate_contract


VALID_WORKFLOWS = ("standard", "motion")
MANIFEST_DIR = Path("state/config/structural-walk")
VALID_DRY_RUN_KINDS = ("manifest", "sequence", "sequence_docs", "contracts", "aggregate", "documents")


@dataclass(frozen=True)
class AssetSpec:
    asset_type: str
    path: str
    contract: bool = False
    redirect_contains: str | None = None
    check_mode: str = "auto"


@dataclass(frozen=True)
class GateSpec:
    gate: str
    name: str
    producing_agent: str
    source_of_truth: str
    contract_path: str
    assets: tuple[AssetSpec, ...]


@dataclass(frozen=True)
class CrossCuttingSpec:
    component: str
    path: str
    redirect_contains: str | None = None
    check_mode: str = "auto"


@dataclass(frozen=True)
class AntiDriftSpec:
    name: str
    path: str
    needles: tuple[str, ...]
    ordered: bool = False


@dataclass(frozen=True)
class LiveProbeSpec:
    name: str
    command: tuple[str, ...]


@dataclass(frozen=True)
class WorkflowSpec:
    key: str
    title: str
    walk_type: str
    gate_specs: tuple[GateSpec, ...]
    cross_cutting_specs: tuple[CrossCuttingSpec, ...]
    anti_drift_specs: tuple[AntiDriftSpec, ...]
    dry_run_steps: tuple["DryRunStep", ...] = ()
    sequence_doc_parity_specs: tuple["SequenceDocParitySpec", ...] = ()


@dataclass(frozen=True)
class DryRunStep:
    key: str
    label: str
    scope: str
    input_ref: str
    kind: str


@dataclass(frozen=True)
class SequenceDocParitySpec:
    stage: str
    path: str
    needle: str


COMMON_GATE_SPECS: tuple[GateSpec, ...] = (
    GateSpec(
        gate="G0",
        name="Source Bundle",
        producing_agent="source-wrangler",
        source_of_truth="Original SME materials",
        contract_path="state/config/fidelity-contracts/g0-source-bundle.yaml",
        assets=(
            AssetSpec("Skill", "skills/source-wrangler/SKILL.md"),
            AssetSpec("Script", "skills/source-wrangler/scripts/source_wrangler_operations.py"),
            AssetSpec("Contract", "state/config/fidelity-contracts/g0-source-bundle.yaml", contract=True),
            AssetSpec("Contract Schema", "state/config/fidelity-contracts/_schema.yaml", check_mode="yaml"),
            AssetSpec("Sensory Bridge", "skills/sensory-bridges/scripts/pdf_to_agent.py"),
        ),
    ),
    GateSpec(
        gate="G1",
        name="Lesson Plan",
        producing_agent="Irene",
        source_of_truth="Source bundle + SME learning intent",
        contract_path="state/config/fidelity-contracts/g1-lesson-plan.yaml",
        assets=(
            AssetSpec("Skill", "skills/bmad-agent-content-creator/SKILL.md"),
            AssetSpec("Template", "skills/bmad-agent-content-creator/references/template-lesson-plan.md"),
            AssetSpec("Config", "state/config/course_context.yaml", check_mode="yaml"),
            AssetSpec("Style Bible", "resources/style-bible/master-style-bible.md"),
            AssetSpec("Contract", "state/config/fidelity-contracts/g1-lesson-plan.yaml", contract=True),
        ),
    ),
    GateSpec(
        gate="G2",
        name="Slide Brief",
        producing_agent="Irene",
        source_of_truth="Lesson plan",
        contract_path="state/config/fidelity-contracts/g2-slide-brief.yaml",
        assets=(
            AssetSpec("Skill", "skills/bmad-agent-content-creator/SKILL.md"),
            AssetSpec("Template", "skills/bmad-agent-content-creator/references/template-slide-brief.md"),
            AssetSpec("Contract", "state/config/fidelity-contracts/g2-slide-brief.yaml", contract=True),
            AssetSpec("Gamma Execution Path", "skills/gamma-api-mastery/scripts/gamma_operations.py"),
        ),
    ),
    GateSpec(
        gate="G3",
        name="Generated Slides",
        producing_agent="Gary",
        source_of_truth="Slide brief",
        contract_path="state/config/fidelity-contracts/g3-generated-slides.yaml",
        assets=(
            AssetSpec("Specialist Skill", "skills/bmad-agent-gamma/SKILL.md"),
            AssetSpec("Execution Skill", "skills/gamma-api-mastery/SKILL.md"),
            AssetSpec("Script", "skills/gamma-api-mastery/scripts/gamma_operations.py"),
            AssetSpec("API Client", "scripts/api_clients/gamma_client.py"),
            AssetSpec("Sensory Bridge", "skills/sensory-bridges/scripts/pptx_to_agent.py"),
            AssetSpec("Sensory Bridge", "skills/sensory-bridges/scripts/png_to_agent.py"),
            AssetSpec("Contract", "state/config/fidelity-contracts/g3-generated-slides.yaml", contract=True),
        ),
    ),
    GateSpec(
        gate="G4",
        name="Narration Script + Segment Manifest",
        producing_agent="Irene (Pass 2)",
        source_of_truth="Lesson plan + approved slide PNGs",
        contract_path="state/config/fidelity-contracts/g4-narration-script.yaml",
        assets=(
            AssetSpec("Skill", "skills/bmad-agent-content-creator/SKILL.md"),
            AssetSpec("Template", "skills/bmad-agent-content-creator/references/template-narration-script.md"),
            AssetSpec("Template", "skills/bmad-agent-content-creator/references/template-segment-manifest.md"),
            AssetSpec("Config", "state/config/narration-grounding-profiles.yaml", check_mode="yaml"),
            AssetSpec("Config", "state/config/narration-script-parameters.yaml", check_mode="yaml"),
            AssetSpec("Sensory Bridge", "skills/sensory-bridges/scripts/png_to_agent.py"),
            AssetSpec("Contract", "state/config/fidelity-contracts/g4-narration-script.yaml", contract=True),
        ),
    ),
    GateSpec(
        gate="G5",
        name="Audio",
        producing_agent="Voice Director",
        source_of_truth="Narration script",
        contract_path="state/config/fidelity-contracts/g5-audio.yaml",
        assets=(
            AssetSpec("Specialist Skill", "skills/bmad-agent-elevenlabs/SKILL.md"),
            AssetSpec("Execution Skill", "skills/elevenlabs-audio/SKILL.md"),
            AssetSpec("Script", "skills/elevenlabs-audio/scripts/elevenlabs_operations.py"),
            AssetSpec("API Client", "scripts/api_clients/elevenlabs_client.py"),
            AssetSpec("Sensory Bridge", "skills/sensory-bridges/scripts/audio_to_agent.py"),
            AssetSpec("Contract", "state/config/fidelity-contracts/g5-audio.yaml", contract=True),
        ),
    ),
    GateSpec(
        gate="G6",
        name="Composition",
        producing_agent="Compositor + Human (Descript)",
        source_of_truth="Segment manifest",
        contract_path="state/config/fidelity-contracts/g6-composition.yaml",
        assets=(
            AssetSpec("Skill", "skills/compositor/SKILL.md"),
            AssetSpec("Script", "skills/compositor/scripts/compositor_operations.py"),
            AssetSpec("Reference", "skills/compositor/references/assembly-guide-format.md"),
            AssetSpec("Reference", "skills/compositor/references/manifest-interpretation.md"),
            AssetSpec("Sensory Bridge", "skills/sensory-bridges/scripts/video_to_agent.py"),
            AssetSpec("Contract", "state/config/fidelity-contracts/g6-composition.yaml", contract=True),
        ),
    ),
)


DEFAULT_LIVE_PROBES: dict[str, LiveProbeSpec] = {
    "contracts-cli": LiveProbeSpec(
        name="contracts-cli",
        command=(sys.executable, "scripts/validate_fidelity_contracts.py"),
    ),
    "heartbeat": LiveProbeSpec(
        name="heartbeat",
        command=("node", "scripts/heartbeat_check.mjs"),
    ),
}

def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc).replace(microsecond=0)


def _normalize_workflow(workflow: str) -> str:
    normalized = workflow.strip().lower()
    if normalized not in VALID_WORKFLOWS:
        raise ValueError(
            f"Unsupported workflow '{workflow}'. Expected one of: {', '.join(VALID_WORKFLOWS)}"
        )
    return normalized


def manifest_path(root: Path, workflow: str) -> Path:
    workflow_key = _normalize_workflow(workflow)
    return root / MANIFEST_DIR / f"{workflow_key}.yaml"


def load_workflow_spec(root: Path, workflow: str) -> WorkflowSpec:
    workflow_key = _normalize_workflow(workflow)
    path = manifest_path(root, workflow_key)
    if not path.exists():
        raise FileNotFoundError(f"Structural-walk manifest not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Structural-walk manifest must be a mapping: {path}")

    if data.get("workflow") != workflow_key:
        raise ValueError(
            f"Structural-walk manifest workflow mismatch in {path}: "
            f"expected '{workflow_key}', got '{data.get('workflow')}'"
        )

    title = data.get("title")
    walk_type = data.get("walk_type")
    cross_cutting_raw = data.get("cross_cutting")
    anti_drift_raw = data.get("anti_drift")
    dry_run_raw = data.get("dry_run")
    sequence_doc_parity_raw = data.get("sequence_doc_parity", [])

    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"Structural-walk manifest missing non-empty title: {path}")
    if not isinstance(walk_type, str) or not walk_type.strip():
        raise ValueError(f"Structural-walk manifest missing non-empty walk_type: {path}")
    if not isinstance(cross_cutting_raw, list):
        raise ValueError(f"Structural-walk manifest cross_cutting must be a list: {path}")
    if not isinstance(anti_drift_raw, list):
        raise ValueError(f"Structural-walk manifest anti_drift must be a list: {path}")
    if not isinstance(sequence_doc_parity_raw, list):
        raise ValueError(f"Structural-walk manifest sequence_doc_parity must be a list: {path}")

    cross_cutting_specs: list[CrossCuttingSpec] = []
    for index, item in enumerate(cross_cutting_raw):
        if not isinstance(item, dict):
            raise ValueError(f"cross_cutting[{index}] must be a mapping in {path}")
        component = item.get("component")
        item_path = item.get("path")
        if not isinstance(component, str) or not component.strip():
            raise ValueError(f"cross_cutting[{index}] missing non-empty component in {path}")
        if not isinstance(item_path, str) or not item_path.strip():
            raise ValueError(f"cross_cutting[{index}] missing non-empty path in {path}")
        redirect_contains = item.get("redirect_contains")
        if redirect_contains is not None and not isinstance(redirect_contains, str):
            raise ValueError(f"cross_cutting[{index}].redirect_contains must be a string in {path}")
        check_mode = item.get("check_mode", "auto")
        if not isinstance(check_mode, str) or not check_mode.strip():
            raise ValueError(f"cross_cutting[{index}].check_mode must be a non-empty string in {path}")
        cross_cutting_specs.append(
            CrossCuttingSpec(
                component=component,
                path=item_path,
                redirect_contains=redirect_contains,
                check_mode=check_mode,
            )
        )

    anti_drift_specs: list[AntiDriftSpec] = []
    for index, item in enumerate(anti_drift_raw):
        if not isinstance(item, dict):
            raise ValueError(f"anti_drift[{index}] must be a mapping in {path}")
        name = item.get("name")
        item_path = item.get("path")
        needles = item.get("needles")
        ordered = item.get("ordered", False)
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"anti_drift[{index}] missing non-empty name in {path}")
        if not isinstance(item_path, str) or not item_path.strip():
            raise ValueError(f"anti_drift[{index}] missing non-empty path in {path}")
        if not isinstance(needles, list) or not needles or not all(
            isinstance(needle, str) and needle for needle in needles
        ):
            raise ValueError(f"anti_drift[{index}].needles must be a non-empty string list in {path}")
        if not isinstance(ordered, bool):
            raise ValueError(f"anti_drift[{index}].ordered must be boolean in {path}")
        anti_drift_specs.append(
            AntiDriftSpec(
                name=name,
                path=item_path,
                needles=tuple(needles),
                ordered=ordered,
            )
        )

    dry_run_steps: list[DryRunStep] = []
    if dry_run_raw is not None:
        if not isinstance(dry_run_raw, dict):
            raise ValueError(f"Structural-walk manifest dry_run must be a mapping: {path}")
        steps_raw = dry_run_raw.get("steps")
        if not isinstance(steps_raw, list) or not steps_raw:
            raise ValueError(f"Structural-walk manifest dry_run.steps must be a non-empty list: {path}")
        for index, item in enumerate(steps_raw):
            if not isinstance(item, dict):
                raise ValueError(f"dry_run.steps[{index}] must be a mapping in {path}")
            key = item.get("key")
            label = item.get("label")
            scope = item.get("scope")
            input_ref = item.get("input")
            kind = item.get("kind")
            if not isinstance(key, str) or not key.strip():
                raise ValueError(f"dry_run.steps[{index}] missing non-empty key in {path}")
            if not isinstance(label, str) or not label.strip():
                raise ValueError(f"dry_run.steps[{index}] missing non-empty label in {path}")
            if not isinstance(scope, str) or not scope.strip():
                raise ValueError(f"dry_run.steps[{index}] missing non-empty scope in {path}")
            if not isinstance(input_ref, str) or not input_ref.strip():
                raise ValueError(f"dry_run.steps[{index}] missing non-empty input in {path}")
            if not isinstance(kind, str) or not kind.strip():
                raise ValueError(f"dry_run.steps[{index}] missing non-empty kind in {path}")
            if kind not in VALID_DRY_RUN_KINDS:
                raise ValueError(
                    "dry_run.steps[{index}].kind must be one of "
                    f"{', '.join(VALID_DRY_RUN_KINDS)} in {path}".format(index=index)
                )
            dry_run_steps.append(
                DryRunStep(
                    key=key,
                    label=label,
                    scope=scope,
                    input_ref=input_ref,
                    kind=kind,
                )
            )

    sequence_doc_parity_specs: list[SequenceDocParitySpec] = []
    for index, item in enumerate(sequence_doc_parity_raw):
        if not isinstance(item, dict):
            raise ValueError(f"sequence_doc_parity[{index}] must be a mapping in {path}")
        stage = item.get("stage")
        item_path = item.get("path")
        needle = item.get("needle")
        if not isinstance(stage, str) or not stage.strip():
            raise ValueError(f"sequence_doc_parity[{index}] missing non-empty stage in {path}")
        if not isinstance(item_path, str) or not item_path.strip():
            raise ValueError(f"sequence_doc_parity[{index}] missing non-empty path in {path}")
        if not isinstance(needle, str) or not needle.strip():
            raise ValueError(f"sequence_doc_parity[{index}] missing non-empty needle in {path}")
        sequence_doc_parity_specs.append(
            SequenceDocParitySpec(stage=stage, path=item_path, needle=needle)
        )

    return WorkflowSpec(
        key=workflow_key,
        title=title,
        walk_type=walk_type,
        gate_specs=COMMON_GATE_SPECS,
        cross_cutting_specs=tuple(cross_cutting_specs),
        anti_drift_specs=tuple(anti_drift_specs),
        dry_run_steps=tuple(dry_run_steps),
        sequence_doc_parity_specs=tuple(sequence_doc_parity_specs),
    )


def load_workflow_specs(root: Path) -> dict[str, WorkflowSpec]:
    return {workflow: load_workflow_spec(root, workflow) for workflow in VALID_WORKFLOWS}


def get_workflow_specs(root: Path | None = None) -> dict[str, WorkflowSpec]:
    return load_workflow_specs(root or project_root())


def _python_importable(root: Path, target: Path) -> list[str]:
    try:
        relative = target.resolve().relative_to(root.resolve())
    except ValueError:
        relative = target

    relative_posix = relative.as_posix()
    if relative_posix == "skills/source-wrangler/scripts/source_wrangler_operations.py":
        try:
            load_source_wrangler_operations(root)
            return []
        except Exception as exc:  # pragma: no cover - exercised through report assertions
            return [f"{type(exc).__name__}: {exc}"]

    if relative_posix.startswith("skills/sensory-bridges/scripts/"):
        module_name = f"skills.sensory_bridges.scripts.{target.stem}"
        try:
            load_sensory_bridge_utils(root)
            load_module_from_path(module_name, target)
            return []
        except Exception as exc:  # pragma: no cover - exercised through report assertions
            return [f"{type(exc).__name__}: {exc}"]

    module_name = f"structural_walk_{hashlib.sha1(str(target).encode('utf-8')).hexdigest()}"
    added_root = False
    try:
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
            added_root = True
        load_module_from_path(module_name, target)
        return []
    except Exception as exc:  # pragma: no cover - exercised through report assertions
        return [f"{type(exc).__name__}: {exc}"]
    finally:
        sys.modules.pop(module_name, None)
        if added_root:
            try:
                sys.path.remove(str(root))
            except ValueError:
                pass


def _yaml_parsable(target: Path) -> list[str]:
    try:
        yaml.safe_load(target.read_text(encoding="utf-8"))
        return []
    except Exception as exc:  # pragma: no cover - exercised through report assertions
        return [f"{type(exc).__name__}: {exc}"]


def _json_parsable(target: Path) -> list[str]:
    try:
        json.loads(target.read_text(encoding="utf-8"))
        return []
    except Exception as exc:  # pragma: no cover - exercised through report assertions
        return [f"{type(exc).__name__}: {exc}"]


def _status_for_asset(root: Path, spec: AssetSpec | CrossCuttingSpec) -> tuple[str, list[str]]:
    target = root / Path(spec.path)
    findings: list[str] = []

    if spec.redirect_contains is not None:
        if not target.exists():
            findings.append(f"Missing redirect placeholder: {spec.path}")
            return "Missing", findings
        text = target.read_text(encoding="utf-8")
        if spec.redirect_contains in text:
            return "Documented redirect", findings
        findings.append(f"Redirect placeholder missing canonical redirect text: {spec.path}")
        return "Invalid redirect", findings

    if not target.exists():
        findings.append(f"Missing required asset: {spec.path}")
        return "Missing", findings

    if isinstance(spec, AssetSpec) and spec.contract:
        errors = validate_contract(target)
        if errors:
            findings.append(f"Invalid contract: {spec.path} ({'; '.join(errors)})")
            return "Invalid", findings
        return "Valid", findings

    if target.is_dir():
        return "Present", findings

    check_mode = spec.check_mode
    if check_mode == "auto":
        suffix = target.suffix.lower()
        if suffix == ".py":
            check_mode = "import_python"
        elif suffix in {".yaml", ".yml"}:
            check_mode = "yaml"
        elif suffix == ".json":
            check_mode = "json"
        else:
            check_mode = "exists"

    if check_mode == "import_python":
        errors = _python_importable(root, target)
        if errors:
            findings.append(f"Import failed: {spec.path} ({'; '.join(errors)})")
            return "Import failed", findings
        return "Importable", findings

    if check_mode == "yaml":
        errors = _yaml_parsable(target)
        if errors:
            findings.append(f"YAML parse failed: {spec.path} ({'; '.join(errors)})")
            return "Invalid YAML", findings
        return "Parsed", findings

    if check_mode == "json":
        errors = _json_parsable(target)
        if errors:
            findings.append(f"JSON parse failed: {spec.path} ({'; '.join(errors)})")
            return "Invalid JSON", findings
        return "Parsed", findings

    return "Present", findings


def _build_gate_result(root: Path, spec: GateSpec) -> dict[str, Any]:
    assets: list[dict[str, str]] = []
    findings: list[str] = []
    for asset in spec.assets:
        status, asset_findings = _status_for_asset(root, asset)
        assets.append({"type": asset.asset_type, "path": asset.path, "status": status})
        findings.extend(asset_findings)
    return {
        "gate": spec.gate,
        "name": spec.name,
        "producing_agent": spec.producing_agent,
        "source_of_truth": spec.source_of_truth,
        "contract_path": spec.contract_path,
        "assets": assets,
        "findings": findings,
    }


def _build_cross_cutting_result(root: Path, specs: tuple[CrossCuttingSpec, ...]) -> dict[str, Any]:
    components: list[dict[str, str]] = []
    findings: list[str] = []
    for spec in specs:
        status, component_findings = _status_for_asset(root, spec)
        components.append({"component": spec.component, "path": spec.path, "status": status})
        findings.extend(component_findings)
    return {"components": components, "findings": findings}


def _build_anti_drift_result(root: Path, specs: tuple[AntiDriftSpec, ...]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    for spec in specs:
        target = root / Path(spec.path)
        if not target.exists():
            checks.append(
                {
                    "check": spec.name,
                    "status": "Fail",
                    "evidence": f"Missing document: {spec.path}",
                }
            )
            continue

        text = target.read_text(encoding="utf-8")
        missing = [needle for needle in spec.needles if needle not in text]
        if missing:
            checks.append(
                {
                    "check": spec.name,
                    "status": "Fail",
                    "evidence": f"{spec.path} missing {missing[0]}",
                }
            )
            continue

        if spec.ordered:
            positions = [text.index(needle) for needle in spec.needles]
            if positions != sorted(positions):
                checks.append(
                    {
                        "check": spec.name,
                        "status": "Fail",
                        "evidence": f"{spec.path} contains required markers out of order",
                    }
                )
                continue

        evidence = f"{spec.path} contains {len(spec.needles)} required marker(s)"
        if spec.ordered and len(spec.needles) > 1:
            evidence += " in order"
        checks.append({"check": spec.name, "status": "Pass", "evidence": evidence})
    return checks


def _run_live_probe(root: Path, spec: LiveProbeSpec) -> dict[str, str]:
    try:
        completed = subprocess.run(
            list(spec.command),
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
    except Exception as exc:  # pragma: no cover - exercised through report assertions
        return {
            "probe": spec.name,
            "status": "Fail",
            "command": " ".join(spec.command),
            "evidence": f"{type(exc).__name__}: {exc}",
        }

    stdout = (completed.stdout or "").strip()
    stderr = (completed.stderr or "").strip()
    evidence = stdout or stderr or "Probe completed with no output"
    if len(evidence) > 300:
        evidence = evidence[:297] + "..."

    return {
        "probe": spec.name,
        "status": "Pass" if completed.returncode == 0 else "Fail",
        "command": " ".join(spec.command),
        "evidence": f"exit={completed.returncode}; {evidence}",
    }


def _resolve_marcus_workflow_sequence(
    root: Path, *, content_type: str, motion_enabled: bool
) -> tuple[str, tuple[str, ...]]:
    module_path = root / "skills" / "bmad-agent-marcus" / "scripts" / "generate-production-plan.py"
    template_path = (
        root / "skills" / "bmad-agent-marcus" / "references" / "workflow-templates.yaml"
    )
    if not module_path.exists():
        raise FileNotFoundError(f"Missing required asset: {module_path.relative_to(root).as_posix()}")
    if not template_path.exists():
        raise FileNotFoundError(f"Missing required asset: {template_path.relative_to(root).as_posix()}")

    module_name = f"structural_walk_marcus_plan_{hashlib.sha1(str(module_path).encode('utf-8')).hexdigest()}"
    module = load_module_from_path(module_name, module_path)
    try:
        workflow_templates = module.load_workflow_templates(template_path)
        workflow_lookup = module.build_workflow_lookup(workflow_templates)
        effective_content_type = module.select_workflow_variant(
            content_type, motion_enabled=motion_enabled
        )
        template_id, workflow = module.resolve_workflow(
            effective_content_type, workflow_templates, workflow_lookup
        )
        if not workflow or not template_id:
            raise ValueError(f"Unknown Marcus workflow template: {effective_content_type}")
        return template_id, tuple(stage["stage"] for stage in workflow["stages"])
    finally:
        sys.modules.pop(module_name, None)


def _validate_marcus_planning_asset_declarations(spec: WorkflowSpec) -> list[str]:
    declared_paths = {item.path for item in spec.cross_cutting_specs}
    required_paths = {
        "skills/bmad-agent-marcus/scripts/generate-production-plan.py",
        "skills/bmad-agent-marcus/references/workflow-templates.yaml",
    }
    missing = sorted(path for path in required_paths if path not in declared_paths)
    return [f"Missing Marcus planning asset declaration: {path}" for path in missing]


def _evaluate_sequence_doc_parity(
    root: Path, spec: WorkflowSpec, stages: tuple[str, ...]
) -> tuple[str, str, str]:
    if not spec.sequence_doc_parity_specs:
        return (
            "Blocked",
            "No sequence_doc_parity mappings declared for this workflow",
            "No manifest-backed sequence-to-document parity mappings configured",
        )

    stage_index = {stage: index for index, stage in enumerate(stages)}
    doc_positions: dict[str, list[tuple[int, int, str]]] = {}

    for entry in spec.sequence_doc_parity_specs:
        index = stage_index.get(entry.stage)
        if index is None:
            return (
                "Blocked",
                f"Sequence-doc parity references unknown Marcus stage: {entry.stage}",
                "Marcus sequence resolution did not include the declared stage mapping",
            )

        target = root / entry.path
        if not target.exists():
            return (
                "Blocked",
                f"Sequence-doc parity asset missing: {entry.path}",
                "Declared sequence-to-document parity asset is absent",
            )

        text = target.read_text(encoding="utf-8")
        position = text.find(entry.needle)
        if position == -1:
            return (
                "Blocked",
                f"Sequence-doc parity marker missing for stage '{entry.stage}': {entry.path}",
                entry.needle,
            )

        doc_positions.setdefault(entry.path, []).append((index, position, entry.needle))

    for path, items in doc_positions.items():
        ordered = sorted(items, key=lambda item: (item[0], item[1]))
        last_position = -1
        for _, position, needle in ordered:
            if position < last_position:
                return (
                    "Blocked",
                    f"Sequence-doc parity markers out of order in {path}",
                    needle,
                )
            last_position = position

    return (
        "Pass",
        "",
        f"Validated {len(spec.sequence_doc_parity_specs)} sequence-doc checkpoint(s) across {len(doc_positions)} document(s)",
    )


def _build_dry_run_result(report: dict[str, Any], spec: WorkflowSpec, root: Path) -> dict[str, Any]:
    if not spec.dry_run_steps:
        raise ValueError("Dry-run planning preview requires manifest-declared dry_run.steps")
    if spec.key == "standard":
        sequence_content_type = "narrated-deck-video-export"
        sequence_motion_enabled = False
    elif spec.key == "motion":
        sequence_content_type = "narrated-deck-video-export"
        sequence_motion_enabled = True
    else:
        raise ValueError(f"Dry-run planning preview is not configured for workflow '{spec.key}'")

    contract_failures = [
        finding
        for gate in report["gates"]
        for finding in gate["findings"]
        if finding.startswith("Invalid contract:") or finding.startswith("Missing required asset:")
    ]
    structural_failures = [
        finding
        for gate in report["gates"]
        for finding in gate["findings"]
        if not any(
            finding.startswith(prefix) and gate["contract_path"] in finding
            for prefix in ("Invalid contract:", "Missing required asset:")
        )
    ]
    structural_failures.extend(report["cross_cutting"]["findings"])
    document_failures = [
        check["evidence"] for check in report["anti_drift"] if check["status"] == "Fail"
    ]

    gate_chain = " -> ".join(gate["gate"] for gate in report["gates"])
    results: list[dict[str, str]] = []
    blocked = 0

    resolved_sequence: tuple[str, tuple[str, ...]] | None = None
    resolved_sequence_error = ""

    def get_resolved_sequence() -> tuple[str, tuple[str, ...]] | None:
        nonlocal resolved_sequence, resolved_sequence_error
        if resolved_sequence is not None or resolved_sequence_error:
            return resolved_sequence
        try:
            resolved_sequence = _resolve_marcus_workflow_sequence(
                root,
                content_type=sequence_content_type,
                motion_enabled=sequence_motion_enabled,
            )
        except Exception as exc:
            resolved_sequence_error = (
                f"Marcus production-plan resolution failed: {type(exc).__name__}: {exc}"
            )
        return resolved_sequence

    for step in spec.dry_run_steps:
        status = "Pass"
        blocker = ""
        evidence = ""
        if step.kind == "manifest":
            manifest_findings = _validate_marcus_planning_asset_declarations(spec)
            if manifest_findings:
                status = "Blocked"
                blocker = manifest_findings[0]
            evidence = f"Resolved {spec.key} manifest with {len(spec.cross_cutting_specs)} cross-cutting checks and {len(spec.anti_drift_specs)} document checks"
        elif step.kind == "sequence":
            resolved = get_resolved_sequence()
            if resolved is not None:
                template_id, stages = resolved
                evidence = f"{template_id}: {' -> '.join(stages)}"
            else:
                status = "Blocked"
                blocker = resolved_sequence_error
                evidence = gate_chain
        elif step.kind == "sequence_docs":
            resolved = get_resolved_sequence()
            if resolved is None:
                status = "Blocked"
                blocker = resolved_sequence_error
                evidence = "Sequence-to-document parity requires Marcus sequence resolution first"
            else:
                _, stages = resolved
                status, blocker, evidence = _evaluate_sequence_doc_parity(root, spec, stages)
        elif step.kind == "contracts":
            if contract_failures:
                status = "Blocked"
                blocker = contract_failures[0]
            evidence = f"Validated {sum(1 for gate in report['gates'] for asset in gate['assets'] if asset['type'] == 'Contract')} workflow contracts"
        elif step.kind == "aggregate":
            if structural_failures:
                status = "Blocked"
                blocker = structural_failures[0]
            evidence = (
                f"{len(report['cross_cutting']['components'])} cross-cutting checks, "
                f"{len(report['anti_drift'])} document checks"
            )
        elif step.kind == "documents":
            if document_failures:
                status = "Blocked"
                blocker = document_failures[0]
            evidence = f"Verified {len(report['anti_drift'])} workflow document checkpoint(s)"
        else:
            raise ValueError(f"Unsupported dry-run step kind '{step.kind}' for workflow '{spec.key}'")

        if status == "Blocked":
            blocked += 1

        results.append(
            {
                "step": step.label,
                "scope": step.scope,
                "input": step.input_ref,
                "result": status,
                "blocker": blocker,
                "evidence": evidence,
            }
        )

    return {
        "supported": True,
        "steps": [
            {
                "step": step.label,
                "scope": step.scope,
                "input": step.input_ref,
                "kind": step.kind,
            }
            for step in spec.dry_run_steps
        ],
        "results": results,
        "summary": {
            "planned": len(spec.dry_run_steps),
            "passed": len(spec.dry_run_steps) - blocked,
            "blocked": blocked,
        },
    }


def build_report(
    *,
    root: Path | None = None,
    generated_at: datetime | None = None,
    workflow: str = "standard",
    live_probes: tuple[LiveProbeSpec, ...] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    repo_root = root or project_root()
    timestamp = generated_at or _now_utc()
    workflow_key = _normalize_workflow(workflow)
    spec = load_workflow_spec(repo_root, workflow_key)

    gates = [_build_gate_result(repo_root, gate_spec) for gate_spec in spec.gate_specs]
    cross_cutting = _build_cross_cutting_result(repo_root, spec.cross_cutting_specs)
    anti_drift = _build_anti_drift_result(repo_root, spec.anti_drift_specs)
    probe_results = [_run_live_probe(repo_root, probe) for probe in (live_probes or ())]

    remediation_items: list[str] = []
    critical_findings = 0

    for gate in gates:
        remediation_items.extend(gate["findings"])
        critical_findings += len(gate["findings"])

    remediation_items.extend(cross_cutting["findings"])
    critical_findings += len(cross_cutting["findings"])

    for check in anti_drift:
        if check["status"] == "Fail":
            remediation_items.append(f"Document check failed: {check['check']} ({check['evidence']})")
            critical_findings += 1

    for probe in probe_results:
        if probe["status"] == "Fail":
            remediation_items.append(f"Live probe failed: {probe['probe']} ({probe['evidence']})")
            critical_findings += 1

    report = {
        "generated_at": timestamp.isoformat(),
        "workflow": workflow_key,
        "workflow_title": spec.title,
        "gates": gates,
        "cross_cutting": cross_cutting,
        "anti_drift": anti_drift,
        "live_probes": probe_results,
        "summary": {
            "walk_type": spec.walk_type,
            "overall_status": "READY" if critical_findings == 0 else "NEEDS REMEDIATION",
            "critical_findings": critical_findings,
            "remediation_items": remediation_items,
        },
    }
    if dry_run:
        report["dry_run"] = _build_dry_run_result(report, spec, repo_root)
    return report


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Structural Walk Report",
        "",
        f"**Workflow:** {report['workflow_title']}",
        f"**Generated at (UTC):** {report['generated_at']}",
        f"**Walk type:** {report['summary']['walk_type']}",
        f"**Overall status:** {report['summary']['overall_status']}",
        "",
        "---",
    ]

    for gate in report["gates"]:
        lines.extend(
            [
                "",
                f"## Gate {gate['gate']} - {gate['name']}",
                "",
                f"**Producing Agent:** {gate['producing_agent']}  ",
                f"**Source of Truth:** {gate['source_of_truth']}  ",
                f"**Fidelity Contract:** {gate['contract_path']}",
                "",
                "### Invoked Assets",
                "",
                "| Type | Path | Status |",
                "|------|------|--------|",
            ]
        )
        for asset in gate["assets"]:
            lines.append(f"| {asset['type']} | {asset['path']} | {asset['status']} |")
        lines.extend(["", "### Findings", ""])
        if gate["findings"]:
            lines.extend([f"- {finding}" for finding in gate["findings"]])
        else:
            lines.append("- None.")
        lines.extend(["", "---"])

    lines.extend(
        [
            "",
            "## Cross-Cutting Checks",
            "",
            "| Component | Path | Status |",
            "|-----------|------|--------|",
        ]
    )
    for component in report["cross_cutting"]["components"]:
        lines.append(
            f"| {component['component']} | {component['path']} | {component['status']} |"
        )
    lines.extend(["", "### Findings", ""])
    if report["cross_cutting"]["findings"]:
        lines.extend([f"- {finding}" for finding in report["cross_cutting"]["findings"]])
    else:
        lines.append("- None.")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Document Integrity Checks",
            "",
            "| Check | Status | Evidence |",
            "|-------|--------|----------|",
        ]
    )
    for check in report["anti_drift"]:
        lines.append(f"| {check['check']} | {check['status']} | {check['evidence']} |")

    if report["live_probes"]:
        lines.extend(
            [
                "",
                "---",
                "",
                "## Live Probes",
                "",
                "| Probe | Status | Command | Evidence |",
                "|-------|--------|---------|----------|",
            ]
        )
        for probe in report["live_probes"]:
            lines.append(
                f"| {probe['probe']} | {probe['status']} | {probe['command']} | {probe['evidence']} |"
            )

    if report.get("dry_run"):
        lines.extend(
            [
                "",
                "---",
                "",
                "## Dry Run Plan",
                "",
                "| Step | Scope | Input | Kind |",
                "|------|-------|-------|------|",
            ]
        )
        for step in report["dry_run"]["steps"]:
            lines.append(
                f"| {step['step']} | {step['scope']} | {step['input']} | {step['kind']} |"
            )
        lines.extend(
            [
                "",
                "## Dry Run Results",
                "",
                "| Step | Result | Blocker | Evidence |",
                "|------|--------|---------|----------|",
            ]
        )
        for result in report["dry_run"]["results"]:
            blocker = result["blocker"] or "-"
            lines.append(
                f"| {result['step']} | {result['result']} | {blocker} | {result['evidence']} |"
            )
        lines.extend(
            [
                "",
                f"**Dry run planned:** {report['dry_run']['summary']['planned']}  ",
                f"**Dry run passed:** {report['dry_run']['summary']['passed']}  ",
                f"**Dry run blocked:** {report['dry_run']['summary']['blocked']}",
            ]
        )

    lines.extend(["", "---", "", "## Summary Verdict", ""])
    lines.append(f"**Overall status:** {report['summary']['overall_status']}  ")
    lines.append(f"**Critical findings:** {report['summary']['critical_findings']}  ")
    remediation_items = report["summary"]["remediation_items"]
    if remediation_items:
        lines.append("**Remediation items:**")
        lines.extend([f"- {item}" for item in remediation_items])
    else:
        lines.append("**Remediation items:** None")
    lines.append("")
    return "\n".join(lines)


def default_output_path(
    root: Path,
    workflow: str = "standard",
    generated_at: datetime | None = None,
    dry_run: bool = False,
) -> Path:
    timestamp = generated_at or _now_utc()
    workflow_key = _normalize_workflow(workflow)
    suffix = "-dry-run" if dry_run else ""
    filename = f"structural-walk-{workflow_key}{suffix}-{timestamp.strftime('%Y%m%d-%H%M%S')}.md"
    return root / "reports" / "structural-walk" / workflow_key / filename


def write_report(output_path: Path, markdown: str) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown + "\n", encoding="utf-8")
    return output_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a canonical structural walk report")
    parser.add_argument("--root", type=Path, default=None, help="Override repository root")
    parser.add_argument(
        "--workflow",
        choices=VALID_WORKFLOWS,
        default="standard",
        help="Which high-level narrated workflow to validate",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Explicit output path for the markdown report",
    )
    parser.add_argument(
        "--live-probe",
        action="append",
        dest="live_probes",
        choices=tuple(DEFAULT_LIVE_PROBES.keys()),
        default=[],
        help="Optional command probe to execute and record in the report",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run the read-only dry-run planning preview",
    )
    return parser.parse_args(argv)


def _validate_cli_args(args: argparse.Namespace) -> str | None:
    if args.dry_run and args.live_probes:
        return "--dry-run cannot be combined with --live-probe; dry-run is local and non-probing"
    return None


GATE_SPECS = COMMON_GATE_SPECS
WORKFLOW_SPECS: dict[str, WorkflowSpec] = {}
CROSS_CUTTING_SPECS: tuple[CrossCuttingSpec, ...] = ()
ANTI_DRIFT_SPECS: tuple[AntiDriftSpec, ...] = ()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cli_error = _validate_cli_args(args)
    if cli_error is not None:
        print(cli_error, file=sys.stderr)
        return 1
    root = args.root.resolve() if args.root else project_root()
    generated_at = _now_utc()
    live_probes = tuple(DEFAULT_LIVE_PROBES[name] for name in args.live_probes)
    try:
        report = build_report(
            root=root,
            generated_at=generated_at,
            workflow=args.workflow,
            live_probes=live_probes,
            dry_run=bool(args.dry_run),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    output_path = args.output.resolve() if args.output else default_output_path(
        root, args.workflow, generated_at, dry_run=bool(args.dry_run)
    )
    write_report(output_path, render_markdown(report))

    print(f"Wrote structural walk report to {output_path}")
    print(
        f"Workflow: {report['workflow']} | "
        f"Overall status: {report['summary']['overall_status']} | "
        f"Critical findings: {report['summary']['critical_findings']}"
    )
    return 0 if report["summary"]["critical_findings"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
