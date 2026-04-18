# Lesson Planner MVP — Plan for First Trial Run

**Created:** 2026-04-18 (session-wrapup artifact, `dev/lesson-planner` branch)
**Author:** Amelia (💻 BMAD Developer Agent) + Four-round party-mode consensus (John / Winston / Dr. Quinn / Sally)
**Status:** R1 party-mode review complete (2026-04-18) — orchestrator ruling applied; 31-1 authored `ready-for-dev`. Downstream stories await next-session R2 green-light + per-story `bmad-create-story`.

---

## Vision

Get APP's agents wired for a new capability set — **Lesson-Plan-driven production** — and ready for first real trial run as reliably but quickly as possible. Representative components (DOCX locator + scite.ai retrieval) stand in for future resource types during initial trial runs; no new providers in this MVP.

**Key product bet (user-ratified after 4 party-mode rounds):**
- A new **Step 4A** slots between existing step 04 (ingestion quality gate + Irene packet) and step 05 (Irene Pass 1 begins).
- Inside 4A, Marcus + Maya co-produce a **Lesson Plan** — a living conversational pact, not a form — rooted in Robert Gagné's Nine Events of Instruction as a pedagogical frame (pluggable seam named for future learning models).
- Irene acts as the **instructional designer** she already is, formalized: she produces an event-by-event source-fitness **diagnosis** (not an outline); Maya makes **scope decisions** per event (`in-scope | out-of-scope | delegated-to-modality-X | blueprint`).
- **Tracy** (re-chartered from Epic 28) is the minimal research agent: embellish / corroborate / gap-fill against the provider directory (Texas's `list_providers()`). She never sees the Lesson Plan — only `RetrievalIntent` Irene distills.
- **Quinn-R step 13** pre-composition QA gate becomes two-branch: per `plan_unit`, either produced-asset-passes-quality OR blueprint-signed-by-Irene+writer. Out-of-scope units are audited as **Declined** with rationale preserved in the provenance tree.

## Architectural Ratifications (four-round party consensus)

### Quinn's Tri-Phasic Contract

The Lesson Plan is a **bilateral typed contract** with three phases:

1. **Diagnosis** — Irene attests (independent surveyor, NOT a signatory); Maya decides scope per event; produces ScopeDecision manifest.
2. **Authorization** — Dials (enrichment / corroboration, operator-set) + IdentifiedGaps (Irene-identified, auto-dispatched on in-scope events with insufficient source).
3. **Execution** — Production-side counterparties (Gary/Gamma for slides, blueprint-producer for APP-can't-produce events, Kira for narration, Tracy for research) fulfill clauses. Every produced asset carries `fulfills: unit_id@plan_revision`.

**Role classes (three, not two):**
- **Signatory**: Maya (sole intent-side authority on scope).
- **Attestor**: Irene (diagnosis is admissible evidence, not a signed clause).
- **Counterparties (production)**: Gary, blueprint-producer, Kira, Tracy.

**Out-of-scope events stay in the tree as Declined nodes** with Irene's diagnosis + Maya's rationale. Declined ≠ omitted.

**ScopeDecision is a jurisdictional primitive** — logically upstream of Dials and Gaps. Only in-scope events can have Gaps; dials valid only on `in | delegated`.

### Winston's Data Primitives

```yaml
lesson_plan:
  learning_model: {id: "gagne-9", version: 1}
  structure: <opaque-to-platform>  # free-shape per learning model
  plan_units[]:
    - unit_id: "gagne-event-3"  # "Stimulate recall of prior learning"
      source_fitness_diagnosis: "..."  # Irene's commentary
      scope_decision: "in | out | delegated | blueprint"
      modality_ref: "slides | leader-guide | handout | classroom-exercise | blueprint"  # null unless delegated
      rationale: "..."  # Maya's own words preserved verbatim
      gaps: [...]
      dials: {enrichment?: float, corroboration?: float}  # only valid on in|delegated
  revision: N  # monotonic
  updated_at: <ts>
  digest: <sha256>
```

- Append-only JSONL revision log. Every downstream envelope 05→13 carries `{lesson_plan_revision, lesson_plan_digest}` for staleness detection.
- **Fit-report-v1** is its own artifact class: `{source_ref, plan_ref, diagnoses[]: {unit_id, fitness: "sufficient|partial|absent", commentary, recommended_scope_decision?}}`.
- **Two registries**: `modality_registry` (atomic producer targets: slides=ready, blueprint=ready, others=pending) + `component_type_registry` (composite packages; N=2 at MVP to prove shape).
- **ModalityProducer ABC**: Gary/Gamma implements slide modality; **blueprint-producer** (new, minimal: Markdown template + LLM fill + human review) implements blueprint modality.

### Marcus-Duality Split

- **Marcus-Intake**: owns steps 01-04 + 4A pre-packet construction.
- **Marcus-Orchestrator**: owns 4A conversation loop + plan-lock commit + downstream fan-out (05+).
- One Maya-facing facade; internal module split. Communication via the append-only Lesson Plan log.

### MVP Discipline (John's deferrals, user-ratified)

- **Gagné hardcoded** — name the seam, don't build second-model support.
- **Sync Irene reassessment only** — no async queues. Revisit if fit-reports take >30s.
- **N=2 modalities** at MVP: slides (Gary/Gamma, existing) + blueprint (new minimal). Leader-guide / handout / classroom-exercise stay `pending` in registry. User resolved the original "ship 1 vs 2 modalities" tension by proposing the blueprint catch-all — **any plan_unit APP can't produce gets represented in blueprint, so nothing is ignored; Quinn-R checks the box in the two-branch form**.
- **Dial-surface UI polish** deferred. Data model must be correct; UI can land a sprint later.
- **Component-type registry inventory** kept to N=2. Expansion deferred.
- **Consensus cross-validation (27-2.5)** stays blocked on its CI 3x-run flake gate. Not in MVP.

### Sally's UX Primitives (for test-fixture and trial-run framing)

- **Weather-band diagnosis** on the Maya-facing Step-4A ribbon: warm-gold / soft-green / pale-amber / dove-gray. No red (Maya didn't fail — her source is what it is).
- **Default scope stances per event-card**: gold → auto in-scope; gray → Marcus-proposed delegation/blueprint. Prevents scope-decision fatigue.
- **Marcus-as-chat-dial** (no form pickers). Maya's sentence IS the rationale.
- **Step-07 "one hour that knows itself"** — artifacts as instruments in one ensemble, not a three-tab deliverable dashboard.

---

## Epic / Story Plan (Amelia's draft — post-R1 ruling)

22 stories across 5 epics; Epic 27 is done and stays closed. *Updated 2026-04-18 per orchestrator R1 adjudication (see §Orchestrator Ruling Record for 17 amendments).*

### Epic 28 — Tracy the Detective (reshape + minimum capability)

| Key | Title | Pts | Deps |
|---|---|---|---|
| **28-1-tracy-reshape-charter** | Retire original Tracy spec; re-charter as minimal research agent wrapping `retrieval.dispatcher`. Codify three postures (embellish / corroborate / gap-fill) with John's four-part contract each: input shape / output shape / success signal / failure mode. State explicitly that corroborate handles BOTH confirming AND disconfirming evidence via scite's supporting/contrasting/mentioning classification — disconfirming is a RESULT TYPE within corroborate, not a 4th posture. Postures align to operator-memory framing (enrichment / gap-filling / evidence-bolster). *Ruling amendment 9.* | 2 | — |
| **28-2-tracy-three-modes** | `tracy.embellish()`, `tracy.corroborate()`, `tracy.gap_fill()` — each dispatches to provider_directory per IdentifiedGap or dial. Murat AC amendments: (a) posture-discrimination matrix + refuse-on-ambiguous-intent negative test, (b) per-posture result-shape contract (embellish=enrichment shape; corroborate=evidence-with-cross-ref shape; gap-fill=derivative-content shape), (c) negative test for `gap_fill` invoked with `scope_decision != in-scope` must fail closed. *Ruling amendment 10.* | 5 | 28-1, 31-1 |
| **28-3-irene-tracy-bridge** | IdentifiedGap on in-scope unit auto-dispatches at plan-lock; dial dispatches per operator endorsement. | 3 | 28-2, 29-2 |
| **28-4-tracy-smoke-fixtures** | Canned research fixtures (DOCX + scite.ai) covering all 3 modes; regression-pins Tracy for trial run. | 3 | 28-2 |

**28-1 landmine (Amelia flagged, resolved by ruling amendment 9):** The charter codifies the three postures with four-part contract language and explicit scite classification mapping. All three hit the same dispatcher, differing only in posture — the distinction is now codified, so the bridge (28-3) routes correctly.

### Epic 29 — Enhanced Irene (Gagné diagnostician + blueprint co-author)

| Key | Title | Pts | Deps |
|---|---|---|---|
| **29-1-fit-report-v1** | `fit-report-v1` artifact class — schema shipped from 31-1; 29-1 implements validator + serializer + emission wiring. *Schema moved to 31-1 per ruling amendment 5.* | 3 | 31-1 |
| **29-2-gagne-diagnostician** | Irene diagnostic pass: event-by-event source-fitness commentary against hardcoded Gagné Nine Events; returns `fit-report-v1`; sync-only, <30s budget. Consumes prior Declined rationales (from 31-5 emission) to avoid re-diagnosing settled ground. *Ruling amendment 15.* | 5 | 29-1 |
| **29-3-irene-blueprint-coauthor** | Irene's blueprint-spec co-authorship protocol with human writer; sign-off pointer emitted into `plan_unit.blueprint_signoff`. | 3 | 31-4, 29-2 |

### Epic 30 — Enhanced Marcus (duality + 4A loop)

| Key | Title | Pts | Deps |
|---|---|---|---|
| **30-1-marcus-duality-split** | Module split: `marcus/intake/` (01-04 + 4A pre-packet) and `marcus/orchestrator/` (4A loop + lock + 05+ fan-out); single Maya-facing facade. **Golden-Trace Baseline Gate (Murat RED, binding):** before 30-1 opens, capture pre-refactor Marcus envelope I/O on trial corpus as committed fixture. DoD adds: byte-identical post-refactor (modulo timestamp/UUID normalization) + zero test edits + coverage non-regression + facade-leak detector AC (Maya's call surface logs one Marcus identity under 50-iter 4A loop + negative test: non-Maya direct invocation of Marcus-Orchestrator fails) + name the `marcus-negotiator` seam in the 30-1 doc even if folded into Marcus-Orchestrator for MVP. **Single-writer rule (Quinn):** Marcus-Orchestrator is sole writer on Lesson Plan log. Marcus-Intake emits exactly one event (`pre_packet_snapshot`) at 4A entry via Orchestrator's write API. **No user-facing string references "Intake" or "Orchestrator"** — Marcus is Marcus, one voice (ruling amendment 17). *Ruling amendments 12, 13, 17.* | 5 | 31-2 |
| **30-2a-pre-packet-extraction-lift** | **Refactor-only lift** of existing extraction code into `marcus/intake/`. No new behavior; preserve all outputs byte-identical. *Ruling amendment 2.* | 1 | 30-1 |
| **30-2b-pre-packet-envelope-emission** | New pre-packet envelope emission + Irene handshake (feature work on top of 30-2a lift). Marcus-Intake emits exactly one `pre_packet_snapshot` event via Orchestrator write API (single-writer enforced). *Ruling amendments 2, 13.* | 2 | 30-2a, 29-1 |
| **30-3a-4a-skeleton-and-lock** | 4A loop shell + scope-decision intake + plan-lock trigger. Dials rendered as read-only "coming soon" affordances with Marcus line *"I'll learn to tune these next sprint"* (Sally guardrail). Stub-dials contract. **AC:** plan-lock is invariant to reassessment outcome (Murat). **AC (ruling amendment 16):** `rationale` field accepts free text, stored verbatim, surfaced verbatim in Marcus's confirmation echo. No parsing, no coercion, no enum. *Ruling amendments 1, 16.* | 4 | 30-2b, 29-2, 31-2 |
| **30-3b-dials-and-sync-reassessment** | Dial tuning + Irene sync reassessment wiring + voice-continuity AC across ≥3 iterations (Sally) + fallback contract when p95 >30s (Murat). **Hard dependency: 30-5 retrieval-narration-grammar must land first** so Marcus can surface Tracy-provenance postures in his voice. *Ruling amendment 1.* | 4 | 30-3a, 30-5 |
| **30-4-plan-lock-fanout** | Plan-lock commit emits Lesson Plan to log; auto-dispatches gaps on in-scope events via Irene→Tracy bridge; fans to step 05+ with plan-ref in envelopes. Marcus-Orchestrator is sole writer on the log (Quinn single-writer rule enforced). *Ruling amendment 13.* | 5 | 30-3b, 28-3, 31-2 |
| **30-5-retrieval-narration-grammar** | **NEW (Sally RED).** Marcus's sentence template for surfacing Tracy-provenance postures (embellish / corroborate / gap-fill) in the voice Maya hears. One sentence template per posture, consistent cadence. Must land BEFORE 30-3b. *Ruling amendment 3.* | 2 | 28-2, 29-2 |

**30-3 pre-split ratified (Round 1, 5/5 GREEN):** 30-3a (skeleton + lock, stub-dials) + 30-3b (dials + sync reassessment), with 30-5 retrieval-narration-grammar interposed as a Sally RED must-fix prerequisite to 30-3b.

### Epic 31 — Tri-phasic contract primitives + gates (FOUNDATION — must ship first)

| Key | Title | Pts | Deps |
|---|---|---|---|
| **31-1-lesson-plan-schema** | **Bumped 3 → 5pts.** Absorbs (as a single reviewable schema PR): `lesson_plan` dataclass + JSON schema; `plan_unit` + `dials` + `gaps[]` + revision/digest; **`fit-report-v1` artifact class schema** (was 29-1); **`ScopeDecision` value-object + state machine** (proposed → ratified → locked, who-can-transition rules — Winston); **`scope_decision_transition` event primitive** (when/why a ScopeDecision flipped; temporal audit — Quinn); **`weather_band` as first-class field on `plan_unit`** (gold \| green \| amber \| gray — Sally); **`no-red` policy as schema validator constraint** (Sally); **`event_type` as open string with validator, NOT closed enum** (Gagné seam — Quinn); **companion artifact `dials-spec.md`** shipped alongside documenting dial semantics (ranges, interactions, operator-facing wording — Quinn hedge for deferred UI). *Ruling amendment 5.* | 5 | — |
| **31-2-lesson-plan-log** | Append-only JSONL log + monotonic revision + digest computation + `assert_plan_fresh(envelope)` staleness detector. **Named mandatory log events (ruling amendment 8):** `plan_unit.created`, `scope_decision.set`, `scope_decision_transition`, `plan.locked`, `fanout.envelope.emitted`, `pre_packet_snapshot`. **Single-writer rule at schema level** — only Marcus-Orchestrator has write permission; Marcus-Intake writes via Orchestrator's write API (Quinn). *Ruling amendments 8, 13.* | 3 | 31-1 |
| **31-3-registries** | **Resized 3 → 2pts** (schema work moved to 31-1). `modality_registry` + `component_type_registry` + `ModalityProducer` ABC. Ships with stubbed consumer-contract fixtures from 30-3, 29-2, 28-2 (Murat amendment). *Ruling amendment 6.* | 2 | 31-1 |
| **31-4-blueprint-producer** | Minimal blueprint-producer: Markdown template + LLM fill + human-review checkpoint; implements ModalityProducer. **HOLD at 5pts single story** — Quinn's split proposal declined; blueprint is human-review-driven, Gary-handoff contract is trivial at MVP. *Ruling amendment 7.* | 5 | 31-3 |
| **31-5-quinn-r-two-branch** | Step-13 Quinn-R gate: per-unit assertion (produced-asset-passes-quality OR blueprint-signed-by-Irene+writer); Declined-with-rationale audit for out-of-scope. **Declined-with-rationale consumer named (ruling amendment 15):** next-run's Irene pre-loads prior Declined rationales to avoid re-diagnosing settled ground. AC on 31-5 (emission) + 29-2 (consumption). *Ruling amendment 15.* | 5 | 31-1, 31-4 |

### Epic 32 — Step 4A landing + trial-run harness

| Key | Title | Pts | Deps |
|---|---|---|---|
| **32-1-step-4a-workflow-wiring** | Insert 4A between step-04 gate and step-05; update sprint-status.yaml + workflow runner; baton handoff contracts. | 3 | 30-4 |
| **32-2-plan-ref-envelope-coverage-manifest** | **Refined (ruling amendment 14):** audit logic lives in 31-2 log; 32-2 becomes coverage-manifest verifier — enumerates full envelope-type × plan-revision matrix, emits `coverage-manifest` artifact. Every envelope 05→13 carries `{lesson_plan_revision, lesson_plan_digest}`. | 3 | 31-2 |
| **32-3-trial-run-smoke-harness** | End-to-end smoke test: canned SME → 01→13 full traversal → trial-run-ready assertion battery. Paired with 32-4 Maya journey walkthrough. | 5 | all-above |
| **32-4-maya-journey-walkthrough** | **NEW (Sally YELLOW).** End-to-end pantomime AC: *"Maya pastes source, sees weather ribbon, clicks a gray card, Marcus proposes delegation, Maya types one sentence, card turns gold."* Paired with 32-3 trial harness. *Ruling amendment 4.* | 3 | 32-3 |

### Totals

- **22 stories, ~80 points, 5 epics** (1 existing reshape + 4 new). *Updated per R1 orchestrator ruling: 30-3 split into 30-3a+30-3b; 30-2 split into 30-2a+30-2b; 30-5 added (Sally RED); 32-4 added (Sally YELLOW); 31-1 bumped 3→5; 31-3 resized 3→2; 29-1 schema absorbed into 31-1.*
- **Critical path: 20 of 22 stories.** Off-path: 28-4 (Tracy smoke fixtures), 29-3 (Irene blueprint co-author — parallelizable against 31-4).
- **Parallelism: ~20% compression** with 2-3 dev streams on Tracks A (Irene 29-*) / B (Tracy 28-*) / C (Marcus 30-*) post-31-foundation.

## Critical Path

Single-threaded longest chain (post-R1 ruling):
`31-1 → 31-2 → 31-3 → 29-1 → 29-2 → 30-1 → 30-2a → 30-2b → 30-3a → 28-1 → 28-2 → 28-3 → 30-5 → 30-3b → 30-4 → 31-4 → 29-3 → 31-5 → 32-1 → 32-2 → 32-3 → 32-4`

## First-Trial-Run Readiness Criteria (Operator-Checkable Pass/Fail Checklist)

*Major rewrite per R1 orchestrator ruling amendment 11 — aggregates John operator-readable criteria + Quinn three failure-mode fixtures + Sally Tuesday-morning experiential AC + Winston schema-change policy + Murat binding PDG (ratified at 5x, not 3x).*

### A. Artifact content floor (John — operator-readable)

- [ ] **A1. Named SME input floor.** At least one named real 7-page SME source file committed under `tests/fixtures/trial_corpus/` with operator-verifiable SHA-256 recorded in the run charter.
- [ ] **A2. Lesson Plan artifact content at plan-lock.** Every locked Lesson Plan MUST contain: `learning_model.id="gagne-9"`, ≥1 `plan_unit` per Gagné event with `source_fitness_diagnosis` populated, `scope_decision` set to one of {in-scope, out-of-scope, delegated-to-modality-X, blueprint}, verbatim `rationale` string per Maya-authored decision, `weather_band` field populated (gold | green | amber | gray — never red), monotonic `revision` int, stable `digest` sha256.
- [ ] **A3. Trial-run pass signal.** Unambiguous single-line assertion in `test_trial_run_e2e.py`: `assert run.trial_run_ready is True` with explicit reason-string on failure.
- [ ] **A4. Tracy modes exercised.** Trial corpus exercises all three postures: one `tracy.embellish()` dispatch (enrichment shape), one `tracy.corroborate()` dispatch with BOTH supporting and contrasting rows (scite classification), one `tracy.gap_fill()` dispatch on an in-scope unit. Refuse-on-ambiguous-intent negative path also fires once.
- [ ] **A5. Blueprint-producer failure-mode coverage.** At least one plan_unit with `scope_decision=blueprint` flagged as "APP-can't-produce"; blueprint-producer emits blueprint-signoff; Quinn-R step-13 gate accepts via blueprint-signed-by-Irene+writer branch.

### B. Failure-mode fixtures (Quinn — three must land)

- [ ] **B1. Silent-cache-miss.** Kill scite mid-loop; verify Marcus declares gap (logged, surfaced to Maya) and does NOT hallucinate corroborating evidence.
- [ ] **B2. Digest-drift / revision-collision.** Maya reverts a dial back to prior value; verify log behavior is explicitly specified (idempotent OR double-log) and AC pins which one. No silent divergence.
- [ ] **B3. Declined-node orphan.** Irene re-diagnoses an upstream signal for a previously-Declined node; verify contract — does the node re-evaluate or stay frozen? AC must pin which, with rationale, and test must assert it.

### C. Sally Tuesday-morning experiential AC

- [ ] **C1. Operator role-play completion.** Operator role-playing Maya with a real 7-page source completes one full 4A loop in **under 12 minutes** (wall-clock, observed), emerges with a locked plan, and can articulate in **one sentence per Declined card** why it was declined. If the operator can't — the rationale-verbatim contract (ruling amendment 16) is leaking.

### D. Winston schema-change policy (lockstep)

- [ ] **D1. Any post-31-1 schema edit.** Requires revision-envelope migration note + digest-recompute pass on trial fixtures. Lockstep test asserts named mandatory log events explicitly: `plan_unit.created`, `scope_decision.set`, `scope_decision_transition`, `plan.locked`, `fanout.envelope.emitted`, `pre_packet_snapshot`.
- [ ] **D2. Single-writer rule invariant.** Automated test: non-Orchestrator write attempt on Lesson Plan log raises explicit permission error.

### E. Murat binding PDG (ratified at 5x-consecutive, not 3x)

- [ ] **E1. Smoke battery green 5x-consecutive in CI.** `test_4a_loop_idempotent.py` + `test_trial_run_e2e.py` pass 5 consecutive runs. Any single flake within the 5x window = merge fail.
- [ ] **E2. Gagné diagnostician p95 ≤30s over 20-run batch.** Fail gate if p95 > 30s OR any single run > 45s. Named fallback contract ships with 29-2 and is exercised when breached.
- [ ] **E3. Diagnosis stability.** Same input → same `source_fitness_diagnosis` across 10 consecutive runs, **0 variance on taxonomy label**.
- [ ] **E4. Per-story `tests_added ≥ K` floor.** Each story specifies K; §6 floor is the sum. Current known floors: 31-1 K≥20; 31-2 K≥12; 31-3 K≥8; 29-1 K≥8; 29-2 K≥10; 30-1 K≥10 (incl. golden-trace baseline + facade-leak); 30-2a K≥4; 30-2b K≥6; 30-3a K≥8; 30-3b K≥8; 30-4 K≥8; 30-5 K≥4; 28-1 K≥4; 28-2 K≥10 (incl. posture-discrimination matrix + negative tests); 28-3 K≥6; 28-4 K≥6; 29-3 K≥6; 31-4 K≥8; 31-5 K≥8; 32-1 K≥4; 32-2 K≥6; 32-3 K≥10; 32-4 K≥4. Floor sum ≈ **170 new tests**.

### F. Governance gates

- [ ] **F1. Provider directory.** `run_wrangler.py --list-providers` shows DOCX + scite.ai = `ready`; no regressions.
- [ ] **F2. `SCHEMA_CHANGELOG.md` in step.** Every schema version referenced in a trial-run fixture is acknowledged.
- [ ] **F3. bmad-code-review passed on every story** before `done` (non-negotiable per CLAUDE.md governance).
- [ ] **F4. bmad-party-mode green-light** on the MVP-complete state before trial run.
- [ ] **F5. Operator dry-run checklist** executed once by dev team before handing to real operator.

## Risk Register

| # | Risk | Mitigation |
|---|---|---|
| **R1** | ~~4A loop 8pt story (30-3) complexity explosion~~ **RESOLVED (R1 ratification, 5/5 GREEN).** | Pre-split ratified into 30-3a (skeleton + lock + stub-dials) / 30-3b (dials + reassessment); 30-5 retrieval-narration-grammar interposed before 30-3b. |
| **R2** | Irene Gagné p95 >30s on real SME | Instrument in 29-2 AC-T-2; Murat §6-E2 gate (p95 ≤30s over 20-run batch, any single run >45s = fail); named fallback contract ships with 29-2. Trim Gagné depth or renegotiate sync constraint before 30-3b if budget blown. |
| **R3** | Blueprint-producer human-review bottleneck | Dev pre-signs canned blueprints for trial corpus; decouple "review cadence" from trial-run blocker. |
| **R4** | Envelope plan-ref retrofit broad surface | 32-2 ships coverage-manifest verifier (ruling amendment 14) that enumerates envelope-type × plan-revision matrix and asserts plan-ref presence before trial. Audit logic lives in 31-2 log. |
| **R5** | Marcus duality refactor regressions on shipped Epic 27 work | Golden-Trace Baseline Gate (ruling amendment 12, Murat RED binding) — captured BEFORE 30-1 opens; DoD requires byte-identical post-refactor output + zero test edits + coverage non-regression + facade-leak detector AC. |
| **R6** | §6 flake-detection gate flake under 5x-consecutive target | Binding Murat PDG §6-E1: 5x-consecutive (not 3x) smoke battery required; per-story K test floors prevent under-tested stories from polluting the gate. Any single flake in the 5x window = merge fail. |
| **R7** | 30-1 Golden-trace baseline drift between capture and refactor | Baseline captured as committed fixture under version control before 30-1 opens; normalization rules (timestamp/UUID) explicit in 30-1 AC; byte-identical check is a regression blocker, not a soft warning. |
| **R8** | Tracy posture discrimination ambiguity at runtime | 28-2 Murat AC amendment (ruling amendment 10): posture-discrimination matrix fixture + refuse-on-ambiguous-intent negative test + per-posture result-shape contract + negative test for `gap_fill` invoked with `scope_decision != in-scope` must fail closed. Must ship as part of 28-2 DoD. |

## Orchestrator Ruling Record (R1 Party-Mode Review)

**Date:** 2026-04-18
**Review panel:** John (PM) / Winston (Architect) / Dr. Quinn (Problem-Solver) / Sally (UX) / Murat (Test)
**Adjudication:** Orchestrator (meta-agent) ratified the 17 amendments below after party-mode rounds. All amendments are additive/refining; original locked ratifications (§Quinn's Tri-Phasic Contract, §Winston's Data Primitives, §Marcus-Duality Split, §MVP Discipline, §Sally's UX Primitives) **unchanged**.

1. **30-3 pre-split ratified (5/5 GREEN)** — 30-3a skeleton + lock + stub-dials (with Sally "coming soon" line + Murat lock-invariant-to-reassessment AC); 30-3b dials + sync reassessment + voice-continuity AC (≥3 iterations) + p95>30s fallback contract.
2. **30-2 split (Winston RED must-fix)** — 30-2a refactor-only extraction lift; 30-2b new envelope emission + Irene handshake.
3. **30-5-retrieval-narration-grammar NEW (Sally RED, 2pts)** — Marcus's posture-sentence-template; must land before 30-3b.
4. **32-4-maya-journey-walkthrough NEW (Sally YELLOW, 3pts)** — end-to-end pantomime AC paired with 32-3.
5. **31-1 resize + absorb (3→5pts)** — absorbs fit-report-v1 schema, ScopeDecision state machine (Winston), scope_decision_transition event (Quinn), weather_band field (Sally), no-red validator (Sally), event_type open-string validator (Quinn Gagné seam), dials-spec.md companion (Quinn).
6. **31-3 resized 3→2pts** — schema work moved to 31-1; ships with stubbed consumer-contract fixtures (Murat).
7. **31-4 HOLD at 5pts** — Quinn's split proposal declined.
8. **31-2 mandatory log events named** — `plan_unit.created`, `scope_decision.set`, `scope_decision_transition`, `plan.locked`, `fanout.envelope.emitted`, `pre_packet_snapshot`.
9. **28-1 reshape charter codifies three postures** with John's four-part contract; corroborate handles both confirming and disconfirming via scite classification (not a 4th posture).
10. **28-2 Murat AC amendments** — posture-discrimination matrix + refuse-on-ambiguous-intent negative test; per-posture result-shape contract; gap_fill-with-non-in-scope fail-closed negative test.
11. **§6 MAJOR REWRITE** — operator-checkable pass/fail checklist aggregating John operator-readable criteria + Quinn three failure-mode fixtures + Sally Tuesday-morning experiential AC + Winston schema-change policy + Murat binding PDG (5x-consecutive, not 3x).
12. **30-1 Golden-Trace Baseline Gate (Murat RED binding)** — pre-refactor envelope I/O captured as committed fixture; byte-identical DoD; facade-leak detector AC; `marcus-negotiator` seam named even if folded for MVP.
13. **Single-writer rule on Lesson Plan log (Quinn)** — Marcus-Orchestrator sole writer; Marcus-Intake emits exactly one `pre_packet_snapshot` event via Orchestrator write API; enforced at 31-2 schema + 30-1/30-4 ACs.
14. **32-2 refined to coverage-manifest verifier** — audit logic lives in 31-2 log; 32-2 enumerates envelope-type × plan-revision matrix and emits coverage-manifest artifact.
15. **Declined-with-rationale consumer named** — next-run Irene pre-loads prior Declined rationales; AC on 31-5 (emission) + 29-2 (consumption).
16. **rationale = free_text verbatim AC on 30-3a** — free text stored verbatim, surfaced verbatim in Marcus's confirmation echo; no parsing, no coercion, no enum.
17. **No user-facing string references "Intake" or "Orchestrator"** — Marcus is Marcus, one voice; added to 30-1 AC + code-review checklist.

### R2 Party-Mode Green-Light on 31-1 (2026-04-18)

**Verdict:** 0 RED, 4 YELLOW — 11 rider amendments applied to `_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md` before dev-story execution. Panel: Winston / Murat / Quinn / Sally.

**Rider amendments:**

1. **W-1 (Winston)** — generic event envelope (`event_id` / `timestamp` / `plan_revision` / `event_type` / `payload`) pinned in 31-1; `pre_packet_snapshot` registered as RESERVED event_type (31-2 emits, 31-1 does not). AC-B.5a + AC-T.4a NEW.
2. **AM-1 (Murat)** — schema-pin test split into three shape-family files (`lesson_plan_shape` / `fit_shape` / `scope_shape`) with per-family SCHEMA_CHANGELOG entries.
3. **AM-2 (Murat)** — required-vs-optional bidirectional parity invariant added to the JSON-Schema ↔ Pydantic parity test (AC-T.2.d NEW).
4. **AM-3 (Murat)** — AC-T.7 digest determinism: tamper sub-assertion removed (tautological); replaced with nested-list-order sensitivity and None-vs-missing-field identity.
5. **M-extra (Murat)** — rationale parametrize expansion: `\r\n`, `\t`, emoji.
6. **Q-3 (Quinn)** — `dials-spec.md` companion test upgraded from presence-only to substance (≥1 default + ≥1 example per section).
7. **Q-5 (Quinn)** — `ScopeDecision` `model_validator(mode="after")` bypass guard rejecting locked-without-Maya, plus dedicated test.
8. **S-1 (Sally)** — abundance framing on weather_band + `dials-spec.md` operator wording (gold "you've got this cold" / green "we're in step" / amber "your call" / gray "Marcus leans in more" — no deficit language).
9. **S-2 (Sally)** — rationale edges (empty / single char / single word / leading-trailing whitespace); `PlanUnit.rationale` has NO `min_length`.
10. **S-3 (Sally)** — NON-NEGOTIABLE automated grep test scanning all user-facing strings for "intake" / "orchestrator" leaks (AC-T.14 NEW; R1 amendment 17 enforcement).
11. **S-4 (Sally + Orchestrator)** — two-level actor surface: public `proposed_by` / `actor` Literal `["system", "operator"]` + private `_internal_proposed_by` / `_internal_actor` Literal `["marcus", "marcus-intake", "marcus-orchestrator", "irene", "maya"]` with `Field(exclude=True)`. AC-T.15 NEW asserts Maya-facing `model_dump()` never leaks internal actors.

**K floor:** 22 → 25 (net +3 mandatory: envelope pin + no-leak grep + actor serialization). Realistic landing estimate unchanged at 30–40.

**Outcome:** 31-1 flips `ready-for-dev → in-progress` on T2 start; dev-story T2–T24 execution authorized. T25 (party-mode implementation review) + T26 (bmad-code-review) + T27 (closure) deferred to subsequent session gates G5 / G6 / G7-9.

## Deferrals (NOT in this MVP)

- 27-2.5 Consensus adapter + CI flake gate
- New retrieval/locator providers beyond DOCX + scite.ai
- Leader-guide / handout / classroom-exercise producers (registered `pending` only)
- Second learning model beyond Gagné
- Async Irene reassessment queue
- Dial-surface UI polish
- Component-type registry inventory beyond N=2
- Original Tracy spec (pre-reshape)
- Epic 27-3+ retrieval providers

## Key Artifacts Referenced in This Plan

- [`skills/bmad-agent-texas/references/retrieval-contract.md`](../../skills/bmad-agent-texas/references/retrieval-contract.md) — Shape 3-Disciplined retrieval contract
- [`skills/bmad-agent-texas/references/extraction-report-schema.md`](../../skills/bmad-agent-texas/references/extraction-report-schema.md) — Schema v1.1
- [`skills/bmad-agent-texas/scripts/retrieval/`](../../skills/bmad-agent-texas/scripts/retrieval/) — Foundation + SciteProvider
- [`_bmad-output/implementation-artifacts/27-0-retrieval-foundation.md`](../implementation-artifacts/27-0-retrieval-foundation.md) — Foundation spec
- [`_bmad-output/implementation-artifacts/27-2-scite-ai-provider.md`](../implementation-artifacts/27-2-scite-ai-provider.md) — scite.ai provider (first real retrieval consumer)
- [`_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md`](../implementation-artifacts/31-1-lesson-plan-schema.md) — foundation schema story (authored 2026-04-18, `ready-for-dev`)
- [`_bmad-output/implementation-artifacts/sprint-status.yaml`](../implementation-artifacts/sprint-status.yaml) — current sprint state

## Party-Mode Consensus Attribution

### Plan authoring (four-round consensus, 2026-04-18)

- **Quinn** — tri-phasic contract frame; attestor/signatory/counterparty role split; ScopeDecision as jurisdictional primitive; Declined nodes preserve deliberation; contract-law metaphor for audit posture.
- **Winston** — `learning_model + plan_units[]` data shape; two-registry separation (modality vs component-type); ModalityProducer ABC; append-only JSONL log with revision+digest; Marcus-duality split at plan-lock.
- **John** — MVP ruthlessness (diagnosis > outline); deferrals list; Gagné-hardcoded-with-seam; 4A one-callback-minimum for living-pact proof.
- **Sally** — conversational Marcus SPOC (ratified by user verbatim); weather-band diagnosis (no red); default scope stances per card; Marcus-as-chat-dial; Step-07 "one hour that knows itself".
- **User (operator)** — Lesson Plan as Marcus-led conversation; Irene = instructional designer (competence already present, not new); diagnosis-not-outline reframe; blueprint catch-all for APP-can't-produce units; no-Friday-spike ("I have greater confidence in the framework"); branch name `dev/lesson-planner`.

### R1 plan-doc review (2026-04-18 — orchestrator adjudication)

- **John** — §6 operator-readable pass/fail checklist frame; named SME input floor; explicit trial-run pass signal; which Tracy modes must be exercised; failure-mode coverage on blueprint scope decisions.
- **Winston** — 30-2 split (refactor-only lift vs feature emission) RED must-fix; 31-1 ScopeDecision state machine with who-can-transition rules; 31-2 mandatory log events named explicitly; schema-change policy with revision-envelope migration note + digest-recompute pass; 30-1 `marcus-negotiator` seam named.
- **Quinn** — 31-1 `scope_decision_transition` event primitive (temporal audit); `event_type` as open string with validator (Gagné seam); `dials-spec.md` companion artifact (deferred-UI hedge); single-writer rule on Lesson Plan log; three failure-mode fixtures (silent-cache-miss / digest-drift / Declined-orphan); 31-4 HOLD (split declined); 28-1 corroborate-handles-both-confirming-and-disconfirming-via-scite-classification framing.
- **Sally** — 30-3a stub-dials "coming soon" affordance + Marcus line; voice-continuity AC across ≥3 iterations on 30-3b; 30-5 retrieval-narration-grammar RED must-fix (Marcus's posture-sentence-template); 32-4 Maya journey walkthrough YELLOW; weather_band as first-class schema field; no-red policy as validator constraint; Tuesday-morning experiential AC (12-min loop with one-sentence Declined articulation); rationale verbatim (free text, no parsing).
- **Murat** — 30-1 Golden-Trace Baseline Gate RED binding; §6 binding PDG ratified at 5x-consecutive (not 3x); Gagné p95 ≤30s over 20-run batch (fail if any single run >45s); diagnosis-stability 0-variance-on-taxonomy across 10 runs; per-story `tests_added ≥ K` floor; 30-3a lock-invariant-to-reassessment AC; 30-3b p95>30s fallback contract; 28-2 posture-discrimination matrix + refuse-on-ambiguous + per-posture result-shape + negative test for gap_fill-non-in-scope; stubbed consumer-contract fixtures on 31-3.
- **Orchestrator (meta-agent adjudication)** — 17-amendment ruling consolidation; resolved all party-mode disagreements to consensus; ratified the original locked ratifications as unchanged; authorized 31-1 authoring in this session with status `ready-for-dev` pending R2 green-light.

## Next Steps

1. **R2 party-mode green-light on 31-1 story spec** (next session kick-off) — pressure-test the schema absorption (seven items in one PR), `tests_added ≥ K` floor, and the `dials-spec.md` companion shape before `bmad-dev-story` execution.
2. **After 31-1 R2 green-light + bmad-dev-story + bmad-code-review closure**: begin 31-2 (log) and 31-3 (registries) per critical-path sequence.
3. **Parallel pre-work during 31-1 dev**: Capture 30-1 Golden-Trace Baseline fixture (Murat RED binding) so it is committed and ready when 30-1 opens. Does not require 31-1 to land first — independent capture on trial corpus.
4. **Subsequent stories flow per updated critical-path sequence** (see §Critical Path — 22-story chain).
