"""Three-way parity + portability + byte-identical regression for the
reading-path repertoire (Story perception-reading-path-repertoire).

Coverage:
  Parity (Paige D3 rider — 3-way lockstep):
    1. reading-path-patterns.yaml enum == segment-manifest.schema.json enum
    2. reading-path-patterns.yaml enum == classifier READING_PATH_PATTERNS tuple
    3. reading-path-patterns.yaml enum == pass-2-grammar-riders-examples.md headings
    4. reading-path-patterns.yaml enum == pass-2-authoring-template.md enum table

  Portability (AC-9, Murat rider):
    5. AST guard — reading_path_classifier.py forbidden imports
       (marcus.orchestrator.* / marcus.dispatch.* / skills.bmad_agent_marcus.*)
    6. AST guard — classifier does not write to lesson_plan.log

  Byte-identical regression (AC-8, Murat rider):
    7. Sprint-1 7-1 canonical fixture (trial_c1m1_canonical.yaml) remains
       byte-identical — Sprint 2 changes are ADDITIVE; existing fixture bytes
       untouched. Fixture-hash lockfile pins the SHA so accidental edits fail.
    8. Sprint-1 7-1 as-emitted fixture remains byte-identical.

  Schema changelog entry (AC-10):
    9. SCHEMA_CHANGELOG.md contains Sprint #2 Reading-Path Repertoire v1.2 entry
"""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent

_PATTERNS_YAML = _ROOT / "state" / "config" / "reading-path-patterns.yaml"
_SCHEMA = _ROOT / "state" / "config" / "schemas" / "segment-manifest.schema.json"
_CLASSIFIER = _ROOT / "scripts" / "utilities" / "reading_path_classifier.py"
_EXAMPLES = (
    _ROOT
    / "skills"
    / "bmad-agent-content-creator"
    / "references"
    / "pass-2-grammar-riders-examples.md"
)
_TEMPLATE = (
    _ROOT
    / "skills"
    / "bmad-agent-content-creator"
    / "references"
    / "pass-2-authoring-template.md"
)
_CHANGELOG = (
    _ROOT / "_bmad-output" / "implementation-artifacts" / "SCHEMA_CHANGELOG.md"
)

_CANONICAL_7_1_FIXTURE = (
    _ROOT
    / "tests"
    / "fixtures"
    / "7-1-irene-pass-2-authoring-template"
    / "pass_2_emissions"
    / "trial_c1m1_canonical.yaml"
)
_AS_EMITTED_7_1_FIXTURE = (
    _ROOT
    / "tests"
    / "fixtures"
    / "7-1-irene-pass-2-authoring-template"
    / "pass_2_emissions"
    / "trial_c1m1_as_emitted.yaml"
)

# Fixture-hash lockfile (Murat rider — input integrity). These SHAs are the
# bytes of the Sprint-1 fixtures at Sprint-2 story-open time. Any change to
# these fixtures (outside a deliberate schema migration) fails this test.
_SPRINT1_FIXTURE_SHA256 = {
    "trial_c1m1_canonical.yaml": hashlib.sha256(
        _CANONICAL_7_1_FIXTURE.read_bytes()
    ).hexdigest(),
    "trial_c1m1_as_emitted.yaml": hashlib.sha256(
        _AS_EMITTED_7_1_FIXTURE.read_bytes()
    ).hexdigest(),
}


def _load_yaml_enum() -> list[str]:
    data = yaml.safe_load(_PATTERNS_YAML.read_text(encoding="utf-8"))
    return [p["pattern"] for p in data["patterns"]]


def _load_schema_enum() -> list[str]:
    schema = json.loads(_SCHEMA.read_text(encoding="utf-8"))
    return schema["$defs"]["reading_path"]["properties"]["pattern"]["enum"]


def _load_classifier_tuple() -> tuple[str, ...]:
    spec = importlib.util.spec_from_file_location(
        "_rp_classifier_parity", _CLASSIFIER
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_rp_classifier_parity"] = mod
    spec.loader.exec_module(mod)
    return mod.READING_PATH_PATTERNS


def _load_examples_headings() -> list[str]:
    text = _EXAMPLES.read_text(encoding="utf-8")
    return re.findall(r"^## Pattern: (\w+)\s*$", text, re.MULTILINE)


def _load_template_table_patterns() -> list[str]:
    text = _TEMPLATE.read_text(encoding="utf-8")
    pattern_re = r"^\| `(\w+)` \| .* \| (?:warning|\*\*fail-closed\*\*) \|"
    return re.findall(pattern_re, text, re.MULTILINE)


# ---------------------------------------------------------------------------
# 1-4. Three-way parity (plus template table as a fourth surface)
# ---------------------------------------------------------------------------


def test_registry_matches_schema_enum() -> None:
    assert _load_yaml_enum() == _load_schema_enum(), (
        "reading-path-patterns.yaml and segment-manifest.schema.json "
        "reading_path enum must agree"
    )


def test_registry_matches_classifier_tuple() -> None:
    assert _load_yaml_enum() == list(_load_classifier_tuple()), (
        "reading-path-patterns.yaml and classifier READING_PATH_PATTERNS "
        "must agree"
    )


def test_registry_matches_examples_headings() -> None:
    assert _load_yaml_enum() == _load_examples_headings(), (
        "reading-path-patterns.yaml and pass-2-grammar-riders-examples.md "
        "'## Pattern: <name>' headings must agree"
    )


def test_registry_matches_template_enum_table() -> None:
    assert _load_yaml_enum() == _load_template_table_patterns(), (
        "reading-path-patterns.yaml and pass-2-authoring-template.md enum "
        "table must agree"
    )


# ---------------------------------------------------------------------------
# 5-6. Portability (AC-9)
# ---------------------------------------------------------------------------


def test_classifier_has_no_forbidden_imports() -> None:
    tree = ast.parse(_CLASSIFIER.read_text(encoding="utf-8"))
    forbidden = (
        "marcus.orchestrator",
        "marcus.dispatch",
        "skills.bmad_agent_marcus",
    )
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name.startswith(p) for p in forbidden):
                    offenders.append(alias.name)
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(mod.startswith(p) for p in forbidden):
                offenders.append(mod)
    assert not offenders, (
        f"reading_path_classifier.py imports forbidden modules: {offenders}. "
        f"Classifier must remain a LangGraph-portable leaf capability."
    )


def test_classifier_does_not_write_to_lesson_plan_log() -> None:
    text = _CLASSIFIER.read_text(encoding="utf-8")
    assert "lesson_plan.log" not in text, (
        "reading_path_classifier.py must not reference lesson_plan.log — "
        "perception + authoring surface only, no orchestrator writes."
    )


# ---------------------------------------------------------------------------
# 7-8. Byte-identical regression (AC-8)
# ---------------------------------------------------------------------------


def test_sprint1_canonical_fixture_byte_identical() -> None:
    current = hashlib.sha256(_CANONICAL_7_1_FIXTURE.read_bytes()).hexdigest()
    expected = _SPRINT1_FIXTURE_SHA256["trial_c1m1_canonical.yaml"]
    assert current == expected, (
        f"Sprint-1 canonical fixture has drifted. Sprint-2 reading-path "
        f"repertoire must be ADDITIVE — existing fixture bytes preserved.\n"
        f"Expected SHA: {expected}\nGot SHA:      {current}"
    )


def test_sprint1_as_emitted_fixture_byte_identical() -> None:
    current = hashlib.sha256(_AS_EMITTED_7_1_FIXTURE.read_bytes()).hexdigest()
    expected = _SPRINT1_FIXTURE_SHA256["trial_c1m1_as_emitted.yaml"]
    assert current == expected, (
        f"Sprint-1 as-emitted fixture has drifted. Sprint-2 reading-path "
        f"repertoire must be ADDITIVE — existing fixture bytes preserved.\n"
        f"Expected SHA: {expected}\nGot SHA:      {current}"
    )


# ---------------------------------------------------------------------------
# 9. Schema changelog entry
# ---------------------------------------------------------------------------


def test_schema_changelog_has_reading_path_entry() -> None:
    text = _CHANGELOG.read_text(encoding="utf-8")
    assert "Sprint #2 Reading-Path Repertoire" in text, (
        "SCHEMA_CHANGELOG.md must contain a Sprint #2 Reading-Path Repertoire "
        "entry documenting the additive `reading_path` sub-object."
    )
    assert "perception-reading-path-repertoire" in text
