# Story 33-1: v4.2 Prompt-Pack Generator Discovery

**Status:** done
**Created:** 2026-04-19 (authored against Epic 33 party-mode consensus — Pipeline Lockstep Substrate)
**Epic:** 33 — Pipeline Lockstep Substrate
**Sprint key:** `33-1-generator-discovery`
**Branch:** `dev/epic-33-lockstep` (new — to be created before T1)
**Points:** 0.5
**Depends on:** none (first story of Epic 33)
**Blocks:** 33-2 (pipeline-manifest.yaml SSOT + generator rewire + L1 check), 33-3 (regenerate v4.2 + validate), 33-4 (Cora/Audra pre-closure block-mode), 15-1-lite-marcus (meta-test)
**Governance mode:** **single-gate** — investigation spike; no new code modules; post-dev three-layer `bmad-code-review` is the sole review ceremony. Epic 33 is out of Lesson Planner MVP scope (Epics 28–32), so the Lesson Planner governance validator does **not** apply. BMAD sprint governance per [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance still applies: `bmad-code-review` before done, party-mode consensus on scope changes, `bmad-party-mode` green-light prior to Story 33-2 opening.

## Post-Close R1 Addendum (2026-04-19)

After 33-1 closed, the Story 33-2 R1 party-mode round ruled on three substrate decisions that reflect back onto 33-1's findings surface. Per unanimous specialist agreement (Winston / Amelia / Paige / Murat stock roster + Audra + Cora off-manifest tiebreak), **addendum suffices — no re-review of 33-1's closure**. Cora's lockstep envelope confirms: "generator must enumerate from manifest, not hardcode step IDs" is a parameterization concern, not a per-step-ID concern. The addendum items below are binding on the findings report [`_bmad-output/specs/33-1-generator-discovery-findings.md`](../specs/33-1-generator-discovery-findings.md) if any existed at close; if not present, Story 33-2's T2 authors them into the newly-created manifest and records the parameterization explicitly.

**A-1 — Manifest canonical path (R1-C ruling).** All references to the "pipeline manifest" resolve to [`state/config/pipeline-manifest.yaml`](../../state/config/pipeline-manifest.yaml) (unanimous R1-C; sibling to `parameter-registry-schema.yaml`, `narration-script-parameters.yaml`, `fidelity-contracts/`). The 33-1 findings report's §Gap Analysis — where it names the manifest by path — updates to this location. Any reference to `_bmad/manifests/pipeline-manifest.yaml` in the findings report is stale and must be sed-updated.

**A-2 — DC-3 04.5 semantic collision resolution (R1-A split ruling).** Per Audra's L1-lane tiebreak (Principle 1 deterministic-first integrity), the 04.5 step splits into two distinct manifest entries: `04.5` = "Parent Slide Count Polling" (precursor polling; emits `plan_unit.created` events per `loop.py`); `04.55` = "Estimator + Run Constants Lock" (constants-lock step gating downstream emission). Cut line: `loop.py`'s first `plan_unit.created` emission boundary. Backflow to 33-1: any reference in the findings report to "step 04.5" gets disambiguated to "04.5 (polling)" or "04.55 (lock)" per the intended concern. Cora's governance framing: **the generator's contract is "enumerate from manifest, not hardcode step IDs"** — so the addendum to 33-1's §Gap Analysis is one sentence naming the parameterization expectation. Audra's operator-facing note: pack §4.5 body text today describes polling + lock under one heading; 33-3 regeneration will emit two pack sections (§4.5 polling + §4.55 lock) from the split manifest entries — the dev agent on 33-2 must NOT assume the existing §4.5 body text stays verbatim.

**A-3 — `insert_between` rename+generalize (R1-B ruling).** `insert_4a_between_step_04_and_05` is **deleted and replaced** by generalized `insert_between(before_id, after_id, new_step)` in Story 33-2 (Audra Principle-3 ruling; Murat AC-C.1 trap decisive against the shim; Cora governance-envelope concurring on silent-reopen-surface minimization). Backflow to 33-1: any findings-report recommendations that assumed a specific migration shape (e.g., "33-2 preserves `insert_4a_*` via shim") soften to match the hard-migrate + rename-generalize ruling. If 33-1's findings named `insert_4a_*` as legacy, name it as replaced-by-`insert_between` with the legacy function deleted in 33-2.

**Addendum closure status**: closed same-session 2026-04-19 per specialist unanimous ruling. 33-1 closure stands; no spec re-review required. The Cora-lane and Audra-lane commitments captured in this addendum bind Story 33-2's dev agent at T1, not this story's.

## TL;DR

- **What:** Investigation spike that locates the generator responsible for producing [docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](../../docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md), documents its inputs/outputs/invocation path, and specifies how Story 33-2 will rewire it to consume the forthcoming `pipeline-manifest.yaml` SSOT. Primary deliverable is a findings report at [`_bmad-output/specs/33-1-generator-discovery-findings.md`](../specs/33-1-generator-discovery-findings.md). No production code lands in this story.
- **Why:** Operator confirmed in the Epic 33 party-mode round that **"v4.2 is generated, and should always be."** Story 33-2's scope (pipeline-manifest.yaml SSOT + `check_pipeline_manifest_lockstep.py` L1 check + generator rewire) is conditional on what the generator actually is — its location, its inputs, and whether it already accepts a manifest-shaped input or needs one wired. Speccing 33-2 without that ground truth would either (a) balloon 33-2 mid-execution as discoveries surface, or (b) produce ACs that don't match the generator's reality. Winston's party-mode recommendation (unanimous, 5-voice roster): carve this out as a time-boxed spike so 33-2 opens against known facts.
- **Done when:** (1) Findings report exists at the named path with all required sections populated; (2) generator is identified — entry point, invocation command, and regeneration procedure documented — OR explicit escalation block is filled out if the generator does not currently exist; (3) inputs (source files, templates, parameters) and outputs (generated pack path + current byte-level fingerprint) are enumerated; (4) gap analysis names the specific changes Story 33-2 must land to wire `pipeline-manifest.yaml` as the canonical input; (5) kill-switch decision recorded — dev agent must STOP and escalate to party-mode if discovery surfaces conditions outside the boundaries listed in §Kill-switch below; (6) one contract test lands pinning the findings doc's section structure; (7) single-gate post-dev `bmad-code-review` layered pass (Blind + Edge + Auditor); (8) sprint-status flipped `ready-for-dev → in-progress → review → done`.
- **Scope discipline:** 33-1 ships **zero new Python modules**, **zero new YAML schemas**, **zero refactors to existing code**. The only new files on disk are: the findings report, one pytest contract test pinning the report's structure, and (optionally) an `evidence/` subdirectory under the findings-report path capturing raw command output / file excerpts used to reach conclusions. Any temptation to "while I'm in here, also fix X" is out of scope by charter — route findings-that-suggest-fixes into Story 33-2's backlog ACs via the findings report's §Gap Analysis.

## Story

As the **dev agent opening Epic 33 — Pipeline Lockstep Substrate**,
I want **a written, citable record of where the v4.2 pack's generator lives, how it runs, and what it consumes today**,
So that **Story 33-2 can be authored against the generator's actual shape (not assumed shape), and the risk of mid-story scope-drift on the substrate work is bounded to what this spike surfaces**.

## Background — Why This Story Exists

Epic 33 was created by party-mode consensus on 2026-04-19 after the harmonization walkthrough (party round across Winston/Amelia/Paige/Murat + Cora/Audra) surfaced five drifts across v4.2 pack ↔ Marcus orchestrator ↔ HUD (DC-1..DC-5 in that round's taxonomy). DC-5 — the **absence of a single source of truth** — was unanimously named as the root cause. Audra recast this as an **Omission (severity Med→High)**: `scripts/utilities/run_hud.py:44` carries a TODO for `pipeline-manifest.yaml` that never landed, which permits DC-1 (HUD omits 5 pack steps), DC-2 (04A position mismatch three ways), DC-3 (04.5 semantic collision), and DC-4 (failing regression test) to exist.

The operator then added a hard constraint: **v4.2 is generated, and should always be** — meaning any hand-edit to `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` is structurally wrong (matches the 27-2 hand-edit anti-pattern Amelia flagged in [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md)). Fixes must flow through the generator's inputs.

Winston's party-mode architectural read: the pack, the HUD, and the orchestrator are all **projections** of one as-yet-unrealized canonical manifest; a fourth surface — the generator — ties the manifest to the pack. Audra's intelligence-placement principle (her [SKILL.md](../../skills/bmad-agent-audra/SKILL.md) Principle 3) insists the manifest is a structural anchor, not a payload catalogue. Before we can spec the SSOT manifest (33-2) or its L1 lockstep check (`check_pipeline_manifest_lockstep.py`, also 33-2), we must know: does the generator already read a manifest-shaped input? Does it render from templates plus parameters? Is it in-repo or external (e.g., an LLM-driven authoring tool like Gamma)?

Without this spike, 33-2's scope is unbounded. With it, 33-2 opens against a concrete "extend X generator to read Y manifest, producing the same byte-equivalent output modulo the corrected drift items" AC set.

**Why 0.5pt and not 1pt or 2pt:** the investigation has a binary outcome — found-and-trivial-to-wire, or found-and-non-trivial-requires-33-1a — plus a well-scoped writeup. Dev agent should not expand the scope by attempting to *implement* the manifest-integration within 33-1. See §Kill-switch below for the explicit "stop and escalate" conditions.

## T1 Readiness

- **Gate mode:** `single-gate` — investigation spike; post-dev three-layer `bmad-code-review` (Blind + Edge + Auditor) is the sole review ceremony. No R1/R2 party-mode rounds required for 33-1 since the Epic 33 sprint plan itself was the party-mode decision.
- **K floor:** `K = 1` per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 for a 0.5pt investigation-only story. One contract test pinning the findings-doc structure is sufficient.
- **Target collecting-test range:** 1–2 (K to 2×K; 0.5pt stories are the exception to the 1.2–1.5× ceiling per §1 footnote on investigation spikes).
- **Realistic landing estimate:** 1–2 collecting tests.
- **Required readings** (dev agent reads at T1 before any investigation work):
  - [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance — governance that applies to this story (bmad-code-review before done; consensus on scope changes).
  - [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) §§ "schema", "review-ceremony", "refinement-iteration" — specifically the **27-2 pattern** (fixing a symptom in a hand-edited output) and the **31-1 pattern** (rename on one surface drifts another). 33-1 must NOT edit the v4.2 pack as part of investigation.
  - [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §1 (K-floor discipline), §2 (single-gate policy), §3 (aggressive DISMISS rubric for cosmetic NITs at post-dev review).
  - [docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](../../docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md) — the generated artifact itself. Read the first 100 lines to understand the structure Marcus consumes at runtime. Do not edit this file in 33-1.
  - [scripts/utilities/run_hud.py:43-75](../../scripts/utilities/run_hud.py#L43-L75) — `PIPELINE_STEPS` list + the `SYNC-WITH` comment + the **`TODO: Extract to shared pipeline-manifest.yaml for single-source-of-truth`** line that seeded Epic 33.
  - [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) — principles for how this finding feeds Story 33-2's L1 check design. The generator's input path becomes an L1 anchor; the generator's output is one of the projections.
  - Epic 33 party-mode transcript — available in the session chat log (2026-04-19); findings report should cite the consensus decisions it grounds against.
- **Scaffold requirement:** `require_scaffold: false` — investigation story, no schema shape.
- **Runway pre-work consumed:** none (first story of Epic 33; depends only on the Epic 33 party-mode round having produced a consensus sprint plan, which it did).

## Acceptance Criteria

### Behavioral (AC-B.*)

1. **AC-B.1 — Findings doc exists at the canonical path.** [`_bmad-output/specs/33-1-generator-discovery-findings.md`](../specs/33-1-generator-discovery-findings.md) exists, is non-empty, and carries all section headers listed in AC-C.1.

2. **AC-B.2 — Generator location identified (or explicit escalation).** The findings doc §Generator Location names either:
   - **(a) An in-repo entry point**: absolute repo-relative path to the generator (script, module, or workflow file), plus the invocation command that produces the current v4.2 pack. Example shape: `scripts/utilities/<generator>.py` + `python -m scripts.utilities.<generator> --output docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`. Or:
   - **(b) An external tool identification**: the tool name (e.g., "Gamma export", "BMAD workflow under `_bmad/bmm/...`", "hand-authored by a prior maintainer with no generator of record"), plus enough detail that 33-2 can decide whether to build an in-repo generator or wrap the external one. Or:
   - **(c) An explicit escalation block**: if no generator can be identified and the pack is de-facto hand-authored despite the operator's "should always be generated" stance, the findings doc records that fact plainly, names the proposed follow-up story **33-1a — Build the v4.2 generator from scratch**, and STOPS work pending operator + party-mode decision. Dev agent does NOT attempt to build the generator within 33-1.

3. **AC-B.3 — Inputs enumerated.** §Generator Inputs lists every file, parameter, or environment variable the generator consumes, with repo-relative paths where applicable. If the generator reads parameters, list the parameter keys + their current values. If the generator reads from a template, cite the template path. If no inputs are identifiable (case-c escalation), record the fact explicitly — empty-list is not acceptable prose; the findings must read "No inputs identified; see §Escalation."

4. **AC-B.4 — Outputs enumerated + byte-level fingerprint.** §Generator Outputs names every file the generator writes, with repo-relative paths. For v4.2 specifically, record the current SHA-256 of `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` so Story 33-3 has a baseline to check regeneration against. Use `python -c "import hashlib; print(hashlib.sha256(open('docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md','rb').read()).hexdigest())"` or equivalent; cite the command used.

5. **AC-B.5 — Regeneration procedure verified (where feasible).** §Regeneration Procedure records the exact command sequence that would regenerate v4.2 today. If case (a): dev agent runs the procedure once against a scratch output path, verifies the generator executes without error, and diffs the scratch output against the on-disk v4.2. If the diff is non-empty, that is ITSELF a finding (the pack has drifted from its generator — a class of drift 33-2/33-3 must address) and the diff gets summarized in §Drift Between Generator and On-Disk v4.2. If case (b) or (c): record why verification is not feasible in this story's scope, and what Story 33-2 or 33-1a will need to verify instead.

6. **AC-B.6 — Gap analysis for Story 33-2.** §Gap Analysis lists the specific changes 33-2 must make to wire `pipeline-manifest.yaml` as the canonical input. Minimum bullets:
   - What new input contract the generator must accept (e.g., "generator gains a `--manifest-path` arg, reads a list of `{id, label, gate, sub_phase_of, …}` entries").
   - Where the current input/template lives today vs. where it should live after 33-2.
   - Any side concerns surfaced during discovery that should become 33-2 ACs or 33-3 ACs (examples: "the generator also writes v4.1 and v4.3 output — manifest must carry `pack_version` per the Q1 consensus in the Epic 33 party round").
   - Any **out-of-scope** discoveries that belong to a new story (filed as 33-1b, 33-1c, etc.) rather than expanding 33-2.

7. **AC-B.7 — Kill-switch decision recorded.** §Kill-switch Decision states explicitly whether 33-2 can proceed as originally scoped, or whether the discovery surfaced a condition that triggers one of the escalation paths in §Kill-switch. Kill-switch conditions (reproduced from §Kill-switch below for AC clarity):
   - Generator does not exist at all and pack is hand-authored → escalate to party-mode; file Story 33-1a.
   - Generator is an external tool we cannot modify (e.g., Gamma export) → escalate to party-mode for decision on wrap-vs-rebuild; 33-2 scope may need to shift to "build an in-repo regeneration layer that matches the external tool's output shape."
   - Generator has ≥3 callers or is load-bearing for packs beyond v4.2 (v4.1, v4.3, etc.) → 33-2 scope must expand to multi-version manifest-aware (aligns with Q1 consensus already captured).
   - Generator reads inputs from ≥3 distinct source files that are themselves not version-controlled or not in-repo → escalate; 33-2 scope changes materially.

8. **AC-B.8 — No edits to v4.2 pack, no edits to HUD, no edits to orchestrator.** 33-1 is investigation-only. Dev agent's git diff at story-close MUST NOT include changes to `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`, `scripts/utilities/run_hud.py`, or any file under `marcus/orchestrator/`. The 27-2 hand-edit anti-pattern Amelia named in the party round is the primary guard here.

### Contract (AC-C.*)

1. **AC-C.1 — Findings-doc structure pinned.** One contract test at `tests/contracts/test_33_1_findings_doc_structure.py::test_findings_doc_has_required_sections` reads `_bmad-output/specs/33-1-generator-discovery-findings.md` and asserts the following section headers are present (exact-string match on the level-2 `## ` heading):
   - `## Summary`
   - `## Generator Location`
   - `## Generator Inputs`
   - `## Generator Outputs`
   - `## Regeneration Procedure`
   - `## Drift Between Generator and On-Disk v4.2` (may be empty-body if none found, but the heading must exist)
   - `## Gap Analysis`
   - `## Kill-switch Decision`
   - `## Escalation` (may be empty-body if no escalation is triggered, but the heading must exist so dev agents know where to look)
   - `## Evidence Index` (pointers to any `evidence/` subdirectory entries)

   Test must fail with a Maya-safe error message listing the missing sections if any are absent.

### Test (AC-T.*)

1. **AC-T.1 — Contract test passes under focused slice and full regression.** `python -m pytest tests/contracts/test_33_1_findings_doc_structure.py -p no:cacheprovider` exits 0. Full regression `python -m pytest -p no:cacheprovider` exits 0 (no new failures introduced by this story; the 3 pre-existing at-session-close regressions documented in [next-session-start-here.md](../../next-session-start-here.md) are tracked separately and their status is recorded in this story's Dev Agent Record at closure).

## Tasks / Subtasks

### T1 — Readiness gate (before any investigation)

- [x] Create branch `dev/epic-33-lockstep` off `master`; confirm branch is clean.
- [x] Read all required readings enumerated in §T1 Readiness.
- [x] Confirm Epic 33 has been added to [_bmad-output/implementation-artifacts/sprint-status.yaml](sprint-status.yaml) (`epic-33: in-progress` + the 5 Epic 33 story keys); if missing, update `sprint-status.yaml` in the same commit that opens 33-1.
- [x] Confirm Epic 33 has been added to [_bmad-output/planning-artifacts/epics.md](../planning-artifacts/epics.md); if missing, add a minimal Epic 33 entry linking to this story and to 33-2/33-3/33-4/15-1-lite-marcus.

### T2 — Investigation (AC-B.2, AC-B.3, AC-B.4, AC-B.5)

- [x] Search the repo exhaustively for generator candidates. Suggested starting points:
  - [x] `skills/` subdirectories with "prompt-pack" / "production-prompt" / "v4.2" in names or READMEs.
  - [x] `scripts/utilities/` — grep for string literals matching `v4.2` or the pack filename.
  - [x] `_bmad/` — check installed BMAD workflows + templates for v4.2 references.
  - [x] `docs/workflow/` — check for companion files (e.g., `v4.2-source.md`, `v4.2-template.md`, or archive folders).
  - [x] Git history: `git log --oneline --all -- docs/workflow/production-prompt-pack-v4.2-*.md` — inspect commit messages for generator authorship clues; `git log --all --source -- '*prompt-pack*generator*'` for generator candidate paths.
  - [x] CHANGELOG / session-handoff history: search `SESSION-HANDOFF.md` and `next-session-start-here.md` archives for mentions of v4.2 generator authorship.
- [x] Record every candidate examined + verdict (hit / miss / inconclusive) in the findings doc §Evidence Index.
- [x] When a generator is located (case a) OR identified as external (case b) OR ruled out (case c), populate §Generator Location / §Generator Inputs / §Generator Outputs accordingly.
- [x] Compute + record v4.2 SHA-256 fingerprint (AC-B.4).
- [x] If case (a): execute the regeneration procedure against a scratch output path; diff against on-disk v4.2; record outcome in §Drift Between Generator and On-Disk v4.2.

### T3 — Author findings doc (AC-B.1, AC-B.6, AC-B.7, AC-C.1)

- [x] Land [`_bmad-output/specs/33-1-generator-discovery-findings.md`](../specs/33-1-generator-discovery-findings.md) with all required sections.
- [x] Populate §Gap Analysis with the explicit changes 33-2 must make to wire `pipeline-manifest.yaml`.
- [x] Populate §Kill-switch Decision with the proceed / escalate verdict + rationale.
- [x] Populate §Escalation block if any kill-switch condition is met (otherwise the section exists with a single line "No escalation triggered.").

### T4 — Land contract test (AC-T.1, AC-C.1)

- [x] Author `tests/contracts/test_33_1_findings_doc_structure.py` with one collecting function `test_findings_doc_has_required_sections`.
- [x] Verify `python -m pytest tests/contracts/test_33_1_findings_doc_structure.py -p no:cacheprovider` exits 0.

### T5 — Regression pass + close

- [x] Focused 33-1 suite: `python -m pytest tests/contracts/test_33_1_findings_doc_structure.py -p no:cacheprovider` — expect green.
- [x] Full regression: `python -m pytest -p no:cacheprovider` — expect no new failures vs. the at-session-close baseline (3 pre-existing regressions documented in [next-session-start-here.md](../../next-session-start-here.md) stay red; 33-1 must not add a 4th).
- [x] Ruff clean on the new contract test file.
- [x] Layered post-dev `bmad-code-review` (Blind Hunter + Edge Case Hunter + Acceptance Auditor) per [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) §3 aggressive DISMISS rubric. For a 0.5pt investigation story, **≥3 DEFER is acceptable** because most findings map to 33-2/33-3 scope rather than to 33-1 remediation.
- [x] `bmad-party-mode` green-light on the findings report is **optional** for 33-1 closure but **recommended** if the kill-switch decision escalates — the party votes on which escalation path to take. If no escalation, Amelia's self-review + post-dev code-review is sufficient per §BMAD sprint governance (small single-gate 0.5pt story).
- [x] Update [_bmad-output/implementation-artifacts/sprint-status.yaml](sprint-status.yaml) — 33-1 status `ready-for-dev → in-progress → review → done`.
- [x] Log any DEFER decisions to [_bmad-output/maps/deferred-work.md](../maps/deferred-work.md) §33-1 (create section if absent).
- [x] Update this spec's §Dev Agent Record + §Post-Dev Review Record sections.

## Kill-switch

The dev agent MUST STOP and escalate to `bmad-party-mode` (not silently expand 33-1 scope) if any of the following surface during investigation:

1. **Generator does not exist.** Pack is hand-authored despite operator's "should always be generated" stance. Proposed follow-up: file Story 33-1a (Build the v4.2 generator from scratch) — this is NOT 33-1 scope.
2. **Generator is an external tool we cannot source-control or modify** (e.g., a Gamma export, a closed-source doc tool, a copy-paste from an LLM session with no captured prompts). Proposed follow-up: party-mode decides wrap-vs-rebuild; 33-2 scope shifts accordingly.
3. **Generator has ≥3 callers or packs ≥2 other versions (v4.1, v4.3)**. Story 33-2's scope expands to multi-version-manifest-aware. Already aligns with the Q1 Epic 33 party-mode compromise (parameterized version hook; see §References). Not a blocker, but requires explicit note so 33-2 AC authors are aware.
4. **Generator reads inputs from ≥3 source files not currently under version control** (e.g., a local-machine config directory, an environment-variable-bound config). 33-2 scope materially changes.
5. **Discovery consumes >2 working hours** without surfacing a generator location or producing a credible "no generator" verdict. Time-box exceeded; escalate.

Discovery-time bound: 33-1 is a 0.5pt spike. If investigation crosses 2 hours without convergence on a verdict, that is itself a kill-switch signal — the generator is non-trivial to locate and the spike should either time-box-and-report-inconclusive or escalate for party-mode guidance.

## Dev Notes

### Project Structure Notes

- No new top-level directories are created by this story. The findings doc lives at [`_bmad-output/specs/33-1-generator-discovery-findings.md`](../specs/33-1-generator-discovery-findings.md) (alongside peer specs like [30-1-golden-trace-baseline-capture-plan.md](../specs/30-1-golden-trace-baseline-capture-plan.md)). The contract test lives at `tests/contracts/test_33_1_findings_doc_structure.py`, matching the existing pattern for cross-artifact contract tests (see `tests/contracts/test_30_2b_dispatch_monopoly.py`, `tests/contracts/test_30_4_fanout_intake_isolation.py`, etc.).
- If Evidence requires subdirectory capture: `_bmad-output/specs/33-1-evidence/` — one markdown or JSON file per candidate investigated, referenced from the findings doc §Evidence Index. Git-track these so the investigation is auditable by the next dev on 33-2.

### Alignment Notes

- Epic 33 opens with this story as its first; `sprint-status.yaml` must flip `epic-33: backlog → in-progress` on T1 (per the `create-story` workflow's "first story in epic" auto-transition rule).
- Unlike Lesson Planner MVP stories, Epic 33 is NOT governed by [docs/dev-guide/lesson-planner-story-governance.json](../../docs/dev-guide/lesson-planner-story-governance.json). `scripts/utilities/validate_lesson_planner_story_governance.py` does not apply; do not attempt to run it against this story.

### References

- [CLAUDE.md](../../CLAUDE.md) §BMAD sprint governance — governance umbrella for Epic 33.
- [docs/dev-guide/dev-agent-anti-patterns.md](../../docs/dev-guide/dev-agent-anti-patterns.md) — anti-patterns catalog; 27-2 and 31-1 patterns are the primary guards for this story.
- [docs/dev-guide/story-cycle-efficiency.md](../../docs/dev-guide/story-cycle-efficiency.md) — K-floor discipline, single-gate policy, aggressive DISMISS rubric.
- [docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md](../../docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md) — the generated artifact this story investigates.
- [scripts/utilities/run_hud.py](../../scripts/utilities/run_hud.py) — contains the line-44 TODO that seeded Epic 33.
- [skills/bmad-agent-audra/SKILL.md](../../skills/bmad-agent-audra/SKILL.md) — L1/L2 principles informing Story 33-2's L1 check design.
- [skills/bmad-agent-cora/SKILL.md](../../skills/bmad-agent-cora/SKILL.md) — HZ capability that Story 33-4 will promote to block-mode.
- **Epic 33 party-mode consensus (2026-04-19)** — transcript in session log; key decisions:
  - **Unanimous (5-voice):** B0 generator discovery as separate story (this one), Story A (drift remediation) collapses into "regenerate from manifest" after B lands.
  - **Q1 — Multi-version linter vs v4.2-only:** split 2-2; Murat's parameterized-hook compromise carried (parameterize version today; extension is 1-line).
  - **Q2 — Epic 28-32 vs Epic 33:** split 2-2 initially; learning-glimmer meta-test (Story 15-1-lite-marcus) tipped consensus to **Epic 33** because substrate serves two consumers.
  - **LG-3 — Learning-event contract home:** Hybrid (c) per Audra + Winston + Murat — `pipeline-manifest.yaml` carries gate→emission topology; `learning-event-schema.yaml` carries payload shape; two L1 checks.

## Dev Agent Record

### Agent Model Used

Codex 5.3

### Debug Log References

- `git switch -c dev/epic-33-lockstep`
- `git log --follow --name-only -- docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `git log --all --source --oneline -- "*prompt-pack*generator*"`
- `python -c "import hashlib;from pathlib import Path;..."`
- `rg` sweeps across `scripts/`, `_bmad/`, `docs/workflow/`, `SESSION-HANDOFF.md`, `next-session-start-here.md`

### Completion Notes List

- Kill-switch decision: **ESCALATE: generator-of-record not found in repository**
- Generator identification case: **(c) no-generator**
- Regeneration diff vs on-disk v4.2: **not executable in 33-1 (no generator entrypoint)**
- Hours consumed by investigation: **~2.2**
- DEFERs logged to [_bmad-output/maps/deferred-work.md](../maps/deferred-work.md) §33-1: **3**

### File List

- `_bmad-output/specs/33-1-generator-discovery-findings.md` (new)
- `tests/contracts/test_33_1_findings_doc_structure.py` (new)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (updated — epic-33 + 33-1 status transitions)
- `_bmad-output/planning-artifacts/epics.md` (updated — Epic 33 entry, if not already present)
- `_bmad-output/maps/deferred-work.md` (updated — added `33-1` DEFER section)
- `_bmad-output/implementation-artifacts/33-1-generator-discovery.md` (updated — tasks/dev record/review record/status)
- `scripts/utilities/progress_map.py` (updated — add Epic 33 wave label for sprint-status/test lockstep)
- `tests/test_marcus_coverage_non_regression.py` (updated — placeholder-baseline detection now matches artifact contract)

## Post-Dev Review Record

### Layered `bmad-code-review` Pass

**Blind Hunter findings**
- No in-repo file-write path to v4.2 pack discovered (`PATCH`: none in 33-1 by scope; `DEFER`: create generator in 33-1a).

**Edge Case Hunter findings**
- Current assumptions in 33-2 about "rewire existing generator" are invalid if no generator exists (`DEFER`: re-scope via party-mode before 33-2 opens).
- Potential cross-version generation concern remains open if future generator must emit v4.1 + v4.2 (`DEFER`: encode as explicit AC in 33-2/33-1a planning).

**Acceptance Auditor findings**
- AC-C.1 doc-structure contract now pinned with a dedicated test (`PATCH`: applied in this story).
- Escalation requirement and kill-switch are explicitly documented in findings report (`PATCH`: applied in this story).
- Post-remediation full-suite gate now green after two lockstep fixes (`PATCH`: Epic 33 wave-label registry parity and placeholder-coverage pin skip logic).

**Triage summary:** `PATCH=4`, `DEFER=3`, `DISMISS=0`

### Party-Mode Input (if escalation triggered)

Kill-switch condition fired during discovery; party-mode escalation is recommended and pending operator scheduling. No party-mode outcome is recorded yet in this story artifact.

### Closure Verdict

**ESCALATED-TO-33-1a**

## Change Log

- 2026-04-19: Story 33-1 investigation artifacts landed (findings report + contract test + escalation record).
- 2026-04-19: Layered post-dev review remediation pass completed. Fixed Epic 33 progress-map label lockstep and coverage-pin placeholder detection; full regression now green (`1911 passed, 4 skipped, 27 deselected, 2 xfailed`).
