"""PR-RC (Run-Constants) capability tests (AC-T.1, T.2, T.7 from story 26-6).

Direct regression coverage for the 2026-04-17 APC C1-M1 Tejal trial halt at
Prompt 1. Asserts that:

- **AC-T.1**: summarize emits a canonical lowercase-nested preview across 4
  input variants (mixed case, aliases, missing-optional, fully-populated).
- **AC-T.2**: the captured UPPERCASE-flat halt fixture is NORMALIZED by
  PR-RC into a form that passes ``parse_run_constants`` — confirming the
  drift is closed.
- **AC-T.7**: re-authoring the same canonical values yields byte-equal output
  (idempotency via sha256 compare).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.marcus_capabilities import pr_rc
from scripts.marcus_capabilities._shared import Invocation, InvocationContext
from scripts.utilities import run_constants as rc

pytestmark = pytest.mark.trial_critical

FIXTURE_DIR = Path(__file__).parent / "fixtures"
HALT_FIXTURE = FIXTURE_DIR / "halt-2026-04-17-prompt1.yaml"


def _base_values() -> dict:
    """A known-good lowercase-nested dict that passes parse_run_constants."""
    return {
        "run_id": "C1-M1-PRES-20260418",
        "lesson_slug": "apc-c1m1-tejal",
        "bundle_path": "course-content/staging/tracked/source-bundles/test-bundle",
        "primary_source_file": "course-content/courses/placeholder.pdf",
        "theme_selection": "hil-2026-apc-nejal-A",
        "theme_paramset_key": "hil-2026-apc-nejal-A",
        "execution_mode": "tracked/default",
        "quality_preset": "production",
    }


def _invoke(mode: str, args: dict, bundle_path: str | None = None) -> Invocation:
    return Invocation(
        capability_code="PR-RC",
        mode=mode,
        args=args,
        context=InvocationContext(run_id="RC-TEST-1", bundle_path=bundle_path, invoked_by="marcus"),
    )


# ---------------------------------------------------------------------------
# AC-T.1: summarize parametrized × 4 input variants
# ---------------------------------------------------------------------------


def _mixed_case_variant() -> dict:
    """UPPERCASE keys (pack-display style) that Marcus accepts + normalizes."""
    return {
        "RUN_ID": "C1-M1-PRES-20260418",
        "LESSON_SLUG": "apc-c1m1-tejal",
        "BUNDLE_PATH": "course-content/staging/tracked/source-bundles/test-bundle",
        "PRIMARY_SOURCE_FILE": "course-content/courses/placeholder.pdf",
        "THEME_SELECTION": "hil-2026-apc-nejal-A",
        "THEME_PARAMSET_KEY": "hil-2026-apc-nejal-A",
        "EXECUTION_MODE": "tracked/default",
        "QUALITY_PRESET": "production",
    }


def _alias_variant() -> dict:
    """Alternate accepted forms (execution_mode aliases etc.)."""
    values = _base_values()
    values["execution_mode"] = "tracked"  # alias for tracked/default
    return values


def _missing_optional_variant() -> dict:
    """Required fields only; no optionals."""
    return _base_values()


def _fully_populated_variant() -> dict:
    """Everything including nested motion_budget."""
    values = _base_values()
    values.update(
        {
            "motion_enabled": True,
            "motion_budget": {"max_credits": 125, "model_preference": "pro"},
            "double_dispatch": True,
            "experience_profile": "visual-led",
            "cluster_density": "default",
        }
    )
    return values


@pytest.mark.parametrize(
    "variant_builder",
    [_mixed_case_variant, _alias_variant, _missing_optional_variant, _fully_populated_variant],
    ids=["mixed_case", "alias", "missing_optional", "fully_populated"],
)
def test_summarize_renders_canonical_preview(variant_builder) -> None:
    """AC-T.1: summarize produces canonical lowercase-nested preview that validates."""
    envelope = pr_rc.summarize(_invoke("summarize", {"values": variant_builder()}))
    assert envelope.status == "ok", f"preview failed validation: {envelope.errors}"
    assert "preview" in envelope.result
    preview = envelope.result["preview"]
    # Canonical shape assertions
    assert "run_id:" in preview
    assert "RUN_ID:" not in preview  # UPPERCASE was normalized away
    # The preview must re-parse through the validator round-trip
    parsed_data = yaml.safe_load(preview)
    rc.parse_run_constants(parsed_data)  # raises if shape is wrong


# ---------------------------------------------------------------------------
# AC-T.2: halt-fixture regression
# ---------------------------------------------------------------------------


def test_halt_fixture_fails_validator_as_captured() -> None:
    """Sanity: the raw UPPERCASE-flat fixture must FAIL the validator —
    confirms the fixture actually reproduces the 2026-04-17 halt condition."""
    raw = yaml.safe_load(HALT_FIXTURE.read_text(encoding="utf-8"))
    with pytest.raises(rc.RunConstantsError):
        rc.parse_run_constants(raw)


def test_pr_rc_normalizes_halt_fixture(tmp_path: Path) -> None:
    """AC-T.2: PR-RC author mode takes the halt fixture's UPPERCASE-flat form
    and writes a canonical lowercase-nested yaml that parse_run_constants accepts."""
    raw = yaml.safe_load(HALT_FIXTURE.read_text(encoding="utf-8"))
    bundle = tmp_path / "test-bundle"
    bundle.mkdir()

    envelope = pr_rc.execute(
        _invoke("execute", {"values": raw, "mode_sub": "author"}, bundle_path=str(bundle))
    )
    assert envelope.status == "ok", f"authoring failed: {envelope.errors}"
    written_path = Path(envelope.result["written_path"])
    assert written_path.is_file()

    # The written yaml MUST validate clean — this closes the halt defect.
    written_data = yaml.safe_load(written_path.read_text(encoding="utf-8"))
    parsed = rc.parse_run_constants(written_data)
    assert parsed.run_id == "C1-M1-PRES-20260415"
    # Nested motion_budget present as a mapping, not flat keys
    assert parsed.motion_budget is not None
    assert parsed.motion_budget.max_credits == 125.0
    assert parsed.motion_budget.model_preference == "pro"


# ---------------------------------------------------------------------------
# AC-T.7: idempotency — re-author same values yields byte-equal output
# ---------------------------------------------------------------------------


def test_author_is_idempotent(tmp_path: Path) -> None:
    """AC-T.7: calling author twice with same values yields byte-equal sha256."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    values = _fully_populated_variant()

    env1 = pr_rc.execute(_invoke("execute", {"values": values}, bundle_path=str(bundle)))
    env2 = pr_rc.execute(_invoke("execute", {"values": values}, bundle_path=str(bundle)))
    assert env1.status == "ok" and env2.status == "ok"
    assert env1.landing_point.sha256 == env2.landing_point.sha256


# ---------------------------------------------------------------------------
# Validate-mode coverage
# ---------------------------------------------------------------------------


def test_validate_mode_passes_on_well_formed_file(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    # First author a file, then validate it.
    pr_rc.execute(_invoke("execute", {"values": _base_values()}, bundle_path=str(bundle)))
    env = pr_rc.execute(
        _invoke("execute", {"mode_sub": "validate"}, bundle_path=str(bundle))
    )
    assert env.status == "ok"
    assert env.result["run_id_validated"] == "C1-M1-PRES-20260418"


def test_validate_mode_fails_cleanly_on_malformed_file(tmp_path: Path) -> None:
    """Validator rejection must go into envelope.errors, not raise."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "run-constants.yaml").write_text(
        "run_id: ''\nlesson_slug: x\n", encoding="utf-8"
    )
    env = pr_rc.execute(
        _invoke("execute", {"mode_sub": "validate"}, bundle_path=str(bundle))
    )
    assert env.status == "error"
    assert env.errors[0].code == "RUN_CONSTANTS_INVALID"


def test_author_refuses_empty_values(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    env = pr_rc.execute(_invoke("execute", {"values": {}}, bundle_path=str(bundle)))
    assert env.status == "error"
    assert env.errors[0].code == "PR_RC_BAD_ARGS"
