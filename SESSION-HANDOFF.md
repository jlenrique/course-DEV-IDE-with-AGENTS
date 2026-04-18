# Session Handoff — 2026-04-17 Evening (27-1 DOCX closed + Shape 3-Disciplined ratified + 27-0 Retrieval Foundation green-lit)

**Session window:** 2026-04-17 ~20:43 (start anchor `07523e0`) → 2026-04-17 ~23:20 (wrapup).
**Branch:** `dev/epic-27-texas-intake`.
**Operator:** Juanl.

## What Was Completed

### 1. Story 27-1 DOCX Provider Wiring — BMAD-closed

- **Dependency & implementation:** `python-docx>=1.1,<2` pinned in `pyproject.toml` + `requirements.txt` (installed 1.2.0). New `wrangle_local_docx()` + `extract_docx_text()` in `source_wrangler_operations.py`; `.docx` dispatch branch in `run_wrangler._fetch_source()`; `_EXTRACTOR_LABELS_BY_KIND` added; `_classify_fetch_error()` extended with module-qualified `docx.PackageNotFoundError` matching; `_fetch_error_known_losses` helper.
- **New AC-S6 pilot contract test:** `tests/contracts/test_transform_registry_lockstep.py` with assertion-encoded `LOCKSTEP_EXEMPTIONS` dict (per Murat + Paige green-light patch) — registry lockstep now DOCX + PDF + Notion (3 formats); HTML/URL + Markdown + Future-Placeholder exempted with rationale.
- **Test delta:** +9 collecting tests (5 unit T.1/T.2a/T.2b/T.3/T.4 + 1 integration T.5 + 3 contract atomic split of T.6). Baseline 1023 → 1036 passed / 2 skipped / 2 xfailed. Zero new xfails/skips/live_api/trial_critical markers.
- **Tejal manual validation (T8):** PDF↔DOCX cross-validation on halted-trial bundle → `word_count_ratio: 1.04`, **100% key-term coverage, 69/69 sections matched, verdict passed: true**. Original trial-halt defect closed.
- **Gates passed:** party-mode green-light (Winston + Amelia + Murat + Paige) → party-mode implementation review (3 SHOULD-FIX patches applied) → `bmad-code-review` layered (Blind Hunter + Edge Case Hunter + Acceptance Auditor). Code-review triage: **0 MUST-FIX, 8 patches applied, 4 deferred to follow-on, 6 dismissed**.
- **Deferred from 27-1 code review** (captured in `_bmad-output/maps/deferred-work.md`): sibling Office-ZIP suffixes (.docm/.dotx/.dotm), `<w:sdt>` / `<w:altChunk>` content drops, docstring exception completeness, Windows short-path test flakiness, negative-control Tejal fixture, `_EXTRACTOR_LABELS` dual-lookup collapse.

### 2. Three-Round Shape Partitioning Debate — Shape 3-Disciplined adopted

- **Round 1**: Path A (synthetic cassettes) unanimous for scite-over-API.
- **Round 2**: Shape 1 (IDE-only MCP, Tracy materializes) vs Shape 2 (Texas Python MCP client). 3-1 Shape 1 majority; John dissent for Shape 2.
- **Round 3** (triggered by operator lane-discipline pushback — "doesn't that violate 'Texas handles technical fetching'?"): four agents + Dr. Quinn as fresh systems-thinking voice. Dr. Quinn reframed the question from "where's the boundary?" to **"what knowledge does each act require, and where does that knowledge live most naturally?"** Partitioning by knowledge-locality (not role-tradition) produced **Shape 3-Disciplined**: Tracy owns editorial (intent + acceptance criteria + provider choice); per-provider adapters own mechanical query translation + fetch + filter + normalize; thin Texas dispatcher owns routing + iteration + cross-validation merger.
- **Round 4** (operator update — "scite and Consensus both available in Cursor MCP already; duplicate scite with Consensus for cross-validation"): cross-validation promoted from v2 to **v1 first-class**; `cross_validate: true` fans out to every provider in `provider_hints`, merges by identity key, annotates rows with `convergence_signal`.

**Ratified architecture**:
- `RetrievalIntent` = natural-language intent + `provider_hints` (required v1) + kind discriminator + three-tier acceptance criteria (mechanical / provider_scored / semantic_deferred) + iteration_budget + convergence_required + cross_validate.
- `AcceptanceCriteria` three-tier schema — mechanical (Texas evaluates deterministically), provider_scored (Texas via provider-native signals), semantic_deferred (Texas does NOT evaluate; Tracy post-fetch pass).
- `RetrievalAdapter` ABC with 8 methods: formulate_query / execute / apply_mechanical / apply_provider_scored / normalize / refine / quality_delta / declare_honored_criteria.
- Iteration Model A (adapter-internal loop, budget-bounded, abort-on-non-improvement) resolved Murat's test-flakiness dissent via deterministic sequence fixtures (NOT stateful mocks).
- Operator-locator providers (27-1 DOCX, 27-5 Notion, 27-6 Box, 27-7 Playwright) keep existing directive shape at CLI; internally route through new dispatcher via degenerate-case transform. No retrofit.

### 3. Story 27-0 Retrieval Foundation — opened, green-lit, ready-for-dev

- **Ratified-stub** authored post-Round-3 party consensus; expanded via `bmad-create-story` to 400+ line full BMAD spec with TL;DR + 7 AC-B + 8 AC-T + 11 AC-C + Pre-Dev Gate + 10 anti-pattern warnings + source tree + Previous-Story Intelligence (from 27-1 closeout) + Test Plan table + Risks table + Non-goals + Dev Agent Record template.
- **Green-light gate**: Winston + Amelia + Murat + Paige panel. **UNANIMOUS Option Y for Python MCP client library** — hand-rolled JSON-RPC-over-HTTP using existing `requests` dep, NOT `mcp` PyPI pre-1.0. Rationale: pre-1.0 breaking-change probability ~60-70% over 6-month epic window vs. JSON-RPC 2.0 frozen since 2010 (<5% drift). Verdicts: Winston GREEN with 7 MUST-FIX, Amelia YELLOW→GREEN with 5 blockers resolved, Murat GREEN with 3 strengthening asks + 3 test adds + CI flake-detection gate, Paige GREEN with 5 authoring-time asks.
- **Green-Light Patches Applied** section captures all 28 consensus patches (contract additions, test expansions, doc patches, scope adjustments).
- **Target suite delta: +30 collecting tests** (1036 → 1066). 5-pt estimate holds IF dev-guide.md authoring deferred to 27-2.
- Status: `ready-for-dev` awaiting fresh-session `bmad-dev-story 27-0-retrieval-foundation`.

### 4. Epic 27 Roster Reshape

- **Critical path reshaped**: 27-1 (done) → **27-0 (foundation)** → **27-2 (scite adapter)** → **27-2.5 (Consensus adapter)** → unblocks Epic 28.
- **27-2 scite.ai provider** — reshaped from direct provider to scite **adapter** against 27-0 contract. Previous 382-line Pre-Dev Gate expansion preserved; now has reshape banner. Status: `blocked`.
- **27-2.5 Consensus adapter** — new story opened as ratified-stub per operator directive. Cross-validation partner to scite; first real `cross_validate: true` exercise. 3 pts. Status: `ratified-stub`.
- **27-3 image / 27-4 YouTube** — reshape to retrieval-shape per 27-0 contract.
- **27-5 Notion / 27-6 Box / 27-7 Playwright** — stay locator-shape; no retrofit; CLI unchanged.
- **Shape classification**: retrieval-shape (scite/Consensus/YouTube/image) vs locator-shape (DOCX done, Notion/Box/Playwright). Both shapes internally route through 27-0's dispatcher; operator-locator = degenerate case of Shape 3 contract.
- **Epic total: 9 stories, ~31 pts** (up from 7 stories, 23 pts pre-Round-3).

### 5. Story 28-1 Tracy Pilot Reshape Banner

Added reshape notice at top of 28-1 spec. Tracy's output contract simplifies from scite-specific queries to provider-agnostic intent + AC + provider_hints. Scite-DSL knowledge relocates to 27-2 scite adapter. Pts drop 9 → ~7 estimate. Full re-expansion via `bmad-create-story` after 27-0 + 27-2 close. Status: `blocked`.

### 6. Notion MCP Dual-Config Research (stashed for 27-5)

Cursor loads two Notion MCP servers in parallel (user-scope hosted HTTP at `https://mcp.notion.com/mcp` vs. project-scope local stdio via `run_mcp_from_env.cjs` → `@notionhq/notion-mcp-server`). They serve different consumers. Recommendation for Story 27-5: Texas's headless Notion adapter uses project-scope stdio; Tracy's IDE-session research uses user-scope hosted. Captured in [_bmad-output/maps/deferred-work.md](_bmad-output/maps/deferred-work.md) + memory.

## What Is Next

**Story 27-0 dev-story** in a fresh session. Operator explicitly chose pause-for-fresh-session (option a from three-way choice) over push-through (b) or scoped-partial (c), given the foundation scope (~2000 lines, 20+ files, 30 tests) deserves a clean-context session.

After 27-0 closes: 27-2 (scite adapter re-expanded via `bmad-create-story`) → 27-2.5 (Consensus adapter) → 28-1 (Tracy pilot re-expanded). Then asset-generation stories (Irene Pass 2 consumption of retrieval results) open.

## Unresolved Issues or Risks

- **27-0 pre-dev checks deferred to dev-story start** (Amelia R1-R3):
  - R1 scite MCP auth shape — assume HTTP Basic; library-agnostic public surface mitigates.
  - R2 refinement registry shape — start flat with `drop_filters_in_order`.
  - R3 FakeProvider fixtures — enumerate during T4.
- **27-0 is session-scale work** — fresh context needed; don't bundle other stories in the same session.
- **Deferred 27-1 code review items** (6 non-blocking follow-ups captured in `deferred-work.md`): sibling Office-ZIP suffixes, SDT/altChunk content drops, docstring completeness, Windows short-path flakiness, negative-control Tejal fixture, `_EXTRACTOR_LABELS` dual-lookup collapse. Batched for future "Texas intake robustness" story.
- **Repo-wide ruff debt** (~377 errors, 77 auto-fixable) — pre-existing warehouse clutter, incremental cleanup strategy holds.
- **28-1 Tracy pre-Pass-2 gate** (Epic 28 AC-S3) still backlog.
- **3x flake-detection CI gate** (Murat green-light ask) — needs CI config update; not blocking for 27-0.

## Key Lessons Learned

1. **"Where's the partition?" is the wrong first question.** Dr. Quinn's reframing — "what knowledge does each act require, and where does that knowledge live most naturally?" — unlocked Shape 3-Disciplined. When roles are contested, derive from knowledge-locality, not role-tradition.
2. **Multi-round party-mode debates are valuable**, not wasteful. Round 3's Shape 3-Disciplined wouldn't have emerged without the Round 1 + Round 2 groundwork that made the team see the limits of Shapes 1 and 2.
3. **Test-flakiness is often a partitioning symptom.** Murat's Model-A dissent traced back to "stateful sequence mocks are brittle" — the resolution (deterministic sequence fixtures) came from partitioning the test state space differently, not from changing the runtime model.
4. **Operator judgment beats team consensus when it surfaces fresh framing.** The 4-0 Shape 1 consensus was about to merge when operator asked "doesn't that violate Texas's technician role?" — which cracked open the right-question rethink.
5. **Library-agnostic public surfaces are the escape hatch for pre-1.0 library decisions.** Option Y (hand-rolled) can migrate to Option X (`mcp` PyPI) as a single-file swap when the ecosystem matures. Don't take library bets when contracts are the priority.
6. **"Cross-validation is first-class v1" forced architecture clarity.** The moment operator said "one service's findings confirm or supplement another's," provider_hints-as-list + convergence_signal stopped being hypothetical — the contract had to be designed for it from day one.

## Validation Summary

- **Step 0a harmonization sweep (Cora-orchestrated)**: CLEAN. L1 catalog 10/10; L2 1 non-blocking observation (new `retrieval/` package placeholder — expected per ratified green-light). Report: [reports/dev-coherence/2026-04-17-2318/harmonization-summary.md](reports/dev-coherence/2026-04-17-2318/harmonization-summary.md). Tripwire cleared for next session.
- **Step 0b pre-closure audit**: Skipped — no stories flipping to done at wrapup (27-1 was flipped to done earlier in session and audited as part of its code-review closure gate).
- **Step 1 quality gate**: ruff clean on changed files (Texas scripts/tests, contract test, new retrieval package). Sprint-status yaml test 2/2 passed. 27-1 DOCX tests 6/6 passed (regression-proof).
- **Full pytest suite**: last ran at 1036/2/0 post-27-1 code-review remediation. Not re-run at wrapup (no production code touched post-27-1 closure).
- **Git tree at wrapup**: 14 modified + 3 untracked files, all session-owned; clean after commit.

## Artifact Update Checklist

- [x] `_bmad-output/implementation-artifacts/27-1-docx-provider-wiring.md` — BMAD closure record with Review Record
- [x] `_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md` — Pre-Round-3 expansion preserved; reshape banner; `blocked`
- [x] `_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md` — NEW; 400-line full BMAD spec + green-light patches; `ready-for-dev`
- [x] `_bmad-output/implementation-artifacts/28-1-tracy-pilot-scite-ai.md` — reshape notice banner; `blocked`
- [x] `_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md` — roster + dependency graph post-Round-3
- [x] `_bmad-output/implementation-artifacts/sprint-status.yaml` — 27-0 + 27-2.5 added; 27-1 `done`; 27-2 + 28-1 `blocked`
- [x] `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` — Epic 27 note reshaped; 27-0 + 27-2.5 entries added
- [x] `_bmad-output/maps/deferred-work.md` — 27-1 code-review deferred items + Notion 27-5 stash
- [x] `pyproject.toml` + `requirements.txt` — `python-docx>=1.1,<2` for 27-1
- [x] `skills/bmad-agent-texas/references/transform-registry.md` — DOCX section cross-reference
- [x] `skills/bmad-agent-texas/scripts/run_wrangler.py` — 27-1 dispatch + classifier + known_losses helper
- [x] `skills/bmad-agent-texas/scripts/source_wrangler_operations.py` — `extract_docx_text` + `wrangle_local_docx`
- [x] `skills/bmad-agent-texas/scripts/tests/test_texas_source_wrangler_operations.py` — 27-1 unit tests
- [x] `skills/bmad-agent-texas/scripts/tests/test_run_wrangler.py` — 27-1 integration test
- [x] `skills/bmad-agent-texas/scripts/retrieval/__init__.py` — NEW package placeholder (namespace only)
- [x] `tests/contracts/test_transform_registry_lockstep.py` — NEW; AC-S6 pilot
- [x] `next-session-start-here.md` — regenerated for next session's 27-0 dev-story
- [x] `SESSION-HANDOFF.md` — this file
- [x] `_bmad/memory/cora-sidecar/chronology.md` — wrapup entry appended
- [x] `reports/dev-coherence/2026-04-17-2318/` — Cora harmonization report

Link to Step 0a audit trail: [reports/dev-coherence/2026-04-17-2318/harmonization-summary.md](reports/dev-coherence/2026-04-17-2318/harmonization-summary.md).
