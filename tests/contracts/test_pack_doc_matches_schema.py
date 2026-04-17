"""Contract test: docs-vs-code run-constants schema lockstep.

Thin Audra L1-W check. Story 26-6 moved run-constants authoring OUT of the
prompt-pack doc and INTO Marcus's PR-RC capability. The canonical schema
reference now lives at ``skills/bmad-agent-marcus/capabilities/pr-rc.md``
(operator-facing) alongside the validator at
``scripts/utilities/run_constants.py`` (code-level enforcement).

This test asserts both locations stay in lockstep with the validator: every
required field the validator enforces must be advertised somewhere the
downstream operator or dev agent can find it.

Defect class guarded: validator adds a required field but the doctrine doc
doesn't mention it — Marcus's PR-RC capability would author an incomplete
yaml and operators would get cryptic failures. Same class that halted the
2026-04-17 APC C1-M1 Tejal trial at Prompt 1, now guarded at the new
doctrine home.
"""

from __future__ import annotations

import pytest

from scripts.utilities.file_helpers import project_root

# Post-26-6: run-constants doctrine lives in the PR-RC capability markdown.
# Pack doc now contains only the redirect stub + workflow prompts.
PR_RC_DOCTRINE = (
    project_root()
    / "skills"
    / "bmad-agent-marcus"
    / "capabilities"
    / "pr-rc.md"
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


def _doctrine_text_lower() -> str:
    return PR_RC_DOCTRINE.read_text(encoding="utf-8").lower()


@pytest.mark.trial_critical
def test_pr_rc_doctrine_advertises_every_required_field() -> None:
    """Post-26-6: canonical doctrine lives in the PR-RC capability markdown,
    not the prompt pack. Every required validator field must be mentioned
    there so Marcus can author a complete run-constants.yaml."""
    text = _doctrine_text_lower()
    missing = [f for f in REQUIRED_RUN_CONSTANTS_FIELDS if f not in text]
    assert not missing, (
        "PR-RC capability doctrine does not advertise these required "
        f"validator fields: {missing}. Every required field must appear in "
        "pr-rc.md so Marcus (and any developer reading the doctrine) knows "
        "what the authored yaml must contain."
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
