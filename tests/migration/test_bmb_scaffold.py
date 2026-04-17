"""
Tests for the Epic 26 BMB sanctum scaffold (scripts/bmb_agent_migration/init_sanctum.py).

Covers:
- Dry-run exits 0 and enumerates the plan.
- Real run creates the expected sanctum tree.
- Scaffold is idempotent (re-running against existing sanctum exits 0).
- Texas parity: running the generic scaffold against the Texas skill dir in an
  isolated tmp_path produces a sanctum shape consistent with the canonical
  `_bmad/memory/bmad-agent-texas/`.
- Marcus BMB frontmatter shape (after migration).
- Activation smoke: every `skills/bmad-agent-marcus/scripts/*.py` still imports cleanly.
"""
from __future__ import annotations

import importlib.util
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAFFOLD = REPO_ROOT / "scripts" / "bmb_agent_migration" / "init_sanctum.py"
TEXAS_SKILL = REPO_ROOT / "skills" / "bmad-agent-texas"
MARCUS_SKILL = REPO_ROOT / "skills" / "bmad-agent-marcus"
IRENE_SKILL = REPO_ROOT / "skills" / "bmad-agent-content-creator"
CANONICAL_TEXAS_SANCTUM = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-texas"

REQUIRED_SANCTUM_FILES = {
    "INDEX.md",
    "PERSONA.md",
    "CREED.md",
    "BOND.md",
    "MEMORY.md",
    "CAPABILITIES.md",
}


def _run_scaffold(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = {"PYTHONIOENCODING": "utf-8"}
    import os
    env = {**os.environ, **env}
    return subprocess.run(
        [sys.executable, str(SCAFFOLD), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(cwd) if cwd else None,
    )


def test_scaffold_script_exists():
    assert SCAFFOLD.exists(), f"scaffold missing at {SCAFFOLD}"


def test_scaffold_refuses_missing_skill_path(tmp_path):
    result = _run_scaffold(["--skill-path", str(tmp_path / "nonexistent")])
    assert result.returncode == 2
    assert "does not exist" in result.stderr


def test_scaffold_refuses_skill_dir_without_skill_md(tmp_path):
    (tmp_path / "assets").mkdir()
    result = _run_scaffold(["--skill-path", str(tmp_path)])
    assert result.returncode == 2
    assert "no SKILL.md" in result.stderr


def test_scaffold_dry_run_texas_smoke():
    """Dry-run against the real Texas skill dir must exit 0 and enumerate templates + refs."""
    result = _run_scaffold(["--skill-path", str(TEXAS_SKILL), "--dry-run"])
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    assert "bmad-agent-texas" in result.stdout
    # Texas has 6 templates in assets/ per the canonical pattern
    assert "PERSONA-template.md" in result.stdout
    assert "CREED-template.md" in result.stdout


def test_scaffold_dry_run_marcus_smoke():
    """Dry-run against the real Marcus skill dir must exit 0 (post-migration)."""
    # This test is active once Marcus has been migrated — i.e. has assets/.
    if not (MARCUS_SKILL / "assets").exists():
        pytest.skip("Marcus migration not yet complete (no assets/ dir)")
    result = _run_scaffold(["--skill-path", str(MARCUS_SKILL), "--dry-run"])
    assert result.returncode == 0, result.stderr
    assert "DRY RUN" in result.stdout
    assert "bmad-agent-marcus" in result.stdout


def test_scaffold_texas_parity_in_isolated_sandbox(tmp_path):
    """
    Run the generic scaffold against a copy of the Texas skill dir in an
    isolated fake repo. The resulting sanctum must have all six core sanctum
    files and a content-preserving set of references/scripts.
    """
    # Set up fake repo: .git marker + _bmad/ + skills/bmad-agent-texas/
    fake_repo = tmp_path / "fake-repo"
    (fake_repo / ".git").mkdir(parents=True)
    (fake_repo / "_bmad").mkdir()
    skill_copy = fake_repo / "skills" / "bmad-agent-texas"
    skill_copy.parent.mkdir(parents=True)
    shutil.copytree(TEXAS_SKILL, skill_copy)

    # Run scaffold
    result = _run_scaffold([
        "--skill-path", str(skill_copy),
        "--project-root", str(fake_repo),
    ])
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"

    sanctum = fake_repo / "_bmad" / "memory" / "bmad-agent-texas"
    assert sanctum.is_dir()

    # All six core files present
    present = {p.name for p in sanctum.iterdir() if p.is_file()}
    missing = REQUIRED_SANCTUM_FILES - present
    assert not missing, f"missing sanctum files: {missing}"

    # Subdirectories present
    assert (sanctum / "sessions").is_dir()
    assert (sanctum / "capabilities").is_dir()
    assert (sanctum / "references").is_dir()
    assert (sanctum / "scripts").is_dir()

    # References copied (first-breath.md should NOT be in the sanctum — skill-only)
    sanctum_refs = {p.name for p in (sanctum / "references").iterdir()}
    assert "first-breath.md" not in sanctum_refs, \
        "first-breath.md must stay in skill bundle, not migrate to sanctum"
    assert "memory-guidance.md" in sanctum_refs
    assert "capability-authoring.md" in sanctum_refs

    # Scripts copied (init-sanctum.py excluded)
    sanctum_scripts = {p.name for p in (sanctum / "scripts").iterdir()}
    assert "init-sanctum.py" not in sanctum_scripts
    # Texas has domain scripts
    assert any(p.endswith(".py") for p in sanctum_scripts)

    # CAPABILITIES.md enumerates built-ins
    caps = (sanctum / "CAPABILITIES.md").read_text(encoding="utf-8")
    assert "# Capabilities" in caps
    assert "## Built-in" in caps


def test_scaffold_idempotent(tmp_path):
    """Running the scaffold twice against the same skill dir must not error or overwrite."""
    fake_repo = tmp_path / "fake-repo"
    (fake_repo / ".git").mkdir(parents=True)
    (fake_repo / "_bmad").mkdir()
    skill_copy = fake_repo / "skills" / "bmad-agent-texas"
    skill_copy.parent.mkdir(parents=True)
    shutil.copytree(TEXAS_SKILL, skill_copy)

    first = _run_scaffold([
        "--skill-path", str(skill_copy),
        "--project-root", str(fake_repo),
    ])
    assert first.returncode == 0

    second = _run_scaffold([
        "--skill-path", str(skill_copy),
        "--project-root", str(fake_repo),
    ])
    assert second.returncode == 0
    assert "already exists" in second.stdout or "already been born" in second.stdout


def test_marcus_skill_md_has_bmb_frontmatter():
    """Post-migration, Marcus's SKILL.md must have valid BMB frontmatter."""
    skill_md = MARCUS_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    # Frontmatter must be present
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    # Must have name + description
    fm_end = text.index("\n---", 4)
    frontmatter = text[4:fm_end]
    assert "name:" in frontmatter
    assert "description:" in frontmatter
    # name should be bmad-agent-marcus
    assert "bmad-agent-marcus" in frontmatter


def test_marcus_skill_md_is_bmb_conformant():
    """
    Post-migration, Marcus's SKILL.md must meet AC A1:
    - ≤ 80 lines (orchestrator ceiling; specialists target ≤ 60, Texas is 35)
    - Contains the canonical BMB blocks + explicit sanctum path
    - Contains "Lane Responsibility" section (per docs/lane-matrix.md invariant)
    """
    skill_md = MARCUS_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Marcus migration not yet complete (no Sacred Truth block)")
    lines = text.splitlines()
    assert len(lines) <= 80, f"SKILL.md exceeds AC A1 ceiling: {len(lines)} lines (≤80)"
    required_blocks = [
        "## On Activation",
        "## Session Close",
        "## Lane Responsibility",
    ]
    for block in required_blocks:
        assert block in text, f"missing required block: {block}"
    assert "_bmad/memory/bmad-agent-marcus" in text, \
        "SKILL.md must name the sanctum path explicitly"


def test_marcus_skill_md_reference_links_resolve():
    """
    Every `./references/<name>.(md|yaml)` link in Marcus's SKILL.md must point at
    a file that actually exists. Guards against silent drift between SKILL.md
    links and the files in the bundle. Applies to all BMB-migrated agents going forward.
    """
    skill_md = MARCUS_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Marcus migration not yet complete")
    link_pattern = re.compile(r"`\./references/([A-Za-z0-9_\-\.]+\.(?:md|yaml))`")
    missing = []
    for name in set(link_pattern.findall(text)):
        target = MARCUS_SKILL / "references" / name
        if not target.exists():
            missing.append(name)
    assert not missing, f"SKILL.md links to non-existent references: {missing}"


def test_marcus_sanctum_scaffolded():
    """Post-migration, Marcus's sanctum must exist at the canonical path."""
    sanctum = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-marcus"
    if not sanctum.exists():
        pytest.skip("Marcus sanctum not yet scaffolded")
    for name in REQUIRED_SANCTUM_FILES:
        assert (sanctum / name).is_file(), f"missing sanctum file: {name}"
    assert (sanctum / "sessions").is_dir()
    assert (sanctum / "capabilities").is_dir()


def test_marcus_scripts_still_import():
    """Activation smoke: every Marcus script module must be importable (no regressions)."""
    scripts_dir = MARCUS_SKILL / "scripts"
    if not scripts_dir.exists():
        pytest.skip("Marcus scripts dir missing")
    failures = []
    for py in scripts_dir.glob("*.py"):
        if py.name in {"init-sanctum.py"}:
            continue
        spec = importlib.util.spec_from_file_location(f"marcus_{py.stem}", py)
        if spec is None or spec.loader is None:
            failures.append((py.name, "no spec"))
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001 — smoke test
            failures.append((py.name, repr(exc)))
    assert not failures, f"import failures: {failures}"


def test_marcus_legacy_sidecar_has_deprecation_banner():
    """Post-migration, marcus-sidecar/index.md must carry a deprecation pointer."""
    sidecar_index = REPO_ROOT / "_bmad" / "memory" / "marcus-sidecar" / "index.md"
    if not sidecar_index.exists():
        pytest.skip("marcus-sidecar not present")
    text = sidecar_index.read_text(encoding="utf-8")
    if "DEPRECATED" not in text:
        pytest.skip("Marcus migration not yet complete (no deprecation banner)")
    assert "bmad-agent-marcus" in text, \
        "deprecation banner must point to new sanctum path"


def test_scaffold_dry_run_irene_smoke():
    """Dry-run against the real Irene skill dir must exit 0 (post-migration)."""
    if not (IRENE_SKILL / "assets").exists():
        pytest.skip("Irene migration not yet complete (no assets/ dir)")
    result = _run_scaffold(["--skill-path", str(IRENE_SKILL), "--dry-run"])
    assert result.returncode == 0, result.stderr
    assert "bmad-agent-content-creator" in result.stdout


def test_irene_skill_md_has_bmb_frontmatter():
    """Post-migration, Irene's SKILL.md must have valid BMB frontmatter."""
    skill_md = IRENE_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    fm_end = text.index("\n---", 4)
    frontmatter = text[4:fm_end]
    assert "name:" in frontmatter
    assert "bmad-agent-content-creator" in frontmatter


def test_irene_skill_md_is_bmb_conformant():
    """Irene is specialist tier — SKILL.md ≤ 60 lines + canonical BMB blocks."""
    skill_md = IRENE_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Irene migration not yet complete (no Sacred Truth block)")
    lines = text.splitlines()
    assert len(lines) <= 60, f"SKILL.md exceeds specialist-tier ceiling: {len(lines)} lines (≤60)"
    required_blocks = [
        "## On Activation",
        "## Session Close",
        "## Lane Responsibility",
    ]
    for block in required_blocks:
        assert block in text, f"missing required block: {block}"
    assert "_bmad/memory/bmad-agent-content-creator" in text, \
        "SKILL.md must name the sanctum path explicitly"


def test_irene_skill_md_reference_links_resolve():
    """Every ./references/<name>.(md|yaml) link in Irene's SKILL.md must resolve."""
    skill_md = IRENE_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Irene migration not yet complete")
    link_pattern = re.compile(r"`\./references/([A-Za-z0-9_\-\.]+\.(?:md|yaml))`")
    missing = []
    for name in set(link_pattern.findall(text)):
        target = IRENE_SKILL / "references" / name
        if not target.exists():
            missing.append(name)
    assert not missing, f"SKILL.md links to non-existent references: {missing}"


def test_irene_sanctum_scaffolded():
    """Post-migration, Irene's sanctum must exist at the canonical path."""
    sanctum = REPO_ROOT / "_bmad" / "memory" / "bmad-agent-content-creator"
    if not sanctum.exists():
        pytest.skip("Irene sanctum not yet scaffolded")
    for name in REQUIRED_SANCTUM_FILES:
        assert (sanctum / name).is_file(), f"missing sanctum file: {name}"
    assert (sanctum / "sessions").is_dir()
    assert (sanctum / "capabilities").is_dir()


def test_irene_scripts_still_import():
    """Activation smoke: every Irene script module must be importable."""
    scripts_dir = IRENE_SKILL / "scripts"
    if not scripts_dir.exists():
        pytest.skip("Irene scripts dir missing")
    failures = []
    for py in scripts_dir.glob("*.py"):
        if py.name in {"init-sanctum.py", "__init__.py"}:
            continue
        spec = importlib.util.spec_from_file_location(f"irene_{py.stem}", py)
        if spec is None or spec.loader is None:
            failures.append((py.name, "no spec"))
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as exc:  # noqa: BLE001 — smoke test
            failures.append((py.name, repr(exc)))
    assert not failures, f"import failures: {failures}"


def test_irene_legacy_sidecar_has_deprecation_banner():
    """Post-migration, irene-sidecar/index.md must carry a deprecation pointer."""
    sidecar_index = REPO_ROOT / "_bmad" / "memory" / "irene-sidecar" / "index.md"
    if not sidecar_index.exists():
        pytest.skip("irene-sidecar not present")
    text = sidecar_index.read_text(encoding="utf-8")
    if "DEPRECATED" not in text:
        pytest.skip("Irene migration not yet complete")
    assert "bmad-agent-content-creator" in text, \
        "deprecation banner must point to new sanctum path"


def _collect_script_refs_from_agent(skill_dir: Path) -> list[tuple[Path, str]]:
    """Scan all references in a skill bundle for `./scripts/<file>.py` mentions."""
    refs_dir = skill_dir / "references"
    if not refs_dir.exists():
        return []
    pattern = re.compile(r"`\./scripts/([A-Za-z0-9_\-]+\.py)`")
    hits: list[tuple[Path, str]] = []
    for md in refs_dir.glob("*.md"):
        text = md.read_text(encoding="utf-8")
        for match in pattern.findall(text):
            hits.append((md, match))
    return hits


@pytest.mark.parametrize("agent_dir", [MARCUS_SKILL, IRENE_SKILL], ids=["marcus", "irene"])
def test_capability_stub_script_refs_resolve(agent_dir: Path):
    """
    Stubs for script-backed capabilities (e.g., Irene's PC, VR, MP, MC, MA) declare
    `./scripts/<name>.py` targets. This test guards against silent rot when scripts
    are renamed or reorganized — every such reference must resolve to an actual
    file in the same skill bundle. Covers Blind-Hunter-M2-style regressions.
    """
    if not (agent_dir / "assets").exists():
        pytest.skip(f"{agent_dir.name} migration not yet complete")
    hits = _collect_script_refs_from_agent(agent_dir)
    missing = [
        (md.name, target)
        for md, target in hits
        if not (agent_dir / "scripts" / target).exists()
    ]
    assert not missing, f"references in {agent_dir.name} cite non-existent scripts: {missing}"


def test_no_sanctum_path_references_in_skill_bundle_refs():
    """
    Post-migration, no reference file in a migrated skill bundle may name the
    legacy sidecar path (e.g., 'marcus-sidecar' or 'irene-sidecar') as a
    write target. Guards against the orphan-init.md-style regression Blind
    Hunter M1 flagged.
    """
    bad_patterns = ("marcus-sidecar", "irene-sidecar")
    failures: list[tuple[str, str, str]] = []  # (agent, file, pattern)
    for agent_dir in (MARCUS_SKILL, IRENE_SKILL):
        if not (agent_dir / "assets").exists():
            continue  # pre-migration
        refs_dir = agent_dir / "references"
        if not refs_dir.exists():
            continue
        for md in refs_dir.glob("*.md"):
            text = md.read_text(encoding="utf-8")
            for pat in bad_patterns:
                if pat in text:
                    failures.append((agent_dir.name, md.name, pat))
    assert not failures, (
        f"migrated skill bundles still reference legacy sidecar paths "
        f"(orphan init.md / memory-system.md regression): {failures}"
    )


def test_irene_all_capability_codes_discovered():
    """
    Irene has 20 documented capability codes. Scaffold dry-run must discover
    all of them (IA, LO, BT, CL, CS, AA, PQ, WD, MG, CD, SB, PC, VR, MP, MC, MA,
    SM, IB, NA, DC). CP is umbrella — not frontmatter-discovered.
    """
    if not (IRENE_SKILL / "assets").exists():
        pytest.skip("Irene migration not yet complete")
    result = _run_scaffold(["--skill-path", str(IRENE_SKILL), "--dry-run"])
    assert result.returncode == 0
    expected_codes = {"IA", "LO", "BT", "CL", "CS", "AA", "PQ", "WD", "MG",
                      "CD", "SB", "PC", "VR", "MP", "MC", "MA", "SM", "IB", "NA", "DC", "CP"}
    found = {code for code in expected_codes if f"[{code}]" in result.stdout}
    missing = expected_codes - found
    assert not missing, f"capability codes not discovered: {missing}"


def test_negative_case_missing_sanctum_routes_to_first_breath():
    """
    Negative test: if Marcus's sanctum is absent, SKILL.md must route activation
    to first-breath.md and NOT fall back silently. This guards against the
    "embedded doctrine leaks through" risk Murat flagged.
    """
    skill_md = MARCUS_SKILL / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    if "Sacred Truth" not in text:
        pytest.skip("Marcus migration not yet complete")
    # Activation block must branch on sanctum existence
    assert "first-breath.md" in text or "First Breath" in text, \
        "SKILL.md must reference first-breath pathway for no-sanctum case"
