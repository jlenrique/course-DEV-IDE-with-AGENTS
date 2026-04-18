# Lesson Planner MVP — Plan for First Trial Run

**Created:** 2026-04-18 (session-wrapup artifact, `dev/lesson-planner` branch)
**Author:** Amelia (💻 BMAD Developer Agent) + Four-round party-mode consensus (John / Winston / Dr. Quinn / Sally)
**Status:** Pending party-mode review (next session) → `bmad-create-story` pass for Epic 31

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

## Epic / Story Plan (Amelia's draft)

19 stories across 5 epics; Epic 27 is done and stays closed.

### Epic 28 — Tracy the Detective (reshape + minimum capability)

| Key | Title | Pts | Deps |
|---|---|---|---|
| **28-1-tracy-reshape-charter** | Retire original Tracy spec; re-charter as minimal research agent wrapping `retrieval.dispatcher`. | 2 | — |
| **28-2-tracy-three-modes** | `tracy.embellish()`, `tracy.corroborate()`, `tracy.gap_fill()` — each dispatches to provider_directory per IdentifiedGap or dial. | 5 | 28-1, 31-1 |
| **28-3-irene-tracy-bridge** | IdentifiedGap on in-scope unit auto-dispatches at plan-lock; dial dispatches per operator endorsement. | 3 | 28-2, 29-2 |
| **28-4-tracy-smoke-fixtures** | Canned research fixtures (DOCX + scite.ai) covering all 3 modes; regression-pins Tracy for trial run. | 3 | 28-2 |

**28-1 landmine (Amelia flagged):** The charter MUST write down the three semantic definitions (embellish / corroborate / gap-fill) as operator-usable contract language. All three hit the same dispatcher, differing only in posture — if the distinction isn't codified, the bridge (28-3) will route incorrectly.

### Epic 29 — Enhanced Irene (Gagné diagnostician + blueprint co-author)

| Key | Title | Pts | Deps |
|---|---|---|---|
| **29-1-fit-report-v1** | `fit-report-v1` artifact class: schema + validator + serializer. | 3 | 31-1 |
| **29-2-gagne-diagnostician** | Irene diagnostic pass: event-by-event source-fitness commentary against hardcoded Gagné Nine Events; returns `fit-report-v1`; sync-only, <30s budget. | 5 | 29-1 |
| **29-3-irene-blueprint-coauthor** | Irene's blueprint-spec co-authorship protocol with human writer; sign-off pointer emitted into `plan_unit.blueprint_signoff`. | 3 | 31-4, 29-2 |

### Epic 30 — Enhanced Marcus (duality + 4A loop)

| Key | Title | Pts | Deps |
|---|---|---|---|
| **30-1-marcus-duality-split** | Module split: `marcus/intake/` (01-04 + 4A pre-packet) and `marcus/orchestrator/` (4A loop + lock + 05+ fan-out); single Maya-facing facade. | 5 | 31-2 |
| **30-2-pre-packet-builder** | Pre-packet construction from step-03 extraction + 02a Maya aims → shipped to Irene for diagnosis. | 3 | 30-1, 29-1 |
| **30-3-4a-conversation-loop** | 4A iteration loop: Maya sees diagnosis → sets scope per event → sets dials → can re-call Irene sync → plan-lock commit. | 8 | 30-2, 29-2, 31-2 |
| **30-4-plan-lock-fanout** | Plan-lock commit emits Lesson Plan to log; auto-dispatches gaps on in-scope events via Irene→Tracy bridge; fans to step 05+ with plan-ref in envelopes. | 5 | 30-3, 28-3, 31-2 |

**30-3 landmine (Amelia flagged R1, HIGH):** 8pts combines loop skeleton + lock + dial surface + sync reassessment + Maya-sole-signatory discipline. **Recommended pre-split**: 30-3a (skeleton + lock) / 30-3b (dial surface + sync reassessment).

### Epic 31 — Tri-phasic contract primitives + gates (FOUNDATION — must ship first)

| Key | Title | Pts | Deps |
|---|---|---|---|
| **31-1-lesson-plan-schema** | Define `lesson_plan` dataclass + JSON schema + `plan_unit` + `dials` + `gaps[]` + revision/digest. | 3 | — |
| **31-2-lesson-plan-log** | Append-only JSONL log + monotonic revision + digest computation + `assert_plan_fresh(envelope)` staleness detector. | 3 | 31-1 |
| **31-3-registries** | `modality_registry` + `component_type_registry` + `ModalityProducer` ABC. | 3 | 31-1 |
| **31-4-blueprint-producer** | Minimal blueprint-producer: Markdown template + LLM fill + human-review checkpoint; implements ModalityProducer. | 5 | 31-3 |
| **31-5-quinn-r-two-branch** | Step-13 Quinn-R gate: per-unit assertion (produced-asset-passes-quality OR blueprint-signed-by-Irene+writer); Declined-with-rationale audit for out-of-scope. | 5 | 31-1, 31-4 |

### Epic 32 — Step 4A landing + trial-run harness

| Key | Title | Pts | Deps |
|---|---|---|---|
| **32-1-step-4a-workflow-wiring** | Insert 4A between step-04 gate and step-05; update sprint-status.yaml + workflow runner; baton handoff contracts. | 3 | 30-4 |
| **32-2-plan-ref-envelope-audit** | Every envelope 05→13 carries `{lesson_plan_revision, lesson_plan_digest}`; lockstep test scans all envelope schemas. | 3 | 31-2 |
| **32-3-trial-run-smoke-harness** | End-to-end smoke test: canned SME → 01→13 full traversal → trial-run-ready assertion battery. | 5 | all-above |

### Totals

- **19 stories, ~76 points, 5 epics** (1 existing reshape + 4 new).
- **Critical path: 18 of 19 stories.** Only 28-4 is strictly off-path.
- **Parallelism: ~20% compression** with 2-3 dev streams on Tracks A (Irene 29-*) / B (Tracy 28-*) / C (Marcus 30-*) post-31-foundation.

## Critical Path

Single-threaded longest chain:
`31-1 → 31-2 → 31-3 → 29-1 → 29-2 → 30-1 → 30-2 → 30-3 → 28-1 → 28-2 → 28-3 → 30-4 → 31-4 → 29-3 → 31-5 → 32-1 → 32-2 → 32-3`

## First-Trial-Run Readiness Criteria

1. **Regression floor**: ≥1149 + N_new passed, 0 failed, skips/xfails annotated.
2. **Smoke battery green 3x consecutive**: `test_trial_run_e2e.py`, `test_tracy_trial_fixtures.py`, `test_irene_gagne_diagnosis.py`, `test_4a_loop_idempotent.py`.
3. **Contract lockstep**: `SCHEMA_CHANGELOG.md` in step; `test_plan_ref_envelope_audit` passes — every envelope 05→13 carries plan-ref fields.
4. **Quinn-R step-13 gate green** on trial corpus — every unit produced / blueprint-signed / Declined-with-rationale.
5. **Provider directory**: `run_wrangler.py --list-providers` shows DOCX + scite.ai = `ready`; no regressions.
6. **Operator dry-run checklist** executed once by dev team before handing to real operator.
7. **bmad-code-review passed** on every story before `done` (non-negotiable per CLAUDE.md governance).
8. **bmad-party-mode green-light** on the MVP-complete state before trial run.

## Risk Register

| # | Risk | Mitigation |
|---|---|---|
| **R1** | 4A loop 8pt story (30-3) complexity explosion | Pre-split into 30-3a (skeleton + lock) / 30-3b (dials + reassessment); party-mode review after 30-3a |
| **R2** | Irene Gagné p95 >30s on real SME | Instrument in 29-2 AC-T-2; trim Gagné depth or renegotiate sync constraint before 30-3 if budget blown |
| **R3** | Blueprint-producer human-review bottleneck | Dev pre-signs canned blueprints for trial corpus; decouple "review cadence" from trial-run blocker |
| **R4** | Envelope plan-ref retrofit broad surface | 32-2 ships scanner that enumerates envelope schemas and asserts plan-ref presence before trial |
| **R5** | Marcus duality refactor regressions on shipped Epic 27 work | Full regression snapshot before 30-1; don't combine refactor + feature work in same story |

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
- [`_bmad-output/implementation-artifacts/sprint-status.yaml`](../implementation-artifacts/sprint-status.yaml) — current sprint state

## Party-Mode Consensus Attribution

- **Quinn** — tri-phasic contract frame; attestor/signatory/counterparty role split; ScopeDecision as jurisdictional primitive; Declined nodes preserve deliberation; contract-law metaphor for audit posture.
- **Winston** — `learning_model + plan_units[]` data shape; two-registry separation (modality vs component-type); ModalityProducer ABC; append-only JSONL log with revision+digest; Marcus-duality split at plan-lock.
- **John** — MVP ruthlessness (diagnosis > outline); deferrals list; Gagné-hardcoded-with-seam; 4A one-callback-minimum for living-pact proof.
- **Sally** — conversational Marcus SPOC (ratified by user verbatim); weather-band diagnosis (no red); default scope stances per card; Marcus-as-chat-dial; Step-07 "one hour that knows itself".
- **User (operator)** — Lesson Plan as Marcus-led conversation; Irene = instructional designer (competence already present, not new); diagnosis-not-outline reframe; blueprint catch-all for APP-can't-produce units; no-Friday-spike ("I have greater confidence in the framework"); branch name `dev/lesson-planner`.

## Next Steps

1. **Party-mode review of this plan** (next session kick-off) — pressure-test sequencing, point estimates, and the R1 pre-split recommendation before authoring. Use `bmad-party-mode` with Winston / Amelia / Murat / Paige (or the same John / Winston / Quinn / Sally four-panel that produced this plan — operator's choice).
2. **After plan ratification**: `bmad-create-story 31-1-lesson-plan-schema` to begin foundation. Subsequent stories flow per critical-path sequence.
