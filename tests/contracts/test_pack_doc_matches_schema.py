"""Contract test: prompt-pack Run Constants section must match the validator.

Thin first version of the Audra L1-W docs-vs-code schema lockstep check.
When the run-constants validator at ``scripts/utilities/run_constants.py``
adds or removes a required field, the prompt-pack doc must be updated in
the same commit. This test catches the drift class that halted the
2026-04-17 APC C1-M1 Tejal trial at Prompt 1.

Defect class guarded: pack doc advertises a schema the validator rejects,
or validator requires a field the pack doesn't mention — either way, the
operator authors a ``run-constants.yaml`` from the pack and hits
``emit-preflight-receipt`` failures on fields they didn't know about.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.utilities.file_helpers import project_root

PACK_DOC = (
    project_root()
    / "docs"
    / "workflow"
    / "production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md"
)

REQUIRED_RUN_CONSTANTS_FIELDS = [
    "run_id",
    "lesson_slug",
    "bundle_path",
    "primary_source_file",
    "theme_selection",
    "theme_paramset_key",
    "execution_mode",
    "quality_preset",
]


def _pack_text_lower() -> str:
    return PACK_DOC.read_text(encoding="utf-8").lower()


@pytest.mark.trial_critical
def test_pack_advertises_every_required_field() -> None:
    text = _pack_text_lower()
    missing = [f for f in REQUIRED_RUN_CONSTANTS_FIELDS if f not in text]
    assert not missing, (
        "Prompt pack doc does not advertise these required validator fields: "
        f"{missing}. Every required field must appear in the pack so the "
        "operator can author a valid run-constants.yaml from the pack alone."
    )


@pytest.mark.trial_critical
def test_pack_required_fields_remain_stable() -> None:
    """Drift alarm: if the validator's required-field set changes, this test
    must be updated in the same commit as the validator change.

    Reads the validator's ``parse_run_constants`` function and asserts it
    still calls ``_require_non_empty_str`` on the same named fields. If a new
    required field is added (or an existing one dropped), this test fails and
    the operator is forced to also update ``REQUIRED_RUN_CONSTANTS_FIELDS``
    above *and* the pack doc in the same commit.
    """
    validator_src = (
        project_root() / "scripts" / "utilities" / "run_constants.py"
    ).read_text(encoding="utf-8")
    # Each required field appears as: _require_non_empty_str(data, "<field>")
    import re

    found = set(re.findall(r'_require_non_empty_str\(data, "(\w+)"\)', validator_src))
    expected = set(REQUIRED_RUN_CONSTANTS_FIELDS)
    new_required = found - expected
    dropped = expected - found
    assert not new_required, (
        f"Validator now requires fields not in REQUIRED_RUN_CONSTANTS_FIELDS: "
        f"{sorted(new_required)}. Update this test AND the prompt pack doc."
    )
    assert not dropped, (
        f"Validator no longer requires: {sorted(dropped)}. "
        f"Update REQUIRED_RUN_CONSTANTS_FIELDS above."
    )
