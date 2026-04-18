"""Tests for Marcus capability registry (AC-C.4, AC-T.9 from story 26-6).

Marked ``trial_critical`` — the router + registry are on the pre-Prompt-1
trial path; a broken registry means Marcus can't find his own capabilities.
See ``docs/dev-guide/testing.md`` for the regimen.
"""

from __future__ import annotations

import pytest

from scripts.marcus_capabilities import CAPABILITY_REGISTRY, UnknownCapability
from scripts.marcus_capabilities.registry import cross_reference_audit, get

pytestmark = pytest.mark.trial_critical

EXPECTED_CODES = {"PR-PF", "PR-RC", "PR-HC", "PR-RS"}
FULL_CODES = {"PR-PF", "PR-RC"}
STUB_CODES = {"PR-HC", "PR-RS"}


def test_all_four_codes_registered() -> None:
    """AC-C.4: registry enumerates all 4 PR-* codes."""
    assert set(CAPABILITY_REGISTRY.keys()) == EXPECTED_CODES


def test_full_vs_stub_classification() -> None:
    """PR-PF and PR-RC ship full; PR-HC and PR-RS are stubs (per 26-6 scope)."""
    for code in FULL_CODES:
        assert CAPABILITY_REGISTRY[code].full_or_stub == "full", code
    for code in STUB_CODES:
        assert CAPABILITY_REGISTRY[code].full_or_stub == "stub", code


def test_every_code_has_description_and_script_module() -> None:
    """Frontmatter contract: every entry has non-empty description and script_module."""
    for code, entry in CAPABILITY_REGISTRY.items():
        assert entry.description, f"{code}: missing description"
        assert entry.script_module, f"{code}: missing script_module"
        assert entry.script_module.startswith("scripts.marcus_capabilities."), entry.script_module
        assert entry.markdown_path.is_file(), f"{code}: markdown file missing"


def test_get_returns_entry() -> None:
    """Registry lookup API returns a RegistryEntry for known codes."""
    entry = get("PR-PF")
    assert entry.code == "PR-PF"
    assert entry.full_or_stub == "full"


def test_get_raises_unknown_capability_on_typo() -> None:
    """AC-T.8: router raises UnknownCapability on typo or empty string."""
    with pytest.raises(UnknownCapability):
        get("PR-PFT")  # typo
    with pytest.raises(UnknownCapability):
        get("")  # empty
    with pytest.raises(UnknownCapability):
        get("HC")  # single-letter built-in namespace (not in PR-* registry)


def test_cross_reference_audit_clean() -> None:
    """AC-T.9: registry-schema cross-reference — markdown, yaml, schema all align.

    Clean state after Task 1 completes: zero findings.
    """
    findings = cross_reference_audit()
    assert findings == [], f"registry/schema/markdown skew detected: {findings}"
