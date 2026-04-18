# Story 28-1: Tracy Pilot (scite.ai End-to-End)

**Epic:** 28 — Tracy the Detective
**Status:** ratified-stub (promoted to full spec)
**Sprint key:** `28-1-tracy-pilot-scite-ai`
**Added:** 2026-04-17
**Points:** 9
**Depends on:** Epic 27 Story 27-2 (scite.ai provider in Texas) — **hard dependency; 28-1 cannot merge until 27-2 merges**. Story drafting and sanctum scaffolding may proceed against a stubbed scite client in parallel.
**Blocks:** 28-2 (gate hardening).

## Story

As the production pipeline,
I want Tracy born as a BMB-sanctum specialist who can receive a scoped research brief from Irene (via Marcus), dispatch scite.ai queries through Texas's scite provider, evaluate candidates with editorial judgment, and produce a `suggested-resources.yaml` manifest that — after operator approval — flows back through Texas second-pass into Irene Pass 2,
So that the first end-to-end demonstration of the Tracy lane validates the architecture, the manifest schema, the hard pre-Pass-2 gate, and the dispatch-vs-artifact rule under a real run.

## Background — Why This Story Exists

This is the pilot story for Tracy. Per the operator's 2026-04-17 non-negotiables:

- **NN2:** Epic/story artifacts updated tonight for Tracy born. Minimum: take research request from Irene via Marcus, direct Texas where/what to look for, return from scite.ai.
- **NN3:** Wrangled content must be available to Irene in Pass 2 and inform the script currently under development.

This story satisfies both. It's intentionally the minimum-viable lane validation — not a horizontal expansion across all future Tracy providers, not an operator-pulled alternative, not the coherence gate from Dr. Quinn. Those all live as v2 backlog per [epic-28 doc](./epic-28-tracy-detective.md).

## Acceptance Criteria

**AC-1: Tracy sanctum bundle complete and bootable**
- [`skills/bmad-agent-tracy/`](../../skills/bmad-agent-tracy/) exists with: `SKILL.md`, `references/` (first-breath + vocabulary.yaml + vocabulary.md + scite-provider.md + authority-tier-mapping.md + editorial-note-examples.md + memory-guidance.md), `scripts/` (dispatch.py + search_scite.py + score.py + emit_suggestions.py + ingest_approval.py), `schemas/` (suggested-resources.schema.yaml + tracy-approved-resources.schema.yaml), `assets/` (per Texas pattern).
- Scaffold v0.2 compliance: operator name = `Juanl`, repo-relative POSIX paths, no literal `{var}` tokens, bond shows operator name.
- Fresh-sanctum First-Breath works: running Tracy's activation from an empty `_bmad/memory/bmad-agent-tracy/` correctly loads `first-breath.md` and bootstraps the sanctum.

**AC-2: Dispatch topology — Irene → Marcus → Tracy**
- Irene's cluster manifest schema extended with optional `gaps[]` array. Each gap entry: `{cluster_id, gap_type, gap_description, enrichment_priority, desired_material_type}`.
- Marcus landing-point `tracy_dispatch` fires when Irene's Pass 1 output contains non-empty `gaps[]`. Landing-point follows Marcus posture rule (ask + show default/prior + recommend).
- Marcus synthesizes `runs/<run-id>/tracy/brief.yaml` from Irene's gaps + Dan's creative directive (read-only) + Texas's primary extraction report (read-only).
- Marcus dispatches Tracy with brief.yaml as input. Tracy is invoked via Skill-tool-native activation (precedent: Marcus Skill-tool load from 2026-04-17 trial runbook).

**AC-3: Tracy executes scite.ai search + scoring**
- Tracy's `dispatch.py` loads brief, formulates scite queries via `search_scite.py`.
- `search_scite.py` invokes Texas's scite provider library (`skills/bmad-agent-texas/scripts/providers/scite_client.py` — built in 27-2) — this is library call, not specialist dispatch.
- Candidate list scored via `score.py` using v1 naive rubric (documented in scoring-rubric.md): weights authority_tier (primary > secondary > tertiary > practitioner when relevance matches; practitioner treated orthogonally when the intent is practitioner-voice) × recency × scite `supporting_count - contradicting_count` × topical-relevance-tfidf.
- v1 rubric is explicit and documented; NOT a black-box learned model. Iteration expected post-pilot.

**AC-4: Tracy emits `suggested-resources.yaml`**
- Output at `runs/<run-id>/tracy/suggested-resources.yaml`.
- Atomic write (temp file + rename) per AC-S2.
- Validates against `schemas/suggested-resources.schema.yaml`.
- Each row has:
  - `id`, `modality`, `title`, `author_or_source`, `date_published`, `date_accessed`, `locator`, `access_method`, `rights_status`
  - `fit_slot_path` (canonical, e.g., `cluster-3/beat-2`) + `fit_slot_label` (human)
  - `fit_score` (0.0-1.0 per vocabulary.yaml scale)
  - `authority_tier` (per vocabulary.yaml enum)
  - `recency_weight`
  - `editorial_note` (non-empty, passes lint — see AC-S6)
  - `intent_class` + `intent_detail` + `reserved` sentinel support (per Paige's two-field pattern)
  - `alternatives_considered` (integer count)
  - `provider: scite` + `provider_metadata.scite: { supporting_count, contradicting_count, mentioning_count, citation_context_snippet, scite_report_url }`
- Companion `research-brief.md` at `runs/<run-id>/tracy/research-brief.md` — human-readable narrative per Paige's 400-word template (scope / top-finds / gaps / authority-posture / alternatives-considered).
- Day-1 `intent_class` enum: `narration_citation | supporting_evidence | counter_example | reserved`.

**AC-5: Marcus operator-approval landing point**
- Marcus landing-point `tracy_review` surfaces the manifest as a redlineable table per Sally's Round 1 UX:
  - Tiered confidence: `≥0.85 all scores = auto-adopted`; `≥0.60 or mixed = review`; `<0.60 authority = auto-rejected`
  - Grouped by `fit_slot_path` cluster
  - One-click promote/demote per row
- Operator decisions written to `runs/<run-id>/tracy/tracy-approved-resources.yaml` (atomic).
- Approved file validates against `schemas/tracy-approved-resources.schema.yaml`.
- Every operator action logged in `runs/<run-id>/tracy/dispatch-log.yaml` with timestamp + rationale.

**AC-6: Marcus dispatches Texas second-pass with approved resources**
- Marcus invokes Texas `run_wrangler.py --tracy-approved-resources <path> --bundle-dir <dir>` (flag added in 27-2).
- Texas reads approved file, fetches via scite provider, appends rows to `extraction-report.yaml` with:
  - `source_origin: tracy-suggested`
  - `tracy_row_ref: <approved-yaml-path>#<row_id>`
  - `provider_metadata.scite` populated
- No direct Tracy→Texas runtime call anywhere in the code path. `tests/contracts/test_dispatch_topology.py` asserts this.

**AC-7: Pre-Pass-2 gate receipt written**
- Marcus writes `runs/<run-id>/receipts/tracy-complete.yaml` atomically after Texas second-pass completes.
- Schema at `skills/bmad-agent-marcus/schemas/tracy-complete.schema.yaml`: `{tracy_status, dispatched_at, resolved_at, approved_rows_count, texas_pass2_receipt_ref, operator_acknowledged}`.
- Gate row added to `skills/bmad-agent-marcus/scripts/manage_run.py::STAGE_GATES` between `irene_pass1` and `irene_pass2`.

**AC-8: Irene Pass 2 ingestion**
- Irene's Pass 2 skill reads:
  - `runs/<run-id>/tracy/tracy-approved-resources.yaml` (the approved manifest with editorial judgment)
  - `runs/<run-id>/texas/extraction-report.yaml` (the second-pass extractions Texas produced)
- Irene's Pass 2 script generation now references Tracy-suggested material where `intent_class` is `narration_citation` or `supporting_evidence`; `counter_example` rows surface as Irene's choice for contrastive framing.
- Irene Pass 2 **refuses to start** without a valid `tracy-complete.yaml` receipt. Marcus's gate enforces.

**AC-9: Vocabulary SSOT + lockstep check**
- `skills/bmad-agent-tracy/references/vocabulary.yaml` authored tonight per Paige's Round-2 skeleton.
- Generated `vocabulary.md` checked in.
- L1 check `tests/contracts/test_tracy_vocab_lockstep.py` asserts every `intent_class` / `authority_tier` value emitted by Tracy's code is defined in vocabulary.yaml, and vice-versa every vocabulary value has a code handler + a test fixture exercising it.
- Check fails commit on divergence.

**AC-10: Test coverage (AC-S7 + Murat Round 3 pilot floor)**
- `tests/test_tracy_manifest_schema.py` — schema validation, all day-1 intent_class values, missing-field detection.
- `tests/test_tracy_pass2_gate.py::test_gate_blocks_without_receipt` — gate family (remaining two members in 28-2).
- `tests/contracts/test_tracy_manifest_shape.py` — locked contract Tracy↔Irene.
- `tests/test_epic_28_1_ratification.py::test_tracy_pilot_wiring_is_coherent` — Murat's ratification test: static check that every capability code + sanctum reference + gate row name + schema version mentioned in epic artifact resolves to a real artifact in the codebase.
- `tests/contracts/test_dispatch_topology.py` — no Tracy→Texas direct runtime call.
- Cassette library at `tests/cassettes/tracy/scite/` (reuses 27-2 cassettes where possible): search_happy, paper_metadata_happy, citation_context_happy, search_empty.
- All tests `@pytest.mark.tracy_pilot`; use `xfail(strict=True)` during implementation, remove marker as each AC lands green.

**AC-11: Dispatch audit log**
- `runs/<run-id>/tracy/dispatch-log.yaml` captures: dispatch_id, requested_at, resolved_at, requesting_agent, brief, queries_issued[], candidates_evaluated_count, candidates_surfaced_count, operator_actions[] (per-row approved/rejected/refined + rationale), outcome.
- One entry per Tracy dispatch in a run.

**AC-12: Regression — no new failures, no new skips**
- Full pytest green (baseline 622 passing as of 2026-04-17 progress-map hardening).
- No `@pytest.mark.skip` or `xfail` in default suite at story closure (except xfail-strict tests gated behind `tracy_pilot` marker, all of which must flip green before closure).

## File Impact

### New — Tracy sanctum bundle (scaffold v0.2)
| File | Purpose |
|------|---------|
| `skills/bmad-agent-tracy/SKILL.md` | Agent persona, Three Laws, activation protocol |
| `skills/bmad-agent-tracy/references/first-breath.md` | First-Breath birthing protocol |
| `skills/bmad-agent-tracy/references/vocabulary.yaml` | **SSOT** for controlled vocabulary |
| `skills/bmad-agent-tracy/references/vocabulary.md` | Generated human-readable view |
| `skills/bmad-agent-tracy/references/scite-provider.md` | Reference guide for scite-specific query patterns |
| `skills/bmad-agent-tracy/references/authority-tier-mapping.md` | Paige Round-3 mapping table |
| `skills/bmad-agent-tracy/references/editorial-note-examples.md` | Excellent / mediocre / bad examples |
| `skills/bmad-agent-tracy/references/scoring-rubric.md` | v1 scoring rubric (documented even if naive) |
| `skills/bmad-agent-tracy/references/memory-guidance.md` | Session-close discipline (Texas pattern) |
| `skills/bmad-agent-tracy/scripts/dispatch.py` | Entry: orchestrates search → score → emit |
| `skills/bmad-agent-tracy/scripts/search_scite.py` | Thin wrapper on Texas's scite_client library |
| `skills/bmad-agent-tracy/scripts/score.py` | v1 scoring rubric implementation |
| `skills/bmad-agent-tracy/scripts/emit_suggestions.py` | Atomic manifest writer |
| `skills/bmad-agent-tracy/scripts/ingest_approval.py` | Writes approved manifest for Marcus to hand to Texas |
| `skills/bmad-agent-tracy/schemas/suggested-resources.schema.yaml` | Manifest schema |
| `skills/bmad-agent-tracy/schemas/tracy-approved-resources.schema.yaml` | Approved-rows schema |
| `skills/bmad-agent-tracy/scripts/init-sanctum.py` | First-Breath scaffold (uses shared `scripts/bmb_agent_migration/init_sanctum.py`) |

### Modified — Marcus
| File | Change |
|------|--------|
| `skills/bmad-agent-marcus/scripts/manage_run.py` | Add `tracy_complete` gate row between `irene_pass1` and `irene_pass2` |
| `skills/bmad-agent-marcus/schemas/tracy-complete.schema.yaml` | New — gate receipt schema |
| `skills/bmad-agent-marcus/references/workflow-templates.yaml` | Insert Tracy dispatch stage between Irene Pass 1 and Texas second-pass |
| `skills/bmad-agent-marcus/templates/landing-points/tracy_dispatch.md` | New — operator landing point for Tracy dispatch decision |
| `skills/bmad-agent-marcus/templates/landing-points/tracy_review.md` | New — redlineable manifest review landing point |

### Modified — Irene
| File | Change |
|------|--------|
| `skills/bmad-agent-content-creator/scripts/pass2_ingest.py` (or equivalent Irene script) | Reads `tracy-approved-resources.yaml` + second-pass `extraction-report.yaml` |
| `skills/bmad-agent-content-creator/references/cluster-manifest-schema.md` | Adds `gaps[]` optional array to Pass 1 output schema |

### Modified — Texas (from 27-2 — not Re-modified in 28-1)
Already covered by 27-2: `--tracy-approved-resources` flag, `source_origin` + `tracy_row_ref` fields, atomic writes.

### Cross-cutting
| File | Change |
|------|--------|
| `_bmad-output/implementation-artifacts/sprint-status.yaml` | Epic 28 block + 28-1, 28-2 rows (done during ratification tonight) |

### Tests
| File | Purpose |
|------|---------|
| `tests/test_tracy_manifest_schema.py` | Schema validation |
| `tests/test_tracy_pass2_gate.py` | Gate family — 28-1 contributes `test_gate_blocks_without_receipt`; 28-2 adds the rest |
| `tests/contracts/test_tracy_manifest_shape.py` | Locked Tracy↔Irene contract |
| `tests/test_epic_28_1_ratification.py` | Murat's static ratification check |
| `tests/contracts/test_dispatch_topology.py` | No Tracy→Texas direct runtime call |
| `tests/contracts/test_tracy_vocab_lockstep.py` | L1 vocab lockstep |
| `tests/test_tracy_dispatch.py` | Tracy scoring + query formulation |
| `tests/cassettes/tracy/scite/*.yaml` | Reused from 27-2 where possible |

## Tasks / Subtasks

- [ ] T1: Author `skills/bmad-agent-tracy/references/vocabulary.yaml` v0.1 per Paige's Round-3 skeleton. **Load-bearing — all other Tracy artifacts reference this.**
- [ ] T2: Generate `vocabulary.md` from vocabulary.yaml; commit both.
- [ ] T3: Scaffold Tracy sanctum bundle using `scripts/bmb_agent_migration/init_sanctum.py` (scaffold v0.2, operator `Juanl`).
- [ ] T4: Author `SKILL.md` (≤60 lines per specialist-tier ceiling from Epic 26).
- [ ] T5: Author references: first-breath, scite-provider, authority-tier-mapping, editorial-note-examples, scoring-rubric, memory-guidance.
- [ ] T6: Author schemas: `suggested-resources.schema.yaml`, `tracy-approved-resources.schema.yaml`, (+ Marcus's `tracy-complete.schema.yaml`).
- [ ] T7: Implement `search_scite.py` against Texas 27-2 `scite_client.py` library.
- [ ] T8: Implement `score.py` with v1 naive rubric.
- [ ] T9: Implement `emit_suggestions.py` with atomic write (temp + rename) and schema validation.
- [ ] T10: Implement `ingest_approval.py` for writing the approved-resources YAML.
- [ ] T11: Implement `dispatch.py` as orchestrator.
- [ ] T12: Add Marcus gate row in `manage_run.py`; write gate receipt schema; add landing-point templates.
- [ ] T13: Extend Irene Pass 1 output schema with `gaps[]`; extend Irene Pass 2 ingestion.
- [ ] T14: Write xfail-strict test scaffold for all AC-10 tests; flip strict-green as each AC lands.
- [ ] T15: Manual end-to-end dry-run: synthesize a sample Irene `gaps[]` file, dispatch Tracy, approve via Marcus landing-point, run Texas second-pass, verify Irene Pass 2 receives enriched inputs.
- [ ] T16: Regression pass (full pytest green + 0 new skips).
- [ ] T17: `bmad-code-review` (Blind Hunter + Edge Case Hunter + Acceptance Auditor); remediate MUST-FIX.
- [ ] T18: Closure record in sprint-status.yaml + worksheet-28-1.md filed in `epic-28/_shared/`.

## Test Plan

| Test | Layer | Cassette | Blocking? |
|------|-------|----------|-----------|
| `test_tracy_manifest_schema` | Unit | No | Yes |
| `test_tracy_pass2_gate::test_gate_blocks_without_receipt` | Integration | No | Yes |
| `test_tracy_manifest_shape` (Tracy↔Irene contract) | Contract | No | Yes |
| `test_epic_28_1_ratification::test_tracy_pilot_wiring_is_coherent` | Static | No | Yes |
| `test_dispatch_topology::test_no_tracy_to_texas_direct_call` | Static | No | Yes |
| `test_tracy_vocab_lockstep::test_every_value_has_handler` | Contract | No | Yes |
| `test_tracy_dispatch::test_search_happy_path` | Integration | Yes | Yes |
| `test_tracy_dispatch::test_score_v1_rubric` | Unit | No | Yes |
| `test_tracy_dispatch::test_empty_search_produces_empty_outcome` | Integration | Yes | Yes |
| Manual dry-run | E2E | Yes | **Yes — this is the story's proof** |

## Out of Scope

- Additional Tracy providers (Notion, Box, YouTube, Playwright) — Epic 29+ or later 28-N stories.
- Coherence gate between Tracy's material and primary material — 28-v2-a backlog.
- Pre-indexed domain map (async cached authority priors) — deferred to post-pilot retro.
- Operator-pulled Tracy — deferred, revisit with pilot evidence.
- Fan-out to asset agents beyond narration (handouts, podcasts, test images, games) — Tracy's manifest carries intent tags but consuming agents don't exist yet.
- Post-pilot rubric iteration — expected but a separate follow-on story.

## Risks

| Risk | Mitigation |
|------|------------|
| 27-2 scite provider not merged when 28-1 code starts | Scaffold against stubbed scite_client; mock responses until real client lands. |
| Marcus's Skill-tool-native load UX rough (known from 2026-04-17 trial) | Accept for pilot; harness-level improvement is out of scope here. |
| Irene's `gaps[]` schema extension creates backward-compat issue for existing Irene tests | Make `gaps[]` optional with default empty; regression-test the old path. |
| Lockstep check (AC-9) too strict for early v1 vocabulary | Start with warn-mode for 48 hours post-merge; promote to error after confidence. |
| Cassette drift between 27-2 scite_client and 28-1 usage | Share cassette directory `tests/cassettes/texas/scite/`; both epics reference same canonical set. |
| Scoring rubric v1 produces obviously-wrong rankings on first real run | Expected. Rubric iteration is a named post-pilot activity. First run is evidence-gathering, not validation. |

## Done When

- [ ] All 12 ACs green.
- [ ] Manual end-to-end pilot run demonstrated: sample Irene gaps → Tracy dispatch → operator approval → Texas second-pass → Irene Pass 2 with enriched inputs.
- [ ] `bmad-code-review` run adversarially; MUST-FIX items remediated or explicitly deferred with rationale.
- [ ] Worksheet filed at `epic-28/_shared/worksheet-28-1.md`.
- [ ] Closure record in `sprint-status.yaml` with test counts + review summary.

## Party Input Captured

- **Winston (Round 1 + dispatch ratification):** Tracy is pure specialist with own manifest. Marcus owns every dispatch edge. Filesystem-mediated artifact handoff.
- **John (PM, Round 3):** 2-story compression — 28-1 stops at operator approval... *amended per operator NN3 and subsequent Round 3 convergence to include Texas second-pass + Irene Pass 2 ingestion in one story so the pilot actually validates the full lane*. Scoring rubric is an explicit AC.
- **Amelia (Dev, Round 3):** file-path inventory (new sanctum bundle + Marcus/Irene mods + schemas + tests); atomic-write requirement.
- **Paige (Docs, Round 2+3):** two-field vocabulary pattern; `editorial_note` field name; authority-tier mapping; research-brief template.
- **Murat (Test, Round 2+3):** 3-test floor + ratification test; cassette-first doctrine; xfail-strict pre-implementation.
- **Sally (UX, Round 1):** redlineable manifest review (not prompt chain); tiered confidence auto-adopt/review/reject; failure UX.
- **Mary (Analyst, Round 1):** cognitive-lineage — Tracy inherits triangulation + authority-scoring; disinherits saturation instinct. `editorial_note` is what distinguishes Tracy from search wrapper.
- **Dr. Quinn (Round 2):** coherence gate + pre-indexed domain map deferred to v2 backlog; dispatch log is load-bearing for post-pilot loop detection.
- **Operator (2026-04-17 NN2 + NN3):** Tracy born tonight, minimum capability confirmed, wrangled content in Pass 2.
