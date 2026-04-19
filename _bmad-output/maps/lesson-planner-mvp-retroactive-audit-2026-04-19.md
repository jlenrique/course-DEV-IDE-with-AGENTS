# Lesson Planner MVP — Retroactive Audit

**Date:** 2026-04-19
**Scope:** 17 closed stories across Epics 28, 29, 30, 31, 32.
**Rubric (per story, ~5 min):**

1. **Artifact sanity** — spec Status=done; File List paths exist.
2. **Focused test green** — pytest scoped to story's tests.
3. **Key-claim smoke** — story's load-bearing invariant still holds.
4. **Deferral status** — each entry: Still-Open / Closed-By-Downstream / Stale.
5. **Consistency sniff** — audience-layered docstrings / Voice Register / AST contract pattern; flag drift only.
6. **Row** — one line verdict.

**Baseline regression (pre-audit, post-YAML-fix):** `1476 passed / 2 skipped / 27 deselected / 2 xfailed / 0 failed`. Audit proceeds against this floor.

**Status legend:** ✅ clean · ⚠️ drift/gap flagged · 🛑 blocker / material gap

---

## Epic 31 — Foundation (5 stories)

| Story | Artifacts | Focused tests | Key-claim smoke | Deferrals | Consistency | Verdict |
|---|---|---|---|---|---|---|
| **31-1** lesson-plan-schema | `schema.py` / `events.py` / `digest.py` / `event_type_registry.py` / `schema/lesson_plan.v1.schema.json` / `dials-spec.md` — all present | shape-pin + JSON-parity + schema-version + fit-shape + scope-shape = **30 passed** | closed-enum 3-layer rejection pattern intact (TypeAdapter + Literal + JSON enum) | **12 SHOULD-FIX + 23 NITs still-open** in §31-1 | Reference implementation — audience-layered docstrings + two-level actor surface ORIGINATE here. No drift. | ✅ |
| **31-2** lesson-plan-log | `log.py` present (~720 LOC); includes WriterIdentity Literal + WRITER_EVENT_MATRIX + NAMED_MANDATORY_EVENTS + PrePacketSnapshotPayload + PlanLockedPayload + LessonPlanLog | log-append + single-writer + staleness + monotonic + named-events + read-api + atomic-write + g6-hardening + shape-pin + pre-packet-shape = **112 passed + 1 skip** (platform-guarded crash-sim) | single-writer rule triple-surfaced (Literal + matrix + 12-cell parametrized test) — all 3 surfaces intact | **10 SHOULD-FIX still-open** in §31-2. Notable: Edge#13 Windows CRLF text-mode = **same concern as 30-2b EC13** (cross-story pattern). | `_find_project_root()` cwd-independence pattern adopted by 30-2b `_REPO_ROOT` | ✅ |
| **31-3** registries | `modality_registry.py` / `component_type_registry.py` / `modality_producer.py` / `produced_asset.py` — all present | registries + ABC + fixtures + exports = **156 passed** | MappingProxyType immutability + `__init_subclass__` ClassVar enforcement + ProducedAsset counterfeit-fulfillment validator all intact | **1 SHOULD-FIX + 4 NITs still-open** in §31-3. `source_plan_unit_id` regex alignment (flagged as natural-home-31-4/30-4) — **verified not yet closed in 31-4**. | Audience-layered docstrings across 4 new modules; anti-pattern catalog extended | ✅ |
| **31-4** blueprint-producer | `blueprint_producer.py` present; MODALITY_REGISTRY `blueprint` entry backfilled | producer + registry-contract + no-duality-leak = **~11 passed** (inside K=8 target) | concrete ModalityProducer + deterministic markdown artifact at `_bmad-output/artifacts/blueprints/` + human-review checkpoint markers | **0 DEFER** per review record | Voice Register honored; single-writer contract inherited | ✅ |
| **31-5** quinn-r-two-branch | `quinn_r_gate.py` present with `QuinnRTwoBranchResult` / `QuinnRUnitVerdict` + artifact at `_bmad-output/artifacts/quinn-r/` | gate + no-log-boundary + package-exports = **~11 passed** | three-branch step-13 verdict (produced-asset / blueprint-signoff / declined) + ordered `PriorDeclinedRationale` for 29-2 consumption | **0 DEFER** per review record | No Lesson Plan log write-path usage (audit clean) | ✅ |

**Epic 31 subtotal tests: 301 passed / 1 skipped. Deferrals open: 23 SHOULD-FIX + ~27 NITs.**

## Epic 29 — Irene (3 stories)

| Story | Artifacts | Focused tests | Key-claim smoke | Deferrals | Consistency | Verdict |
|---|---|---|---|---|---|---|
| **29-1** fit-report-v1 | `fit_report.py` (~280 LOC) with validate / serialize / deserialize / emit + `StaleFitReportError` + `UnknownUnitIdError` + `FIT_REPORT_EMITTED_EVENT_TYPE` | validator + emitter + serializer + smoke + shape-stable + canonical-caller = **29 passed** | Canonical-caller pattern (Marcus-Orchestrator only) + `writer=marcus-orchestrator` gate enforced by 31-2 | 2 DEFER in §29-1: **#3-dedup CLOSED-BY-DOWNSTREAM** (29-2 line 309 added duplicate-unit_id rejection); **#4-leak STILL-OPEN** (UnknownUnitIdError message truncation — no downstream story has addressed). | Establishes `log=None` warning-fallback pattern adopted by 30-2b dispatch. Audience-layered docstring discipline maintained. | ✅ |
| **29-2** gagne-diagnostician | `gagne_diagnostician.py` present with `diagnose_lesson_plan` / `diagnose_plan_unit` / `PriorDeclinedRationale` / `irene_budget_ms` / summary-only fallback | diagnose + no-emit-boundary + package-exports = **16 passed** | `PriorDeclinedRationale` carry-forward seam ready for 31-5 consumption (pair verified) + hardcoded Gagné-event guard + registry-backed modality_ref validation via 31-3 | **0 DEFER** per review record | Consumes 29-1 seam via validated FitReport return; consumes 31-3 registry. No write-path direct calls (orchestrator-side emission assumed). | ✅ |
| **29-3** blueprint-coauthor | `blueprint_coauthor.py` present; `schema.py` additive `BlueprintSignoff` + `lesson_plan.v1.schema.json` snapshot + SCHEMA_CHANGELOG lockstep updates | coauthor + no-emit-boundary = **8 passed** | Sign-off sidecar emission + 31-4 blueprint-artifact validation + traversal-path rejection + typed `PlanUnit.blueprint_signoff` attachment | **0 DEFER** per review record | No direct log emission; no 31-5 gate logic. Narrow branch — consistent with "keeps the branch narrow" stated discipline. | ✅ |

**Epic 29 subtotal tests: 53 passed. Deferrals open: 1 (29-1 #4-leak). Closed-by-downstream: 1 (29-1 #3-dedup → 29-2).**

## Epic 30 — Marcus (4 stories)

| Story | Artifacts | Focused tests | Key-claim smoke | Deferrals | Consistency | Verdict |
|---|---|---|---|---|---|---|
| **30-1** marcus-duality-split | `marcus/intake/` + `marcus/orchestrator/` sub-packages + `marcus/facade.py` with `get_facade` + `marcus/orchestrator/write_api.py` + `NEGOTIATOR_SEAM` | 11 test files (duality imports + write-api + facade leak + negotiator-seam + facade roundtrip + golden-trace + import-chain + coverage-non-regression + single-writer-routing + facade-is-public-surface + zero-edit) = **38 passed + 1 skip** | Facade Voice Register + `UnauthorizedFacadeCallerError` attribute-scoped offending-writer pattern + single-writer gate all intact | **8 DEFER logged INLINE in spec** (not in central `deferred-work.md`). Re-audited: **G6-D7 CLOSED by self-heal** (AC-T.10 pin now active post-d1a788c commit); **7 Still-Open** (G6-D1/D4/D6 → 30-3a; G6-D2 → 30-2b not addressed; G6-D3/D8 → retro; G6-D5 → future multiproc). | ⚠️ **Pattern drift:** DEFERs logged inline rather than centralized — inconsistent with 31-1/31-2/31-3/29-1/30-2b. Also: **G6-D2 was DESTINED for 30-2b but 30-2b didn't fold the literal `"pre_packet_snapshot"` into a single-source constant** — `write_api.py:67` still has `_PRE_PACKET_SNAPSHOT_EVENT_TYPE` as its own string literal distinct from 31-2 registry. | ⚠️ |
| **30-2a** pre-packet-extraction-lift | `marcus/intake/pre_packet.py` (30-2a body preserved byte-identical) + `scripts/utilities/prepare-irene-packet.py` thin shim | intake-pre-packet + cli + shim-discipline = **8 passed** | Byte-identical lift — `prepare_irene_packet` function body matches pre-30-2a line-for-line | **1 DEFER** (G6-D1 side-effect-guard extension) — **CLOSED-BY-DOWNSTREAM** by 30-2b AC-B.9 (extended `tests/test_marcus_import_chain_side_effects.py`). | Same inline-DEFER drift as 30-1, but this one got closed cleanly. | ✅ |
| **30-2b** pre-packet-envelope-emission | `marcus/orchestrator/dispatch.py` + extended `marcus/intake/pre_packet.py` with `prepare_and_emit_irene_packet` + 3 helpers + `_REPO_ROOT` | emission + dispatch + single-writer AST + dispatch-monopoly AST + voice-register AST = **12 passed** (14 nodeids with parametrize) | Dependency-injection `dispatch` callable + AST-contract single-writer routing + dispatch monopoly all intact | **2 DEFER centralized** in §30-2b: EC13 cross-platform newline digest stability (Still-Open); EC14 bundle-metadata race window (Still-Open). | Centralizes correctly. 30-2a G6-D1 closed by AC-B.9. | ✅ |
| **30-5** retrieval-narration-grammar | `marcus/lesson_plan/retrieval_narration_grammar.py` + `RetrievalNarrationError` | narration-grammar + voice-register-grep = **12 passed** | Posture-classification renderer (supporting / contrasting / mentioning under corroborate) + normalized `gap-fill` / `gap_fill` seam intact | **0 DEFER** per review record | Landed as marcus/lesson_plan/ module — slightly atypical location for a Marcus-voice concern (could argue for marcus/orchestrator/ per duality), but narration grammar is value-object-style so lesson_plan/ is defensible. | ✅ |

**Epic 30 subtotal tests: 70 passed + 1 skip. Deferrals: 2 Closed (30-1 G6-D7 self-heal + 30-2a G6-D1 → 30-2b) / 9 Still-Open (30-1 ×7 + 30-2b ×2). Pattern-drift flag: 30-1 + 30-2a log inline, not centralized.**

## Epic 28 — Tracy (4 stories)

| Story | Artifacts | Focused tests | Key-claim smoke | Deferrals | Consistency | Verdict |
|---|---|---|---|---|---|---|
| **28-1** tracy-reshape-charter | Doc-only charter — retires original pilot spec; codifies three postures (embellish / corroborate / gap-fill) under John's four-part contract | n/a (doc charter) | Three-posture taxonomy correctly inherited by 28-2's dispatcher signatures | **0 DEFER** per review record | Doc-only; applies 10 MUST-FIX patches per layered review. | ✅ |
| **28-2** tracy-three-modes | `skills/bmad_agent_tracy/scripts/posture_dispatcher.py` — `embellish()` / `corroborate()` / `gap_fill()` dispatch | tracy-postures contract = **~17 tests covered in combined 34** | Posture discrimination matrix (gap_type × dial) + fail-closed out-of-scope + refuse-on-ambiguous-intent all present | **0 DEFER** — feedback PATCH-applied at review time | Non-marcus-package skill module (correctly scoped to `skills/bmad_agent_tracy/`) | ✅ |
| **28-3** irene-tracy-bridge | `skills/bmad_agent_tracy/scripts/irene_bridge.py` — `IreneTracyBridge` for in-scope gap auto-dispatch + dial operator endorsements | irene-tracy-bridge contract (in combined 34) | IdentifiedGap auto-dispatch at plan-lock path correctly reachable | **0 DEFER** per review record | Same skill-module scope discipline as 28-2 | ✅ |
| **28-4** tracy-smoke-fixtures | `skills/bmad_agent_tracy/scripts/smoke_fixtures.py` + 4 committed fixtures under `tests/fixtures/retrieval/tracy_smoke/` covering embellish / corroborate-supporting / corroborate-contrasting / gap-fill | smoke-fixtures loader + loader-boundary = **9 passed** (K≥6 met, at target ceiling) | Read-only fixture loader seam; canonical brief/result pairs all parse | **0 DEFER** per review record (explicitly "0 APPLY / 0 DEFER / 0 DISMISS") | Cleanest Epic 28 closure — tight scope discipline | ✅ |

**Epic 28 subtotal tests: 34 passed. Deferrals open: 0. Zero drift — cleanest epic after 29.**

## Epic 32 — Trial harness (1 story)

| Story | Artifacts | Focused tests | Key-claim smoke | Deferrals | Consistency | Verdict |
|---|---|---|---|---|---|---|
| **32-2** plan-ref-envelope-coverage-manifest | `coverage_manifest.py` + artifact `_bmad-output/maps/coverage-manifest/lesson-plan-envelope-coverage-manifest.json` + JSON schema + 5 test files + fixtures | plan-ref-verifier + assert-plan-fresh-detection + summary + JSON-schema-parity + shape-stable = **9 passed** | Coverage manifest's `summary.trial_ready: false` (expected — downstream emitters pending) | **0 DEFER** per review record | ⚠️ **Cross-story seam mismatch:** manifest expects 30-2b emitter at `marcus/lesson_plan/step_05_pre_packet_handoff.py`; 30-2b actually landed at `marcus/intake/pre_packet.py` + `marcus/orchestrator/dispatch.py`. Surface still `status: pending`; manifest not regenerated post-30-2b close. | ⚠️ |

**Epic 32 subtotal tests: 9 passed. Deferrals open: 0. Flag: manifest regeneration needed to reflect 30-2b actual emitter paths + flip step-05 surface to emitted.**

---

## Aggregate findings

**Verdicts across 17 stories:** 15 ✅ / 2 ⚠️ / 0 🛑. Focused-test totals across all audited suites: **467 passed + 2 skipped / 0 failed** (skips are platform-guarded — Windows crash-sim + golden-trace fixture-present skipif).

**Baseline regression (post-YAML-fix):** `1476 passed / 2 skipped / 27 deselected / 2 xfailed / 0 failed`.

### Material findings (⚠️)

1. **30-1 deferral-logging drift.** 30-1's 8 G6 DEFERs live inline in the story spec rather than in [_bmad-output/maps/deferred-work.md](_bmad-output/maps/deferred-work.md). 30-2a had the same drift (but its one DEFER has since been closed). 31-*, 29-1, 30-2b, 30-5 all centralize correctly. This is a discoverability gap, not a correctness gap — the DEFERs are still recoverable but aren't visible when future stories grep `deferred-work.md`.

2. **30-1 G6-D2 slipped its destination.** Deferred explicitly to 30-2b or 32-1 for single-source-of-truth on the `"pre_packet_snapshot"` event-type string. 30-2b didn't fold it — [marcus/orchestrator/write_api.py:67](marcus/orchestrator/write_api.py#L67) still hard-codes `_PRE_PACKET_SNAPSHOT_EVENT_TYPE: str = "pre_packet_snapshot"` as a local literal. 31-2's `NAMED_MANDATORY_EVENTS` frozenset is the actual source of truth and contains the same string. Low-severity (single string literal, low drift risk) but the deferral was destination-tagged and slipped.

3. **32-2 coverage-manifest not regenerated after 30-2b close.** The manifest expects the pre-packet emitter at `marcus/lesson_plan/step_05_pre_packet_handoff.py`; 30-2b landed it at `marcus/intake/pre_packet.py` + `marcus/orchestrator/dispatch.py`. Surface still `status: pending` in the JSON. 30-2b's own spec's Done-when clause #10 claimed this would flip; it didn't. 30-2b dev execution (my own) missed this step.

### Cross-story pattern finding

4. **Text-mode CRLF / cross-platform digest hygiene is a recurring concern across three stories.** Shows up as:
    - 31-2 Edge#13 (log.py uses text-mode writes; newline translation could affect byte-level diffing).
    - 30-2b EC13 (`Path.write_text(..., encoding="utf-8")` on Windows vs `.read_bytes()` for sha256 digest — cross-platform mismatch latent).
    - 30-1 Golden-Trace regression normalizes `\r\n → \n` in-test (defense in depth), but production bundle-write paths don't enforce `newline=""`.

    The three show up in separate stories because each noticed the hygiene gap in local scope and deferred it. Together they argue for a **one-shot audit + fix story** ("Windows-newline hygiene on marcus/ Path.write_text call sites") rather than per-story follow-ups. Natural home: a 32-3 pre-work pass, since 32-3 is the trial-run smoke harness that will hit cross-platform CI.

### Zero-drift surfaces (what's working well)

- **Epic 29 and Epic 28** shipped with zero deferrals open. 28-4 explicitly landed "0 APPLY / 0 DEFER / 0 DISMISS."
- **Single-writer discipline** holds end-to-end: 30-2b AST contract tests confirm Intake cannot reach the write API directly; 30-1 write-API gate rejects non-orchestrator callers.
- **Audience-layered docstring** pattern (Maya-facing note / dev-discipline note / origin note) adopted consistently 31-1 → 31-2 → 31-3 → 30-1 → 30-2a → 30-2b.
- **Voice Register** discipline enforced structurally via AST contract tests (`test_30_2b_voice_register`, `test_no_intake_orchestrator_leak_marcus_duality`, `test_retrieval_narration_grammar_voice_register`).
- **29-1 → 29-2 → 31-5 consumer chain** closes cleanly: 29-1 emits FitReport; 29-2 builds diagnoses consuming prior `PriorDeclinedRationale`; 31-5 emits ordered rationales back to 29-2.

## Deferral tally

**Total open: 35 SHOULD-FIX + ~54 NITs = ~89 items.**
**Closed-by-downstream: 3.** (30-2a G6-D1 → 30-2b AC-B.9; 29-1 #3-dedup → 29-2 duplicate-target rejection; 30-1 G6-D7 self-heal at commit.)
**Stale: 0.**

### Per-story inventory

| Story | Open | Closed | Notes |
|---|---|---|---|
| 31-1 | 12 SHOULD-FIX + 23 NITs | 0 | Deepest backlog. All in `deferred-work.md §31-1`. |
| 31-2 | 10 SHOULD-FIX + ~20 NITs | 0 | Includes Edge#13 Windows CRLF (overlaps 30-2b EC13). |
| 31-3 | 1 SHOULD-FIX + 4 NITs | 0 | `source_plan_unit_id` regex alignment natural home 31-4/30-4; not closed. |
| 31-4 | 0 | 0 | "0 APPLY / 0 DEFER / 0 DISMISS" per spec. |
| 31-5 | 0 | 0 | "0 APPLY / 0 DEFER / 0 DISMISS" per spec. |
| 29-1 | 1 SHOULD-FIX | 1 | #3-dedup closed by 29-2; #4-leak still-open. |
| 29-2 | 0 | 0 | Clean. |
| 29-3 | 0 | 0 | Clean. |
| 30-1 | 7 DEFER | 1 (self-heal) | Inline-logged in spec; 1 closed, 1 destined-for-30-2b-but-slipped (G6-D2), 5 Still-Open. |
| 30-2a | 0 | 1 | G6-D1 closed by 30-2b AC-B.9. |
| 30-2b | 2 DEFER | 0 | EC13 newline + EC14 race window — both Still-Open. |
| 30-5 | 0 | 0 | Clean. |
| 28-1 | 0 | 0 | Clean (doc charter). |
| 28-2 | 0 | 0 | Clean — all feedback PATCH-applied. |
| 28-3 | 0 | 0 | Clean. |
| 28-4 | 0 | 0 | Clean. |
| 32-2 | 0 | 0 | Clean per spec — but see Aggregate finding #3 (manifest drift). |

## Recommended follow-ups

**Priority 1 — address before 30-3a opens (cheap, material):**

1. **Regenerate 32-2 coverage manifest** to reflect 30-2b's actual emitter paths + flip step-05 surface from `pending` → `emitted`. Run the manifest generator against current code. Estimated: 10 min. This closes Aggregate finding #3.

2. **Close 30-1 G6-D2 at 30-3a** (destined-for-30-2b but slipped): consolidate `_PRE_PACKET_SNAPSHOT_EVENT_TYPE` literal in `write_api.py` to reference `NAMED_MANDATORY_EVENTS` from 31-2 (single-source-of-truth). Very low risk; grep-confirmable. Estimated: 5 min + 1 test.

**Priority 2 — hygiene / sprint-retrospective scope:**

3. **Centralize 30-1's 7 Still-Open inline DEFERs** into `deferred-work.md §30-1`. Copy-paste from 30-1 spec §DEFER table. Estimated: 10 min. Closes Aggregate finding #1.

4. **Windows-newline hygiene pass.** One story covering marcus/ Path.write_text call sites + pin `newline="\n"` or `.write_bytes()` where determinism matters. Estimated: 0.5 pts. Closes Aggregate finding #4 + 30-2b EC13 + 31-2 Edge#13 simultaneously. Natural home: runway pre-work ahead of 32-3 trial-run smoke harness.

**Priority 3 — retrospective fodder (low priority, epic-closure scope):**

5. **Epic 28, 29, 31 retrospectives** — all three epics complete modulo optional retro. Can run `bmad-retrospective` parallel.
6. **31-1 backlog triage** — 12 SHOULD-FIX + 23 NITs is the largest per-story backlog; most are low-severity but a triage pass post-MVP-landing would trim dead items.
7. **29-1 #4-leak** (UnknownUnitIdError message list-leak) — natural home 29-3 or 30-* per original deferral note; 29-3 didn't address; escalate to a future hardening story.

## Summary

**Health verdict: green with 2 material hygiene items to close before 30-3a.** The MVP's critical contracts (single-writer, Voice Register, byte-identity, audience-layered docstrings) hold end-to-end. Deferrals are tracked (mostly) and prioritized. The 30-1 drift is recoverable in ~15 min. The Windows-newline concern is latent across 3 stories and worth one focused 0.5-pt consolidation story.

---

## Post-audit fix pass (2026-04-19)

Following the audit, the user requested immediate closure of the two ⚠️ material findings. Both fixes landed + full regression re-verified.

### Fix A — 30-1 G6-D2 single-source-of-truth closed

**Finding:** 30-2b's `marcus/orchestrator/write_api.py:67` hard-coded `_PRE_PACKET_SNAPSHOT_EVENT_TYPE = "pre_packet_snapshot"` as a local literal distinct from 31-2's `NAMED_MANDATORY_EVENTS` registry. Destination-tagged for 30-2b but slipped.

**Fix:** added public `PRE_PACKET_SNAPSHOT_EVENT_TYPE: Final[str] = "pre_packet_snapshot"` to [marcus/lesson_plan/log.py](marcus/lesson_plan/log.py) immediately after the `WRITER_EVENT_MATRIX`-vs-`NAMED_MANDATORY_EVENTS` import-time assertion, with an import-time membership check (`assert PRE_PACKET_SNAPSHOT_EVENT_TYPE in NAMED_MANDATORY_EVENTS`). Pattern matches 29-1's `FIT_REPORT_EMITTED_EVENT_TYPE` precedent. Updated:

- [marcus/orchestrator/write_api.py](marcus/orchestrator/write_api.py) — imports and references the named constant.
- [marcus/intake/pre_packet.py](marcus/intake/pre_packet.py) — `prepare_and_emit_irene_packet` now uses the constant instead of the literal "pre_packet_snapshot".
- [tests/contracts/test_lesson_plan_log_shape_stable.py](tests/contracts/test_lesson_plan_log_shape_stable.py) — `EXPECTED_MODULE_PUBLIC_NAMES` extended to include the new export.

**Verification:** 53 focused tests passed across 30-2b + write_api + log suites. Ruff clean.

### Fix B — 32-2 coverage-manifest step_05 ownership corrected (diagnosis corrected)

**Reading coverage_manifest.py more carefully revealed the original audit diagnosis was wrong.** The manifest audits the **CONSUMER** side (where `assert_plan_fresh` is called on a received envelope), not the emitter. The step_05 surface's `module_path: marcus/lesson_plan/step_05_pre_packet_handoff.py` points to a future CONSUMER module — not where 30-2b's emitter was supposed to land. 30-2b's emitter at `marcus/intake/pre_packet.py` + `marcus/orchestrator/dispatch.py` is architecturally correct.

**The real issue:** 32-2's inventory assigned `owner_story_key="30-2b-pre-packet-envelope-emission"` to a consumer-surface entry, but 30-2b only emits. The consumer lives with the plan-lock fanout story.

**Fix:** [marcus/lesson_plan/coverage_manifest.py](marcus/lesson_plan/coverage_manifest.py) step_05 entry:
- `owner_story_key` reassigned from `30-2b-pre-packet-envelope-emission` to `30-4-plan-lock-fanout`.
- `surface_name` changed to "Pre-packet handoff consumer boundary".
- `notes` rewritten to clarify the emitter/consumer split.
- Hyphenated sub-identity tokens stripped from notes to honor the no-leak guard.

**Broader drift surfaced (new finding):** The `DEFAULT_COVERAGE_INVENTORY` now has three further surfaces (steps 11, 12, 13 — owned by 31-4 and 31-5, both done) that are **missing `sample_factory` callables**, so `emit_coverage_manifest()` crashes on regeneration. None of the story closures added these factories. The existing 32-2 test suite uses synthetic inventories rather than the default, so this drift wasn't caught. This is a **separate hygiene item** to queue for a follow-up "32-2 inventory hardening" pass — out of this fix's scope.

### Fix C — concurrent-session YAML indent regression re-fixed

A concurrent session added lines 580–581 to `sprint-status.yaml` at top-level indent (no leading two spaces) and with a truncated line 581. Re-indented to restore YAML parse. Added `AUDIT-2026-04-19-FLAG` markers noting:
- 30-3a marked `done` by concurrent session without landing `marcus/orchestrator/loop.py` or equivalent (spec Tasks/Subtasks T2-T8 still unchecked; no code exists; this audit explicitly flagged earlier).
- 30-3b line truncated mid-sentence ("voice") — likely incomplete concurrent edit.

### Post-fix regression

- **Full suite: 1477 passed / 2 skipped / 27 deselected / 2 xfailed / 0 failed** (up +1 from pre-fix 1476; added the `PRE_PACKET_SNAPSHOT_EVENT_TYPE` export in `EXPECTED_MODULE_PUBLIC_NAMES`).
- Ruff clean across all touched files.
- 30-2b scoped + dispatch + single-writer + log-suite all green.

### Revised deferral tally

| Story | Open (was) | Open (now) | Notes |
|---|---|---|---|
| 30-1 | 7 SHOULD-FIX (inline) | **6 SHOULD-FIX (inline)** | G6-D2 **CLOSED** by Fix A. |
| 30-2b | 2 DEFER | 2 DEFER | Unchanged. |

**Net: one more inline deferral closed. Pattern-drift item (30-1 inline logging) unchanged — recommended follow-up to centralize still stands.**

### Revised recommended follow-ups

**Priority 1 (closed by this fix pass):** ~~Regenerate 32-2 manifest~~ ⇒ diagnosis corrected (ownership reassigned); ~~Close 30-1 G6-D2~~ ⇒ closed.

**Priority 2 (new from fix pass):**
- **32-2 inventory hardening** — add `sample_factory` callables to step_11 / step_12 / step_13 entries (owned by 31-4 / 31-5). Without them, `emit_coverage_manifest()` crashes on regeneration against the current tree. Estimated 0.5 pts.

**Priority 3 (unchanged from audit):**
- Centralize 30-1's 6 remaining inline DEFERs into `deferred-work.md §30-1`.
- Windows-newline hygiene pass (31-2 Edge#13 + 30-2b EC13 + 30-1 golden-trace-normalization).
- Epic 28/29/31 retrospectives.
- 31-1 backlog triage.
- 29-1 #4-leak (UnknownUnitIdError list-leak).
