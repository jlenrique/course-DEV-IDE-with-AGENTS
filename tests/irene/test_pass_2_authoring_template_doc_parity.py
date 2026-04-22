"""T11 AC-T.5 — doc-parity lockstep between pass-2-authoring-template.md and
segment-manifest.schema.json.

If the schema gains or loses a structural constraint, the operator-facing
authoring template MUST reflect it in lockstep. Drift = test failure =
Irene's authors would see a template that lies about what the schema
enforces.

Tests in this file assert that the key structural commitments in the schema
are named in the authoring template, and vice versa, without attempting to
parse the template's free-form prose.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = _REPO_ROOT / "state" / "config" / "schemas" / "segment-manifest.schema.json"
TEMPLATE_PATH = (
    _REPO_ROOT
    / "skills"
    / "bmad-agent-content-creator"
    / "references"
    / "pass-2-authoring-template.md"
)


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def template_text() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def test_template_names_every_top_level_required_envelope_field(schema, template_text):
    for field in schema["required"]:
        assert field in template_text, (
            f"Authoring template is missing envelope field {field!r} "
            f"(schema declares it required; template must surface it)"
        )


def test_template_names_every_segment_required_field(schema, template_text):
    for field in schema["$defs"]["segment"]["required"]:
        assert field in template_text, (
            f"Authoring template is missing segment field {field!r} "
            f"(schema declares it required; template must surface it)"
        )


def test_template_surfaces_schema_version_1_1(schema, template_text):
    declared_version = schema["properties"]["schema_version"]["const"]
    assert declared_version == "1.1"
    assert declared_version in template_text


def test_template_declares_motion_asset_legacy_ban(template_text):
    """§6.3 ban is the most-referenced in trial-run debrief; template must
    call it out explicitly, not hide it in a bullet."""
    assert "motion_asset" in template_text
    # Template must explicitly label motion_asset as forbidden / ban / do NOT.
    ban_markers = ["ban", "forbidden", "do NOT", "legacy"]
    assert any(marker in template_text for marker in ban_markers), (
        "Template must use explicit ban vocabulary for motion_asset legacy key"
    )


def test_template_points_at_upstream_receipt_reader(template_text):
    assert "motion_gate_receipt_reader" in template_text


def test_template_points_at_lint_validator(template_text):
    assert "pass_2_emission_lint" in template_text


def test_template_names_all_visual_mode_enum_values(schema, template_text):
    enum_values = schema["$defs"]["segment"]["properties"]["visual_mode"]["enum"]
    for value in enum_values:
        if value is None:
            continue  # null is an absence, not a named mode in prose
        assert value in template_text, (
            f"Authoring template missing visual_mode value {value!r}"
        )


def test_template_points_at_retrieval_intake_contract_for_third_example(
    template_text,
):
    """Paige's ruling: template ships 2 worked examples (static + motion);
    retrieval-intake-consuming segments get a pointer-only reference to the
    intake story's contract doc (SSOT + decoupling from intake slippage)."""
    assert "retrieval-intake-contract.md" in template_text
