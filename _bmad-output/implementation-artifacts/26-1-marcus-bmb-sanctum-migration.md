# Story 26-1: Marcus BMB Sanctum Migration (Pilot)

**Epic:** 26 — BMB Sanctum Migration
**Tier:** Pilot (validates the reusable pattern for 12-17 remaining agents)
**Status:** done
**Created:** 2026-04-17
**Closed BMAD-clean:** 2026-04-17 (layered review + remediation complete; 933/2/0 full suite, 14 migration tests, 0 contract errors)

## Story

As the platform maintainer, I want Marcus — the creative production orchestrator — to conform to the March 2026 BMAD Module Builder (bmb) sanctum pattern (as shipped with Texas), so that:
- The agent fleet runs on a single substrate (preparing for Party / LangGraph orchestration work in Epic 15/16).
- The pilot pattern (shared scaffold, shared AC, shared runbook, per-agent worksheet) is validated on the hardest case before Irene (26-2), Dan (26-3), and the remaining Tier-2/3 agents follow.

## Dependencies

- **Party-mode consensus** captured 2026-04-17 (Winston / Amelia / Murat / John / Paige) — see epic file.
- **Shared artifacts** under [epic-26/_shared/](./epic-26/_shared/) completed:
  - [acceptance-criteria.md](./epic-26/_shared/acceptance-criteria.md)
  - [runbook.md](./epic-26/_shared/runbook.md)
  - [migration-worksheet-TEMPLATE.md](./epic-26/_shared/migration-worksheet-TEMPLATE.md)
  - [downstream-reference-map-marcus.md](./epic-26/_shared/downstream-reference-map-marcus.md) (Murat pre-work)
- **Generic scaffold** at [scripts/bmb_agent_migration/init_sanctum.py](../../scripts/bmb_agent_migration/init_sanctum.py) with Texas-parity regression test.

## Acceptance Criteria

Inherits the shared spine at [epic-26/_shared/acceptance-criteria.md](./epic-26/_shared/acceptance-criteria.md) — Tiers A through F apply.

**Marcus-specific additions (Tier-E):**
- **E1** — `epic-26/_shared/downstream-reference-map-marcus.md` complete before scaffolding.
- **E2** — Marcus↔Texas delegation contract reference (`skills/bmad-agent-texas/references/delegation-contract.md`) still resolves; Marcus's new SKILL.md or its refs surface the contract routing.
- **E3** — External Specialist Agents table (legacy SKILL.md lines ~220-246) preserved in `skills/bmad-agent-marcus/references/external-specialist-registry.md`.
- **E4** — Capability codes (CM, PR, HC, MM, SP, SM, SB) preserved — each with a canonical destination in the new structure. Worksheet records.
- **E5** — Ad-hoc contract refs preserved: `docs/ad-hoc-contract.md:9-10` still resolves against `mode-management.md` + `conversation-mgmt.md`.
- **E6** — Gary slide storyboard procedure (legacy SKILL.md lines ~122-189) moved verbatim to `skills/bmad-agent-marcus/references/storyboard-procedure.md`; new SKILL.md links to it.

## Implementation Plan

Per [runbook.md](./epic-26/_shared/runbook.md):

1. **Pre-work (done):** downstream-reference map + Epic 26 shared artifacts.
2. **Worksheet:** `epic-26/_shared/migration-worksheet-marcus.md` (filled during Step 2 of runbook).
3. **Seed refs:** create `first-breath.md`, `memory-guidance.md`, `capability-authoring.md` under Marcus's references/.
4. **Template assets:** create six `assets/*-template.md` files for Marcus.
5. **Doctrine extraction:** move storyboard procedure, external specialist registry, cluster workflow knowledge into new reference files; leave existing `conversation-mgmt.md`, `mode-management.md`, etc. intact (paths cemented).
6. **New SKILL.md:** terse BMB-conformant rewrite (≤ 120 lines for orchestrator — tolerance above Texas's 35 because of capability surface).
7. **Forwarder:** `skills/bmad-agent-marcus/scripts/init-sanctum.py` — thin subprocess call into shared scaffold.
8. **Run scaffold:** produce `_bmad/memory/bmad-agent-marcus/` with all six core sanctum files.
9. **Deprecation banner:** update `_bmad/memory/marcus-sidecar/index.md`.
10. **Link-rewrite sweep:** one specific update per downstream-reference-map — `docs/dev-guide.md:566` (External Skills routing table anchor).
11. **Tests:** `tests/migration/test_bmb_scaffold.py` green (13 tests); full suite at ≥ baseline (919 passed).
12. **Worksheet closeout:** fill `during-migration-decisions`, `post-migration-verification`, template version stamp.
13. **Code review:** `bmad-code-review` (layered). Remediate MUST-FIX + SHOULD-FIX. Record in §Review Record below.
14. **Status:** `26-1-marcus-bmb-sanctum-migration: done` in sprint-status.yaml.

## Risks (Marcus-Specific)

| Risk | Mitigation |
|------|-----------|
| Pilot-debt: Marcus's scaffold shape locks in for 16 downstream migrations | Freeze scaffold to v0.1 before Marcus runs; iterate shape after 26-3 (Dan) closes |
| Marcus's 500+-line legacy SKILL.md has embedded tables that are the substrate for other agents' behavior | Tier-E5, E6 ACs enumerate preserved tables; grep sweep in Step 10 catches drift |
| `marcus-sidecar` path appears in 92 reports + 2 runtime callers | Deprecate, don't remove; verify `init_state.py` + `test_state_management.py` still resolve |
| First test of the generic scaffold against a non-Texas agent could expose Texas-specific assumptions | Test suite (`test_scaffold_texas_parity_in_isolated_sandbox`) already green; Marcus post-run adds `test_scaffold_dry_run_marcus_smoke` + `test_marcus_sanctum_scaffolded` coverage |

## Validation Evidence

- Scaffold dry-run: exit 0; enumerates 6 templates, 15 refs, 23 scripts, 7 capabilities auto-discovered
- Scaffold real-run: sanctum created with all six core files + `sessions/` + `capabilities/` + copied `references/` + copied `scripts/`. Idempotent verified.
- `tests/migration/`: **14 passed, 0 skipped, 0 failed** (was 13; added `test_marcus_skill_md_reference_links_resolve` during remediation)
- Full pytest suite: **933 passed, 2 skipped, 27 deselected, 0 failed** (baseline 919 + 14 migration tests = 933 exact)
- Contract validator (`scripts/validate_fidelity_contracts.py`): 9 files, 79 criteria, **0 errors**
- Structural walks: not re-run this session; baseline 3/3 READY preserved (no changes to structural-walk configs)

## Review Record

Layered `bmad-code-review` completed 2026-04-17 (three parallel reviewers: Blind Hunter, Edge Case Hunter, Acceptance Auditor). All MUST-FIX + high-value SHOULD-FIX remediated before closure.

| Layer | MUST-FIX | SHOULD-FIX | CONSIDER | Disposition |
|-------|----------|------------|----------|-------------|
| Blind Hunter | 3 | 5 | 1 | 3/3 MUST-FIX fixed; 4/5 SHOULD-FIX fixed; CONSIDER logged as follow-up |
| Edge Case Hunter | 5 | 10 | 10 | 5/5 MUST-FIX fixed (scaffold hardening); 4/10 SHOULD-FIX fixed (highest-leverage); rest logged as follow-up |
| Acceptance Auditor | 2 | 2 | 0 | 2/2 MUST-FIX fixed (A1 SKILL.md trim + AC tiering, F3 bmm-workflow-status); 2/2 SHOULD-FIX fixed |

**Status:** BMAD clean — all MUST-FIX remediated; high-value SHOULD-FIX remediated; remaining SHOULD-FIX + CONSIDER items logged in Epic 26 risk register for follow-up stories.

### Remediation log (MUST-FIX)

1. **Blind Hunter F1 (scaffold `.MD` transform bug):** rewrote `plan_actions` to use `tmpl.stem.replace("-template","").upper() + ".md"`. Added collision-guard that raises `ValueError` on duplicate output names.
2. **Blind Hunter F3 (overly-generic scaffold claim):** added two warnings — `len(templates) < 6` and `len(capabilities) == 0` — so downstream migrations surface shape mismatches at scaffold time, not First Breath.
3. **Blind Hunter F5 (Lane Boundaries renamed — lane-matrix invariant broken):** restored `## Lane Responsibility` section name in Marcus SKILL.md. Added AC clarification codifying the canonical name.
4. **Blind Hunter F7 (stray `.orig` file):** `validate-gary-dispatch-ready.py.orig` deleted.
5. **Edge Case Hunter CASE #20 (`SCRIPT_EXCLUSIONS` name mismatch):** broadened to `{"init-sanctum.py", "init_sanctum.py"}`.
6. **Edge Case Hunter CASE #21 (cp1252 print crash):** added `sys.stdout.reconfigure(encoding="utf-8")` at top of `main()` on Windows.
7. **Edge Case Hunter CASE #24 (template output name collision silent overwrite):** added explicit `ValueError` with the two colliding source filenames.
8. **Edge Case Hunter CASE #25 (duplicate capability code silent):** added `seen_codes` dict in `discover_capabilities` — raises with both source filenames on collision.
9. **Acceptance Auditor A1 (SKILL.md 84 > 80):** trimmed Marcus SKILL.md from 84 → 73 lines. Amended AC A1 to tier: orchestrator ≤80, specialist ≤60. Tightened `test_marcus_skill_md_is_bmb_conformant` from ≤120 → ≤80 (aligned with AC).
10. **Acceptance Auditor F3 (`bmm-workflow-status.yaml` not updated):** added Epic 26 + story 26-1 entries; updated `next_workflow_step`.

### Remediation log (high-value SHOULD-FIX)

- **Blind Hunter F6 (no link-resolution test):** added `test_marcus_skill_md_reference_links_resolve` — regex-scans SKILL.md for `./references/*.(md|yaml)` and asserts each target exists. Protects all 16 downstream migrations from broken links.
- **Blind Hunter F9 (CAPABILITIES.md `_(describe purpose)_` placeholders):** added `script_purpose()` that extracts the first-line of each script's module docstring. Regenerated Marcus's `CAPABILITIES.md` — 23 scripts now have real descriptions.
- **Edge Case Hunter CASE #28 (runbook Step 10 has no verifier):** added Step 10b with mandatory grep commands that must return zero matches.
- **Edge Case Hunter CASE #26 (runbook Step 7 forwarder diverges from Marcus's hardened version):** updated runbook to point at `skills/bmad-agent-marcus/scripts/init-sanctum.py` as the canonical template. Removed the minimal inline example.
- **Acceptance Auditor F1 (worksheet stale 78-line claim):** corrected to 73-line post-remediation.

### Follow-ups (logged, not blocking Marcus closure)

- **Blind Hunter F4 (script duplication — scripts live in both skill bundle and sanctum):** architectural question. Decision deferred to Story 26-2 (Irene) pilot: does the sanctum copy get used at runtime, or only for introspection? If not runtime, drop from scaffold.
- **Edge Case Hunter unresolved SHOULD-FIX:** Cases #2, #5, #11, #14, #16, #22, #23 — improvements to scaffold robustness. Logged in Epic 26 risk register; may bundle into a scaffold v0.2 hardening story after 2-3 agent migrations reveal which actually bite.
- **Blind Hunter F8 (branch naming):** cosmetic; user decides at merge time whether to rename `dev/trial-run-c1m1-tejal-20260417` or cherry-pick.
- **Blind Hunter F3 (Desmond pattern divergence):** Desmond scaffold rework explicitly scheduled as its own Epic 26 grace story after Tier-1/2 agents migrate.

## Closure

- Sprint-status: `26-1-marcus-bmb-sanctum-migration: done`, `epic-26: in-progress` (still open for 14+ remaining agents).
- `bmm-workflow-status.yaml`: Epic 26 block added with pilot_status tracked.
- Migration worksheet ([epic-26/_shared/migration-worksheet-marcus.md](./epic-26/_shared/migration-worksheet-marcus.md)): complete, template-version v0.1 stamped.
- Closure note: Pilot validated the reusable pattern (shared AC spine + runbook + worksheet + generic scaffold). Scaffold v0.1 is frozen for Irene (26-2) pilot; any agent-specific pressure on the scaffold shape during 26-2 triggers v0.2 proposal, not inline patches.
