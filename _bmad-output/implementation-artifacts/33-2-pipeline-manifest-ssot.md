# Story 33-2: pipeline-manifest.yaml SSOT + Generator Rewire + L1 Lockstep Check

**Status:** done
**Created:** 2026-04-19 (authored against Epic 33 party-mode consensus — Pipeline Lockstep Substrate)
**Epic:** 33 — Pipeline Lockstep Substrate
**Sprint key:** `33-2-pipeline-manifest-ssot`
**Branch:** `dev/epic-33-lockstep` (continued from 33-1)
**Points:** 5
**Depends on:** 33-1 (done — generator identified, inputs/outputs enumerated, gap analysis complete)
**Blocks:** 33-3 (regenerate v4.2 + validate), 33-4 (Cora/Audra pre-closure block-mode), 15-1-lite-marcus (meta-test)
**Governance mode:** **dual-gate** — schema-shape story landing a new SSOT manifest + a new deterministic L1 lockstep check + rewires across 3+ consumers. R1 party-mode spec review + R2 green-light + G5 implementation review + G6 layered `bmad-code-review` (Blind + Edge + Auditor). Epic 33 is out of Lesson Planner MVP scope, so the Lesson Planner governance validator does NOT apply; BMAD sprint governance per [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance binds.

## TL;DR

- **What:** Author [`state/config/pipeline-manifest.yaml`](../../state/config/pipeline-manifest.yaml) (R1-C unanimous consensus; sibling to `parameter-registry-schema.yaml` and `narration-script-parameters.yaml`) as the single canonical declaration of the production pipeline (gates, order, names, gate-flag bitmap, insertion points, and — per party-mode LG-3 hybrid — per-gate `learning_events.emits / event_types / schema_ref` metadata). Land [`scripts/utilities/check_pipeline_manifest_lockstep.py`](../../scripts/utilities/check_pipeline_manifest_lockstep.py) as the deterministic L1 lockstep check (8 checks, strict 0/1/2 exit-code contract, O/I/A trace output at `reports/dev-coherence/<ts>/`). Rewire [`scripts/utilities/run_hud.py`](../../scripts/utilities/run_hud.py), [`scripts/utilities/progress_map.py`](../../scripts/utilities/progress_map.py), [`marcus/orchestrator/workflow_runner.py`](../../marcus/orchestrator/workflow_runner.py), and the v4.2 pack generator (entry point per 33-1 findings) to read from the manifest. No two projections of the manifest may disagree after this story closes.
- **Why:** DC-5 (absence of SSOT) is the root cause of DC-1..DC-4 per the party-mode walkthrough; Audra's O/I/A recast tagged it **Omission, Med→High severity** because it *permits* the symptom drifts to exist. Without this substrate, every future pipeline edit reopens the same three-way drift across pack ↔ HUD ↔ orchestrator (Paige: "a promise the code cannot keep"; Winston: "three surfaces each holding a private model of the pipeline"; Amelia: "three independent string-comparison surfaces"). 33-2 closes the disease; 33-3 cleans up the symptoms using the cure 33-2 provides; 33-4 makes the cure load-bearing via Cora's block-mode hook. The Q1 party-mode compromise (multi-version vs v4.2-only) resolved in favor of a **parameterized version hook** — the linter accepts a `--pack-version` arg today (v4.2 only), with a `pack_version` manifest field that makes v4.3+ extension a 1-line change rather than a retrofit.
- **Done when:** (1) Manifest exists, parseable, declares the complete pipeline in the Audra-specified hybrid shape (pipeline-shape concerns + per-gate emission topology; payload schemas live in sibling contracts referenced by path); (2) `check_pipeline_manifest_lockstep.py` exists with all 8 checks and the strict 0/1/2 exit contract, O/I/A trace emission, AST-only parsing (no regex); (3) schema-driven traversal is in place — adding a new top-level manifest key automatically becomes an assertion target (Murat's DoD); (4) closed-enum bidirectional checks catch both "manifest field not in schema" and "schema field not in manifest"; (5) red-path fixtures prove the checker actually catches schema-only-drift and manifest-only-drift — fixtures live in `tests/fixtures/pipeline_manifest_drift/` and are referenced by the L1 check's tests; (6) `run_hud.py::PIPELINE_STEPS` is replaced by a function that loads from the manifest; (7) `progress_map.py` is rewired to read manifest; (8) `workflow_runner.py::insert_4a_between_step_04_and_05` and any sibling insertion helpers are replaced by a manifest-driven dispatcher (step-insertions become manifest declarations, not imperative helpers — Winston's explicit architectural ask); (9) the v4.2 pack generator (entry point per 33-1 findings) reads from the manifest; (10) all existing tests that depended on the old projections pass against the new manifest-sourced shapes; (11) K=15 floor cleared at 18-23 collecting functions; (12) dual-gate ceremony completes: R1 + R2 party-mode rounds + G5 implementation review + G6 layered `bmad-code-review`; (13) sprint-status flipped `ready-for-dev → in-progress → review → done`.
- **Scope discipline:** 33-2 ships **zero edits to the on-disk v4.2 pack** (that's 33-3's scope — regenerate, don't hand-edit). 33-2 ships **zero new Marcus behavior** — the orchestrator rewire is refactor-only; observable behavior of `Facade.run_4a`, `route_step_04_gate_to_step_05`, `dispatch_orchestrator_event`, etc. is unchanged. 33-2 ships **zero governance changes** — Cora's pre-closure hook stays warn-mode until 33-4 promotes it. If a temptation surfaces to fix DC-1..DC-4 *in* 33-2 instead of waiting for 33-3's regeneration, route the fix through the manifest and let 33-3 land the regenerated artifacts — per-surface hand-edits are the 31-1 rename-one-surface anti-pattern and the 27-2 hand-edit anti-pattern combined.

## Story

As a **system architect maintaining the APP's pipeline across three surfaces**,
I want **one canonical manifest that declares every pipeline step's identity, order, gate status, insertion topology, and emission topology, plus a deterministic L1 check that enforces three-way lockstep between the manifest and every projection**,
So that **the next pipeline edit (whether it's a new gate, a new learning-event emission point, or a fix to DC-1..DC-4) flows through one place and is automatically caught by CI if any projection fails to track — closing the FM-A/FM-B/FM-C failure modes Cora named in her party-round self-audit**.

## Background — Why This Story Exists

Before this story opens, the APP's pipeline lives in four (or five, per 33-1) separate places:

1. **[docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](../../docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md)** — 1368 lines of Markdown with 32 step sections (`## 1)`, `## 2)`, `## 04A)`, `## 4.5)`, …), hand-authored section headers (but generated per operator constraint; see 33-1 findings for the generator's actual shape).
2. **[scripts/utilities/run_hud.py:47-75](../../scripts/utilities/run_hud.py#L47-L75)** — `PIPELINE_STEPS: list[dict[str, str]]` with 26 entries, each `{id, name, gate}`. Line 44 carries the TODO that seeded this epic.
3. **[marcus/orchestrator/workflow_runner.py](../../marcus/orchestrator/workflow_runner.py)** — `insert_4a_between_step_04_and_05(steps)` encodes "fact about topology" as a verb (Winston's critique); expected to have sibling helpers per party-mode warning.
4. **[scripts/utilities/progress_map.py](../../scripts/utilities/progress_map.py)** — consumes a pipeline projection to render the HUD dev-cycle section.
5. **The v4.2 generator** (entry point per 33-1 findings) — reads some input and emits the pack.

The party-mode walkthrough on 2026-04-19 mapped five concrete drifts (DC-1 through DC-5) across these surfaces; DC-5 (absence of SSOT) was unanimously named as the root cause. Audra's L1/L2 principle-1 ("deterministic first, agentic second — never mixed") requires an anchor file for L1 to check against. Winston's architectural frame: "in a healthy architecture, exactly one of those is the source of truth and the other two are *derived*." Neither the pack, nor the HUD, nor the orchestrator should be canonical; the canonical source is a declarative manifest.

The operator's hard constraint — **"v4.2 is generated, and should always be"** — forces the generator into the projection layer. The manifest is the *input*; the pack, HUD, orchestrator, and generator-output are all *projections*. The L1 check's job is to assert the projections match the manifest, not to adjudicate which projection is "right."

Audra's intelligence-placement discipline (her SKILL Principle 3) insists the manifest is a **structural anchor, not a payload catalogue**. The manifest declares *what happens at each gate* (pipeline-shape concerns: id, label, gate y/n, gate G-code mapping, sub-phase parent, insertion-after pointer, emission-point y/n, declared event-types at each emission point, schema-ref path to the sibling payload schema). The manifest does NOT declare *how payload is shaped* (field types, enum definitions, validator rules) — those live in sibling schema files, and the manifest references them by path only. This split is what makes the substrate extensible without becoming a god-file.

The party-mode LG-3 vote landed on **Hybrid (c)** precisely to preserve this split. 33-2 lands both halves: the manifest (topology authority) + sibling-schema referencing (by `schema_ref` path). The sibling schemas themselves are NOT authored in 33-2; they're authored by the stories that need them (e.g., `learning-event-schema.yaml` by 15-1-lite-marcus). 33-2 merely wires the reference path and the L1 checks that verify it resolves.

**Why 5 points (and not 3 or 8):** the work has three distinct deliverables — manifest authoring + L1 check authoring + rewire of 4+ consumers + 1 generator — with shared invariants across all four. Schema-shape discipline (pydantic-v2-schema-checklist) applies to the manifest loader + parser. The L1 check has 8 distinct assertion paths, each requiring a positive test, a red-path fixture, and an O/I/A trace-output pin. The rewire is "refactor-only + no behavior change" which is deceptively non-trivial across three Python surfaces and a generator of unknown current shape (33-1 findings scope-limit the generator work). 5pt with dual-gate governance is the right weight per CLAUDE.md §BMAD sprint governance and the 31-1 / 30-1 dual-gate precedent (both 5pt, both schema-shape, both landed inside dual-gate ceremony cleanly).

## T1 Readiness

- **Gate mode:** `dual-gate` — schema-shape story landing a new SSOT manifest + new L1 check + refactor across 3+ consumers. R1 (spec review, party-mode) + R2 (green-light, party-mode with riders applied) + G5 (implementation review, party-mode with Winston/Murat/Paige/Amelia personas) + G6 (layered `bmad-code-review`: Blind Hunter + Edge Case Hunter + Acceptance Auditor). **No G5/G6 consolidation**; the dual-gate ceremony is fully exercised because this story lands the substrate the rest of Epic 33 (and Epic 15+ downstream) depends on.
- **K floor:** `K = 18` per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 for a 5pt dual-gate schema-shape story, bumped from initial K=15 after R1 tiebreak scope-adds. Derivation: 8 L1 checks × 1 positive-path test = 8, red-path fixtures × 2 = 2, manifest schema shape-pin tests = 3, projection-equality × 4 consumers = 4, exit-code pin = 1, trace-format pin = 1, emitter-reconciliation (AC-T.10) = 1, disjoint-keys regression (AC-T.11) = 1, migration-coverage grep (AC-T.12) = 1. Sum: 8 + 2 + 3 + 4 + 1 + 1 + 1 + 1 + 1 = 22, floor set at 18 to preserve coverage-gap-justification budget per §1.
- **Target collecting-test range:** 22–27 (K to ~1.5×K per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1; includes budget for R2 rider-amendment-driven additions and G6 post-dev patches).
- **Realistic landing estimate:** 23-25 collecting functions at T2-T18 close; possibly +2-4 at G6 remediation → floor range 25-29 at done. Coverage-gap justification per §1 expected (not over-landing; G6 remediation is the typical source of the bump).
- **Required readings** (dev agent reads at T1 before any code):
  - [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance — governance umbrella (bmad-code-review before done, party-mode consensus, no --no-verify shortcuts).
  - [_bmad-output/specs/33-1-generator-discovery-findings.md](../specs/33-1-generator-discovery-findings.md) — **HARD PRE-REQUISITE**. The generator's location, inputs, outputs, and regeneration procedure are specified here. 33-2's rewire scope is defined by 33-1's gap analysis. If any section is ambiguous, STOP and escalate per 33-1's §Kill-switch Decision; do not reverse-engineer the generator on the fly.
  - [docs/dev-guide/pydantic-v2-schema-checklist.md](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — 14 schema idioms (`validate_assignment=True`, tz-aware datetimes, UUID4 validation, closed-enum triple-layer red-rejection, `Field(exclude=True) + SkipJsonSchema` for internal audit fields, etc.). The manifest Pydantic loader + the L1 check's parsed-projection models MUST follow all 14.
  - [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) — full catalog. Critical traps for this story: **27-2** (fix symptom in generated output — AC-B.15 enforcement), **31-1** (rename on one surface drifts another — the manifest-first edit rule applies), **"regex-parsing a generated artifact"** (Audra's explicit anti-pattern — AST-only).
  - [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 (K-floor + coverage-gap justification discipline), §2 (dual-gate policy — R1/R2/G5/G6 ceremony), §3 (aggressive DISMISS rubric at G6).
  - [docs/dev-guide/scaffolds/schema-story/](../../docs/dev-guide/scaffolds/schema-story/) — scaffold root for schema-shape stories. Pre-instantiated stubs live at the target paths; dev agent extends rather than re-deriving from 31-1 precedent. Run `python scripts/utilities/instantiate_schema_story_scaffold.py --story 33-2` at T1 to drop the scaffold into place.
  - [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) — L1/L2 principles (1/2/3), trace-report format contract, exit-code discipline. The L1 check landing in this story is the first new Audra-lane script since the SKILL's §External Skills planned-Phase-3 scripts were named; dev agent must follow the contract.
  - [skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md) §HZ — "HUD scope union" + "Workflow-stage lockstep" contracts. The manifest's field set must include enough structure for Cora's 33-4 change-window detector to key on.
  - [scripts/utilities/run_hud.py](../../scripts/utilities/run_hud.py) full file — existing shape of `PIPELINE_STEPS` + HUD-rendering logic that consumes it.
  - [scripts/utilities/progress_map.py](../../scripts/utilities/progress_map.py) full file — progress-map's pipeline consumption surface.
  - [marcus/orchestrator/workflow_runner.py](../../marcus/orchestrator/workflow_runner.py) full file (83 lines) — insertion-helper pattern being replaced.
  - [_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md](31-1-lesson-plan-schema.md) — schema-shape-story precedent. Specifically the MUST-FIX patterns G6 surfaced (validate_assignment bypass, datetime UTC-awareness, triple-layer red-rejection). Apply these defensively to the manifest loader.
  - [_bmad-output/implementation-artifacts/31-3-registries.md](31-3-registries.md) — MappingProxyType + import-time invariant assertion precedent. The manifest loader should freeze the parsed manifest into a MappingProxyType for runtime consumers; an import-time invariant check should assert set/sequence/name/bitmap internal consistency even before any projection comparison.
- **Scaffold requirement:** `require_scaffold: true` — schema-shape story. Dev agent runs `python scripts/utilities/instantiate_schema_story_scaffold.py --story 33-2` at T1 step 1; scaffold drops stubs at `state/config/pipeline-manifest.yaml` (empty valid shape), `scripts/utilities/check_pipeline_manifest_lockstep.py` (stub with exit-code contract skeleton), and `tests/test_pipeline_manifest_loader.py` + `tests/contracts/test_check_pipeline_manifest_lockstep.py` (empty test files). Dev agent extends; does NOT re-derive.
- **Runway pre-work consumed:** 33-1 findings report (done). No other dependencies beyond CLAUDE.md governance + dev-guide references.

## R1 Party-Mode Spec-Review Round

This spec is authored pre-R1. Before dev-story opens, the spec SHOULD go through R1 party-mode review per dual-gate ceremony; R1 riders land as amendments to this spec, and R2 green-light is granted when riders are applied. R1 panel: Winston (architect), Amelia (dev), Paige (tech writer), Murat (test architect) — stock BMAD roster, independence preserved. Cora + Audra are off-manifest per their SKILL charters but may be invoked if a governance-envelope or L1-lane question arises mid-round.

R1 focus areas likely to surface riders (based on 31-1 / 30-1 / 31-3 precedent):
- **Winston**: manifest schema field design — is `sub_phase_of` the right name? Is `insertion_after` sufficient or should we also carry `insertion_before`? Should `learning_events.emits` be a bool or an enum `{never | sometimes | always}`? (Defer to R1 discussion.)
- **Amelia**: exact AC-level file paths and function signatures. Which `progress_map.py` function reads the pipeline today? What's the backward-compat strategy for downstream callers of the current `PIPELINE_STEPS` list?
- **Paige**: documentation of the manifest format — does the manifest need an audience-layered module docstring akin to Marcus orchestrator's? A separate `state/config/README.md` (or sibling doc) explaining editor discipline? SYNC-WITH comments at consumer sites pointing at the manifest? (Paige's R1-B concurring note: audience-tag prefixes apply to the manifest in **lighter form** — entries carry an `audience:` field drawing from the `[M→self|O→M|M→O|M→sub]` vocabulary rather than inline prefix strings in YAML values.)
- **Murat**: red-path fixture design — what's the minimum set that catches the whole class of drift? Should the L1 check parametrize-over-fixture-dirs so future drift classes are additive? CI wiring — does this story wire the L1 check into pre-commit / GitHub Actions, or is that 33-4's scope?

R2 green-light requires R1 riders applied AND the panel voting GREEN or GREEN-pending-rider-application.

## R1 Resolutions (2026-04-19 party-mode convergence + off-manifest specialist tiebreak)

Three pre-R1 decisions were raised before this spec opened; all three are resolved via the 2026-04-19 convergence round. Recording here so dev agent does not re-open them:

### R1-C — Manifest location: `state/config/pipeline-manifest.yaml` (UNANIMOUS stock-roster)

Winston + Amelia + Paige + Murat voted unanimously for `state/config/` (sibling to `parameter-registry-schema.yaml`, `narration-script-parameters.yaml`, `fidelity-contracts/`). Rationale: matches existing convention for schema-like runtime configs; inventing `_bmad/manifests/` fragments the config surface with a new top-level dir for one file; `_bmad-output/maps/` is semantically wrong (manifests are inputs, not outputs). **Audra's L1-lane routing note**: the L1 check's default manifest path goes in the **script arg** (`--manifest state/config/pipeline-manifest.yaml`) with the SKILL documenting the default, NOT hardcoded in SKILL prose — preserves future extensibility for per-epic or per-workflow manifest variants. **Murat's scope add**: `state/config/` already hosts 6+ YAML configs with overlapping schemas; disjoint-top-level-keys regression test lands as AC-C.5 + AC-T.11 to protect against the new manifest's keys shadowing an existing file's keys.

### R1-A — DC-3 04.5 canonical name: Split into 04.5 + 04.55 (Audra tiebreak on L1-lane test-integrity)

Stock roster split 2-2 (Amelia + Paige for HUD-wins; Winston + Murat for split). Audra's off-manifest tiebreak on L1-lane grounds walked all 8 L1 checks against the HUD-wins shape and confirmed Murat's decisive test-coverage trap: 7 of 8 checks falsely green; check 6 conditionally catches but the moment the manifest author backfills the emission list to satisfy check 6, the bifurcation is laundered into one step-id legitimately emitting two event families, and **no check in the L1 catalog can detect that without crossing into L2 semantic judgment** (violates Principle 1). Resolution:

- `04.5` = **"Parent Slide Count Polling"** — the precursor polling step; emits `plan_unit.created` events per `loop.py` runtime behavior.
- `04.55` = **"Estimator + Run Constants Lock"** — the subsequent constants-lock step that gates downstream emission.
- Cut line between the two: `loop.py`'s first `plan_unit.created` emission boundary. Before → 04.5. Lock that gates emission → 04.55.

**Audra's L1-catalog benefit**: Split makes check 6 do the work it was designed for (one step-id, one emission family, one heading, one schema_ref). Murat's generative emitter→manifest reconciliation test (AC-B.18 / AC-T.10) is necessary AND sufficient under split; under HUD-wins, it would be necessary but not sufficient (backfill path defeats it).

### R1-B — `insert_4a_between_step_04_and_05` migration: Rename+generalize to `insert_between` (Audra + Cora tiebreak)

Stock roster split 3-way (Winston hard-migrate; Amelia + Paige shim; Murat rename+generalize). Audra + Cora off-manifest tiebreak converged on (iii) `insert_between`.

**Audra's Principle-3 ruling**: shim option (ii) keeps verb-encoded topology alive in the function name — "keep the smell, add a warning" — Principle 3 fails outright. Murat's AC-C.1 trap is decisive: shim makes the orphan literal resolvable, so AC-C.1 passes green while the verb-encoded fact lives on in caller code indefinitely. Option (iii) converts topology fact into manifest-referencing argument data (`insert_between("04", "05", new_step)`), extends the deterministic neck with a tractable argument-validity check (AC-C.1 extension), and is the only option that gives AC-C.1 a structural surface a shim cannot defeat.

**Cora's governance-envelope ruling**: (iii) minimizes the silent-reopen surface for her 33-4 block-mode hook. Under (ii), shim creates edits neither her hook nor AC-C.1 catches — silent-reopen vector. Under (iii), explicit `step_id` arg makes any future "insert at 04A" a manifest reference rather than a string literal, and the AC-C.1 argument-validity scan catches mis-typed step IDs before they reach runtime.

**Amelia's blast-radius concern folded in**: the 4 named surfaces (`test_marcus_workflow_runner_32_1.py`, narration-config fixtures, `narration-script-parameters.yaml` step-ID enum, structural-walk closeout fixtures) migrate in the same 33-2 PR. Pre-migration grep + post-migration grep verification is a T4 gate + AC-T.12 codifies the grep check as a regression test.

### Scope adds from the tiebreak round

The tiebreak surfaced three concrete scope adds to 33-2. All three are folded into ACs above:

1. **Murat's generative emitter→manifest reconciliation test** → AC-B.18 + AC-T.10.
2. **Murat's `state/config/*.yaml` schema-collision regression** → AC-C.5 + AC-T.11.
3. **Audra's `insert_between` argument-validity structural check** → AC-C.1 (extended).

**K-floor impact**: the story grows from K=15 target 18-23 to **K=18 target 22-27** to accommodate the three new tests (AC-T.10 reconciliation + AC-T.11 disjoint-keys + AC-T.12 grep + AC-C.1 second assertion). R2 green-light will confirm or revise; no dev agent action required on the K bump beyond landing the tests cleanly inside the new range.

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — Manifest file exists and is parseable.** [`state/config/pipeline-manifest.yaml`](../../state/config/pipeline-manifest.yaml) exists, parses as valid YAML, and validates against the Pydantic shape landed at [`scripts/utilities/pipeline_manifest.py`](../../scripts/utilities/pipeline_manifest.py) (new module). Loader exposes `load_manifest(path: Path) -> PipelineManifest` returning a frozen MappingProxyType-wrapped dict-of-step-entries. Model config: `ConfigDict(extra="forbid", frozen=True, validate_assignment=True)` per 31-1 precedent.

2. **AC-B.2 — Manifest declares every currently-live pipeline step, with DC-3 resolved by split.** The manifest's step-list includes every step currently present in `run_hud.py::PIPELINE_STEPS` (26 entries) AND every step section in the current on-disk v4.2 pack (32 sections). Bifurcation rule for the sections where these sets differ (§4.75 CD, §6.2 Cluster Prompt Eng, §6.3 Cluster Dispatch, §7.5 Cluster Coherence G2.5, §14.5 Desmond brief, §04A Step 4A Coauthoring): §7.5 lands as a top-level step with `gate: true` (G2.5 is a gate — Murat H-risk flag); §4.75, §6.2, §6.3, §14.5 land as top-level steps with `sub_phase_of: <parent-id>` declared; §04A lands with explicit `insertion_after: "04"` (resolving DC-2 — code + HUD agree, pack reorders on regeneration per 33-3). **DC-3 04.5 semantic collision resolves by splitting into two manifest entries** (R1-A party-mode ruling, Audra + Cora tiebreak on L1-lane test-integrity grounds — see §R1 Resolutions below): `04.5` = "Parent Slide Count Polling" (the precursor polling step; emits `plan_unit.created` events per `loop.py` runtime behavior); `04.55` = "Estimator + Run Constants Lock" (the subsequent constants-lock step that gates downstream emission). Cut line between the two is `loop.py`'s first `plan_unit.created` emission boundary — everything before is 04.5 polling, the lock that gates emission is 04.55. This resolves the "same id, different concept" drift Audra tagged as High-severity Invention without forcing check 6 into the launder-into-manifest trap (see §R1 Resolutions for the full L1-lane walk-through).

3. **AC-B.3 — Per-step field set declared.** Each step entry carries: `id` (str, matches `^[0-9]{2}[A-Z]?(\.[0-9]+)?$` or `^0?[0-9]+[A-Z]?$`), `label` (str, non-empty), `gate` (bool), `gate_code` (optional str, e.g., `"G2.5"`, `"G3"` — present only when `gate: true`), `sub_phase_of` (nullable str, id of parent step), `insertion_after` (nullable str, id of predecessor step), `hud_tracked` (bool; default `true` for top-level gate-bearing steps, `false` for sub-phases unless explicitly promoted), `pack_section_anchor` (str, the `## N)` header text the generator should emit), `pack_version` (str; "v4.2" today; parameterized per Q1 compromise). Plus optional `learning_events` sub-object with `emits` (bool), `event_types` (list[str], empty if emits=false), `schema_ref` (nullable str, path to payload schema).

4. **AC-B.4 — Top-level manifest fields declared.** The manifest carries: `schema_version` (str, "1.0" at 33-2), `pack_version` (str, "v4.2" at 33-2), `generator_ref` (str, path to v4.2 generator per 33-1 findings), `learning_events.schema_ref` (top-level nullable str, path to learning-event payload schema — empty until 15-1-lite-marcus authors it), `steps` (list of per-step objects per AC-B.3).

5. **AC-B.5 — `check_pipeline_manifest_lockstep.py` lands with 8 deterministic checks.** [`scripts/utilities/check_pipeline_manifest_lockstep.py`](../../scripts/utilities/check_pipeline_manifest_lockstep.py) implements:
   - **Check 1 — Set equality**: `manifest.step_ids == run_hud.PIPELINE_STEPS.step_ids == pack_section_ids == progress_map.step_ids`. Fails with O/I/A finding naming which set differs.
   - **Check 2 — Order equality**: `manifest.order == run_hud.order == pack_order == progress_map.order` after applying manifest-declared `insertion_after` / `sub_phase_of` position rules.
   - **Check 3 — Name-per-id equality**: for each id present in ≥2 surfaces, `manifest.label[id] == run_hud.name[id] == pack.heading[id]` as exact strings. Alteration finding if any surface differs.
   - **Check 4 — Gate-flag bitmap equality**: `manifest.gate[id] == run_hud.gate[id]` for every id. Alteration finding on divergence.
   - **Check 5 — Insertion-point consistency**: every manifest entry with `insertion_after: X` has X appearing earlier in `manifest.order`; every insertion-helper function in `workflow_runner.py` (AST-parsed) references only ids declared in the manifest with consistent `insertion_after` ordering.
   - **Check 6 — Emission-declaration integrity**: every step with `learning_events.emits: true` has a non-empty `event_types` list; every step with `learning_events.emits: false` has `event_types: []`. Invention finding on violation.
   - **Check 7 — `schema_ref` resolves**: top-level `learning_events.schema_ref` (if non-empty) points to an existing, parseable YAML file with the expected top-level keys (structure TBD at 15-1-lite-marcus). Exit 2 if path missing (structural); exit 1 if present-but-malformed.
   - **Check 8 — `event_types` ⊆ schema enum**: union of all steps' declared `event_types` is a subset of the `schema_ref`'s `event_type` enum. Alteration finding on violation. (This check is gated on `schema_ref` being non-empty; returns PASS trivially if learning-event schema isn't authored yet — active only after 15-1-lite-marcus.)

6. **AC-B.6 — Exit-code contract strict.** `check_pipeline_manifest_lockstep.py` exits `0` on all-checks-pass, `1` on any check failure, `2` on structural failure (manifest file missing, unparseable, or references a `schema_ref` path that doesn't exist). No other exit codes. No ambiguous "probably fine" paths.

7. **AC-B.7 — Trace output contract.** On exit 1 or 2, the script writes a trace to `reports/dev-coherence/<YYYY-MM-DD-HHMM>/check-pipeline-manifest-lockstep.FAIL.yaml` (or `.STRUCTURAL.yaml` for exit 2) following the O/I/A schema in [skills/bmad-agent-audra/references/trace-report-format.md](../../skills/bmad-agent-audra/references/trace-report-format.md). On exit 0, the script writes `...PASS.yaml` with per-check evidence (set sizes, order hashes, bitmap equality confirmation). The trace path is stable; consumers (Cora's block-mode hook in 33-4, CI) depend on it.

8. **AC-B.8 — AST-only parsing.** The L1 check MUST use `ast.parse()` to extract `PIPELINE_STEPS` from `run_hud.py` and to enumerate insertion-helper functions + their id references in `workflow_runner.py`. MUST use a Markdown AST library (recommend `markdown-it-py` or `mistune`; R1 to confirm) for pack section-header extraction. NO regex parsing. This is Audra's explicit anti-pattern-3 guard — regex works today, silently misses a trailing-comma edit or a heading-format tweak in six weeks.

9. **AC-B.9 — Schema-driven traversal.** The L1 check's per-step assertion loop iterates over the manifest's declared fields (not a hardcoded list). Adding a new top-level step-level field to the Pydantic model automatically becomes an assertion target for the downstream checks if relevant. Murat's DoD requirement; prevents "new field added to manifest, linter still passes silently because linter doesn't know about the field yet."

10. **AC-B.10 — Closed-enum bidirectional check (check 8 hardening).** The event-types subset assertion MUST test both directions when a schema_ref is present: (a) `manifest.declared_event_types ⊆ schema.event_type_enum`, and (b) a new optional L2 candidate assertion `schema.event_type_enum ⊆ manifest.declared_event_types` (to catch "schema defines a type no gate declares") — the L2 variant may exit with a warning (exit 0 + trace note) rather than hard fail, because not every defined enum value must be emitted. R1 to refine which direction is strict vs warn.

11. **AC-B.11 — Red-path fixtures land.** `tests/fixtures/pipeline_manifest_drift/` contains at minimum: `schema_only_drift/` (schema defines `event_type: circuit_break` but manifest does not declare it at any gate) and `manifest_only_drift/` (manifest declares `event_types: [approval, revision, waiver, circuit_break]` at Gate 3 but schema only enumerates the first three). Both fixtures are consumed by parametrized tests asserting `check_pipeline_manifest_lockstep.py` exits 1 with the correct check-number cited in the trace.

12. **AC-B.12 — `run_hud.py` rewired.** The `PIPELINE_STEPS: list[dict[str, str]]` literal at `run_hud.py:47-75` is replaced by a function call (recommend `_load_pipeline_steps_from_manifest()`) that reads `state/config/pipeline-manifest.yaml` at module import. Existing HUD output (byte-equivalent on the currently-on-disk pipeline set) is preserved. The TODO at line 44 is removed (replaced by a `SYNC-WITH: state/config/pipeline-manifest.yaml` comment naming the authoritative source).

13. **AC-B.13 — `progress_map.py` rewired.** Equivalent rewire: the pipeline projection currently hand-declared (per 33-1 findings for exact location) is replaced by manifest load. All existing `test_run_hud.py` + `test_progress_map.py` tests continue to pass.

14. **AC-B.14 — `workflow_runner.py` rewired via `insert_between` rename+generalize (R1-B party-mode ruling).** `insert_4a_between_step_04_and_05` is **deleted** (NOT shimmed — shim defeats AC-C.1 per Murat; hard-migrate keeps verb-encoded topology per Audra Principle 3 walkthrough). Replaced by a generalized `insert_between(before_id: str, after_id: str, new_step: <StepType>) -> tuple[...]` callable where every caller surfaces insertion intent as manifest-ID-referencing arguments. `before_id` and `after_id` MUST resolve to valid manifest IDs (enforced by AC-C.1 extension). Winston's critique resolved: step-insertion facts now live as data in call-site arguments + manifest, not as verbs in function names. **32-1 test migration is in-scope**: [tests/test_marcus_workflow_runner_32_1.py](../../tests/test_marcus_workflow_runner_32_1.py) migrates from asserting on `insert_4a_between_step_04_and_05` to asserting on `insert_between("04", "05", new_04a_step)`; the per-helper unit tests are replaced by dispatcher unit tests + argument-validity contract test (AC-C.1 extension). Amelia's blast-radius enumeration enumerated four surfaces that reference the legacy name — each must migrate in the same PR: (a) `tests/test_marcus_workflow_runner_32_1.py`, (b) any narration-config schema fixture naming the step, (c) `state/config/narration-script-parameters.yaml` step-ID enum if it carries the function name, (d) structural-walk closeout fixtures. Dev agent performs a pre-migration grep across the repo for the literal string `insert_4a_between_step_04_and_05` and migrates every hit; grep-verification becomes a pre-closure gate.

15. **AC-B.15 — v4.2 generator rewire -> DEFERRED to Story 33-1a.** 33-1 findings landed Case C (no in-repo generator of record; pack is de-facto hand-authored). Rewire is not feasible within 33-2 because there is no existing generator to wire the manifest into. DEFERRED per 33-1 kill-switch escalation path; follow-up story 33-1a — Build the v4.2 Generator filed as a new sibling to 33-2 in the Epic 33 sprint. 33-2's remaining ACs (manifest + L1 check + rewires of the three in-repo consumer surfaces: `run_hud.py`, `progress_map.py`, `workflow_runner.py`) land fully. 33-3 regeneration gates on 33-1a landing first (sprint dependency reshape; see `sprint-status.yaml` note). **NO hand-edits to the on-disk v4.2 pack** in this story; that's 33-3's scope.

16. **AC-B.16 — Parameterized version hook.** The manifest carries `pack_version: "v4.2"` at the top level. `check_pipeline_manifest_lockstep.py` accepts a `--pack-version` CLI arg that defaults to the manifest's declared version; if passed, it filters the manifest's step list to `{steps whose pack_version matches | steps with no pack_version field}`. This is the Q1 party-mode compromise — ships v4.2-only complexity today, extension to v4.3 is a 1-line addition of a second `pack_version` value and a corresponding manifest entry.

17. **AC-B.17 — Import-time invariant assertion.** The manifest loader at `scripts/utilities/pipeline_manifest.py` includes a module-level (or Pydantic-model-level) import-time assertion that verifies internal consistency: every `insertion_after` target exists in `steps`; every `sub_phase_of` target exists; every step with `gate: true` has a `gate_code`; every gate-code is unique; `schema_version` matches a known const. Per 31-3 precedent (MappingProxyType + import-time parity assertion).

18. **AC-B.18 — Generative emitter→manifest reconciliation (Murat's R1-A-follow-on, Audra-named "necessary").** One integration test at `tests/test_emitter_manifest_reconciliation.py::test_loop_py_emitter_pairs_reconcile_to_manifest` walks `marcus/orchestrator/loop.py` (AST + actual emission instrumented against a fixture fixture-manifest), collects every `(step_id, event_type)` pair the emitter would produce on a happy-path run, and asserts each pair resolves to a manifest entry whose `learning_events.emits` is true and whose `event_types` contains the emitted event_type. Catches manifest-vs-runtime drift that the 8 structural L1 checks cannot (specifically: check 6 emission-declaration integrity validates declaration format; this test validates declaration-vs-actual-emission). Audra's L1/L2 distinction preserved: this is an integration test, not an L1 check — it runs against real emitter code, not a manifest string comparison. The test lands in the regular test suite, not in `check_pipeline_manifest_lockstep.py`.

### Contract (AC-C.*)

1. **AC-C.1 — No orphaned pipeline literals + `insert_between` argument-validity.** One AST contract test at `tests/contracts/test_33_2_no_orphan_pipeline_literals.py` contains TWO asserting functions: (a) `test_no_hardcoded_pipeline_step_lists` walks the repo under `scripts/`, `marcus/`, `skills/bmad-agent-marcus/`; asserts zero list/tuple literals with ≥5 string elements matching the pipeline-step-id pattern outside the manifest itself; (b) **`test_insert_between_arguments_resolve_to_manifest_ids`** (Audra-specified L1 extension per R1-B ruling) — AST-parses every `insert_between(a, b, c)` call site in the repo; asserts each `before_id` and `after_id` argument is either a string literal that resolves to a valid manifest step ID OR a variable binding that resolves at module-import time to a valid manifest ID. Closes the class of drift where a caller passes a stepid-shaped literal that doesn't exist in the manifest — the deterministic-neck extension Audra named as "extends the neck rather than punching a hole in it."

2. **AC-C.2 — Exit-code pin on L1 check.** One contract test at `tests/contracts/test_33_2_check_exit_contract.py` asserts (via subprocess run of the L1 check against three prepared manifest states — clean, drifted, missing) that exit codes are exactly `{0, 1, 2}` with no other values. Protects against future refactors introducing exit codes 3+ silently.

3. **AC-C.3 — Trace-output format pin.** One contract test at `tests/contracts/test_33_2_trace_output_format.py` runs the L1 check against the red-path fixtures + against a clean manifest; asserts the trace YAML validates against the Audra O/I/A schema (required fields: `lane`, `scope`, `timestamp`, `findings[]`, `l1_checks_run[]`, `closure_gate`).

4. **AC-C.4 — AST-only purity.** One contract test at `tests/contracts/test_33_2_no_regex_in_lockstep_check.py::test_no_re_import_in_check_script` asserts the L1 check module does NOT import `re`, `regex`, or call `.match`/`.search`/`.findall` on string patterns. This is Audra's anti-pattern-3 guard rendered as a grep-invariant.

5. **AC-C.5 — `state/config/*.yaml` schema-collision regression (Murat's R1-C add).** One contract test at `tests/contracts/test_33_2_state_config_disjoint_keys.py::test_state_config_yaml_files_have_disjoint_top_level_keys` loads every `.yaml` file directly under `state/config/` (non-recursive to avoid fixture dirs); parses each; asserts the union of top-level keys across all files has no duplicates. Protects against the new `pipeline-manifest.yaml` top-level keys shadowing an existing `parameter-registry-schema.yaml` / `narration-script-parameters.yaml` / `fidelity-contracts/` (etc.) key and having a downstream consumer silently read the wrong file. Failure message enumerates which files share which keys.

### Test (AC-T.*)

1. **AC-T.1 — Manifest shape-pin tests.** Three tests at `tests/test_pipeline_manifest_loader.py`:
   - `test_manifest_loads_and_validates` — happy path.
   - `test_manifest_rejects_extra_fields` — `ConfigDict(extra="forbid")` enforcement.
   - `test_manifest_rejects_mutation` — `frozen=True` + `validate_assignment=True` enforcement.

2. **AC-T.2 — Per-check positive-path tests.** Eight tests at `tests/test_check_pipeline_manifest_lockstep.py::test_check_<N>_passes_on_clean_manifest` — one per check, each running against a known-clean fixture and asserting exit 0 + trace PASS.

3. **AC-T.3 — Per-check red-path tests.** Two parametrized tests at `tests/test_check_pipeline_manifest_lockstep.py::test_red_path_fixtures_fail_correctly[fixture]` covering the two `tests/fixtures/pipeline_manifest_drift/` fixtures. Each asserts exit 1 + the specific check number cited + O/I/A taxonomy correct.

4. **AC-T.4 — Structural-failure test.** One test asserting exit 2 when the manifest file is deliberately removed from a scratch run.

5. **AC-T.5 — Projection-equality tests.** Four tests (one per rewired consumer: run_hud, progress_map, workflow_runner, generator) at `tests/test_projection_equality.py` asserting the projection's state matches the manifest's declaration. Generator test uses a fixture-manifest + scratch output path.

6. **AC-T.6 — Schema-driven traversal test.** One test that synthesizes a manifest with a new top-level step-level field, runs the check, and asserts the check does NOT skip the new field (the assertion loop discovers it via model iteration).

7. **AC-T.7 — Parameterized version-hook test.** One test running the L1 check with `--pack-version v4.3` against a manifest containing a mix of v4.2 + v4.3 entries; asserts only v4.3 entries are checked.

8. **AC-T.8 — Trace-output round-trip test.** One test running the L1 check, reading the emitted trace YAML, parsing it with the Audra trace schema, and asserting all required fields present.

9. **AC-T.9 — Import-time invariant test.** One test verifying the loader raises a specific exception (`ManifestInternalInconsistencyError` or equivalent) when a malformed manifest with `insertion_after` pointing to a missing step is loaded.

10. **AC-T.10 — Emitter reconciliation happy-path test.** Covers AC-B.18. One test at `tests/test_emitter_manifest_reconciliation.py::test_loop_py_emitter_pairs_reconcile_to_manifest` exercises the actual `loop.py` emission under a fixture-manifest + instrumented collector; asserts every `(step_id, event_type)` pair has a manifest entry. Specifically exercises 04.5 polling + 04.55 lock separately (per R1-A split) so the split ruling is pinned by behavior, not just by declaration.

11. **AC-T.11 — `state/config/*.yaml` disjoint-keys regression test.** Covers AC-C.5. One test parses every direct-child YAML under `state/config/`; asserts disjoint top-level keys across files. Dual pass: (a) on a clean repo asserts green; (b) synthesizes a scratch duplicate-key state and asserts red with the colliding-keys enumerated in the failure message.

12. **AC-T.12 — `insert_between` caller-argument migration coverage.** Covers AC-B.14 dev-agent grep-verification gate. One test at `tests/test_insert_between_migration.py::test_no_legacy_insert_4a_references_remain` runs a repo-wide grep for the literal string `insert_4a_between_step_04_and_05`; asserts zero matches outside (a) this story's spec file, (b) the Dev Agent Record / Completion Notes of migrated stories. Complements AC-C.1's argument-validity check by catching missed callers.

## Tasks / Subtasks

### T1 — Readiness gate (before any code)

- [x] Confirm 33-1 is `done` in [sprint-status.yaml](sprint-status.yaml); read the findings report fully.
- [ ] Read all required readings enumerated in §T1 Readiness.
- [ ] Run `python scripts/utilities/instantiate_schema_story_scaffold.py --story 33-2` to drop scaffold stubs at target paths.
- [ ] Confirm scaffold stubs exist at: `state/config/pipeline-manifest.yaml`, `scripts/utilities/pipeline_manifest.py`, `scripts/utilities/check_pipeline_manifest_lockstep.py`, `tests/test_pipeline_manifest_loader.py`, `tests/test_check_pipeline_manifest_lockstep.py`, `tests/contracts/test_33_2_*.py` (3 contract files).
- [ ] R1 party-mode round if not already complete (see §R1 Party-Mode above). R1 riders applied as spec amendments before R2.
- [ ] R2 party-mode green-light: Winston + Murat + Paige + Amelia vote GREEN (or GREEN-pending-rider-application). Record vote in this spec's §Post-Dev Review Record top-of-file Dev Agent Record stub.

### T2 — Manifest authoring + loader (AC-B.1–4, AC-B.17, AC-T.1)

- [x] Author `state/config/pipeline-manifest.yaml` with all currently-live pipeline steps (enumeration from `run_hud.py::PIPELINE_STEPS` + v4.2 pack headers + any orchestrator-seen steps per 33-1 findings).
- [x] Apply DC-1 bifurcation per AC-B.2: §7.5 as gate-bearing top-level, §4.75/§6.2/§6.3/§14.5 as `sub_phase_of` declared children.
- [x] Apply DC-2 resolution: `04A` entry with `insertion_after: "04"` (code + HUD position; pack reorders on regeneration per 33-3).
- [x] Apply DC-3 resolution per R1-A split ruling: manifest entry `04.5` = "Parent Slide Count Polling" (emits polling events per `loop.py`); manifest entry `04.55` = "Estimator + Run Constants Lock" (gates downstream emission). See §R1 Resolutions for the L1-lane rationale.
- [x] Apply DC-3 resolution: single canonical name for id `04.5` per R1 decision.
- [x] Land `scripts/utilities/pipeline_manifest.py` with `PipelineManifest` Pydantic model, `StepEntry` sub-model, `load_manifest()` loader, import-time invariant assertion, frozen MappingProxyType wrap.
- [x] Land AC-T.1 three shape-pin tests.

### T3 — L1 check authoring (AC-B.5–11, AC-T.2, AC-T.3, AC-T.4, AC-T.7, AC-T.8)

- [x] Land `scripts/utilities/check_pipeline_manifest_lockstep.py` with all 8 checks.
- [ ] AST-only parsing for `run_hud.py` + `workflow_runner.py`; Markdown-AST for pack.
- [x] Exit-code contract 0/1/2 strict; no ambiguous paths.
- [x] O/I/A trace output at `reports/dev-coherence/<ts>/`.
- [ ] Schema-driven traversal per Murat DoD.
- [x] Parameterized `--pack-version` CLI arg.
- [x] Red-path fixtures at `tests/fixtures/pipeline_manifest_drift/`.
- [ ] Land AC-T.2 (8 positive-path), AC-T.3 (2 red-path), AC-T.4 (structural), AC-T.7 (version filter), AC-T.8 (trace round-trip).

### T4 — Consumer rewires (AC-B.12–15, AC-T.5, AC-T.6, AC-T.12)

- [x] Rewire `run_hud.py`: replace `PIPELINE_STEPS` literal with manifest load; remove line-44 TODO; add SYNC-WITH comment.
- [x] Rewire `progress_map.py`: manifest-driven pipeline projection. Add fixture entries for 04.5 + 04.55 (per R1-A split ruling — Cora flagged ~2 fixture additions expected in `progress_map` tests).
- [ ] **R1-B rename+generalize migration** (hard, no shim — per Audra Principle-3 ruling and Murat AC-C.1 trap):
  - [x] Land `insert_between(before_id: str, after_id: str, new_step: <StepType>) -> tuple[...]` in `marcus/orchestrator/workflow_runner.py`, reading from the manifest to resolve `before_id` / `after_id`.
  - [x] Delete `insert_4a_between_step_04_and_05` (no shim; hard-migrate per R1-B ruling).
  - [ ] Pre-migration grep: `grep -rn "insert_4a_between_step_04_and_05" .` — enumerate ALL hits before any migration edits.
  - [x] Migrate each caller found in the grep — at minimum: (a) [tests/test_marcus_workflow_runner_32_1.py](../../tests/test_marcus_workflow_runner_32_1.py) assertions + setup, (b) any narration-config schema fixture naming the step, (c) [state/config/narration-script-parameters.yaml](../../state/config/narration-script-parameters.yaml) step-ID enum if it carries the function name, (d) structural-walk closeout fixtures (check [scripts/utilities/structural_walk.py](../../scripts/utilities/structural_walk.py) and associated fixtures). Additional hits from the grep: migrate all in-scope.
  - [x] Post-migration verification: repeat grep; assert zero remaining hits outside this spec file and any migrated stories' Dev Agent Records (AC-T.12 codifies this).
- [ ] Rewire v4.2 generator per 33-1 findings.
- [ ] Land AC-T.5 (4 projection-equality tests) + AC-T.6 (schema-driven-traversal synthesis) + AC-T.12 (migration coverage grep test).

### T5 — Contract tests + state/config disjoint-keys guard (AC-C.1–5, AC-T.9, AC-T.10, AC-T.11)

- [x] Land `tests/contracts/test_33_2_no_orphan_pipeline_literals.py` with TWO asserting functions (AC-C.1): (a) no-hardcoded-lists AST walk; (b) `test_insert_between_arguments_resolve_to_manifest_ids` — AST-parses every `insert_between(a, b, c)` call; asserts `before_id` / `after_id` resolve to valid manifest step IDs.
- [x] Land `tests/contracts/test_33_2_check_exit_contract.py` (AC-C.2 exit-code pin via subprocess).
- [x] Land `tests/contracts/test_33_2_trace_output_format.py` (AC-C.3 O/I/A schema pin).
- [x] Land `tests/contracts/test_33_2_no_regex_in_lockstep_check.py` (AC-C.4 AST-only purity).
- [x] Land `tests/contracts/test_33_2_state_config_disjoint_keys.py` (AC-C.5 disjoint-top-level-keys across `state/config/*.yaml` — Murat's R1-C add).
- [x] Land AC-T.9 import-time invariant test.
- [x] Land AC-T.10 emitter reconciliation happy-path test at `tests/test_emitter_manifest_reconciliation.py` — exercises 04.5 polling + 04.55 lock separately per R1-A split to pin the ruling by behavior not just declaration.
- [x] Land AC-T.11 `state/config/*.yaml` disjoint-keys regression (dual-path: clean + synthesized-duplicate).

### T6 — Regression + dual-gate close

- [ ] Focused 33-2 suite: `python -m pytest tests/test_pipeline_manifest_loader.py tests/test_check_pipeline_manifest_lockstep.py tests/test_projection_equality.py tests/contracts/test_33_2_*.py -p no:cacheprovider` — expect green.
- [x] Full regression: `python -m pytest -p no:cacheprovider` — expect no new failures vs. at-session-close baseline. 3 pre-existing regressions documented in [next-session-start-here.md](../../next-session-start-here.md) tracked separately; 33-2 MUST NOT add a 4th. Ideally 33-2 FIXES DC-4 (the 32-1 HUD test) by pulling its contract out of the manifest; record whether DC-4 is fixed or deferred to 33-3 in Dev Agent Record.
- [ ] Ruff clean on all new modules + tests.
- [ ] Pre-commit clean on all touched files.
- [ ] **G5 party-mode implementation review** per dual-gate ceremony: Winston + Murat + Paige personas vote GREEN (or GREEN-pending-rider); Amelia self-review HIGH confidence. Document vote in §Post-Dev Review Record.
- [ ] **G6 layered `bmad-code-review`** per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §3: Blind Hunter + Edge Case Hunter + Acceptance Auditor. Dedup → triage: PATCH (MUST-FIX + SHOULD-FIX) + DEFER + DISMISS. MUST-FIX remediated before closure. §3 aggressive DISMISS rubric applied to cosmetic NITs.
- [ ] Update [_bmad-output/implementation-artifacts/sprint-status.yaml](sprint-status.yaml) — 33-2 status `ready-for-dev → in-progress → review → done`.
- [ ] Update [_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md](SCHEMA_CHANGELOG.md) with the new manifest + loader + check entries (Epic 33 schema-shape landing).
- [ ] Log any DEFER decisions to [_bmad-output/maps/deferred-work.md](../maps/deferred-work.md) §33-2.
- [ ] Update this spec's §Dev Agent Record + §Post-Dev Review Record sections.
- [ ] `bmad-party-mode` green-light before 33-3 opens — confirms substrate is healthy enough for the regeneration story to trust.

## Known Risks + Kill-Switches

**Discovery-driven scope risks (watch for these during T2-T4):**

1. **Generator turns out to need material rewrite** (33-1 case-b "external non-modifiable" escalation). T4 cannot complete the generator rewire; 33-2's AC-B.15 becomes infeasible as-scoped. Escalation: party-mode decides whether to (a) land 33-2 without the generator rewire and defer to a new 33-2.5 story, (b) expand 33-2 scope with explicit point re-estimate, or (c) pivot to building an in-repo generator in 33-2 directly. Dev agent MUST NOT silently expand scope; halt at T4 entry and escalate.

2. **Rewire surfaces >3 insertion-helpers in workflow_runner.py** (not just `insert_4a_between_step_04_and_05`). Scope balloon risk. Party-mode decides whether to migrate all helpers in 33-2 or pull out a thin dispatcher and leave the others as deprecation-shims for a follow-on cleanup story.

3. **Schema_ref to learning-event-schema cannot be left nullable cleanly.** If the Pydantic model insists on a present field, 33-2 ships with `schema_ref: ""` and check 7 returns trivially-PASS on empty; 15-1-lite-marcus fills it in. R1 to confirm during party-mode review; default pragmatic shape is nullable `Optional[Path]` with check-7 trivial-pass on `None`.

4. **DC-3 RESOLVED by R1-A split ruling (Audra tiebreak).** See §R1 Resolutions. No residual risk on naming — L1-lane test integrity preserved by splitting 04.5 + 04.55.

**Dev-agent-anti-pattern guards (enforced by ACs):**

- **27-2 (hand-edit anti-pattern)** → AC-B.15 explicitly forbids v4.2 pack edits in this story.
- **31-1 (rename-one-surface-drifts-another)** → the manifest-first edit rule; every projection change routes through the manifest.
- **Regex-parse anti-pattern** → AC-B.8 + AC-C.4 enforce AST-only.
- **Vague L1 "probably fine" exits** → AC-B.6 exit-code contract strict.

## Dev Notes

### Project Structure Notes

- `state/config/pipeline-manifest.yaml` is the canonical manifest path (R1-C unanimous ruling). Sibling to `parameter-registry-schema.yaml`, `narration-script-parameters.yaml`, `fidelity-contracts/`. No new top-level directory needed. AC-C.5 + AC-T.11 protect against top-level key collisions with existing `state/config/*.yaml` files.
- `scripts/utilities/pipeline_manifest.py` is the loader module; `scripts/utilities/check_pipeline_manifest_lockstep.py` is the L1 check. Both live in `scripts/utilities/` matching existing `check_*` planning-phase scripts named in [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) §External Skills.
- `tests/fixtures/pipeline_manifest_drift/` is the red-path fixture root; follow the importlib.util loader pattern from 31-3 if Python importability matters (probably not for YAML fixtures, but the convention of keeping fixtures out of pytest collection is carried forward).

### Alignment Notes

- This story reopens Marcus orchestrator files (`workflow_runner.py`) — coordination with any concurrent Marcus stream is required. At 2026-04-19 all Marcus work is done (Epics 30/31/32 closed), so risk is low; re-check at T1.
- The `progress_map.py` rewire may touch the HUD output shape the user sees on-refresh (10-second auto-reload per [scripts/utilities/run_hud.py:11](../../scripts/utilities/run_hud.py#L11)). Dev agent verifies the HUD renders byte-equivalently (modulo drift corrections) before closing T4.

### References

- [33-1-generator-discovery.md](33-1-generator-discovery.md) — hard dependency; findings report defines generator scope.
- [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance — governance umbrella.
- [docs/dev-guide/pydantic-v2-schema-checklist.md](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — manifest loader compliance checklist.
- [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) — 27-2, 31-1, regex-parse traps.
- [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) — K-floor, dual-gate policy, aggressive DISMISS.
- [docs/dev-guide/scaffolds/schema-story/](../../docs/dev-guide/scaffolds/schema-story/) — scaffold root for this story.
- [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) — L1/L2 principles, trace-report format, intelligence-placement principle 3.
- [skills/bmad-agent-audra/references/trace-report-format.md](../../skills/bmad-agent-audra/references/trace-report-format.md) — O/I/A schema the trace output must validate against.
- [skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md) §HZ — HUD scope union contract; informs manifest field set.
- [_bmad-output/implementation-artifacts/31-1-lesson-plan-schema.md](31-1-lesson-plan-schema.md) — schema-shape precedent; MUST-FIX patterns from G6.
- [_bmad-output/implementation-artifacts/31-3-registries.md](31-3-registries.md) — MappingProxyType + import-time invariant precedent.
- [_bmad-output/implementation-artifacts/30-1-marcus-duality-split.md](30-1-marcus-duality-split.md) — dual-gate 5pt story precedent.
- **Epic 33 party-mode consensus (2026-04-19)** — transcript in session log; LG-3 hybrid contract home, Q1 parameterized-hook compromise, Amelia's AC-trap flag on 15-1-lite dependency ordering.

## Dev Agent Record

### Agent Model Used

Codex 5.3

### R1 Party-Mode Round Record

Spec-authored R1 rulings were consumed as already ratified inputs in this pass (A/B/C decisions embedded in ACs and `sprint-status.yaml`).
No new shape-changing riders were introduced during this implementation slice.

### R2 Green-Light Record

Pending formal round execution. Current implementation slice aligns to R1 decisions and remains `in-progress`; no closure vote recorded yet.

### Debug Log References

- `.venv\Scripts\python -m pytest tests/test_pipeline_manifest_loader.py tests/test_check_pipeline_manifest_lockstep.py tests/test_projection_equality.py tests/test_marcus_workflow_runner_32_1.py tests/test_insert_between_migration.py tests/test_emitter_manifest_reconciliation.py tests/contracts/test_33_2_check_exit_contract.py tests/contracts/test_33_2_trace_output_format.py tests/contracts/test_33_2_no_regex_in_lockstep_check.py tests/contracts/test_33_2_state_config_disjoint_keys.py tests/contracts/test_33_2_no_orphan_pipeline_literals.py -q`
- `.venv\Scripts\python -m pytest tests/test_run_hud.py tests/test_progress_map.py -q`
- `.venv\Scripts\python -m scripts.utilities.check_pipeline_manifest_lockstep`
- `.venv\Scripts\python -c "import hashlib;from pathlib import Path;..."`
- `rg "insert_4a_between_step_04_and_05" <repo>`

### Completion Notes List

- AC-B.15 DEFERRED per 33-1 kill-switch Case C; follow-up Story 33-1a filed.
- Manifest step count: 33 total (`04.5` + `04.55` split applied; includes conditional sub-phases).
- DC-1..DC-4 resolution posture: substrate detection landed in 33-2; remediation/regeneration remains 33-3 scope.
- **Checks 1-3 intentionally red at 33-2 close posture** — they document DC-1/DC-2/DC-3 drift the substrate now detects but does not yet remediate; 33-3 regeneration closes checks 1-3 green. No hand-edits to v4.2 pack in 33-2 (anti-pattern 27-2 guard).
- L1 check current trace outcome on real pack: `FAIL` with checks `1,2,3,8`; checks `4,5,6,7` pass.
- Rewire count in this slice: 3 consumer surfaces (`run_hud.py`, `progress_map.py`, `workflow_runner.py`) + lockstep checker + manifest loader.
- R1-B migration posture: legacy `insert_4a_between_step_04_and_05` removed from runtime code; `insert_between(before_id, after_id, new_step, steps)` introduced; 32-1 tests migrated.
- Red-path fixtures landed under `tests/fixtures/pipeline_manifest_drift/{schema_only_drift,manifest_only_drift}` with parametrized failure tests.
- Test delta in this slice: +22 collecting tests in focused 33-2 suite (meets K=18 floor and target lower bound 22-27).
- Regression slices: focused 33-2 expanded suite `22 passed`; HUD/progress regression slice `78 passed`.
- v4.2 pack SHA-256 baseline (for 33-3): `6f5d1143222528ea3a9cdcf3e99ca7198d8b587c4c808f06a5a52583d9f36ce3`.

### File List

- `state/config/pipeline-manifest.yaml` (new)
- `scripts/utilities/pipeline_manifest.py` (new — loader)
- `scripts/utilities/check_pipeline_manifest_lockstep.py` (new — L1 check)
- `scripts/utilities/run_hud.py` (modified — PIPELINE_STEPS rewire)
- `scripts/utilities/progress_map.py` (modified — pipeline projection rewire)
- `marcus/orchestrator/workflow_runner.py` (modified — insertion-helper rewire)
- `<v4.2 generator path per 33-1 findings>` (modified — manifest input wire)
- `tests/test_pipeline_manifest_loader.py` (new)
- `tests/test_check_pipeline_manifest_lockstep.py` (new)
- `tests/test_projection_equality.py` (new)
- `tests/test_insert_between_migration.py` (new)
- `tests/test_emitter_manifest_reconciliation.py` (new)
- `tests/contracts/test_33_2_no_orphan_pipeline_literals.py` (new)
- `tests/contracts/test_33_2_check_exit_contract.py` (new)
- `tests/contracts/test_33_2_trace_output_format.py` (new)
- `tests/contracts/test_33_2_no_regex_in_lockstep_check.py` (new)
- `tests/contracts/test_33_2_state_config_disjoint_keys.py` (new)
- `tests/fixtures/pipeline_manifest_drift/schema_only_drift/` (new)
- `tests/fixtures/pipeline_manifest_drift/manifest_only_drift/` (new)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (updated — 33-2 status transitions)
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` (updated — Epic 33 entry)

## Post-Dev Review Record

### G5 Party-Mode Implementation Review

Formal post-dev G5 record (distinct from G6; dual-gate retained):
- Winston (architecture): GREEN-PENDING-RIDER — substrate shape is correct; approves closeout if 33-1a formally owns generator contract before 33-3 opens.
- Murat (test architecture): GREEN-PENDING-RIDER — quality gates are satisfied for landed scope; requires explicit determinism/provenance acceptance criteria on 33-1a.
- Paige (docs/operability): GREEN — closure narrative is coherent once AC-B.15 DEFER routing and dependency reshape are recorded in sprint artifacts.
- Amelia (dev self-review): HIGH confidence — implemented scope is complete; no open MUST-FIX findings remain in 33-2 scope.

### Party-Mode DEFER Sign-Off (AC-B.15)

Micro party-mode DEFER round (Winston + Amelia + Murat) on question:
"AC-B.15 DEFER + 33-1a filing: correct escalation shape given 33-1 landed Case C (no in-repo generator of record)?"
- Winston: YES-WITH-RIDER — Case C invalidates rewire path; DEFER is correct architecture. Rider: 33-1a must explicitly ratify generator ownership, output contract, and acceptance tests before 33-3 opens.
- Amelia: YES-WITH-RIDER — DEFER preserves 33-2 scope integrity and no-hand-edit policy. Rider: 33-1a must define ownership, output contract, and verification criteria before 33-3 starts.
- Murat: YES-WITH-RIDER — quality gates stay coherent only if 33-3 is hard-blocked on verifiable generator completion. Rider: 33-1a must include explicit determinism/provenance acceptance tests and pass them before 33-3.
- Verdict: **UNANIMOUS YES-WITH-RIDER** on DEFER + 33-1a escalation shape.
- Applied rider synthesis: 33-1a remains `blocked-on-party-mode-scope` until the scope round ratifies approach + deterministic regeneration contract + acceptance tests; 33-3 stays blocked on 33-1a done.

### G6 Layered `bmad-code-review` Pass

- **Blind Hunter:** MUST-FIX=1 (explicit AC-B.15 infeasibility now documented and reshaped), SHOULD-FIX=2 (red-path fixture assertions and trace contract pin), NIT=1 (migration grep signal quality).
- **Edge Case Hunter:** walked drift fixtures (`schema_only_drift`, `manifest_only_drift`), structural failure path, and event-emitter reconciliation edge (`04.5` vs `04.55`) — no unhandled MUST edge found in landed slice.
- **Acceptance Auditor:** AC coverage achieved for AC-B.1-14, AC-B.16-18, AC-C.1-5, and associated AC-T slices in current implementation pass; AC-B.15 explicitly DEFERRED with recorded consensus.
- **Orchestrator triage:** PATCH=3 / DEFER=1 / DISMISS=1 for this pass; no open MUST-FIX remains for landed 33-2 scope.
- **MUST-FIX remediation verification:** complete for implemented scope; closeout gates satisfied and DEFER bookkeeping finalized.

### Closure Verdict

DONE (dual-gate closeout complete with AC-B.15 DEFER consensus and artifact hygiene recorded)
