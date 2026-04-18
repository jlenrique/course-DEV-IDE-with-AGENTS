"""Contract test — `schema_version` field is never absent from canonical outputs.

Amelia green-light strengthening (Story 27-0). SHOULD-FIX from code-review
2026-04-18: standalone test was specified in the green-light patch record
but not shipped in the first pass.

Two surfaces are covered:

1. The **retrieval contract** module-level constant (`retrieval.SCHEMA_VERSION`)
   must be present and track the `contracts.py`-declared value.

2. The **extraction-report envelope** constant in `run_wrangler.py`
   (`EXTRACTION_REPORT_SCHEMA_VERSION`) must be present and is emitted on every
   `extraction-report.yaml` write. These are DIFFERENT schemas — the retrieval
   contracts pin the `RetrievalIntent` / `AcceptanceCriteria` / `TexasRow`
   wire formats; the extraction-report schema pins the run_wrangler.py output
   envelope. Renaming the run_wrangler constant (from the original
   `SCHEMA_VERSION` to `EXTRACTION_REPORT_SCHEMA_VERSION`) disambiguates the
   two and is guarded here.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def test_retrieval_schema_version_constant_present() -> None:
    """`retrieval.SCHEMA_VERSION` module constant must exist and be a string."""
    from retrieval import SCHEMA_VERSION

    assert isinstance(SCHEMA_VERSION, str)
    assert SCHEMA_VERSION, "retrieval.SCHEMA_VERSION must be non-empty"
    # Pin the current value for regression detection.
    assert SCHEMA_VERSION == "1.1", (
        f"retrieval.SCHEMA_VERSION drifted from expected '1.1'; "
        f"got {SCHEMA_VERSION!r}. Update SCHEMA_CHANGELOG.md in the same commit."
    )


def test_extraction_report_schema_version_constant_present() -> None:
    """`run_wrangler.EXTRACTION_REPORT_SCHEMA_VERSION` must be non-empty."""
    module_path = (
        Path(__file__).parents[2]
        / "skills"
        / "bmad-agent-texas"
        / "scripts"
        / "run_wrangler.py"
    )
    spec = importlib.util.spec_from_file_location(
        "texas_run_wrangler_schema_version_check", module_path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texas_run_wrangler_schema_version_check"] = mod
    spec.loader.exec_module(mod)

    assert hasattr(mod, "EXTRACTION_REPORT_SCHEMA_VERSION"), (
        "run_wrangler.py must export EXTRACTION_REPORT_SCHEMA_VERSION — "
        "code-review finding M-9 (2026-04-18) required disambiguating the "
        "extraction-report envelope version from retrieval.SCHEMA_VERSION."
    )
    version = mod.EXTRACTION_REPORT_SCHEMA_VERSION
    assert isinstance(version, str) and version
    # Pin the current value for regression detection.
    assert version == "1.0", (
        f"extraction-report schema drifted from expected '1.0'; got {version!r}. "
        f"Update SCHEMA_CHANGELOG.md in the same commit."
    )


def test_retrieval_and_extraction_report_schemas_are_distinct() -> None:
    """The retrieval contract and extraction-report envelope are intentionally
    separate schemas. They may share the same major version family for
    alignment reasons, but one can bump without the other."""
    from retrieval import SCHEMA_VERSION as RETRIEVAL_VERSION

    module_path = (
        Path(__file__).parents[2]
        / "skills"
        / "bmad-agent-texas"
        / "scripts"
        / "run_wrangler.py"
    )
    spec = importlib.util.spec_from_file_location(
        "texas_run_wrangler_distinct_schemas_check", module_path
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texas_run_wrangler_distinct_schemas_check"] = mod
    spec.loader.exec_module(mod)

    # They can coincidentally match, but they must be SEPARATE constants so
    # bumping one doesn't implicitly bump the other.
    retrieval_src = (
        Path(__file__).parents[2]
        / "skills"
        / "bmad-agent-texas"
        / "scripts"
        / "retrieval"
        / "contracts.py"
    ).read_text(encoding="utf-8")
    run_wrangler_src = module_path.read_text(encoding="utf-8")
    assert 'SCHEMA_VERSION = "1.1"' in retrieval_src, (
        "retrieval/contracts.py must literally declare SCHEMA_VERSION"
    )
    assert 'EXTRACTION_REPORT_SCHEMA_VERSION = "1.0"' in run_wrangler_src, (
        "run_wrangler.py must literally declare EXTRACTION_REPORT_SCHEMA_VERSION "
        "(code-review M-9 rename discipline)"
    )
    assert RETRIEVAL_VERSION == "1.1"
    assert mod.EXTRACTION_REPORT_SCHEMA_VERSION == "1.0"
