# Next Session Start Here

> Scope note: this file is the hot-start for the next repo session.
> Current objective: Migrate Marcus from sidecar pattern to bmb sanctum pattern (re-establish Marcus as model agent).

## Current State (as of 2026-04-16 late session closeout)

- Active branch: `dev/marcus-sanctum-migration` (freshly created from `master`)
- `master` reconciled this closeout: 24-commit merge from `DEV/slides-redesign` landed cleanly (merge commit `e2be90f`); post-merge regression 567 passed; pushed to origin
- `DEV/slides-redesign` preserved on origin as historical branch
- Full repo regression: **567 passed, 0 failed**
- **Texas agent (Source Wrangler) — DONE.** Built via bmb workflow. Full sanctum pattern. 33 tests passing.
- **Progress Map evergreen hardening — DONE.** 4 fixes, 40 new tests (52 total).
- **Run HUD v2 — DONE.** Self-refreshing HTML dashboard with 3 tabs (System Health / Production Run / Dev Cycle), two-column layout, freshness meter, collapsible right panel. 38 tests passing.
- **Propagation complete**: Texas registered in agent-environment.md, session protocol, Marcus references, v4.2 prompt pack, dev-guide, user-guide, structural_walk.py, skill_module_loader.py.

## Immediate Next Action

**Migrate Marcus to the bmb sanctum pattern** — use `bmad-quick-dev` skill to restructure Marcus from monolithic SKILL.md + sidecar (4 files) to lean bootloader SKILL.md + full sanctum (6 files + sessions/ + references/ + capabilities/).

Rationale: Marcus was the first agent built, created via bmm workflow. The framework has since advanced to bmb. Texas is now on the current pattern — Marcus should be the model agent again. He's the linchpin of every production run; he deserves the latest architecture.

### Migration Scope

1. **Extract** current Marcus identity, personality, communication style, principles from `skills/bmad-agent-marcus/SKILL.md` into sanctum templates (PERSONA, CREED, BOND)
2. **Migrate** sidecar content (`_bmad/memory/marcus-sidecar/index.md`, `patterns.md`, `chronology.md`, `access-boundaries.md`) into sanctum structure (INDEX, MEMORY, CREED Dominion section, sessions/)
3. **Preserve** all scripts and references unchanged — they don't need migration, only the identity layer
4. **Update** `scripts/utilities/ad_hoc_persistence_guard.py` to recognize sanctum paths in addition to sidecar paths
5. **Update** `tests/test_state_management.py` MEMORY_ENTRIES list (Marcus row changes from `marcus-sidecar/index.md` to `bmad-agent-marcus/INDEX.md`)
6. **Update** cross-agent memory reading pattern in Marcus's references (sidecar paths → check both sidecar and sanctum)
7. **Run** full regression; ensure no production pipeline regressions
8. **Party Mode review + BMAD code review** before marking done

### Estimated Complexity

High. Marcus has the most complex SKILL.md in the system (200+ lines), 10+ reference files, 10+ scripts. The sanctum migration is primarily about **identity extraction** — scripts and references don't change.

## Key Risks / Unresolved Issues

- **Marcus migration is a linchpin change**: if anything breaks the production pipeline, the next trial run is blocked. Recommend full regression + party mode sign-off before merge.
- **Sidecar ecosystem coupling**: 16 other agents still use sidecar pattern. After Marcus, queue these for migration under Epic 15 (Learning & Compound Intelligence). See memory note `project_sanctum_migration.md`.
- **Trial run still pending**: the fresh trial run using prompt pack v4.2f (original objective at session start) was deferred in favor of Texas creation + HUD + progress map work. The 30-line stub disaster is now preventable (Texas extraction validator), but a fresh trial run is still needed to validate the end-to-end pipeline.
- **v4.2g preflight --bundle-dir**: still required on next trial run.

## Texas Agent Quick Reference

- **Location**: `skills/bmad-agent-texas/`
- **Sanctum**: `_bmad/memory/bmad-agent-texas/` (initialized via `init-sanctum.py`)
- **Core scripts**: `extraction_validator.py` (4-tier quality classification), `cross_validator.py` (section + key term matching against reference assets)
- **Capabilities**: Source Interview (SI), Extract & Validate (EV), Fallback Resolution (FR)
- **Delegation contract**: `skills/bmad-agent-texas/references/delegation-contract.md`
- **Key use case**: Use `course-content/courses/tejal-APC-C1/C1M1Part01.md` as validation asset to cross-check PDF extraction from `APC C1-M1 Tejal 2026-03-29.pdf`

## Run HUD Quick Reference

- **Generator**: `.venv/Scripts/python -m scripts.utilities.run_hud --open`
- **Output**: `reports/run-hud.html` (self-refreshing every 10s)
- **Three tabs**: System Health (preflight + MCP health) / Production Run (pipeline steps + gates) / Dev Cycle (epics/stories from progress_map)
- **Gate sidecar schema**: `state/config/schemas/gate-result-schema.yaml` — YAML files written to `{bundle}/gates/gate-{step_id}-result.yaml`

## Protocol Status

- Follows the canonical BMAD session protocol pair (`bmad-session-protocol-session-START.md` / `bmad-session-protocol-session-WRAPUP.md`).

## Branch Metadata

- Repository baseline branch: `master` (synced with `origin/master` at closeout — includes 24-commit consolidation merge `e2be90f` from `DEV/slides-redesign`)
- Next working branch: `dev/marcus-sanctum-migration` (created from master, pushed to origin with upstream set)

Resume commands:

```powershell
cd c:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS
git checkout dev/marcus-sanctum-migration
git pull origin dev/marcus-sanctum-migration
git status --short
git log --oneline -5
```

## Hot-Start Files

- `SESSION-HANDOFF.md` — backward-looking record of this session
- `skills/bmad-agent-marcus/SKILL.md` — migration source
- `skills/bmad-agent-texas/SKILL.md` — model sanctum agent (reference architecture)
- `skills/bmad-agent-desmond/` — other sanctum agent (reference)
- `.claude/skills/bmad-agent-builder/references/build-process.md` — bmb workflow reference
- `_bmad/memory/marcus-sidecar/` — source material for sanctum migration
- `_bmad-output/planning-artifacts/source-wrangler-agent-vision.md` — historical (Texas supersedes)
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `scripts/utilities/progress_map.py` — evergreen-hardened (Fix 1-4 applied)
- `scripts/utilities/run_hud.py` — HUD generator
- `reports/run-hud.html` — live HUD (open in browser)
- `tests/test_progress_map.py` — 52 tests (40 new this session)
- `tests/test_run_hud.py` — 38 tests
- `tests/agents/bmad-agent-texas/` — 33 tests
