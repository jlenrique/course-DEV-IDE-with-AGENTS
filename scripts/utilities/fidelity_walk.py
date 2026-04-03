"""Canonical fidelity walk generator.

Builds a static readiness report for the documented G0-G6 happy path using
the repository's authoritative contract names and anti-drift checkpoints.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.utilities.file_helpers import project_root
from scripts.validate_fidelity_contracts import validate_contract


@dataclass(frozen=True)
class AssetSpec:
    asset_type: str
    path: str
    contract: bool = False
    redirect_contains: str | None = None


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


@dataclass(frozen=True)
class AntiDriftSpec:
    name: str
    path: str
    needle: str


GATE_SPECS: tuple[GateSpec, ...] = (
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
            AssetSpec("Contract Schema", "state/config/fidelity-contracts/_schema.yaml"),
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
            AssetSpec("Config", "state/config/course_context.yaml"),
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
            AssetSpec("Config", "state/config/narration-grounding-profiles.yaml"),
            AssetSpec("Config", "state/config/narration-script-parameters.yaml"),
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


CROSS_CUTTING_SPECS: tuple[CrossCuttingSpec, ...] = (
    CrossCuttingSpec("Marcus orchestrator", "skills/bmad-agent-marcus/SKILL.md"),
    CrossCuttingSpec("Production coordination", "skills/production-coordination/scripts/manage_baton.py"),
    CrossCuttingSpec("Fidelity assessor", "skills/bmad-agent-fidelity-assessor/SKILL.md"),
    CrossCuttingSpec("Quality reviewer", "skills/bmad-agent-quality-reviewer/SKILL.md"),
    CrossCuttingSpec("Quality reviewer sidecar", "_bmad/memory/quality-reviewer-sidecar"),
    CrossCuttingSpec("Marcus sidecar", "_bmad/memory/bmad-agent-marcus-sidecar"),
    CrossCuttingSpec(
        "Redirect placeholder",
        "_bmad/memory/master-orchestrator-sidecar/index.md",
        redirect_contains="Active sidecar: `_bmad/memory/bmad-agent-marcus-sidecar/`",
    ),
    CrossCuttingSpec("Contract validator", "scripts/validate_fidelity_contracts.py"),
)


ANTI_DRIFT_SPECS: tuple[AntiDriftSpec, ...] = (
    AntiDriftSpec(
        "Prompt 6B in prompt pack",
        "docs/workflow/trial-run-prompts-to-irene-pass2-v4.md",
        "## 6B) Literal-Visual Operator Build + Confirmation",
    ),
    AntiDriftSpec(
        "Storyboard A in prompt pack",
        "docs/workflow/trial-run-prompts-to-irene-pass2-v4.md",
        "Required HIL review (Storyboard A)",
    ),
    AntiDriftSpec(
        "Storyboard B in prompt pack",
        "docs/workflow/trial-run-prompts-to-irene-pass2-v4.md",
        "Required HIL review (Storyboard B",
    ),
    AntiDriftSpec(
        "Gate 6B in operator card",
        "docs/workflow/trial-run-v3-operator-card.md",
        "### 6B. Prompt 6B",
    ),
    AntiDriftSpec(
        "Operator packet in contract",
        "docs/workflow/trial-run-pass2-artifacts-contract.md",
        "literal-visual-operator-packet.md",
    ),
)


def _now_utc() -> datetime:
    return datetime.now(tz=timezone.utc).replace(microsecond=0)


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

    if isinstance(spec, AssetSpec) and spec.contract:
        if not target.exists():
            findings.append(f"Missing required asset: {spec.path}")
            return "Missing", findings
        errors = validate_contract(target)
        if errors:
            findings.append(f"Invalid contract: {spec.path} ({'; '.join(errors)})")
            return "Invalid", findings
        return "Valid", findings

    if target.exists():
        return "Present", findings

    findings.append(f"Missing required asset: {spec.path}")
    return "Missing", findings


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


def _build_cross_cutting_result(root: Path) -> dict[str, Any]:
    components: list[dict[str, str]] = []
    findings: list[str] = []
    for spec in CROSS_CUTTING_SPECS:
        status, component_findings = _status_for_asset(root, spec)
        components.append({"component": spec.component, "path": spec.path, "status": status})
        findings.extend(component_findings)
    return {"components": components, "findings": findings}


def _build_anti_drift_result(root: Path) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    for spec in ANTI_DRIFT_SPECS:
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
        if spec.needle in text:
            checks.append(
                {
                    "check": spec.name,
                    "status": "Pass",
                    "evidence": f"{spec.path} contains {spec.needle}",
                }
            )
            continue
        checks.append(
            {
                "check": spec.name,
                "status": "Fail",
                "evidence": f"{spec.path} missing {spec.needle}",
            }
        )
    return checks


def build_report(root: Path | None = None, generated_at: datetime | None = None) -> dict[str, Any]:
    repo_root = root or project_root()
    timestamp = generated_at or _now_utc()

    gates = [_build_gate_result(repo_root, spec) for spec in GATE_SPECS]
    cross_cutting = _build_cross_cutting_result(repo_root)
    anti_drift = _build_anti_drift_result(repo_root)

    remediation_items: list[str] = []
    critical_findings = 0

    for gate in gates:
        remediation_items.extend(gate["findings"])
        critical_findings += len(gate["findings"])

    remediation_items.extend(cross_cutting["findings"])
    critical_findings += len(cross_cutting["findings"])

    for check in anti_drift:
        if check["status"] == "Fail":
            remediation_items.append(f"Anti-drift check failed: {check['check']} ({check['evidence']})")
            critical_findings += 1

    return {
        "generated_at": timestamp.isoformat(),
        "gates": gates,
        "cross_cutting": cross_cutting,
        "anti_drift": anti_drift,
        "summary": {
            "overall_status": "READY" if critical_findings == 0 else "NEEDS REMEDIATION",
            "critical_findings": critical_findings,
            "remediation_items": remediation_items,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Fidelity Walk Report",
        "",
        f"**Generated at (UTC):** {report['generated_at']}",
        "**Walk type:** Static readiness walk (asset presence + contract/anti-drift wiring checks)",
        f"**Overall status:** {report['summary']['overall_status']}",
        "",
        "---",
    ]

    for gate in report["gates"]:
        lines.extend(
            [
                "",
                f"## Gate {gate['gate']} — {gate['name']}",
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
        lines.append("")
        lines.append("---")

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
            "## Anti-Drift Checkpoints",
            "",
            "| Check | Status | Evidence |",
            "|-------|--------|----------|",
        ]
    )
    for check in report["anti_drift"]:
        lines.append(f"| {check['check']} | {check['status']} | {check['evidence']} |")

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


def default_output_path(root: Path, generated_at: datetime | None = None) -> Path:
    timestamp = generated_at or _now_utc()
    return root / "tests" / f"fidelity-walk-{timestamp.strftime('%Y%m%d-%H%M%S')}.md"


def write_report(output_path: Path, markdown: str) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown + "\n", encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a canonical fidelity walk report")
    parser.add_argument("--root", type=Path, default=None, help="Override repository root")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Explicit output path for the markdown report",
    )
    args = parser.parse_args()

    root = args.root.resolve() if args.root else project_root()
    generated_at = _now_utc()
    report = build_report(root=root, generated_at=generated_at)
    output_path = args.output.resolve() if args.output else default_output_path(root, generated_at)
    write_report(output_path, render_markdown(report))

    print(f"Wrote fidelity walk report to {output_path}")
    print(
        f"Overall status: {report['summary']['overall_status']} | "
        f"Critical findings: {report['summary']['critical_findings']}"
    )
    return 0 if report["summary"]["critical_findings"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())