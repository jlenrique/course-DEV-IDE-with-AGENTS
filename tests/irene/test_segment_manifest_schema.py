"""T2 schema-validation tests for segment-manifest.schema.json.

Asserts the JSON Schema accepts the canonical fixture and rejects each of the
three §7.1 malformed variants (§6.3 / §6.4 / §6.5 structural failure modes).

Structural constraints enforced by the schema (AC-B.2):
- Forbid legacy `motion_asset` key anywhere in segments (§6.3 ban list)
- Require `visual_file` on every segment with non-null `visual_mode` (§6.4)
- Require non-null `motion_duration_seconds` on every segment with
  `visual_mode == "video"` (§6.5 structural — value-vs-receipt cross-validation
  is T5/lint territory, NOT schema)

Note: §6.5 cross-artifact check (receipt↔manifest duration) lives in the T5
lint validator (AC-B.3), NOT in the JSON Schema. Schema guards structural
presence + non-null; lint guards value-vs-receipt agreement.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
import yaml

_REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = _REPO_ROOT / "state" / "config" / "schemas" / "segment-manifest.schema.json"
FIXTURE_ROOT = (
    _REPO_ROOT / "tests" / "fixtures" / "7-1-irene-pass-2-authoring-template"
)
PASS_2_DIR = FIXTURE_ROOT / "pass_2_emissions"


@pytest.fixture(scope="module")
def schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def validator(schema) -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(schema)


def _load(name: str) -> dict:
    return yaml.safe_load((PASS_2_DIR / name).read_text(encoding="utf-8"))


def test_schema_file_exists_and_is_draft_2020_12():
    assert SCHEMA_PATH.exists(), f"Schema not found at {SCHEMA_PATH}"
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
    assert schema.get("title") == "SegmentManifest"


def test_canonical_fixture_passes_schema(validator):
    canonical = _load("trial_c1m1_canonical.yaml")
    errors = sorted(validator.iter_errors(canonical), key=lambda e: e.path)
    assert not errors, (
        "Canonical fixture must pass schema unchanged (AC-T.3 regression canary). "
        f"Errors: {[e.message for e in errors]}"
    )


def test_malformed_6_3_duplicate_motion_keys_fails_schema(validator):
    """§6.3 — motion_asset is a forbidden legacy key."""
    manifest = _load("malformed_6_3_duplicate_motion_keys.yaml")
    errors = list(validator.iter_errors(manifest))
    assert errors, "Schema must reject manifests containing legacy motion_asset key"
    # motion_asset rejection is declarative: error surfaces either in message,
    # path, or schema_path depending on how the ban is encoded.
    def _touches_motion_asset(err):
        return (
            "motion_asset" in err.message
            or "motion_asset" in str(list(err.absolute_path))
            or "motion_asset" in str(list(err.absolute_schema_path))
        )
    assert any(_touches_motion_asset(e) for e in errors), (
        f"§6.3 rejection must reference motion_asset. Got errors: "
        f"{[(e.message, list(e.absolute_path)) for e in errors]}"
    )


def _error_touches(errors, needle: str) -> bool:
    for e in errors:
        if (
            needle in e.message
            or needle in str(list(e.absolute_path))
            or needle in str(list(e.absolute_schema_path))
        ):
            return True
    return False


def test_malformed_6_4_missing_visual_file_fails_schema(validator):
    """§6.4 — segments with non-null visual_mode must carry visual_file."""
    manifest = _load("malformed_6_4_missing_visual_file.yaml")
    errors = list(validator.iter_errors(manifest))
    assert errors, (
        "Schema must reject manifests missing visual_file on non-null-visual-mode segments"
    )
    assert _error_touches(errors, "visual_file"), (
        f"§6.4 rejection must reference visual_file. Got: "
        f"{[(e.message, list(e.absolute_path)) for e in errors]}"
    )


def test_malformed_6_5_null_motion_duration_fails_schema(validator):
    """§6.5 — motion segments must carry non-null motion_duration_seconds."""
    manifest = _load("malformed_6_5_null_motion_duration.yaml")
    errors = list(validator.iter_errors(manifest))
    assert errors, "Schema must reject motion segments with null motion_duration_seconds"
    assert _error_touches(errors, "motion_duration_seconds"), (
        f"§6.5 rejection must reference motion_duration_seconds. Got: "
        f"{[(e.message, list(e.absolute_path)) for e in errors]}"
    )


def test_as_emitted_fixture_fails_schema_with_all_three_modes(validator):
    """Trial-#1 as-emitted manifest exhibits all three bugs; schema rejects it."""
    manifest = _load("trial_c1m1_as_emitted.yaml")
    errors = list(validator.iter_errors(manifest))

    assert errors, "As-emitted trial manifest exhibits 3 bugs; schema must reject"
    assert _error_touches(errors, "motion_asset"), "§6.3 violation must surface"
    assert _error_touches(errors, "visual_file"), "§6.4 violation must surface"
    assert _error_touches(errors, "motion_duration_seconds"), "§6.5 violation must surface"


def test_schema_version_pinned_to_1_1():
    """Schema declares which manifest schema_version it validates.

    §7.1 ships as v1.1 tightening (strict enforcement on existing v1.1 shape);
    no version bump — see SCHEMA_CHANGELOG entry for segment-manifest.
    """
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "1.1"


def test_schema_forbids_motion_asset_key_declaratively():
    """The ban on motion_asset must be a declarative schema rule, not a regex
    scan. Future readers should see the forbidden key in the schema itself.
    """
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    segment_schema = schema["$defs"]["segment"]
    forbidden = segment_schema.get("properties", {}).get("motion_asset")
    # Either declared as false-schema (impossible to set) or listed in a
    # 'not' constraint — both are acceptable declarative forms.
    has_declarative_ban = (
        forbidden is False
        or (isinstance(forbidden, dict) and forbidden.get("not") == {})
        or any(
            "motion_asset" in str(rule)
            for rule in segment_schema.get("allOf", []) + segment_schema.get("not", [])
        )
    )
    assert has_declarative_ban, (
        "motion_asset ban must be declarative in the schema, not merely enforced "
        "via additionalProperties: false"
    )
