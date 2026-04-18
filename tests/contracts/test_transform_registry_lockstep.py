"""Contract test: transform-registry.md <-> Texas extractor code lockstep.

A lockstep-check exemption is a registry row whose Priority-1 method does
not map to a dedicated ``wrangle_local_*`` extractor — either because the
extraction is remote (URL), a fall-through (Markdown), or out-of-code
(HIL escalation). Any new registry format that does NOT meet this
exemption rule must land with a working extractor or this test fails.

Story 27-1 introduces this check as the initial pilot of AC-S6 from the
Epic 27 spine: the defect class "registry promises capability X, code
silently delivers something else" halted the 2026-04-17 APC C1-M1 Tejal
trial at Prompt 1. The DOCX drift (registry promised python-docx;
run_wrangler._fetch_source fell through to read_text_file) is now closed.

The lockstep is encoded as Python constants in this file — NOT parsed
from the registry's cross-reference footnotes. That decouples prose
evolution from test brittleness: renaming a function in code does not
require editing a prose footnote, and a stale footnote cannot silently
pass the check.
"""

from __future__ import annotations

import importlib.util
import inspect
import re
import sys
from pathlib import Path

import pytest

from scripts.utilities.file_helpers import project_root

# ---------------------------------------------------------------------------
# Registry-method -> (extractor function name, dispatch-presence probe)
# ---------------------------------------------------------------------------
#
# Keys: the Priority-1 "Method" column value (lowercased for matching) that
#   appears in a ## {Format} section of skills/bmad-agent-texas/references/
#   transform-registry.md.
# Values: (extractor_function_name_in_source_wrangler_operations,
#          regex_pattern_that_must_appear_in_run_wrangler._fetch_source_source).
#
# A format is "in scope" when its parsed Priority-1 method matches a key here.
# Out-of-scope formats must appear in LOCKSTEP_EXEMPTIONS with a reason
# string, else the test FAILS.

# Fragility signpost (Murat implementation-review SHOULD-FIX, 2026-04-17):
# The dispatch-presence regexes below match the _CURRENT_ source-text shape of
# run_wrangler._fetch_source. This is a source-inspection contract, not a
# behavioral one — if _fetch_source is refactored in any of these directions,
# update the patterns here in the same commit:
#   - Pulling a suffix into a constant: DOCX_SUFFIX = ".docx"; if suffix == DOCX_SUFFIX
#   - match/case rewrite: case ".docx":
#   - Tuple membership: if suffix in (".docx", ".docm")
#   - Method-style comparison: suffix.lower() == ".docx"
# Behavioral equivalence alone is insufficient for this lockstep check — the
# test validates that a human reading run_wrangler.py sees the registry's
# promise literally honored, not just honored-through-indirection. The
# integration test (test_docx_integration_scenario) separately proves
# end-to-end routing works.
REGISTRY_METHOD_TO_EXTRACTOR: dict[str, tuple[str, str]] = {
    # DOCX — Story 27-1 pilot (contract drift fix).
    "python-docx text extraction": (
        "wrangle_local_docx",
        r'suffix\s*==\s*["\']\.docx["\']',
    ),
    # PDF — established before 27-1.
    "pypdf (text extraction)": (
        "wrangle_local_pdf",
        r'suffix\s*==\s*["\']\.pdf["\']\s*or\s*provider\s*==\s*["\']pdf["\']',
    ),
    # Notion — established before 27-1.
    "notion mcp / rest api": (
        "wrangle_notion_page",
        r'provider\s*==\s*["\']notion["\']',
    ),
}


# ---------------------------------------------------------------------------
# Shape classification (Story 27-0 AC-C.5 + cross-reference)
# ---------------------------------------------------------------------------
#
# The retrieval-shape / locator-shape distinction introduced in Story 27-0
# lives in the sibling `test_provider_directory_locator_lockstep.py` contract
# test. That test is the bidirectional lockstep enforcer against
# `retrieval/provider_directory.py::_LOCATOR_SHAPE_DIRECTORY`.
#
# This module (transform-registry lockstep) is the original locator-shape
# drift-guard from Story 27-1 — it enforces that `transform-registry.md`
# format sections map to concrete extractor functions. The two tests serve
# different purposes:
#
#   - This test: "every format promised by transform-registry.md has a
#     working extractor wired into run_wrangler._fetch_source"
#   - Sibling: "every provider listed in the runtime directory matches the
#     RETRIEVAL_SHAPE_PROVIDERS / LOCATOR_SHAPE_PROVIDERS classification"
#
# The AC-C.5 meta-principle bears repeating here per Paige's green-light
# prose ask (Story 27-0): "A retrieval-shape exemption is a registry row
# whose extraction output originates from a remote provider call and is
# shaped by a `RetrievalIntent`; a locator-shape exemption is a registry row
# whose extraction output originates from a local filesystem locator and is
# shaped by a path/selector. The distinction lives in the input-origin axis,
# not the extractor axis."
#
# See: tests/contracts/test_provider_directory_locator_lockstep.py
# for the canonical RETRIEVAL_SHAPE_PROVIDERS / LOCATOR_SHAPE_PROVIDERS dicts.


LOCKSTEP_EXEMPTIONS: dict[str, str] = {
    # Lowercased format-name -> exemption rationale.
    # Exemption rule: a registry row whose Priority-1 method does not map to a
    # dedicated wrangle_local_* extractor — either remote (URL), fall-through
    # (Markdown), or out-of-code (HIL, Future/Placeholder).
    "html / url": (
        "remote fetch provider-name is shape-mismatched with format-name "
        "(registry 'HTML / URL' → code routes to summarize_url_for_envelope "
        "under provider='url', not the wrangle_local_* pattern)"
    ),
    "markdown (.md)": (
        "fall-through path via read_text_file — no dedicated extractor by design"
    ),
    "future (placeholder)": (
        "prose-only section enumerating planned-but-not-yet-wired formats "
        "(PPTX, XLSX/CSV, SRT/VTT, Scanned PDFs via OCR, Images via Vision API); "
        "no code expected until promotion to its own registry section"
    ),
}


# ---------------------------------------------------------------------------
# Test harness
# ---------------------------------------------------------------------------


def _registry_path() -> Path:
    return (
        project_root()
        / "skills"
        / "bmad-agent-texas"
        / "references"
        / "transform-registry.md"
    )


def _parse_registry_sections(text: str) -> list[tuple[str, str | None]]:
    """Parse the registry into [(format_name, priority_1_method), ...].

    A "section" starts at a ## heading. The Priority-1 method is the cell
    in the first data row of the first markdown table under that heading
    (Priority column == 1). Returns None for the method when no table is
    present (e.g., a prose-only section).
    """
    sections: list[tuple[str, str | None]] = []
    current_format: str | None = None
    current_method: str | None = None
    found_table_header = False
    saw_method_for_current = False

    for line in text.splitlines():
        heading_match = re.match(r"^##\s+(.+?)\s*$", line)
        if heading_match:
            # Flush previous section
            if current_format is not None:
                sections.append((current_format, current_method))
            current_format = heading_match.group(1).strip()
            current_method = None
            found_table_header = False
            saw_method_for_current = False
            continue
        if current_format is None:
            continue
        # Detect markdown table rows; the Priority-1 row is the first data row
        # after the header separator.
        stripped = line.strip()
        if stripped.startswith("|") and "Priority" in stripped and "Method" in stripped:
            found_table_header = True
            continue
        if found_table_header and re.match(r"^\|[\s-]+\|", stripped):
            # Separator row
            continue
        if (
            found_table_header
            and not saw_method_for_current
            and stripped.startswith("|")
            and not stripped.startswith("|-")
        ):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            # Match exact "1" (or "1" followed by annotation like "1 (fallback)")
            # — NOT prefix-match "10", "11", etc. (code-review Blind+Edge
            # Hunter, 2026-04-17).
            first_token = cells[0].strip().split()[0] if cells[0].strip() else ""
            if len(cells) >= 2 and first_token == "1":
                raw_method = cells[1].strip()
                # Strip all markdown backticks (registry sometimes wraps
                # only the library name in backticks, e.g. `` `pypdf` (text extraction) ``
                # → we want "pypdf (text extraction)").
                current_method = raw_method.replace("`", "").strip()
                saw_method_for_current = True

    if current_format is not None:
        sections.append((current_format, current_method))
    return sections


def _load_source_wrangler_operations():
    """Load source_wrangler_operations via the same path-based loader Texas uses."""
    module_path = (
        project_root()
        / "skills"
        / "bmad-agent-texas"
        / "scripts"
        / "source_wrangler_operations.py"
    )
    spec = importlib.util.spec_from_file_location(
        "texas_source_wrangler_operations_lockstep", module_path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texas_source_wrangler_operations_lockstep"] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_run_wrangler():
    module_path = (
        project_root()
        / "skills"
        / "bmad-agent-texas"
        / "scripts"
        / "run_wrangler.py"
    )
    spec = importlib.util.spec_from_file_location(
        "texas_run_wrangler_lockstep", module_path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texas_run_wrangler_lockstep"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def registry_sections() -> list[tuple[str, str | None]]:
    return _parse_registry_sections(_registry_path().read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def source_wrangler_module():
    return _load_source_wrangler_operations()


@pytest.fixture(scope="module")
def run_wrangler_module():
    return _load_run_wrangler()


# ---------------------------------------------------------------------------
# Main lockstep assertion (Story 27-1 AC-T.6)
# ---------------------------------------------------------------------------


def test_every_format_covered_or_exempted(
    registry_sections: list[tuple[str, str | None]],
) -> None:
    """Every ## {Format} section in transform-registry.md must either:
    (a) have a Priority-1 method that matches a REGISTRY_METHOD_TO_EXTRACTOR key, OR
    (b) have the format-name listed in LOCKSTEP_EXEMPTIONS with a rationale string.

    Any section that is neither in-scope nor documented-exempt → FAIL with an
    instructive message pointing to "add an extractor or add an exemption entry."
    This is the anti-silent-rot guard (Murat + Paige green-light patches).
    """
    in_scope_methods = {m.lower() for m in REGISTRY_METHOD_TO_EXTRACTOR}
    exempt_formats = {f.lower() for f in LOCKSTEP_EXEMPTIONS}

    unclassified: list[str] = []
    for fmt_name, method in registry_sections:
        method_l = (method or "").lower()
        fmt_l = fmt_name.lower()
        if method_l in in_scope_methods:
            continue  # covered by REGISTRY_METHOD_TO_EXTRACTOR
        if fmt_l in exempt_formats:
            continue  # covered by LOCKSTEP_EXEMPTIONS
        unclassified.append(f"'{fmt_name}' (Priority-1 method: {method!r})")

    assert not unclassified, (
        "transform-registry.md sections present but neither covered by the "
        "lockstep check nor declared exempt:\n  "
        + "\n  ".join(unclassified)
        + "\n\nAdd an extractor for each, or add a LOCKSTEP_EXEMPTIONS entry "
        "with rationale (see module docstring for the exemption rule)."
    )


def test_in_scope_extractors_importable(source_wrangler_module) -> None:
    """Every REGISTRY_METHOD_TO_EXTRACTOR value's extractor_function_name
    must be importable from source_wrangler_operations."""
    missing = [
        extractor
        for (extractor, _pattern) in REGISTRY_METHOD_TO_EXTRACTOR.values()
        if not hasattr(source_wrangler_module, extractor)
    ]
    assert not missing, (
        "Registry promises these extractor functions but source_wrangler_operations "
        "does not export them:\n  " + "\n  ".join(missing)
    )


def test_in_scope_dispatches_wired(run_wrangler_module) -> None:
    """Every REGISTRY_METHOD_TO_EXTRACTOR value's dispatch-presence regex
    must match against the source of run_wrangler._fetch_source.

    Uses inspect.getsource() rather than parsing the file textually so
    refactors that move the function within the file stay green as long as
    the dispatch logic remains inside _fetch_source."""
    fetch_source_text = inspect.getsource(run_wrangler_module._fetch_source)
    unwired: list[str] = []
    for method, (extractor, pattern) in REGISTRY_METHOD_TO_EXTRACTOR.items():
        if not re.search(pattern, fetch_source_text):
            unwired.append(
                f"method='{method}' extractor='{extractor}' "
                f"pattern={pattern!r} not found in _fetch_source"
            )
    assert not unwired, (
        "Registry promises these formats but _fetch_source lacks dispatch:\n  "
        + "\n  ".join(unwired)
    )
