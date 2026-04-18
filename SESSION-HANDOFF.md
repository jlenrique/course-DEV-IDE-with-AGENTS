# Session Handoff — 2026-04-18 (Story 27-0 Retrieval Foundation BMAD-closed + Provider Directory operator amendment)

**Session window:** 2026-04-18 ~00:00 (start anchor `b99a0b8`) → 2026-04-18 ~00:59 (wrapup).
**Branch:** `dev/epic-27-texas-intake`.
**Operator:** Juanl.

## What Was Completed

### 1. Story 27-0 Retrieval Foundation — BMAD-closed

Shape 3-Disciplined foundation landed full-stack from green-lit spec through implementation, both BMAD gates, and closure artifact updates. Scope:

**8 new retrieval modules** under `skills/bmad-agent-texas/scripts/retrieval/`:
- `contracts.py` — Pydantic v2 `RetrievalIntent`, `AcceptanceCriteria`, `TexasRow`, `ProviderHint`, `ConvergenceSignal`, `ProviderInfo`, `ProviderResult`, `RefinementLogEntry` + `SCHEMA_VERSION = "1.1"`
- `base.py` — `RetrievalAdapter` ABC (7 abstract + 2 concrete-default methods) with `__init_subclass__` auto-registry hook
- `dispatcher.py` — single-provider + multi-provider cross-validation + Model A iteration loop + `_cross_validate_merge` (structural convergence signals)
- `mcp_client.py` — hand-rolled JSON-RPC-over-HTTP (Option Y; unanimous green-light decision), library-agnostic public surface (`call_tool`, `list_tools` → dict), Basic + Bearer auth styles with lazy env resolution
- `normalize.py` + `refinement_registry.py` — canonical TexasRow helpers + flat registry with `drop_filters_in_order` default
- `fake_provider.py` — reference adapter + `make_fake_provider_class(id, rows)` helper for multi-provider cross-val tests
- `provider_directory.py` — **operator-directed amendment** (AC-B.8 / B.9 / T.9-11): runtime registry + 11 static locator-shape entries + 5 retrieval-shape placeholders including `openai_chatgpt: backlog`

**Schema v1.1 additive bump:** `extraction-report-schema.md` Changelog section with "Why minor bump" paragraph + new `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` gate artifact.

**Audience-segmented `retrieval-contract.md`:** For Tracy / For operators / For dev-agents sections; anti-pattern "DON'T X, because Y, instead Z" three-beat prose; copy-pasteable YAML example.

**CLI + integration:** `run_wrangler.py --list-providers [--shape ...] [--status ...] [--json]` short-circuits dispatch; `.cursor/mcp.json` + `.mcp.json` scite + Consensus URL entries; `CLAUDE.md` pointer section; Marcus `external-specialist-registry.md` breadcrumb (Paige green-light ask).

**Test delta: +70 collecting** (target was +34). Full suite: **1106 passed / 2 skipped / 0 failed / 2 xfailed** (baseline 1036). Ruff clean on all 27-0 code.

### 2. BMAD closure gates — both GREEN

- **Party-mode implementation review**: Winston / Amelia / Murat **GREEN**; Paige **YELLOW → GREEN** after single must-fix (operator-section `--list-providers` discovery-path pointer for env vars, since `.env.example` was blocked by repo policy).
- **bmad-code-review layered (Blind Hunter + Edge Case Hunter + Acceptance Auditor)**: 42 findings triaged.
  - **5 MUST-FIX applied**: budget=1 distinct log reason (CR-1), min_results=0 rejection (CR-2), intra-provider identity_key duplicate logging (CR-3), non-improvement abort preserves better prior (bh-m2), Marcus breadcrumb.
  - **9 SHOULD-FIX applied**: refinement_registry snapshot fixture, dead None-check removal, consistent sort ordering + populated providers_disagreeing in single-source branch, --list-providers warning on conflicting flags, EXTRACTION_REPORT_SCHEMA_VERSION rename, dual-version schema pin, schema_version_field_present test, RETRIEVAL_SHAPE_PROVIDERS cross-reference, min_results non-integer rejection.
  - **4 DISMISSED with rationale**: AC-B.7 literal dispatcher wiring (deferred to 27-2 per anti-pattern #3 shape-separation); dual-emit writer + log-stream parity + parametrized schema-compliance cascade (same rationale); anti-pattern #8 under-guarded (spec self-contradictory, flag-based branching honors both readings).
  - **~22 NITs logged to `_bmad-output/maps/deferred-work.md`**.
  - **0 MUST-FIX remaining at close.**

### 3. Forward-design discipline captured (user memory)

Three distinct parameter knobs needed for future work but not yet built:
1. **Enrichment degree** — how much research-based depth Irene aspires to add beyond SME (aspirational).
2. **Gap-filling** — content for derivative artifacts (quizzes, handouts) that SME package didn't fully cover (completeness-driven).
3. **Evidence-bolster** — corroboration of existing SME claims via cross-validation (validation-driven; natural fit for `cross_validate: true` with convergence_signal).

All three route through Irene → Tracy → Texas via the same `RetrievalIntent` contract but have different rubrics. Conflating them will leak authority-tier requirements and completeness budgets across modes. Captured in `memory/project_enrichment_vs_gap_filling_control.md` for the future epic that opens this feature surface.

### 4. Sprint / workflow tracking updates

- `sprint-status.yaml`: `27-0-retrieval-foundation: done`; `27-2-scite-ai-provider: ratified-stub (unblocked 2026-04-18, absorbs AC-B.7 cascade)`; `27-2.5-consensus-adapter: ratified-stub (unblocked, soft-blocked on 27-2)`.
- `bmm-workflow-status.yaml`: closure metadata + unblock timestamps.
- `epic-27-texas-intake-expansion.md`: roster row flipped; 27-2 scope absorbs deferred cascade.
- `27-0-retrieval-foundation.md`: Status `done`; Dev Agent Record + Review Record fully populated.
- `docs/project-context.md`: 2026-04-18 update added.
- `docs/agent-environment.md`: Texas entry enhanced with retrieval package + `--list-providers` surface.

## What Is Next

**Immediate (next session):** Open Story 27-2 (scite.ai adapter) via `bmad-create-story`. It absorbs:
- First real consumer of the `RetrievalAdapter` ABC
- AC-B.7 degenerate-case dispatcher wiring (deferred from 27-0 per anti-pattern #3)
- `docs/dev-guide.md` "how to add a provider" section
- AC-T.7 log-stream parity + malformed-DOCX exception parity tests
- Dual-emit `schema_version` writer on dispatcher path
- Parametrized `test_extraction_report_schema_compliance` over v1.0 / v1.1

**After 27-2 closes:** Open Story 27-2.5 (Consensus adapter) — first real `cross_validate: true` exercise against 27-0 foundation.

**Downstream unblock sequence:** 27-2 → 27-2.5 → 28-1 Tracy pilot re-expand (reshape banner already on spec per Round 3 consensus).

## Unresolved Issues or Risks

1. **AC-B.7 deferred to 27-2** — NOT a block for 27-0 closure, but flagged as known-drift in `reports/dev-coherence/2026-04-18-0059/harmonization-summary.md`. When 27-2 lands, the first real retrieval-shape integration will drive the dispatcher wiring + schema dual-emit + log-parity tests. If 27-2 green-light discovers the deferral rationale doesn't hold, the sub-items may need promotion to a dedicated 27-0.1 hotfix.

2. **Repo-wide ruff debt — 1565 findings** (up from handoff's "377"). All pre-existing warehouse clutter outside 27-0 scope; 27-0 code itself is ruff-clean. This is a known backlog item. Counts may reflect newly-enabled rules or simply the full-repo scan vs prior sampling. Not a blocker.

3. **~22 NIT-class code-review findings** logged to `_bmad-output/maps/deferred-work.md` batch. Polymorphic dispatch return-type, MCPFetchError/MCPConfigError taxonomy split (H-4, bh-m3/m4), HTTP redirect default (`allow_redirects=False`), identity_key mid-merge exception handling, and others. These are future-work, not regressions.

4. **Nothing committed to git yet.** Per operator preference, all 27-0 work sits uncommitted in the working tree (15 modified + 24 untracked files). Next session or a follow-on action by the operator will stage + commit. `next-session-start-here.md` Step 12 instructions assume operator chooses to commit before resuming dev work on 27-2.

5. **Three missing parameter knobs** (enrichment / gap-filling / evidence-bolster) — not blockers, but captured in user memory so the future epic that opens this surface inherits the design discipline.

## Key Lessons Learned

- **Operator amendment post-green-light is OK when additive.** The Provider Directory fold (AC-B.8 / B.9 / T.9-11) added 140 LOC + 100 LOC tests to an already-green-lit spec without invalidating the prior green-light, because the fold strictly composes with the existing contract (directory is read-surface, never feeds dispatch). Pattern for future amendments: verify architectural coherence via a brief re-review, proceed if additive.

- **Deterministic sequence fixtures > stateful mocks.** Murat's test-flakiness concern resolved cleanly by pre-scripting `rows_by_query` JSON fixtures. The dispatcher's iteration loop became a pure function over the pre-scripted sequence; zero flake risk across 60+ test runs. Pattern for 27-2+: same shape.

- **Shape separation prevents anti-pattern leak.** The distinction between retrieval-shape adapters (RetrievalAdapter subclasses) and locator-shape handlers (static directory declarations) is enforced at the ABC level — `__init_subclass__` rejects `shape != "retrieval"`. This made AC-B.7's deferral defensible: anti-pattern #3 forbids locator-shape refactor, and shape separation formalizes why.

- **Auto-registration via `__init_subclass__` + autouse test fixture = clean isolation.** The adapter registry populates at class-definition time; the pytest autouse fixture snapshots and restores per test. Tests that define inline subclasses get clean state. Same pattern extended to `_STRATEGIES` in `refinement_registry.py` during code-review remediation (SHOULD-FIX bh-h2).

- **Operator-directed backlog placeholders prevent silent directory-drop.** `openai_chatgpt: backlog` (no adapter class yet) appears in `--list-providers` output as a forward-looking entry. The `test_provider_directory_roster_placeholders.py` test guards against silent removal. Pattern for future: any story that lands in Epic 27 roster gets a directory placeholder from day one.

## Validation Summary

- **Full pytest suite**: 1106 passed / 2 skipped / 0 failed / 2 xfailed / 27 deselected (baseline 1036 → **+70** collecting; target was +34).
- **Ruff on 27-0 code**: CLEAN.
- **Sprint-status YAML regression test**: 2 passed.
- **Harmonization sweep (Step 0a)**: L1 verdict CLEAN. See `reports/dev-coherence/2026-04-18-0059/harmonization-summary.md`.
- **Party-mode implementation review**: 3 GREEN + 1 YELLOW → GREEN after Paige must-fix applied.
- **bmad-code-review layered**: 0 MUST-FIX remaining; 5 MUST-FIX + 9 SHOULD-FIX applied; 4 DISMISSED with rationale; ~22 NITs deferred.

## Content Creation Summary

N/A — this was pure system development (retrieval foundation). No course content staged or moved.

## Artifact Update Checklist

- [x] `_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md` — Status `done`; Dev Agent Record + Review Record populated.
- [x] `_bmad-output/implementation-artifacts/sprint-status.yaml` — `27-0` flipped to done; `27-2` + `27-2.5` unblocked.
- [x] `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` — closure metadata + unblock timestamps.
- [x] `_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md` — roster row flipped.
- [x] `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — NEW gate artifact.
- [x] `skills/bmad-agent-texas/references/extraction-report-schema.md` — v1.1 Changelog section.
- [x] `skills/bmad-agent-texas/references/retrieval-contract.md` — NEW audience-segmented contract doc.
- [x] `skills/bmad-agent-texas/scripts/retrieval/` — 8 new modules + updated `__init__.py`.
- [x] `skills/bmad-agent-texas/scripts/run_wrangler.py` — `--list-providers` CLI + `EXTRACTION_REPORT_SCHEMA_VERSION` rename.
- [x] `skills/bmad-agent-marcus/references/external-specialist-registry.md` — 27-0 breadcrumb (Paige ask).
- [x] `.cursor/mcp.json` + `.mcp.json` — scite + Consensus URL entries.
- [x] `CLAUDE.md` — Texas retrieval pointer section.
- [x] `pyproject.toml` + `requirements.txt` — `responses` dev-dep + pythonpath extension.
- [x] `tests/conftest.py` — retrieval-registry + refinement-strategy autouse snapshot fixture.
- [x] `tests/contracts/` — 7 new test files + 4 fixture JSONs.
- [x] `tests/` — 3 new retrieval test files + `_helpers/mcp_fixtures.py`.
- [x] `tests/contracts/test_transform_registry_lockstep.py` — RETRIEVAL_SHAPE_PROVIDERS cross-reference.
- [x] `docs/project-context.md` — 2026-04-18 update.
- [x] `docs/agent-environment.md` — Texas entry enhanced.
- [x] `next-session-start-here.md` — rewritten for 27-2 pickup.
- [x] `SESSION-HANDOFF.md` — this file.
- [x] `reports/dev-coherence/2026-04-18-0059/harmonization-summary.md` — Step 0a audit trail.

## Dev-Coherence Report

Permanent audit-trail link: [reports/dev-coherence/2026-04-18-0059/harmonization-summary.md](reports/dev-coherence/2026-04-18-0059/harmonization-summary.md)

## Memory Updates

- **New**: `memory/project_enrichment_vs_gap_filling_control.md` — three distinct parameter knobs (enrichment / gap-filling / evidence-bolster) for future epic.
