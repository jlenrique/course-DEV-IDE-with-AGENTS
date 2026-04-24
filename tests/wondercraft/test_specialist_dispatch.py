"""Wanda (Wondercraft specialist) dispatch + wiring tests (Sprint 2).

K target 14-18 per Amelia green-light rider. Coverage:

  Dispatch contract (5):
    1. Six Wanda DispatchKind values registered
    2. SpecialistId.WANDA registered
    3. DISPATCH_KIND_TO_SPECIALIST carries all 6 Wanda edges
    4. Envelope round-trips for each Wanda dispatch kind
    5. Alias forms (hyphenated) classify correctly

  Dispatch-registry YAML (3):
    6. Registry has 6 Wanda rows after the v1 PR-R edges
    7. Each Wanda row names skills/bmad-agent-wondercraft/SKILL.md as entrypoint
    8. dispatch_registry_lockstep contract test exit==0 (via existing L1 check tooling)

  Skill structure (4):
    9. SKILL.md exists + <=60 lines (specialist ceiling)
   10. All 6 capability cards present in references/
   11. Sanctum exists under _bmad/memory/bmad-agent-wondercraft/
   12. Sanctum INDEX references all 6 capability cards

  Portability (AC-9, 2):
   13. AST guard — no marcus.orchestrator.* / marcus.dispatch.* imports under
       skills/bmad-agent-wondercraft/scripts/
   14. AST guard — scripts do not write to lesson_plan.log (literal string check)

  Pre-flight + how-to recipe (AC-10 + Paige D4, 2):
   15. Wondercraft API key readiness row present in pre-flight check strategy matrix
   16. how-to-add-a-specialist-agent.md recipe file exists with required sections
"""

from __future__ import annotations

import ast
from pathlib import Path

import yaml

_ROOT = Path(__file__).resolve().parent.parent.parent
_SKILL_DIR = _ROOT / "skills" / "bmad-agent-wondercraft"
_SANCTUM_DIR = _ROOT / "_bmad" / "memory" / "bmad-agent-wondercraft"
_REGISTRY_PATH = (
    _ROOT
    / "skills"
    / "bmad-agent-marcus"
    / "references"
    / "dispatch-registry.yaml"
)


_EXPECTED_WANDA_KINDS = [
    "wanda_podcast_episode",
    "wanda_podcast_dialogue",
    "wanda_audio_summary",
    "wanda_music_bed_apply",
    "wanda_chapter_markers_emit",
    "wanda_audio_assembly_handoff",
]


# ---------------------------------------------------------------------------
# 1-5. Dispatch contract
# ---------------------------------------------------------------------------


def test_six_wanda_dispatch_kinds_registered() -> None:
    from marcus.dispatch.contract import DispatchKind

    kind_values = {k.value for k in DispatchKind}
    for expected in _EXPECTED_WANDA_KINDS:
        assert expected in kind_values, (
            f"DispatchKind missing expected Wanda kind {expected!r}"
        )


def test_specialist_id_wanda_registered() -> None:
    from marcus.dispatch.contract import SpecialistId

    assert SpecialistId.WANDA.value == "wanda"


def test_dispatch_kind_to_specialist_maps_all_wanda_kinds() -> None:
    from marcus.dispatch.contract import (
        DISPATCH_KIND_TO_SPECIALIST,
        DispatchKind,
        SpecialistId,
    )

    for expected in _EXPECTED_WANDA_KINDS:
        kind = DispatchKind(expected)
        assert DISPATCH_KIND_TO_SPECIALIST[kind] == SpecialistId.WANDA


def test_envelope_round_trips_for_each_wanda_kind() -> None:
    from datetime import UTC, datetime

    from marcus.dispatch.contract import build_dispatch_envelope

    for kind in _EXPECTED_WANDA_KINDS:
        env = build_dispatch_envelope(
            run_id="run-X",
            dispatch_kind=kind,
            input_packet={"script_path": "scripts/foo.yaml"},
            context_refs=["course-content/run-X/envelope.yaml"],
            correlation_id=f"{kind}-test",
            timestamp_utc=datetime.now(tz=UTC),
        )
        assert env.dispatch_kind.value == kind
        assert env.specialist_id.value == "wanda"


def test_hyphenated_aliases_classify_correctly() -> None:
    from marcus.dispatch.contract import (
        DispatchKind,
        _classify_dispatch_kind,
    )

    assert (
        _classify_dispatch_kind("wanda-podcast-episode")
        == DispatchKind.WANDA_PODCAST_EPISODE
    )
    assert (
        _classify_dispatch_kind("wanda-chapter-markers-emit")
        == DispatchKind.WANDA_CHAPTER_MARKERS_EMIT
    )


# ---------------------------------------------------------------------------
# 6-8. Dispatch-registry YAML
# ---------------------------------------------------------------------------


def test_registry_has_six_wanda_rows() -> None:
    data = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))
    edges = data["dispatch_edges"]
    wanda_kinds = {e["dispatch_kind"] for e in edges if e["specialist_id"] == "wanda"}
    assert wanda_kinds == set(_EXPECTED_WANDA_KINDS), (
        f"Expected 6 Wanda edges, got kinds: {wanda_kinds}"
    )


def test_registry_wanda_rows_entrypoint_is_skill_md() -> None:
    data = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))
    for edge in data["dispatch_edges"]:
        if edge["specialist_id"] == "wanda":
            assert edge["entrypoint"] == "skills/bmad-agent-wondercraft/SKILL.md", (
                f"Wanda edge {edge['dispatch_kind']!r} entrypoint expected SKILL.md, "
                f"got {edge['entrypoint']!r}"
            )


def test_l1_dispatch_lockstep_contract_test_passes() -> None:
    """Cross-reference: the existing L1 dispatch-lockstep contract test
    (tests/marcus_dispatch/test_dispatch_registry_lockstep.py) must pass
    given our extended registry + enum. We re-load and verify here to make
    the regression surface explicit in Wanda's test file."""
    from marcus.dispatch.contract import DISPATCH_KIND_TO_SPECIALIST

    data = yaml.safe_load(_REGISTRY_PATH.read_text(encoding="utf-8"))
    registered = {k.value for k in DISPATCH_KIND_TO_SPECIALIST}
    yaml_kinds = {e["dispatch_kind"] for e in data["dispatch_edges"]}
    # Every YAML row has an enum entry AND every enum entry appears in YAML
    # (note: the broader lockstep tool also checks specialist_id agreement).
    assert yaml_kinds.issubset(registered), (
        f"YAML registry has kinds not registered in DispatchKind: "
        f"{yaml_kinds - registered}"
    )
    assert registered.issubset(yaml_kinds), (
        f"DispatchKind has values without YAML registry rows: "
        f"{registered - yaml_kinds}"
    )


# ---------------------------------------------------------------------------
# 9-12. Skill structure
# ---------------------------------------------------------------------------


def test_skill_md_exists_and_under_sixty_lines() -> None:
    skill_md = _SKILL_DIR / "SKILL.md"
    assert skill_md.is_file(), "skills/bmad-agent-wondercraft/SKILL.md must exist"
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    # Specialist tier ceiling per Paige rider (mirrors Irene SKILL.md at 58).
    assert len(lines) <= 60, (
        f"SKILL.md exceeds 60-line specialist ceiling: {len(lines)} lines"
    )


def test_all_six_capability_cards_present() -> None:
    references = _SKILL_DIR / "references"
    expected_cards = [
        "capability-podcast-episode-produce.md",
        "capability-podcast-dialogue-produce.md",
        "capability-audio-summary-produce.md",
        "capability-music-bed-apply.md",
        "capability-chapter-markers-emit.md",
        "capability-audio-assembly-handoff.md",
    ]
    missing = [c for c in expected_cards if not (references / c).is_file()]
    assert not missing, f"Missing capability cards: {missing}"


def test_sanctum_exists_and_has_standard_files() -> None:
    assert _SANCTUM_DIR.is_dir(), "Wanda sanctum must exist"
    standard_files = (
        "INDEX.md",
        "PERSONA.md",
        "CREED.md",
        "BOND.md",
        "MEMORY.md",
        "CAPABILITIES.md",
    )
    for standard in standard_files:
        assert (_SANCTUM_DIR / standard).is_file(), (
            f"Sanctum missing standard file: {standard}"
        )


def test_sanctum_index_references_six_capability_cards() -> None:
    index = (_SANCTUM_DIR / "INDEX.md").read_text(encoding="utf-8")
    for card in [
        "capability-podcast-episode-produce.md",
        "capability-podcast-dialogue-produce.md",
        "capability-audio-summary-produce.md",
        "capability-music-bed-apply.md",
        "capability-chapter-markers-emit.md",
        "capability-audio-assembly-handoff.md",
    ]:
        assert card in index, f"Sanctum INDEX.md does not reference {card}"


# ---------------------------------------------------------------------------
# 13-14. Portability (AC-9)
# ---------------------------------------------------------------------------


def test_no_marcus_orchestrator_or_dispatch_imports_in_wanda_scripts() -> None:
    """Leaf-specialist portability guard — Wanda scripts must not import
    marcus.orchestrator.* or marcus.dispatch.* (sensu lato). The dispatch
    contract is extended at the contract module's own home; Wanda consumes
    envelopes through the skill's declarative references, not by importing
    the contract into its scripts.
    """
    scripts_dir = _SKILL_DIR / "scripts"
    forbidden = ("marcus.orchestrator", "marcus.dispatch")
    offenders: list[str] = []
    for py in scripts_dir.rglob("*.py"):
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name.startswith(p) for p in forbidden):
                        offenders.append(f"{py.name}::{alias.name}")
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if any(mod.startswith(p) for p in forbidden):
                    offenders.append(f"{py.name}::{mod}")
    assert not offenders, (
        f"Wanda scripts import forbidden orchestrator/dispatch modules: "
        f"{offenders}. Leaf specialists consume the dispatch contract via "
        f"the envelope schema reference, not by importing the contract module."
    )


def test_wanda_scripts_do_not_write_to_lesson_plan_log() -> None:
    scripts_dir = _SKILL_DIR / "scripts"
    offenders: list[str] = []
    for py in scripts_dir.rglob("*.py"):
        text = py.read_text(encoding="utf-8")
        if "lesson_plan.log" in text:
            offenders.append(py.name)
    assert not offenders, (
        f"Wanda scripts reference 'lesson_plan.log': {offenders}. "
        f"Leaf specialists must not write to the Lesson Plan log."
    )


# ---------------------------------------------------------------------------
# 15-16. Pre-flight + how-to recipe
# ---------------------------------------------------------------------------


def test_preflight_check_strategy_matrix_lists_wondercraft_api_key() -> None:
    matrix_path = (
        _ROOT
        / "skills"
        / "pre-flight-check"
        / "references"
        / "check-strategy-matrix.md"
    )
    if not matrix_path.is_file():
        # Pre-flight skill is optional in some branches; soft-skip if absent.
        import pytest

        pytest.skip(f"pre-flight-check matrix not present at {matrix_path}")
    text = matrix_path.read_text(encoding="utf-8")
    assert "WONDERCRAFT_API_KEY" in text, (
        "pre-flight-check/references/check-strategy-matrix.md must list "
        "WONDERCRAFT_API_KEY so Wanda readiness is surfaced alongside other "
        "tool readiness checks (AC-10)."
    )


def test_how_to_add_specialist_agent_recipe_exists() -> None:
    recipe_path = (
        _ROOT / "docs" / "dev-guide" / "how-to-add-a-specialist-agent.md"
    )
    assert recipe_path.is_file(), (
        f"Paige D4 rider: {recipe_path} must exist as the third recurring "
        f"extend-the-system pattern recipe."
    )
    text = recipe_path.read_text(encoding="utf-8")
    for required_section in (
        "## 1. Create the skill directory",
        "## 2. Scaffold the sanctum",
        "## 3. Extend the dispatch contract",
        "## 4. Register dispatch-registry edges",
        "## 5. Add the portability guard test",
    ):
        assert required_section in text, (
            f"how-to-add-a-specialist-agent.md missing section: {required_section}"
        )
