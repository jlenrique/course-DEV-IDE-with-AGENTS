from __future__ import annotations

import json
from pathlib import Path

from scripts.utilities.marcus_prompt_harness import (
    build_consistency_findings,
    build_step_reports,
    infer_context,
    render_quinn_report,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _minimal_run_constants(bundle_dir: Path) -> None:
    _write(
        bundle_dir / "run-constants.yaml",
        "\n".join(
            [
                "schema_version: 1",
                'frozen_at_utc: "2026-04-05T00:00:00Z"',
                "run_id: C1-M1-PRES-20260405",
                "lesson_slug: apc-c1m1-tejal",
                f"bundle_path: {bundle_dir.as_posix()}",
                "primary_source_file: C:/example/source.pdf",
                "optional_context_assets: none",
                "theme_selection: hil-2026-apc-nejal-A",
                "theme_paramset_key: hil-2026-apc-nejal-A",
                "execution_mode: tracked/default",
                "quality_preset: production",
                "double_dispatch: false",
            ]
        ),
    )


def test_infer_context_prefers_run_constants(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _minimal_run_constants(bundle_dir)

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)

    assert context.run_id == "C1-M1-PRES-20260405"
    assert context.lesson_slug == "apc-c1m1-tejal"
    assert context.field_sources["run_id"] == "run-constants.yaml"
    assert context.double_dispatch is False


def test_build_step_reports_marks_prompt_2_inferred_without_direct_map(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _minimal_run_constants(bundle_dir)
    _write(bundle_dir / "ingestion-evidence.md", "# evidence")
    _write(bundle_dir / "metadata.json", json.dumps({"source": "ok"}))

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    reports = build_step_reports(context)
    prompt2 = next(item for item in reports if item.step == "2")

    assert prompt2.status == "INFERRED"
    assert "ingestion-evidence.md present" in prompt2.evidence


def test_build_consistency_findings_detects_run_id_drift(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _minimal_run_constants(bundle_dir)
    _write(
        bundle_dir / "preflight-results.json",
        json.dumps({"run_id": "C1-M1-PRES-20260406", "gate": {"overall_status": "pass"}}),
    )

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    findings = build_consistency_findings(context)

    assert findings == [
        "preflight-results.json run_id=C1-M1-PRES-20260406 does not match canonical run_id=C1-M1-PRES-20260405"
    ]


def test_render_quinn_report_includes_step_summary(tmp_path: Path) -> None:
    bundle_dir = tmp_path / "bundle"
    bundle_dir.mkdir()
    _minimal_run_constants(bundle_dir)
    _write(
        bundle_dir / "preflight-results.json",
        json.dumps({"run_id": "C1-M1-PRES-20260405", "gate": {"overall_status": "pass"}}),
    )

    context = infer_context(root=tmp_path, bundle_dir=bundle_dir)
    step_reports = build_step_reports(context)
    report = render_quinn_report(
        context=context,
        step_reports=step_reports,
        consistency_findings=[],
    )

    assert "# Quinn Watcher Report" in report
    assert "Overall watcher status:" in report
    assert "| `1` | `PASS` |" in report
    assert "| `8` | `MISSING` |" in report
