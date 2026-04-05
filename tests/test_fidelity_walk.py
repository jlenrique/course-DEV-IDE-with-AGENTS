from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from scripts.utilities.fidelity_walk import (
    ANTI_DRIFT_SPECS,
    CROSS_CUTTING_SPECS,
    GATE_SPECS,
    build_report,
    render_markdown,
)


def _valid_contract_yaml(gate: str) -> str:
    secondary = ""
    if gate == "G4":
        secondary = (
            "  schema_ref_secondary: "
            "skills/bmad-agent-content-creator/references/template-segment-manifest.md\n"
        )
    return (
        f"gate: {gate}\n"
        f"gate_name: {gate} Sample\n"
        "producing_agent: sample-agent\n"
        "source_of_truth:\n"
        "  primary: sample\n"
        "  schema_ref: skills/sample/template.md\n"
        f"{secondary}"
        "criteria:\n"
        "  - id: SAMPLE-01\n"
        "    name: Sample\n"
        "    description: Sample criterion\n"
        "    fidelity_class: [creative]\n"
        "    severity: critical\n"
        "    evaluation_type: deterministic\n"
        "    check: sample\n"
        "    requires_perception: false\n"
    )


def _write(root: Path, relative_path: str, content: str = "ok\n") -> None:
    target = root / Path(relative_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")


def _mkdir(root: Path, relative_path: str) -> None:
    (root / Path(relative_path)).mkdir(parents=True, exist_ok=True)


def _create_minimal_repo(root: Path) -> None:
    _write(root, "pyproject.toml", "[project]\nname='fidelity-walk-test'\n")

    for gate in GATE_SPECS:
        for asset in gate.assets:
            if asset.contract:
                _write(root, asset.path, _valid_contract_yaml(gate.gate))
            else:
                _write(root, asset.path)

    for spec in CROSS_CUTTING_SPECS:
        path = Path(spec.path)
        if spec.redirect_contains is not None:
            _write(
                root,
                spec.path,
                "# Redirect\n\n"
                "**This sidecar is superseded.**\n\n"
                f"{spec.redirect_contains}\n",
            )
        elif path.suffix:
            _write(root, spec.path)
        else:
            _mkdir(root, spec.path)

    anti_drift_docs: dict[str, list[str]] = {}
    for spec in ANTI_DRIFT_SPECS:
        anti_drift_docs.setdefault(spec.path, []).append(spec.needle)

    for path, needles in anti_drift_docs.items():
        _write(root, path, "\n".join(needles) + "\n")


def test_happy_path_uses_canonical_g5_and_g6_contracts(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path)

    report = build_report(root=tmp_path, generated_at=datetime(2026, 4, 3, 20, 0, 0, tzinfo=timezone.utc))
    markdown = render_markdown(report)

    assert report["summary"]["overall_status"] == "READY"
    assert report["summary"]["critical_findings"] == 0
    assert "state/config/fidelity-contracts/g5-audio.yaml" in markdown
    assert "state/config/fidelity-contracts/g6-composition.yaml" in markdown
    assert "g5-audio-fidelity.yaml" not in markdown
    assert "g6-composed-video.yaml" not in markdown


def test_missing_asset_is_reported_with_exact_path(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path)
    (tmp_path / "state/config/fidelity-contracts/g6-composition.yaml").unlink()

    report = build_report(root=tmp_path)

    assert report["summary"]["overall_status"] == "NEEDS REMEDIATION"
    assert any(
        item == "Missing required asset: state/config/fidelity-contracts/g6-composition.yaml"
        for item in report["summary"]["remediation_items"]
    )


def test_documented_redirect_does_not_count_as_critical_finding(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path)

    report = build_report(root=tmp_path)
    redirect_row = next(
        component
        for component in report["cross_cutting"]["components"]
        if component["component"] == "Redirect placeholder"
    )

    assert redirect_row["status"] == "Documented redirect"
    assert report["summary"]["critical_findings"] == 0


def test_anti_drift_failure_is_reported(tmp_path: Path) -> None:
    _create_minimal_repo(tmp_path)
    _write(
        tmp_path,
        "docs/workflow/production-prompt-pack-v4.md",
        "## 6B) Literal-Visual Operator Build + Confirmation\n"
        "Required HIL review (Storyboard A)\n",
    )

    report = build_report(root=tmp_path)

    assert report["summary"]["overall_status"] == "NEEDS REMEDIATION"
    assert any(check["check"] == "Storyboard B in prompt pack" and check["status"] == "Fail" for check in report["anti_drift"])