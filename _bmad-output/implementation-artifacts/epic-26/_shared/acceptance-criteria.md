# Epic 26 Shared Acceptance Criteria

**Purpose:** Single canonical AC spine referenced by every per-agent BMB sanctum migration story. When criteria tighten, fix them here once; every subsequent migration inherits.

**Invocation:** Per-agent stories include `See: _bmad-output/implementation-artifacts/epic-26/_shared/acceptance-criteria.md#<tier>-AC`. Stories add agent-specific ACs on top.

**Template version:** v0.1 (2026-04-17). Stamp worksheets with this version.

---

## Tier-A: Structural Conformance (all migrations)

**A1 — SKILL.md shape.** The migrated `skills/<agent>/SKILL.md` meets the size ceiling and contains the canonical BMB blocks.

Size ceiling (codified 2026-04-17 after Marcus pilot):
- **Orchestrator-class agent (Marcus, future meta-orchestrators):** ≤ 80 lines.
- **Specialist / manual-tool agent (Texas, Desmond, Irene, Gary, Kira, Vera, Quinn-R, …):** ≤ 60 lines (Texas is 35).

The `Lane Responsibility` section name is canonical per `docs/lane-matrix.md` — do not rename to "Lane Boundaries" or similar.

Required blocks:
- Valid BMB frontmatter (`name:`, `description:`).
- Persona opener.
- Three Laws block.
- A "Your Mission" paragraph.
- A "Sacred Truth" rebirth block.
- An "On Activation" block that branches: no-sanctum → `references/first-breath.md`; existing sanctum → batch-load `INDEX.md PERSONA.md CREED.md BOND.md MEMORY.md CAPABILITIES.md`.
- A "Session Close" block pointing to `references/memory-guidance.md`.
- Sanctum path explicit: `_bmad/memory/bmad-agent-<name>/`.
- A "Lane Responsibility" block (preserves `docs/lane-matrix.md` invariant).
- Every `./references/<name>.(md|yaml)` link in SKILL.md must resolve to an existing file (enforced by `test_marcus_skill_md_reference_links_resolve`-style test).

**A2 — Sanctum shape.** `_bmad/memory/bmad-agent-<name>/` exists and contains, post-scaffold:
- `INDEX.md`, `PERSONA.md`, `CREED.md`, `BOND.md`, `MEMORY.md`, `CAPABILITIES.md` (all non-empty).
- `sessions/` directory (with `.gitkeep` if empty).
- `capabilities/` directory (with `.gitkeep` if empty).
- `references/` subdirectory populated by the scaffold from `skills/<agent>/references/` (minus SKILL-only files).
- `scripts/` subdirectory populated by the scaffold from `skills/<agent>/scripts/` (minus `init-sanctum.py` itself).

**A3 — Template assets.** `skills/<agent>/assets/` contains six `*-template.md` files using `{user_name}`, `{birth_date}`, `{sanctum_path}`, `{project_root}` placeholders: `INDEX-template.md`, `PERSONA-template.md`, `CREED-template.md`, `BOND-template.md`, `MEMORY-template.md`, `CAPABILITIES-template.md`.

**A4 — Seed references.** `skills/<agent>/references/` contains the three BMB seed docs: `first-breath.md`, `memory-guidance.md`, `capability-authoring.md`. Existing references remain untouched (paths cemented by external callers).

**A5 — Generic scaffold wired.** `skills/<agent>/scripts/init-sanctum.py` is a thin forwarder to `scripts/bmb_agent_migration/init_sanctum.py --skill-path .`. No agent-specific branching in the generic script.

## Tier-B: Path Preservation (all migrations)

**B1 — Script paths preserved.** Every file under `skills/<agent>/scripts/*.py` (excluding newly-added `init-sanctum.py`) keeps its exact relative path. No renames, no moves. External callers must continue to resolve.

**B2 — Reference paths preserved.** Every pre-existing file under `skills/<agent>/references/*.md` keeps its exact relative path. New BMB seed refs (A4) are additive, not replacements.

**B3 — Test paths preserved.** Every file under `skills/<agent>/scripts/tests/` keeps its path. `.vscode/settings.json` and `pyproject.toml` references must continue to resolve.

**B4 — No broken external refs.** `grep -r "skills/<agent>/" docs/ scripts/ tests/ _bmad-output/` shows zero newly-broken paths. Verify with the downstream-reference map (pre-work for tier-A agents, optional for Tier-3 batch).

## Tier-C: Content Migration (agents with ≥200-line legacy SKILL.md)

**C1 — Chunk inventory.** The migration worksheet lists every non-frontmatter chunk from the legacy SKILL.md with its destination (`sanctum/PERSONA.md`, `sanctum/CREED.md`, `references/<newfile>.md`, `references/examples/<file>.md`, or "deleted — restated by BMB template").

**C2 — No duplication.** No chunk exists in two homes. If the new SKILL.md links to `references/storyboard-procedure.md`, the procedure text is not restated anywhere else.

**C3 — Link rewrite sweep.** Every reference to the old chunk location (internal docs, external agent SKILL.md files, story artifacts) is updated or confirmed still-valid. Use `grep` before commit; record result in worksheet.

## Tier-D: Validation (all migrations)

**D1 — Dry-run scaffold.** `.venv/Scripts/python scripts/bmb_agent_migration/init_sanctum.py --skill-path skills/<agent> --dry-run` exits 0 and prints the exact tree it would create.

**D2 — Real scaffold.** Running without `--dry-run` creates `_bmad/memory/bmad-agent-<agent>/` populated per A2. Idempotent: re-running against existing sanctum exits 0 without overwriting.

**D3 — Frontmatter lint.** New SKILL.md and the six sanctum files parse as valid YAML frontmatter + markdown. (Test: `tests/migration/test_bmb_frontmatter.py`.)

**D4 — Activation smoke.** In a fresh Python context, `from importlib import import_module` on every script under `skills/<agent>/scripts/*.py` succeeds (no import errors introduced by migration). SKILL.md opening section mentions the sanctum path verbatim.

**D5 — Negative test.** When `_bmad/memory/bmad-agent-<agent>/` is missing, Marcus's activation instruction explicitly routes to `references/first-breath.md` — it does **not** silently fall back to embedded doctrine. (Confirmed via grep that no doctrine survives in SKILL.md besides the canonical BMB blocks.)

**D6 — Regression suite green.** `.venv/Scripts/python -m pytest tests -v` passes at ≥ prior baseline count (919 passed, 2 skipped, 0 failed pre-migration for epic baseline).

**D7 — Contract validator clean.** `.venv/Scripts/python scripts/validate_fidelity_contracts.py` → 0 errors.

**D8 — Texas byte-identical regression (for the scaffold story, not per-agent).** The generic scaffold, given Texas's config, produces a sanctum byte-identical to `_bmad/memory/bmad-agent-texas/` minus session logs. (Test: `tests/migration/test_texas_parity.py`.)

## Tier-E: Marcus-Specific (26-1 only)

**E1 — Downstream reference map complete.** `epic-26/_shared/downstream-reference-map-marcus.md` enumerates every external reference to Marcus's SKILL.md sections (not just paths). Built before migration starts.

**E2 — Delegation contract handshake.** Marcus↔Texas delegation contract reference (`skills/bmad-agent-texas/references/delegation-contract.md`) resolves post-migration; Marcus's new SKILL.md or its refs still route the contract surface correctly.

**E3 — External specialist registry preserved.** The External Specialist Agents table from the legacy Marcus SKILL.md lands in `skills/bmad-agent-marcus/references/specialist-registry.md` (or equivalent). All rows preserved; no silent drops.

**E4 — Capability codes (CM/PR/HC/MM/SP/SM/SB) preserved.** Each capability has a canonical destination in the new structure. The worksheet records destination per code.

**E5 — Ad-hoc contract refs preserved.** `docs/ad-hoc-contract.md` lists two refs to Marcus (`mode-management.md`, `conversation-mgmt.md`). Both still resolve post-migration.

**E6 — Storyboard procedure preservation.** The Gary slide storyboard procedure block (lines 122-189 of legacy SKILL.md) lands in `skills/bmad-agent-marcus/references/storyboard-procedure.md` verbatim; new SKILL.md links to it.

## Tier-F: Documentation (all migrations)

**F1 — Migration worksheet filed.** A filled `migration-worksheet-<agent>.md` lives in `epic-26/_shared/` and records: chunk inventory, destinations, grep results, review decisions, template version stamp.

**F2 — Legacy sidecar deprecation notice.** If the agent had `_bmad/memory/<name>-sidecar/`, its `index.md` gets a deprecation banner linking to the new sanctum. Files remain for backward-compat until Epic 27 cleanup.

**F3 — bmm-workflow-status + sprint-status updated.** Epic 26 and the story key are tracked in `_bmad-output/implementation-artifacts/sprint-status.yaml` and `bmm-workflow-status.yaml`.
