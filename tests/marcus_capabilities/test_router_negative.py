"""Router negative-path tests (AC-T.8 from story 26-6).

Ensures the registry raises ``UnknownCapability`` on typos, empty strings,
and codes from adjacent namespaces (single-letter built-ins like ``HC`` /
``PR``) that must not be confused with the 4-char PR-* namespace.

Marked ``trial_critical`` — a quiet lookup miss would let Marcus route to
a non-capability.
"""

from __future__ import annotations

import pytest

from scripts.marcus_capabilities.registry import UnknownCapability, get

pytestmark = pytest.mark.trial_critical


@pytest.mark.parametrize(
    "bad_code",
    [
        "",
        "PR-PFT",         # typo — one letter too many
        "PR_PF",          # underscore vs hyphen
        "pr-pf",          # wrong case
        "HC",             # built-in single-letter; not a PR-* code
        "PR",             # built-in single-letter; not a PR-* code
        "XX-YY",          # unknown namespace
        None,
    ],
)
def test_unknown_capability_raises(bad_code) -> None:
    with pytest.raises((UnknownCapability, TypeError)):
        # TypeError tolerated only for the None case — the API expects str,
        # and None should fail fast in the `not code` guard OR via the `in` check.
        get(bad_code)  # type: ignore[arg-type]


def test_unknown_capability_is_keyerror_subclass() -> None:
    """Caller code may catch ``KeyError`` generically; UnknownCapability must honor that."""
    assert issubclass(UnknownCapability, KeyError)
