# Session Handoff — 2026-04-17 (Epic 27 + Epic 28 Ratified: Texas Intake Surface Expansion + Tracy the Detective)

## Session Summary

**Objective (as executed):** Ratify two new epics via BMAD party-mode consensus — Epic 27 (Texas Intake Surface Expansion; technician-capability upgrade) and Epic 28 (Tracy the Detective; new production-tier research-specialist born-sanctum). Four rounds of structured party consultation + one dispatch-vs-artifact architecture ratification landed: shape, scope, story spines, AC cross-cuts, v2 backlog capture, and sequencing. Progress-map routine hardened alongside (WAVE_LABELS coverage + `ratified-stub` vocabulary + incidental ruff cleanup). Commit + branch push + merge-to-master + master push all completed cleanly through pre-commit hooks.

**Branch:** `dev/epic-26-pretrial-prep` — merged to master via `90f19eb` (`--no-ff`).
**Session-anchor commit (prior handoff):** `8b76729`
**Head after session:** `90f19eb` (merge commit on master).
**Commits this session (1 net, on feature branch):**
- `8dd7d51` — feat(epics-27-28): ratify Texas intake expansion + Tracy the Detective (18 files, +2411/-52)
- `90f19eb` — Merge dev/epic-26-pretrial-prep into master (--no-ff)

## Major Deliverables

### Epic 27 — Texas Intake Surface Expansion (ratified-draft; 7 stories, 23 pts)

Technician-capability upgrade. Epic artifact at [epic-27-texas-intake-expansion.md](_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md). Stories:

- **27-1 DOCX provider wiring (2 pts, full spec):** contract-drift fix — wire `python-docx` into `.docx` branch of `local_file` handler. Blocks Tejal trial restart. Includes initial lockstep check (AC-S6 of the spine) that would have caught the drift pre-trial.
- **27-2 scite.ai provider (5 pts, full spec):** scholarly citation retrieval with smart-citation-context metadata. **Blocks Epic 28.** Introduces `--tracy-approved-resources` flag, `source_origin` tag, `tracy_row_ref` tag, and atomic-write artifact hygiene.
- **27-3..27-7 (ratified stubs):** image / YouTube / Notion-MCP / Box / Playwright-MCP providers. Parallel fan-out after 27-2 merges.
- **AC-S spine (8 cross-cutting ACs):** provider-contract compliance, fidelity-manifest compatibility, structured-manifest-not-blob-dump (John's Round-1 Tracy-anticipation), failure-mode coverage, per-provider test floor, **transform-registry lockstep check** (Audra-style), CP1252 guard sanity (inherit 26-7 pattern), documentation currency.

### Epic 28 — Tracy the Detective (ratified-draft; 2 pilot stories + 2 v2 stubs, 12 pts)

New production-tier specialist. Epic artifact at [epic-28-tracy-detective.md](_bmad-output/implementation-artifacts/epic-28-tracy-detective.md) + shared spine at [epic-28/_shared/](_bmad-output/implementation-artifacts/epic-28/_shared/).

**Operator framing (authoritative):** Texas is the technician, Tracy is the Detective. Tracy partners with Texas to source high-value supplementary research for lessons under development. Tracy dispatched by Irene (via Marcus) when the lesson plan reveals enrichment gaps. HIL operator remains primary indicator of source material; Tracy finds supplementary.

- **28-1 Tracy pilot (9 pts, full spec + 12 ACs):** Tracy born-sanctum under scaffold v0.2. Pilot provider scite.ai. End-to-end: Irene→Marcus→Tracy dispatch → `suggested-resources.yaml` with `editorial_note` + scoring → operator-approval redlineable manifest → Marcus dispatches Texas second-pass → pre-Pass-2 hard gate → Irene Pass 2 ingestion.
- **28-2 Tracy gate hardening (3 pts, stub):** Gate family (absent / stale / tampered receipt) + cross-agent asset-intent registry orphan detector + e2e gate-refusal test.
- **28-v2-a Coherence gate (backlog stub, Dr. Quinn Round 2):** Correctness concern — Tracy's additions register-coherent with primary material. Promote post-pilot if evidence warrants.
- **28-v2-b Dispatch budget (backlog stub, Dr. Quinn Round 2):** Loop-B mitigation — soft cap on Tracy-dispatches-per-run + approval-queue throttling. Promote if pilot evidence shows reflexive flagging.

**Shared spine artifacts** (all at [epic-28/_shared/](_bmad-output/implementation-artifacts/epic-28/_shared/)):
- `ac-spine.md` — 8 cross-cutting ACs (dispatch-vs-artifact rule, atomic writes, hard pre-Pass-2 gate, manifest schema compliance, vocabulary SSOT, editorial_note required, test coverage floor, dispatch audit trail)
- `runbook.md` — 14-step Tracy dispatch procedure with failure-mode resolution (complete / empty / failed) + invariants + rollback
- `worksheet-template.md` — per-story worksheet (mirrors Epic 26 pattern)

### Tracy sanctum bundle — breadcrumb for 28-1 implementation

- [skills/bmad-agent-tracy/README.md](skills/bmad-agent-tracy/README.md) — what lives here, what gets built in 28-1
- [skills/bmad-agent-tracy/references/vocabulary.yaml](skills/bmad-agent-tracy/references/vocabulary.yaml) v0.1 — **SSOT** for `intent_class`, `authority_tier`, `fit_score` scale, `editorial_note` constraints, `provider_metadata.scite` schema. Authored tonight per Paige's Round-2 doc-contract discipline.

### Governing architecture principle (Winston ratification)

**Specialists never dispatch specialists at runtime. Artifact handoff via filesystem is NOT a rule violation. Marcus owns every dispatch edge.** Captured as AC-S1 of Epic 28's shared spine. Applies to Tracy↔Texas AND as general principle for all future specialist-to-specialist data exchange. Winston added two hygiene edge cases: atomic artifact writes (temp + rename) and Marcus's freshness-check at dispatch time.

### progress_map.py hardening

Incremental additions on top of the April correctness hardening:
- Epic 27 + Epic 28 added to `WAVE_LABELS` so they render with proper names.
- `ratified-stub` added to `READY_STATUSES` so newly-scoped stubs don't flag as `unknown-status`.
- Incidental ruff cleanup: E501 line wraps, UP017 (`timezone.utc` → `datetime.UTC`), UP037 (remove forward-ref quotes), SIM108 (ternary for json/text dispatch). "Clearing the warehouse as we go" per the 26-7 commit's regression-proof-tests discipline.

## What Is Next

**Immediate:** Epic 27 + Epic 28 are ratified and ready for dev. Implementation sequencing:

1. **27-1 DOCX drift fix** (2 pts) — unblocks the pending APC C1-M1 Tejal trial restart
2. **27-2 scite.ai provider** (5 pts) — blocks Epic 28; critical path
3. **28-1 Tracy pilot** (9 pts) — born-sanctum specialist end-to-end with scite.ai
4. **28-2 Tracy gate hardening** (3 pts) — rounds out the gate family

Fan-out 27-3/4/5/6/7 (image, YouTube, Notion MCP, Box, Playwright MCP) parallel after 27-2 merges.

Per John's Round-3 branch hygiene, implementation opens per-epic branches (`dev/epic-27-texas-intake`, `dev/epic-28-tracy-pilot`) cut from master, NOT layered on the merged `dev/epic-26-pretrial-prep`. See next-session-start-here.md for startup commands.

**Tejal trial restart** still blocked by 27-1 at minimum. Full unblock after 27-2 if scite.ai referenced in prior trial brief.

## Unresolved Issues / Risks Carried Forward

1. **Repo-wide ruff debt:** 377 errors repo-wide (77 auto-fixable). Session-owned files are clean; the debt is pre-existing warehouse clutter the 26-7 commit began chipping at. Not a blocker. Strategy per 26-7 commit message: "clearing the warehouse as we go per regression-proof-tests discipline." Each new story that touches an affected file should pre-commit-clean it. No story solely for cleanup opened.

2. **Tejal trial restart still pending.** Unblocked once 27-1 (DOCX fix) ships. Full robustness pending 27-2 (scite.ai if referenced in trial brief). Trial runbook at [trial-run-c1m1-tejal-20260417.md](_bmad-output/implementation-artifacts/trial-run-c1m1-tejal-20260417.md) still describes the halt point; restart with the remediation.

3. **Story 26-5 (scaffold preservation semantics)** remains backlog. Gates the batch migration wave of the remaining ~14 agents per `project_sanctum_migration` memory. Not blocking Epic 27/28 work (Tracy is born-sanctum, no migration required).

4. **Tracy's scoring rubric is v1 naive by design** (AC-28-1 explicit). Expect iteration post-pilot. John Round-3 red flag: first run is evidence-gathering, not rubric validation.

5. **Dr. Quinn's adversarial scenarios** (coherence drift across downstream assets; Loops A/B/C/D on dispatch/vocabulary/calibration/approval-fatigue) are captured as 28-v2-a / 28-v2-b backlog stubs + cited in Epic 28 risk register. Post-pilot retrospective owns the re-litigation.

6. **No course content was created this session.** Pure ratification + planning work.

## Key Lessons Learned

- **Party-mode discipline pays compounding dividends.** Three rounds + one ratification spawn (9 distinct agent voices across the session) produced convergent story spines, well-named failure modes, and explicit v1-vs-v2 boundaries. The dispatch-vs-artifact distinction — load-bearing for all future specialist pairs — emerged only after Murat flagged Marcus-hop contract-test cost, and was clarified by operator during mid-round-2. Would have been missed by any single voice.
- **Doc-contract-first authoring** (Paige's insistence) — authoring `vocabulary.yaml` as SSOT tonight even though implementation is tomorrow removes a circular dependency. Future stories can't drift from a non-existent contract.
- **Operator non-negotiables over-ride consensus when given.** John's "wait for Tejal evidence" and Dr. Quinn's "flip to operator-pulled" were both defensible positions that the operator overruled for pilot scope. Consensus is a tool for clarity, not a veto on operator intent.
- **Ratification vs implementation boundary is load-bearing.** Tonight shipped epics + story specs + shared spine + ONE doc-contract artifact (vocabulary.yaml). All code implementation deferred. This matches Epic 26's pattern and prevents scope-creep into overnight sessions.
- **Incidental cleanup discipline** — the 26-7 commit's "clearing the warehouse as we go" philosophy carried through. 77 ruff auto-fixes applied in-flight on progress_map.py without expanding session scope.

## Validation Summary

- **Step 0a (harmonization):** not formally run through Cora (Cora-skill invocation deferred this session); change window = single session commit `8dd7d51` + merge `90f19eb`, both self-contained doc + code changes. No known drift.
- **Step 0b (pre-closure audit):** no stories flipped to `done` this session — all new (ratified-stub or ready-for-dev). Skip per protocol.
- **Step 1 quality gate:** `ruff check` on session-owned files (`progress_map.py`, `test_progress_map.py`, `_bmad-output/.../epic-27`, `_bmad-output/.../epic-28/`, `skills/bmad-agent-tracy/`) → **all checks passed**. Repo-wide remains at 377 (pre-existing debt).
- **Step 4a sprint-status regression:** `tests/test_sprint_status_yaml.py` → **2 passed**.
- **Full pytest suite:** **688 passed, 2 xfailed, 0 failed** (prior baseline 622; growth from session's +20 regression tests + parallel 26-6/26-7 test additions).
- **progress_map regression suite:** **40/40 green** after WAVE_LABELS + ratified-stub additions.
- **Pre-commit hooks:** all passed on commit `8dd7d51` — ruff (lint), orphan-reference detector, co-commit invariant.
- **`bmad-code-review` on session work:** not re-run this session; the code-review cycle for progress_map hardening was completed in the earlier thread + remediated (Claude Code Opus 4.7 adversarial Blind Hunter + Edge Case Hunter + Acceptance Auditor triad). Tonight's ratification is doc-only; no code-review required.

## Content Creation Summary

No course content created, reviewed, or moved to staging/courses this session. Pure epic/story planning + sanctum breadcrumb.

## Artifact Update Checklist

- [x] [_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md](_bmad-output/implementation-artifacts/epic-27-texas-intake-expansion.md) — new epic artifact
- [x] [_bmad-output/implementation-artifacts/epic-28-tracy-detective.md](_bmad-output/implementation-artifacts/epic-28-tracy-detective.md) — new epic artifact
- [x] [_bmad-output/implementation-artifacts/epic-28/_shared/ac-spine.md](_bmad-output/implementation-artifacts/epic-28/_shared/ac-spine.md) — 8 cross-cutting ACs
- [x] [_bmad-output/implementation-artifacts/epic-28/_shared/runbook.md](_bmad-output/implementation-artifacts/epic-28/_shared/runbook.md) — 14-step dispatch
- [x] [_bmad-output/implementation-artifacts/epic-28/_shared/worksheet-template.md](_bmad-output/implementation-artifacts/epic-28/_shared/worksheet-template.md) — per-story template
- [x] [_bmad-output/implementation-artifacts/27-1-docx-provider-wiring.md](_bmad-output/implementation-artifacts/27-1-docx-provider-wiring.md) — full spec
- [x] [_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md](_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md) — full spec
- [x] [_bmad-output/implementation-artifacts/27-3-image-provider.md](_bmad-output/implementation-artifacts/27-3-image-provider.md) — stub
- [x] [_bmad-output/implementation-artifacts/27-4-youtube-provider.md](_bmad-output/implementation-artifacts/27-4-youtube-provider.md) — stub
- [x] [_bmad-output/implementation-artifacts/27-5-notion-mcp-provider.md](_bmad-output/implementation-artifacts/27-5-notion-mcp-provider.md) — stub
- [x] [_bmad-output/implementation-artifacts/27-6-box-provider.md](_bmad-output/implementation-artifacts/27-6-box-provider.md) — stub
- [x] [_bmad-output/implementation-artifacts/27-7-playwright-mcp-provider.md](_bmad-output/implementation-artifacts/27-7-playwright-mcp-provider.md) — stub
- [x] [_bmad-output/implementation-artifacts/28-1-tracy-pilot-scite-ai.md](_bmad-output/implementation-artifacts/28-1-tracy-pilot-scite-ai.md) — full spec
- [x] [_bmad-output/implementation-artifacts/28-2-tracy-gate-hardening.md](_bmad-output/implementation-artifacts/28-2-tracy-gate-hardening.md) — stub
- [x] [skills/bmad-agent-tracy/README.md](skills/bmad-agent-tracy/README.md) — Tracy sanctum breadcrumb
- [x] [skills/bmad-agent-tracy/references/vocabulary.yaml](skills/bmad-agent-tracy/references/vocabulary.yaml) — v0.1 SSOT
- [x] [_bmad-output/implementation-artifacts/sprint-status.yaml](_bmad-output/implementation-artifacts/sprint-status.yaml) — Epic 27 + 28 blocks (committed in `8fc2121` alongside 26-7 co-evolution)
- [x] [_bmad-output/implementation-artifacts/bmm-workflow-status.yaml](_bmad-output/implementation-artifacts/bmm-workflow-status.yaml) — `next_workflow_step` updated; Epic 27 + 28 blocks added
- [x] [scripts/utilities/progress_map.py](scripts/utilities/progress_map.py) — WAVE_LABELS 27/28 + ratified-stub + ruff cleanup
- [x] [tests/test_progress_map.py](tests/test_progress_map.py) — +20 regression tests
- [x] [SESSION-HANDOFF.md](SESSION-HANDOFF.md) — this file
- [x] [next-session-start-here.md](next-session-start-here.md) — rewritten for Epic 27/28 implementation kickoff

## Dev-Coherence Report Home

No formal Step 0a report home created this session (Cora skill invocation deferred; doc-only ratification change set self-audits clean). Full-repo harmonization recommended at the start of next session (per the tripwire clause in the wrapup protocol: one skip is absorbed by the next session, two consecutive skips force a full sweep).
