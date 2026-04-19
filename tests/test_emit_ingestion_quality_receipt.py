"""Tests for ``scripts.utilities.emit_ingestion_quality_receipt``.

Covers the canonical-shape writer that closes the 2026-04-19 trial's
silent-empty-receipt gap.

Name coverage satisfies the ``-k "ingestion_receipt or emit_receipt"``
operator selector.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from scripts.utilities import emit_ingestion_quality_receipt as emit

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_PASS_VERDICTS = {
    "completeness": "pass",
    "readability": "pass",
    "anchorability": "pass",
    "provenance_quality": "pass",
    "planning_usability": "pass",
    "fidelity_usability": "pass",
}


def _happy_spec_mapping(
    *,
    gate_decision: str = "proceed",
    override_verdict: dict[str, str] | None = None,
    vera_verdict: str = "pass",
) -> dict:
    verdicts = dict(_PASS_VERDICTS)
    if override_verdict:
        verdicts.update(override_verdict)
    return {
        "run_id": "C1-M1-PRES-20260419",
        "bundle_path": "course-content/staging/tracked/source-bundles/test",
        "per_source": [
            {
                "source_ref": "SRC-PRIMARY-01",
                "kind": "local_md",
                "verdicts": verdicts,
                "confidence_basis": "high",
                "source_anchor_set": [
                    "extracted.md#SRC-PRIMARY-01",
                    "ingestion-evidence.md row: SRC-PRIMARY-01",
                ],
                "notes": "Part 1-focused extraction retains all instructional material.",
            }
        ],
        "vera_g0": {
            "verdict": vera_verdict,
            "critical_findings": "none",
            "remediation_target": "none",
            "interpretation_notes": [
                "G0-01 section coverage: pass.",
                "G0-02 media capture notation: pass.",
            ],
        },
        "gate_decision": gate_decision,
        "artifacts_written": [
            "irene-packet.md",
            "ingestion-quality-gate-receipt.md",
        ],
        "next_action": "Prompt 5 (Irene Pass 1 Structure + Gate 1 Fidelity)",
    }


# ---------------------------------------------------------------------------
# build_spec / ReceiptSpec validation
# ---------------------------------------------------------------------------


class TestBuildSpecValidation:
    def test_happy_spec_builds_and_validates(self) -> None:
        spec = emit.build_spec(_happy_spec_mapping())
        assert spec.run_id == "C1-M1-PRES-20260419"
        assert len(spec.per_source) == 1
        assert spec.gate_decision == "proceed"

    def test_missing_dimension_raises(self) -> None:
        mapping = _happy_spec_mapping()
        del mapping["per_source"][0]["verdicts"]["completeness"]
        with pytest.raises(emit.ReceiptSpecError, match="completeness"):
            emit.build_spec(mapping)

    def test_invalid_verdict_raises(self) -> None:
        mapping = _happy_spec_mapping(override_verdict={"completeness": "maybe"})
        with pytest.raises(emit.ReceiptSpecError, match="completeness"):
            emit.build_spec(mapping)

    def test_invalid_gate_decision_raises(self) -> None:
        mapping = _happy_spec_mapping(gate_decision="continue")
        with pytest.raises(emit.ReceiptSpecError, match="gate_decision"):
            emit.build_spec(mapping)

    def test_proceed_with_failed_dimension_raises(self) -> None:
        mapping = _happy_spec_mapping(
            override_verdict={"readability": "fail"},
            gate_decision="proceed",
        )
        with pytest.raises(emit.ReceiptSpecError, match="fail"):
            emit.build_spec(mapping)

    def test_proceed_with_failed_vera_raises(self) -> None:
        mapping = _happy_spec_mapping(vera_verdict="fail", gate_decision="proceed")
        with pytest.raises(emit.ReceiptSpecError, match="vera_g0"):
            emit.build_spec(mapping)

    def test_halt_with_failed_dimension_is_allowed(self) -> None:
        mapping = _happy_spec_mapping(
            override_verdict={"readability": "fail"},
            gate_decision="halt",
        )
        spec = emit.build_spec(mapping)
        assert spec.gate_decision == "halt"

    def test_empty_per_source_raises(self) -> None:
        mapping = _happy_spec_mapping()
        mapping["per_source"] = []
        with pytest.raises(emit.ReceiptSpecError, match="per_source"):
            emit.build_spec(mapping)


# ---------------------------------------------------------------------------
# render_receipt_markdown — canonical shape
# ---------------------------------------------------------------------------


class TestRenderReceiptMarkdown:
    def test_renders_all_canonical_sections(self) -> None:
        spec = emit.build_spec(_happy_spec_mapping())
        frozen = datetime(2026, 4, 19, 22, 21, 40, tzinfo=UTC)
        md = emit.render_receipt_markdown(spec, generated_at=frozen)
        for header in (
            "# Ingestion Quality Gate Receipt",
            "## Per-source quality evaluation",
            "## Vera G0 receipt (internal)",
            "## Gate decision",
        ):
            assert header in md, f"missing canonical header: {header}"

    def test_renders_six_dimension_labels_with_spaces(self) -> None:
        spec = emit.build_spec(_happy_spec_mapping())
        md = emit.render_receipt_markdown(spec)
        # Golden-trace fixture uses space-separated labels, not snake_case.
        for label in (
            "- completeness:",
            "- readability:",
            "- anchorability:",
            "- provenance quality:",
            "- planning usability:",
            "- fidelity usability:",
        ):
            assert label in md, f"missing six-dimension label: {label}"

    def test_renders_gate_decision_line_for_marcus_harness(self) -> None:
        """``marcus_prompt_harness._check_step_4`` parses the receipt for
        ``gate_decision: proceed`` — the canonical writer must emit exactly
        that key-value line so the downstream evidence check resolves."""
        spec = emit.build_spec(_happy_spec_mapping())
        md = emit.render_receipt_markdown(spec)
        assert "- gate_decision: proceed" in md

    def test_renders_timestamp_utc(self) -> None:
        spec = emit.build_spec(_happy_spec_mapping())
        frozen = datetime(2026, 4, 19, 22, 21, 40, tzinfo=UTC)
        md = emit.render_receipt_markdown(spec, generated_at=frozen)
        assert "- generated_at_utc: 2026-04-19T22:21:40Z" in md

    def test_renders_source_anchor_set_bullets(self) -> None:
        spec = emit.build_spec(_happy_spec_mapping())
        md = emit.render_receipt_markdown(spec)
        assert "  - extracted.md#SRC-PRIMARY-01" in md
        assert "  - ingestion-evidence.md row: SRC-PRIMARY-01" in md


# ---------------------------------------------------------------------------
# Template scaffold
# ---------------------------------------------------------------------------


class TestTemplateSpec:
    def test_template_contains_fill_in_markers(self) -> None:
        spec = emit.build_template_spec(
            run_id="TEMPLATE-RUN",
            bundle_path="course-content/staging/test-bundle",
        )
        md = emit.render_receipt_markdown(spec)
        assert "[FILL IN:" in md

    def test_template_validates_against_spec_shape(self) -> None:
        """Template spec still satisfies ReceiptSpec.validate() so the
        writer can emit a well-formed scaffold the operator then edits."""
        spec = emit.build_template_spec(
            run_id="TEMPLATE-RUN",
            bundle_path="course-content/staging/test-bundle",
            source_refs=[("SRC-PRIMARY-01", "local_md"), ("SRC-VALIDATION-01", "local_pdf")],
        )
        assert len(spec.per_source) == 2
        assert spec.per_source[0].source_ref == "SRC-PRIMARY-01"
        assert spec.per_source[1].kind == "local_pdf"

    def test_template_renders_both_sources(self) -> None:
        spec = emit.build_template_spec(
            run_id="TEMPLATE-RUN",
            bundle_path="course-content/staging/test-bundle",
            source_refs=[("SRC-PRIMARY-01", "local_md"), ("SRC-VALIDATION-01", "local_pdf")],
        )
        md = emit.render_receipt_markdown(spec)
        assert "### SRC-PRIMARY-01 (local_md)" in md
        assert "### SRC-VALIDATION-01 (local_pdf)" in md


# ---------------------------------------------------------------------------
# inspect_receipt_state (shim guard primitive)
# ---------------------------------------------------------------------------


class TestInspectReceiptState:
    def test_missing_file_reports_not_ok(self, tmp_path: Path) -> None:
        path = tmp_path / "receipt.md"
        ok, reason = emit.inspect_receipt_state(path)
        assert ok is False
        assert "missing" in reason.lower()

    def test_empty_file_reports_not_ok(self, tmp_path: Path) -> None:
        path = tmp_path / "receipt.md"
        path.write_text("   \n\n", encoding="utf-8")
        ok, reason = emit.inspect_receipt_state(path)
        assert ok is False
        assert "empty" in reason.lower()

    def test_fill_in_markers_report_not_ok(self, tmp_path: Path) -> None:
        path = tmp_path / "receipt.md"
        path.write_text(
            "# Ingestion Quality Gate Receipt\n\n"
            "- gate_decision: proceed\n"
            "- notes: [FILL IN: operator fills this in]\n",
            encoding="utf-8",
        )
        ok, reason = emit.inspect_receipt_state(path)
        assert ok is False
        assert "[FILL IN:" in reason

    def test_missing_gate_decision_reports_not_ok(self, tmp_path: Path) -> None:
        path = tmp_path / "receipt.md"
        path.write_text(
            "# Ingestion Quality Gate Receipt\n\nSome prose without the key line.\n",
            encoding="utf-8",
        )
        ok, reason = emit.inspect_receipt_state(path)
        assert ok is False
        assert "gate_decision" in reason

    def test_valid_receipt_reports_ok(self, tmp_path: Path) -> None:
        spec = emit.build_spec(_happy_spec_mapping())
        md = emit.render_receipt_markdown(spec)
        path = tmp_path / "receipt.md"
        path.write_text(md, encoding="utf-8")
        ok, reason = emit.inspect_receipt_state(path)
        assert ok is True
        assert reason == "ok"


# ---------------------------------------------------------------------------
# CLI end-to-end
# ---------------------------------------------------------------------------


class TestCli:
    def test_cli_spec_mode_writes_canonical_receipt(self, tmp_path: Path) -> None:
        bundle = tmp_path / "bundle"
        bundle.mkdir()
        spec_path = tmp_path / "spec.yaml"
        spec_path.write_text(yaml.safe_dump(_happy_spec_mapping()), encoding="utf-8")

        exit_code = emit.main([
            "--bundle-dir",
            str(bundle),
            "--spec",
            str(spec_path),
        ])
        assert exit_code == 0
        written = (bundle / "ingestion-quality-gate-receipt.md").read_text(encoding="utf-8")
        assert "# Ingestion Quality Gate Receipt" in written
        assert "- gate_decision: proceed" in written

    def test_cli_template_mode_writes_fill_in_scaffold(self, tmp_path: Path) -> None:
        bundle = tmp_path / "bundle"
        bundle.mkdir()
        exit_code = emit.main([
            "--bundle-dir",
            str(bundle),
            "--template",
            "--run-id",
            "TEMPLATE-001",
            "--source-ref",
            "SRC-PRIMARY-01:local_md",
        ])
        assert exit_code == 0
        written = (bundle / "ingestion-quality-gate-receipt.md").read_text(encoding="utf-8")
        assert "[FILL IN:" in written
        assert "### SRC-PRIMARY-01 (local_md)" in written

    def test_cli_template_mode_rejects_missing_run_id(self, tmp_path: Path) -> None:
        bundle = tmp_path / "bundle"
        bundle.mkdir()
        exit_code = emit.main([
            "--bundle-dir",
            str(bundle),
            "--template",
        ])
        assert exit_code != 0

    def test_cli_spec_mode_rejects_internally_inconsistent_spec(
        self, tmp_path: Path
    ) -> None:
        bundle = tmp_path / "bundle"
        bundle.mkdir()
        spec_path = tmp_path / "spec.yaml"
        mapping = _happy_spec_mapping(
            override_verdict={"readability": "fail"},
            gate_decision="proceed",
        )
        spec_path.write_text(yaml.safe_dump(mapping), encoding="utf-8")

        exit_code = emit.main([
            "--bundle-dir",
            str(bundle),
            "--spec",
            str(spec_path),
        ])
        assert exit_code != 0
        assert not (bundle / "ingestion-quality-gate-receipt.md").exists()

    def test_cli_output_override_respected(self, tmp_path: Path) -> None:
        bundle = tmp_path / "bundle"
        bundle.mkdir()
        spec_path = tmp_path / "spec.yaml"
        spec_path.write_text(yaml.safe_dump(_happy_spec_mapping()), encoding="utf-8")
        out_path = tmp_path / "custom.md"

        exit_code = emit.main([
            "--bundle-dir",
            str(bundle),
            "--spec",
            str(spec_path),
            "--output",
            str(out_path),
        ])
        assert exit_code == 0
        assert out_path.exists()
        assert not (bundle / "ingestion-quality-gate-receipt.md").exists()
