# BMB Migration Worksheet — Irene (bmad-agent-content-creator)

**Template version:** v0.1
**Migration date:** 2026-04-17
**Migrator:** Claude (Opus 4.7, branch `dev/epic-26-irene-bmb-migration`)
**Story:** [26-2-irene-bmb-sanctum-migration.md](../26-2-irene-bmb-sanctum-migration.md)
**Legacy SKILL.md line count:** 203
**New SKILL.md line count:** 58 (specialist tier ≤60 ceiling)

---

## Pre-Migration Inventory

### Legacy SKILL.md Chunks

| Chunk (H2 heading) | Lines | Type | Destination | Notes |
|-------------------|-------|------|-------------|-------|
| `## Overview` | 8-16 | persona + mission | new SKILL.md opener + `assets/PERSONA-template.md` + `assets/CREED-template.md` § Mission | compressed; detail in sanctum |
| `## Lane Responsibility` | 18-22 | doctrine | new SKILL.md § Lane Responsibility (preserved canonical name per AC) + `assets/CREED-template.md` § Boundaries | |
| `## Identity` | 24-26 | persona | `assets/PERSONA-template.md` § Identity | verbatim |
| `## Communication Style` | 28-37 | persona | `assets/PERSONA-template.md` § Communication Style | verbatim |
| `## Principles` (12 items) | 39-52 | doctrine | `assets/CREED-template.md` § Core Principles | all 12 verbatim |
| `## Does Not Do` | 54-58 | doctrine | `assets/CREED-template.md` § Boundaries + new SKILL.md § Lane Responsibility (one-line consolidation) | |
| `## Degradation Handling` | 60-67 | runbook | `references/degradation-handling.md` (NEW, verbatim) | |
| `## On Activation` (Pass 1 + Pass 2 intake) | 69-90 | activation protocol | new SKILL.md § On Activation (BMB first-breath/rebirth pattern) + `references/pass-2-procedure.md` § Intake | BMB branching pattern |
| Pass 2 Steps 0-4 | 92-117 | runbook (large) | `references/pass-2-procedure.md` (NEW, verbatim) | AC I3 — near-verbatim preservation (enumerated edits: bold markers added to 3 cluster-contract bullet leads for scannability; removed from 1 line where it broke a contract-test substring match; one legacy typo "entperception-confirmed" → "perception-confirmed" fixed) |
| `## Capabilities` (20 codes) | 122-148 | capability router | new SKILL.md § Capabilities (Router) + 10 capability stub refs + 10 frontmatter retrofits | AC I1 — all 20 codes preserved |
| `### External Agents` | 150-158 | delegation table | `references/external-agent-registry.md` (NEW) | AC I4 |
| `### Delegation Protocol` (inbound/outbound envelope) | 160-191 | contract | new SKILL.md § Passes + Delegation (one-line summary) + `references/delegation-protocol.md` + `references/external-agent-registry.md` | envelope detail preserved in delegation-protocol.md (already existed); registry adds pairing context |
| `### Output Artifact Templates` (table) | 193-203 | declarative | all 7 `template-*.md` files preserved at existing paths | AC I2 — artifact templates NOT migrated to assets/ (separate concept) |

### Legacy Sidecar

| File | Lines | Disposition |
|------|-------|-------------|
| `_bmad/memory/irene-sidecar/index.md` | 32 | **deprecation banner added** pointing to `bmad-agent-content-creator` sanctum |
| `_bmad/memory/irene-sidecar/access-boundaries.md` | ~20 | content merged to `assets/CREED-template.md` § Dominion |
| `_bmad/memory/irene-sidecar/patterns.md` | stub | no merge needed |
| `_bmad/memory/irene-sidecar/chronology.md` | stub | no merge needed |

### Downstream Reference Map Summary

| Reference type | Count | Affected files |
|---------------|-------|----------------|
| Path-only (scripts/, references/) | ~135 | Tier-B AC covers (paths preserved) |
| Section-anchor | 1 | `_bmad-output/implementation-artifacts/13-1-mandatory-perception-contract.md:126` ("SKILL.md#Pass 2") — **updated to point at new `references/pass-2-procedure.md`** |
| Doctrine quote (contract test) | 1 | `tests/test_cluster_aware_pass2_contract_docs.py::test_irene_skill_documents_cluster_aware_pass2_rules` — **updated to read `references/pass-2-procedure.md`** (migration assertion) |
| Legacy sidecar path (`irene-sidecar`) | ~7 | deprecated with banner; Epic 27 cleanup |

**Link-rewrite sweep pre-count:** 1 section-anchor + 1 contract-test doctrine quote
**Link-rewrite sweep post-count (newly-broken):** 0 (Step 10b verifier clean)

---

## During-Migration Decisions

- **Decision 1 — 10 capability stub refs for codes without a dedicated ref** (LO/BT/CL/CS share `pedagogical-framework.md`; PQ shares `delegation-protocol.md`; PC/VR/MP/MC/MA are script-backed). Each stub is a thin ~15-line file with frontmatter that declares the code and a one-screen pointer to the authoritative source. Rationale: preserves 20-code granularity, satisfies scaffold's unique-code guard, avoids splitting existing refs (which would break ~75 external callers).
- **Decision 2 — 10 frontmatter retrofits on existing refs.** Each retrofit adds `name:`, `code:`, `description:` frontmatter without altering content. Conservative — preserves all existing path callers.
- **Decision 3 — CP (cluster planning) stays as umbrella-only in the capability table; no dedicated ref.** CP coordinates CD+NA+DC+IB+CS; giving it its own ref would duplicate. Documented in SKILL.md Capabilities section and in CAPABILITIES.md Tools section.
- **Decision 4 — 7 artifact-template files (`template-*.md`) stay in `references/`, not `assets/`.** These are Irene's production-output templates (lesson-plan, slide-brief, narration-script, segment-manifest, dialogue-script, assessment-brief, first-person-explainer), not BMB sanctum templates. `assets/` contains only the 6 BMB `*-template.md` files for sanctum rendering. Distinction called out in AC I2.
- **Decision 5 — Legacy sidecar deprecated, not removed.** ~7 historical-report refs + no active runtime callers. Epic 27 cleanup.
- **Decision 6 — Cluster-doctrine formatting edits during extraction (enumerated):** (a) added `**Head segments**`, `**Interstitials**`, `**Segment \`behavioral_intent\`**` bold markers to 3 bullet leads for scannability; (b) removed bold markers from ONE bullet (`**Interstitials must not introduce new concepts**`) to restore substring match for `test_cluster_aware_pass2_contract_docs.py` whose assertion crossed the bolded phrase; (c) fixed legacy typo "entperception-confirmed" → "perception-confirmed" in Step 4. Net effect: near-verbatim, not strictly verbatim. AC I3 language tightened accordingly in this worksheet. The initial claim in an earlier draft of this file mis-described the edit as "removed bold markers" — corrected post-review.

---

## Post-Migration Verification

### Scaffold Dry Run
```
$ .venv/Scripts/python skills/bmad-agent-content-creator/scripts/init-sanctum.py --dry-run
BMB Sanctum Scaffold v0.1 — DRY RUN
Skill: bmad-agent-content-creator
Target sanctum: _bmad/memory/bmad-agent-content-creator
Would render 6 templates + copy 33 reference files + copy 5 scripts
Would discover 20 capabilities via frontmatter
```

### Scaffold Real Run
```
$ .venv/Scripts/python skills/bmad-agent-content-creator/scripts/init-sanctum.py
BMB Sanctum Scaffold v0.1 — COMPLETE
```

### Sanctum Tree
```
_bmad/memory/bmad-agent-content-creator/
├── BOND.md CAPABILITIES.md CREED.md INDEX.md MEMORY.md PERSONA.md
├── capabilities/ sessions/
├── references/  (33 files)
└── scripts/     (5 files)
```

All 20 capability codes present in `CAPABILITIES.md` Built-in table.

### Step 10b Link-Rewrite Verifier
```
$ grep -rn "skills/bmad-agent-content-creator/SKILL.md#" docs/ scripts/ tests/ _bmad-output/ state/ maintenance/
(no matches — clean)
```

### Test Results
- `tests/migration/test_bmb_scaffold.py`: **22 passed, 0 skipped, 0 failed** (was 14 with Marcus; +8 new Irene tests)
- Full pytest suite (all testpaths): **941 passed, 2 skipped, 27 deselected, 0 failed** (baseline 933 + 8 Irene = 941 exact)
- Contract validator (`scripts/validate_fidelity_contracts.py`): **0 errors** (9 files, 79 criteria)

### Fixes Applied to Pre-Existing Tests/Docs

1. `tests/test_cluster_aware_pass2_contract_docs.py::test_irene_skill_documents_cluster_aware_pass2_rules` — updated to read `references/pass-2-procedure.md` (content migrated).
2. `_bmad-output/implementation-artifacts/13-1-mandatory-perception-contract.md:126` — updated section-anchor reference from `SKILL.md#Pass 2` to `references/pass-2-procedure.md`.

### Negative Test
- Scenario: Irene's sanctum absent
- Observed: `test_negative_case_missing_sanctum_routes_to_first_breath` passes. SKILL.md line 29-30 explicitly routes `no sanctum → First Breath` and line 31 states "do NOT fall back to embedded doctrine."

---

## Review Record

_(filled after `bmad-code-review` runs)_

---

## Lessons Learned

- **Scaffold v0.1 survived Irene's 20-code complexity** without modification. The warn-on-empty-caps + dedup-guards added after Marcus review paid for themselves: the scaffold correctly flagged the 3 info-only refs (cluster-workflow-knowledge, external-specialist-registry, memory-guidance clones) as carrying `name:` without `code:` — the earlier false-positive warning fix is correctly silent on these.
- **Capability stub refs are cheap and clean.** 10 stubs × ~15 lines = 150 lines of scaffolding. Preserved 20-code granularity without splitting existing refs or breaking callers. Recommend for any future agent with more than 6-8 capability codes.
- **Artifact templates vs sanctum templates is a legitimate taxonomy split.** Irene's 7 `template-*.md` files are production output contracts, NOT BMB rendering templates. Don't confuse them. Document explicitly in worksheets.
- **Markdown bold markers inside contract-asserted sentences are a hazard.** Tests that substring-match doctrine phrases break when `**word**` wraps tokens mid-sentence. Future migrations: either keep migrated doctrine verbatim (no added bold) OR update the contract test. Recommendation: verbatim is easier.
- **Step 10b link-rewrite verifier caught a real issue** (the `SKILL.md#Pass 2` anchor in Story 13.1 artifact). The Marcus pilot had zero hits on this verifier; Irene had one. Confirms the Step 10b discipline is load-bearing — not just hygiene.
- **Contract-test fragility**: tests that read agent SKILL.md for specific phrases will break on migration. Pattern for future agents: either (a) update the tests as part of migration, (b) co-locate such asserts against reference files that outlive SKILL.md rewrites, or (c) add a migration-stability AC requiring tests to assert against `references/` paths rather than SKILL.md.
- **Irene's SKILL.md size of 58 lines validates the ≤60 specialist tier.** With 20 capability codes and Pass 1 / Pass 2 / delegation seams to document, 58 lines is the practical floor for a specialist this complex. Simpler specialists can aim lower.
