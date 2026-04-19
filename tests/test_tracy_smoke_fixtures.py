"""Smoke-fixture tests for Story 28-4 Tracy regression artifacts."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from scripts.utilities.tracy_vocab_lockstep import validate_suggested_resources


def _load_smoke_fixtures_module():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "skills"
        / "bmad_agent_tracy"
        / "scripts"
        / "smoke_fixtures.py"
    )
    spec = importlib.util.spec_from_file_location("tracy_smoke_fixtures", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SMOKE_FIXTURES = _load_smoke_fixtures_module()
TRACY_SMOKE_FIXTURE_DIR = SMOKE_FIXTURES.TRACY_SMOKE_FIXTURE_DIR
list_tracy_smoke_fixtures = SMOKE_FIXTURES.list_tracy_smoke_fixtures
load_tracy_smoke_fixture = SMOKE_FIXTURES.load_tracy_smoke_fixture


def test_list_tracy_smoke_fixtures_returns_canonical_order() -> None:
    assert list_tracy_smoke_fixtures() == (
        "embellish_examples",
        "corroborate_supporting",
        "corroborate_contrasting",
        "gap_fill_background",
    )


def test_load_tracy_smoke_fixture_round_trips_catalog() -> None:
    for fixture_name in list_tracy_smoke_fixtures():
        fixture = load_tracy_smoke_fixture(fixture_name)

        assert fixture["fixture_id"] == fixture_name
        assert "brief" in fixture
        assert "result" in fixture


def test_tracy_smoke_results_validate_against_schema() -> None:
    for fixture_name in list_tracy_smoke_fixtures():
        fixture = load_tracy_smoke_fixture(fixture_name)
        assert validate_suggested_resources(fixture["result"])


def test_tracy_smoke_suite_covers_all_three_postures() -> None:
    postures = {
        load_tracy_smoke_fixture(name)["result"]["posture"]
        for name in list_tracy_smoke_fixtures()
    }

    assert postures == {"embellish", "corroborate", "gap-fill"}


def test_corroborate_smoke_suite_covers_supporting_and_contrasting() -> None:
    corroborate_classifications = {
        load_tracy_smoke_fixture(name)["result"]["output"]["classification"]
        for name in list_tracy_smoke_fixtures()
        if load_tracy_smoke_fixture(name)["result"]["posture"] == "corroborate"
    }

    assert corroborate_classifications == {"supporting", "contrasting"}


def test_tracy_smoke_fixture_brief_matches_result_posture() -> None:
    for fixture_name in list_tracy_smoke_fixtures():
        fixture = load_tracy_smoke_fixture(fixture_name)
        brief = fixture["brief"]
        posture = fixture["result"]["posture"]

        if posture == "embellish":
            assert brief["gap_type"] == "enrichment"
        elif posture == "corroborate":
            assert brief["gap_type"] == "evidence"
        else:
            assert brief["gap_type"] == "missing_concept"


def test_gap_fill_smoke_fixture_remains_in_scope() -> None:
    fixture = load_tracy_smoke_fixture("gap_fill_background")

    assert fixture["brief"]["scope_decision"] == "in-scope"


def test_tracy_smoke_fixture_dir_is_repo_stable() -> None:
    assert TRACY_SMOKE_FIXTURE_DIR.is_dir()
    assert TRACY_SMOKE_FIXTURE_DIR.name == "tracy_smoke"
    assert TRACY_SMOKE_FIXTURE_DIR.as_posix().endswith("tests/fixtures/retrieval/tracy_smoke")
