"""AC-T.7 — Parametrized extraction-report schema compliance (Story 27-2).

Two parametrized cases:

- `version="1.0"` — legacy locator-shape directive produces a v1.0
  extraction-report with the documented field set.
- `version="1.1"` — retrieval-shape directive produces a v1.1
  extraction-report with the six additive fields populated on every
  retrieval-shape source entry.

Runs the wrangler end-to-end on an in-test fixture so schema drift in any
writer path (locator → `_write_extraction_report`; retrieval →
`_retrieval_outcomes_to_report_entries`) surfaces as a single test failure.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest
import responses
import yaml

_THIS_DIR = Path(__file__).resolve().parent
_WRANGLER_PATH = (
    _THIS_DIR.parents[1]
    / "skills"
    / "bmad-agent-texas"
    / "scripts"
    / "run_wrangler.py"
)
_LEGACY_FIXTURE_DIR = (
    _THIS_DIR.parents[1]
    / "skills"
    / "bmad-agent-texas"
    / "scripts"
    / "tests"
    / "fixtures"
    / "wrangler-golden"
)
_SCITE_FIXTURE_DIR = _THIS_DIR.parent / "fixtures" / "retrieval" / "scite"


def _load_runner() -> Any:
    spec = importlib.util.spec_from_file_location(
        "texas_run_wrangler_schema_compliance", _WRANGLER_PATH
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["texas_run_wrangler_schema_compliance"] = mod
    spec.loader.exec_module(mod)
    return mod


_runner = _load_runner()


# The set of fields required on EVERY source entry, per schema version.
_V10_SOURCE_REQUIRED = {
    "ref_id",
    "provider",
    "locator",
    "role",
    "tier",
    "tier_value",
    "passed",
    "counts",
    "structural_fidelity",
    "completeness_ratio",
    "extractor_used",
    "fetched_at",
    "evidence",
    "known_losses",
    "recommendations",
}

# v1.1 retrieval-shape: six additive fields land on every retrieval source entry.
_V11_RETRIEVAL_ADDITIVES = {
    "retrieval_intent",
    "provider_hints",
    "cross_validate",
    "source_origin",
    "tracy_row_ref",
    # convergence_signal is nullable — present but may be None for single-provider.
}


@pytest.fixture(autouse=True)
def _scite_creds(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SCITE_USER_NAME", "test-user")
    monkeypatch.setenv("SCITE_PASSWORD", "test-pass")


def _write_directive(tmp_path: Path, body: dict[str, Any]) -> Path:
    path = tmp_path / "directive.yaml"
    path.write_text(yaml.safe_dump(body, sort_keys=False), encoding="utf-8")
    return path


def _run_locator(tmp_path: Path) -> dict[str, Any]:
    bundle = tmp_path / "bundle"
    directive = _write_directive(
        tmp_path,
        {
            "run_id": "TEST-SCHEMA-V10-001",
            "sources": [
                {
                    "ref_id": "src-v10",
                    "provider": "local_file",
                    "locator": str(_LEGACY_FIXTURE_DIR / "primary.md"),
                    "role": "primary",
                    "description": "Legacy locator-shape for schema v1.0",
                    "expected_min_words": 200,
                }
            ],
        },
    )
    _runner.run(directive, bundle)
    return yaml.safe_load(
        (bundle / "extraction-report.yaml").read_text(encoding="utf-8")
    )


def _run_retrieval(tmp_path: Path) -> dict[str, Any]:
    from retrieval.scite_provider import SCITE_MCP_URL

    from tests._helpers.mcp_fixtures import jsonrpc_response

    bundle = tmp_path / "bundle"
    directive = _write_directive(
        tmp_path,
        {
            "run_id": "TEST-SCHEMA-V11-001",
            "sources": [
                {
                    "ref_id": "src-v11",
                    "role": "primary",
                    "intent": "sleep hygiene studies",
                    "provider_hints": [{"provider": "scite"}],
                    "acceptance_criteria": {"mechanical": {"min_results": 1}},
                    "iteration_budget": 3,
                }
            ],
        },
    )
    fixture = json.loads(
        (_SCITE_FIXTURE_DIR / "search_happy.json").read_text(encoding="utf-8")
    )
    with responses.RequestsMock() as rsps:
        rsps.post(SCITE_MCP_URL, json=jsonrpc_response(result=fixture))
        _runner.run(directive, bundle)
    return yaml.safe_load(
        (bundle / "extraction-report.yaml").read_text(encoding="utf-8")
    )


@pytest.mark.parametrize("version", ["1.0", "1.1"])
def test_extraction_report_schema_compliance(
    version: str, tmp_path: Path
) -> None:
    """Parametrized AC-T.7: v1.0 and v1.1 extraction-reports comply with schema."""
    report = _run_locator(tmp_path) if version == "1.0" else _run_retrieval(tmp_path)

    # Top-level envelope fields common across versions.
    for field in (
        "schema_version",
        "run_id",
        "generated_at",
        "overall_status",
        "validator_version",
        "sources",
        "cross_validation",
        "evidence_summary",
    ):
        assert field in report, f"Missing top-level field at v{version}: {field}"

    assert report["schema_version"] == version

    # Per-source field presence: version-specific.
    source = report["sources"][0]
    if version == "1.0":
        missing = _V10_SOURCE_REQUIRED - set(source.keys())
        assert not missing, f"v1.0 source entry missing fields: {sorted(missing)}"
    else:
        missing = _V11_RETRIEVAL_ADDITIVES - set(source.keys())
        assert not missing, (
            f"v1.1 retrieval source entry missing additive fields: "
            f"{sorted(missing)}"
        )
        assert source["retrieval_intent"] == "sleep hygiene studies"
        assert isinstance(source["provider_hints"], list)
        assert source["cross_validate"] is False
