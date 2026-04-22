"""T12 AC-T.6 — pipeline-integration smoke test.

Asserts the v4.2 pack (both generator template and regenerated pack file)
invokes the Pass 2 emission lint at end of §08 so failing lint blocks §08B
Storyboard B render.

Automated per story §7.1 AC-T.6 — structurally guards against the lint
invocation being removed from the pack during a future refactor.
"""

from __future__ import annotations

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
PACK_FILE = (
    _REPO_ROOT
    / "docs"
    / "workflow"
    / "production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md"
)
TEMPLATE_FILE = (
    _REPO_ROOT
    / "scripts"
    / "generators"
    / "v42"
    / "templates"
    / "sections"
    / "08-irene-pass-2-segment-manifest.md.j2"
)


def test_pack_invokes_pass_2_emission_lint_in_section_08():
    pack = PACK_FILE.read_text(encoding="utf-8")
    assert "scripts/validators/pass_2_emission_lint.py" in pack
    assert "motion-gate-receipt" in pack


def test_pack_declares_lint_as_fail_closed_gate_before_storyboard_b():
    pack = PACK_FILE.read_text(encoding="utf-8")
    # Anchor text: the lint section must precede §08B Storyboard B.
    lint_idx = pack.find("pass_2_emission_lint")
    storyboard_b_idx = pack.find("08B) Storyboard B")
    assert 0 < lint_idx < storyboard_b_idx, (
        "Lint invocation must appear in §08 BEFORE §08B Storyboard B "
        "(so lint can block §08B on failure)"
    )


def test_pack_documents_all_three_finding_kinds():
    pack = PACK_FILE.read_text(encoding="utf-8")
    # Operators must know what exit-1 findings mean — all three §7.1 kinds
    # should be referenced.
    for marker in ["§6.3", "§6.4", "§6.5"]:
        assert marker in pack, (
            f"Pack §08 lint section must reference {marker} so operators "
            "know the finding vocabulary"
        )


def test_pack_documents_exit_code_discipline():
    pack = PACK_FILE.read_text(encoding="utf-8")
    # All three exit codes of the lint must be documented.
    assert "Exit 0" in pack
    assert "Exit 1" in pack
    assert "Exit 2" in pack


def test_generator_template_matches_pack_on_lint_invocation():
    """Generator template → pack regeneration → L1 lockstep check. If
    template gains the lint invocation but pack regeneration is skipped,
    the L1 check catches the drift at commit time. This test is a
    belt-and-suspenders sanity check that the template + pack agree on the
    lint command shape."""
    template = TEMPLATE_FILE.read_text(encoding="utf-8")
    pack = PACK_FILE.read_text(encoding="utf-8")
    assert "scripts/validators/pass_2_emission_lint.py" in template
    assert "scripts/validators/pass_2_emission_lint.py" in pack
