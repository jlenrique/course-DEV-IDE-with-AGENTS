# Story 26-2: Irene BMB Sanctum Migration

**Epic:** 26 — BMB Sanctum Migration
**Tier:** Tier 1 (second pilot — stresses scaffold v0.1 against highest-iteration-churn agent)
**Status:** done
**Created:** 2026-04-17
**Closed BMAD-clean:** 2026-04-17 (layered review + remediation)
**Predecessor:** 26-1 Marcus (done 2026-04-17)

## Story

As the platform maintainer, I want Irene (`bmad-agent-content-creator`) — the instructional architect — to conform to the BMB sanctum pattern, so that:
- The highest-iteration-churn agent (per memory) validates that scaffold v0.1 survives a substantially more complex agent than Marcus.
- Content preservation on a 203-line SKILL.md with 20 capability codes, 7 artifact templates, and cluster/pedagogy/delegation doctrine proves the runbook's Tier-C chunk inventory discipline is sound for subsequent Tier-2/3 agents.
- The test pattern (activation smoke, frontmatter lint, link-resolution, negative-activation) generalizes to a specialist-class agent without scaffold changes.

## Dependencies

- [26-1 Marcus](./26-1-marcus-bmb-sanctum-migration.md) closed BMAD-clean 2026-04-17.
- Shared AC spine at [epic-26/_shared/acceptance-criteria.md](./epic-26/_shared/acceptance-criteria.md) — Tiers A-F apply; specialist tier A1 ceiling is ≤60 lines.
- Runbook at [epic-26/_shared/runbook.md](./epic-26/_shared/runbook.md) — 14 steps + 10b verifier + rollback + invariants.
- Generic scaffold at [scripts/bmb_agent_migration/init_sanctum.py](../../scripts/bmb_agent_migration/init_sanctum.py) v0.1 (frozen for this pilot).
- Pre-work: [downstream-reference-map-content-creator.md](./epic-26/_shared/downstream-reference-map-content-creator.md).

## Acceptance Criteria

Inherits the shared spine at [epic-26/_shared/acceptance-criteria.md](./epic-26/_shared/acceptance-criteria.md) — Tiers A, B, C, D, F apply (Tier-E is Marcus-specific; Irene-specific additions below under Tier-I).

**Irene-specific additions (Tier-I):**
- **I1** — 20 capability codes preserved (IA, LO, BT, CL, CS, AA, PQ, WD, MG, CD, SB, PC, VR, MP, MC, MA, SM, IB, NA, DC, CP). Worksheet records destination per code.
- **I2** — 7 artifact-template files (template-lesson-plan.md, template-slide-brief.md, template-narration-script.md, template-segment-manifest.md, template-dialogue-script.md, template-assessment-brief.md, template-first-person-explainer.md) preserved at existing paths — these are Irene's **production output templates**, NOT BMB sanctum templates. New `assets/*-template.md` files are separate.
- **I3** — Pass 2 procedure (legacy SKILL.md Steps 0-4, lines ~101-117) extracted verbatim to `references/pass-2-procedure.md`.
- **I4** — External Agents table (legacy SKILL.md lines ~150-158) preserved in `references/external-agent-registry.md` (delegation targets: Paige, Sophia, Caravaggio, editorial-review-prose, editorial-review-structure).
- **I5** — Degradation Handling block (legacy SKILL.md lines ~60-67) preserved in `references/degradation-handling.md`.
- **I6** — 10 stub capability refs created for codes without a dedicated existing ref file (LO, BT, CL, CS, PQ, PC, VR, MP, MC, MA). Each stub frontmatter-declares the code + points at the authoritative source.
- **I7** — Marcus↔Irene delegation contract still resolves (envelope schema referenced by Marcus's `external-specialist-registry.md`).

## Implementation Plan

Per [runbook.md](./epic-26/_shared/runbook.md) Steps 1-14. Applying lessons from Marcus pilot:

1. Worksheet ([migration-worksheet-content-creator.md](./epic-26/_shared/migration-worksheet-content-creator.md)) — filled during work.
2. Seed refs (first-breath, memory-guidance, capability-authoring) — tailored to specialist identity.
3. Asset templates (6 × `*-template.md`) — Irene-specific persona/creed/bond wording.
4. Doctrine extraction:
   - Pass 2 procedure → `pass-2-procedure.md`
   - External Agents table → `external-agent-registry.md`
   - Degradation handling → `degradation-handling.md`
5. Stub capability refs (10 total): `learning-objective-decomposition.md` (LO), `blooms-taxonomy-application.md` (BT), `cognitive-load-management.md` (CL), `content-sequencing.md` (CS), `delegation-intent-verification.md` (PQ), `perception-contract-enforcement.md` (PC), `visual-reference-injection.md` (VR), `motion-plan-hydration.md` (MP), `motion-perception-confirmation.md` (MC), `manual-animation-support.md` (MA).
6. Retrofit frontmatter on 10 existing refs with a canonical code (pedagogical-framework → IA, template-assessment-brief → AA, delegation-protocol → WD, template-segment-manifest → MG, cluster-decision-criteria → CD, spoken-bridging-language → SB, save-memory → SM, interstitial-brief-specification → IB, cluster-narrative-arc-schema → NA, cluster-density-controls → DC).
7. New SKILL.md (≤ 60 lines; specialist tier).
8. Forwarder using Marcus's canonical template.
9. Run scaffold.
10. Deprecate legacy `irene-sidecar` in place.
11. Link-rewrite sweep + Step 10b verifier.
12. Tests: migration suite includes new Irene coverage; full suite at ≥ post-Marcus baseline.
13. Worksheet closeout.
14. `bmad-code-review` (layered).
15. Remediate + close.

## Risks (Irene-Specific)

| Risk | Mitigation |
|------|-----------|
| Pilot debt from Marcus — scaffold v0.1 may have Irene-specific gaps | Test coverage includes `test_irene_sanctum_scaffolded` + link-resolution + negative-activation (pattern ported from Marcus) |
| 20 capability codes = 20 scaffold-discovery opportunities for mismatched frontmatter | Stub files plus frontmatter retrofit covers all 20; unique-code guard in scaffold enforces correctness |
| Pass 2 procedure is operationally load-bearing (motion, perception, cluster) | Verbatim move to `pass-2-procedure.md`; SKILL.md retains only the BMB activation branch, links to procedure for detail |
| 7 artifact templates could be confused with BMB asset templates | Worksheet Tier-I2 explicitly distinguishes; new `assets/` dir is BMB-only |
| Cluster-related refs are the highest iteration area (per memory) | Preservation is structural; no semantic rewriting. Any cluster-iteration follow-up is outside this story. |

## Validation Evidence

- Scaffold dry-run: 6 templates, 33 references, 5 scripts, **21 capabilities** (20 file-backed + CP umbrella stub) auto-discovered
- Scaffold real-run: sanctum at `_bmad/memory/bmad-agent-content-creator/` with 6 core files + sessions/ + capabilities/ + references/ (31 files after orphan cleanup) + scripts/ (5 files). Idempotent verified.
- `tests/migration/`: **25 passed, 0 skipped, 0 failed** (was 14 before Irene; +11 new Irene + cross-agent tests)
- Full pytest suite (all testpaths): **944 passed, 2 skipped, 27 deselected, 0 failed** (was 919 pre-Marcus baseline; +25 migration tests = 944 exact)
- Contract validator: **0 errors** (9 files, 79 criteria)
- Step 10b link-rewrite verifier: **clean** (1 section-anchor in Story 13.1 artifact + 1 contract-test assertion rewritten during migration)

## Review Record

Layered `bmad-code-review` completed 2026-04-17 (three parallel reviewers: Blind Hunter, Edge Case Hunter, Acceptance Auditor).

| Layer | MUST-FIX | SHOULD-FIX | CONSIDER | Disposition |
|-------|----------|------------|----------|-------------|
| Blind Hunter | 2 | 5 | 0 | 2/2 MUST-FIX fixed; 4/5 SHOULD-FIX fixed; C1 cluster-doctrine-coherence logged as follow-up |
| Edge Case Hunter | 2 (CASE3+CASE6) | 3 (CASE4+CASE5+CASE10) | 3 | 2/2 MUST-FIX fixed (stub-drift test added; orphan refs deleted from BOTH agents); SHOULD-FIX partial (cross-agent code collision logged, SKILL.md persona-name test logged) |
| Acceptance Auditor | 1 (F3) | 0 | 0 | 1/1 F3 fixed — bmm-workflow-status.yaml updated with stories map showing 26-1 done + 26-2 review→done |

**Status:** BMAD clean.

### Remediation log (MUST-FIX)

1. **BH-M1 / EC-CASE6 (orphan `init.md` + `memory-system.md` referencing legacy sidecar path):** deleted from BOTH Marcus and Irene skill bundles AND from scaffolded sanctums. Added `test_no_sanctum_path_references_in_skill_bundle_refs` migration test to prevent future regression; added new AC **B5** to the shared spine ("No legacy sidecar path references inside the migrated skill bundle"). Also fixed the stale `marcus-sidecar` reference inside Marcus's `save-memory.md` (surfaced by the new test). Same class of regression is now impossible on future agents.
2. **BH-M2 (`manual-animation-support.md` stub cited non-existent functions):** rewrote the stub's Entry-point section to reference actual module API (`generate_animation_guidance`, `import_manual_motion_asset`, `ManualAnimationError`). Added `test_capability_stub_script_refs_resolve` (parametrized per migrated agent) to catch this class going forward + new AC **B6** in the shared spine.
3. **EC-CASE3 (no test for stub-to-script drift):** same test as #2 covers this — any ref mentioning `./scripts/<file>.py` must resolve.
4. **AA-F3 (`bmm-workflow-status.yaml` not updated for 26-2):** updated with a proper `stories` map — 26-1 done, 26-2 review→done, 26-3 backlog. Fixed the recurring F3 failure pattern from Marcus.

### Remediation log (SHOULD-FIX)

- **BH-S1 (worksheet narrative reversed):** corrected the "removed bold markers" claim — bold was added to 3 bullet leads for scannability, removed from 1 line that broke a test, and one typo was fixed. Worksheet Decision 6 now enumerates all three edits honestly.
- **BH-S2 (CP umbrella missing from auto-generated CAPABILITIES.md):** created `cluster-planning.md` stub with `code: CP`, so the umbrella now auto-discovers. CAPABILITIES.md rendering matches SKILL.md prose. 21 total codes.
- **BH-S4 (artifact-template vs BMB-template distinction not in INDEX):** added prominent note in `assets/INDEX-template.md` Artifact templates section clarifying that `template-*.md` files in `references/` are production output contracts, distinct from sanctum rendering templates.
- **C3 / BH-pattern #4 ("sidecar" legacy wording in `memory-guidance.md`):** replaced "durable sidecar writes" with "durable sanctum writes" in both Marcus and Irene BMB seed refs.

### Remediation log (test additions)

- `test_capability_stub_script_refs_resolve` (parametrized per agent — catches Blind Hunter M2 class)
- `test_no_sanctum_path_references_in_skill_bundle_refs` (catches Blind Hunter M1 / Edge Case CASE 6 class)
- `test_irene_all_capability_codes_discovered` expected set extended to include CP (21 codes)

### Follow-ups (logged, not blocking Irene closure)

- **BH-S5 (contract-test fragility systemic):** Epic 26 runbook should gain a pre-migration step that enumerates tests asserting against `skills/<agent>/SKILL.md` content, so they're planned before breaking. Defer to 26-3 (Dan) pre-work.
- **BH-C1 (cluster-doctrine coherence):** cluster vocabulary is distributed across 6+ files. Add `test_cluster_doctrine_coherence.py` to guard against term drift. Defer — not migration-caused, pre-existing condition.
- **BH-C2 (Pass 2 "Interactive" direct-invocation greeting lost in migration):** minor. Can restore a one-line "Greeting" bullet in SKILL.md if needed — operator can decide.
- **EC-CASE8 (cross-agent code collisions SB/SM):** Marcus SB = storyboard-procedure; Irene SB = spoken-bridging-language. Both have SM = save-memory. Codes are intentionally per-agent-scoped today; no orchestrator dispatches by code across agents. If that changes, namespace codes (`MARCUS:SB` vs `IRENE:SB`). Logged but not acted on.
- **EC-CASE5 (persona-name vs skill-name resolution):** minor. Add a future test asserting `description:` contains the persona name + activation triggers. Defer.

## Closure

- Sprint-status: `26-2-irene-bmb-sanctum-migration: done`.
- bmm-workflow-status: `stories.26-2-...status: done` with closure date.
- Migration worksheet ([epic-26/_shared/migration-worksheet-content-creator.md](./epic-26/_shared/migration-worksheet-content-creator.md)): filled, Decision 6 narrative corrected post-review, template-version v0.1 stamped.
- Closure note: Second pilot validated scaffold v0.1 on a 2.9× more complex agent than Marcus (20 → 21 capability codes, 33 refs, 2-pass delegation model). Pattern survives. Key learning: the orphan-legacy-ref problem (init.md/memory-system.md) exists on ALL agents that predate the BMB pattern — the new AC B5 + regression test catches it uniformly going forward. Scaffold v0.1 remains frozen; Dan (26-3) pilot continues to stress-test before any scaffold v0.2 discussion.
