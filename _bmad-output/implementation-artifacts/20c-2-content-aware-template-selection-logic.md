# Story 20c-2: Content-Aware Template Selection Logic

**Epic:** 20c - Cluster Intelligence Expansion & Iteration
**Status:** in-progress
**Sprint key:** `20c-2-content-aware-template-selection-logic`
**Added:** 2026-04-12
**Depends on:** [20c-1-cluster-structure-template-library.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-1-cluster-structure-template-library.md), [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md)

## Story

As Irene,
I want content-aware logic for selecting which cluster template to apply to each cluster head,
So that template selection is driven by the content's pedagogical structure — not just its density score — and the resulting cluster sequence across the presentation creates rhythm and variety.

## Context

Currently Irene decides IF a slide clusters (20a-1 criteria) and generates interstitial briefs ad hoc. With the template library (20c-1), Irene needs a second decision: WHICH template pattern fits this content? This is where the presentation design intelligence lives.

## Acceptance Criteria

**AC-1: Content Signal Analysis**
For each cluster head candidate, Irene must analyze:
- **Concept structure:** Single core idea (→ quick-punch/cognitive-reset) vs. multi-faceted concept (→ deep-dive/framework-expose)
- **Data presence:** Tables, charts, statistics (→ data-walkthrough/simplification patterns)
- **Contrast/tension:** Competing perspectives, tradeoffs, debates (→ contrast-pair/narrative-pivot)
- **Evidence density:** Multiple examples or case studies (→ evidence-build)
- **Emotional weight:** Stories, scenarios, stakes (→ emotional-arc)
- **Visual decomposability:** Complex diagrams, multi-element layouts (→ zoom-and-return/reveal patterns)

**AC-2: Template Scoring and Selection**
- Each template scores against the content signals (weighted match)
- Selection considers:
  - Best content-to-template fit (primary)
  - Presentation-level variety (don't repeat the same template consecutively)
  - Pacing balance (not all tight-pacing or all breathing-room in a row)
  - Operator overrides (can force or exclude specific templates per cluster)
- Selection is explainable: Irene must state WHY this template was chosen in the cluster plan

**AC-3: Master Arc Integration**
- Template selection respects the presentation's master arc (beginning → middle → end)
- Early clusters may favor `deep-dive` or `framework-expose` (establishing foundations)
- Middle clusters may favor `contrast-pair`, `evidence-build`, `narrative-pivot` (developing complexity)
- Late clusters may favor `emotional-arc`, `zoom-and-return` (landing meaning)
- The master arc influence is a bias, not a hard rule — content fit overrides arc position

**AC-4: Selection Transparency**
- Cluster plan output includes per-cluster:
  - Selected template_id
  - Content signals that drove selection (top 2-3 reasons)
  - Alternative templates considered and why they were ranked lower
  - Master arc position influence (if any)
- This transparency enables operator review and iterative refinement

**AC-5: Operator Override Vocabulary**
- Operator can specify per-cluster: `force_template: deep-dive` or `exclude_templates: [cognitive-reset, quick-punch]`
- Operator can set presentation-level preferences: `prefer_templates: [contrast-pair, evidence-build]`
- Overrides surface in operator-directives.md (existing Prompt 2A mechanism)

## Tasks / Subtasks

- [x] Task 1: Implement content signal extraction
  - [x] 1.1: Analyze source material / slide brief for concept structure signals
  - [x] 1.2: Detect data presence (tables, statistics, charts from source)
  - [x] 1.3: Detect contrast/tension signals (competing perspectives, tradeoffs)
  - [x] 1.4: Detect evidence density (multiple examples, case studies)
  - [x] 1.5: Detect emotional weight (stories, scenarios, stakes)
  - [x] 1.6: Detect visual decomposability (complex diagrams, multi-element layouts)

- [x] Task 2: Implement template scoring
  - [x] 2.1: Score each template against content signals
  - [x] 2.2: Apply presentation-level variety penalty (consecutive same template)
  - [x] 2.3: Apply pacing balance penalty (too many tight or breathing-room in a row)
  - [x] 2.4: Apply master arc position bias

- [x] Task 3: Implement operator overrides
  - [x] 3.1: Parse force_template and exclude_templates from operator directives
  - [x] 3.2: Parse presentation-level prefer_templates
  - [x] 3.3: Apply overrides before final selection

- [x] Task 4: Implement selection transparency
  - [x] 4.1: Log content signals per cluster head
  - [x] 4.2: Log template ranking with reasons
  - [ ] 4.3: Include selection rationale in cluster plan output

- [ ] Task 5: Testing and iteration
  - [ ] 5.1: Run selection against C1-M1 source content — evaluate template choices
  - [ ] 5.2: Compare template-driven clustering vs. ad-hoc clustering from trial
  - [ ] 5.3: Identify signal extraction gaps (content types not well-served by current signals)

## Slice 1 Completion Notes (deterministic selector core)

- Added selector module:
  - `skills/bmad-agent-marcus/scripts/cluster_template_selector.py`
- Added selector tests:
  - `skills/bmad-agent-marcus/scripts/tests/test_cluster_template_selector.py`
- Implemented in this slice:
  - deterministic signal normalization
  - weighted template scoring
  - variety and pacing penalties
  - master arc bias
  - operator override handling (`force_template`, `exclude_templates`, `prefer_templates`)
  - explainability payload (`reasons`, `alternatives`, full ranking score breakdown)
- Deferred to next slice:
  - C1-M1 comparative run loop and weight refinement

## Slice 2 Runtime Bridge Notes

- Added runtime seam for advisory selection output in Pass 2 handoff prep:
  - `skills/bmad-agent-marcus/scripts/cluster_template_planner.py`
  - `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py`
- Added tests:
  - `skills/bmad-agent-marcus/scripts/tests/test_cluster_template_planner.py`
  - `skills/bmad-agent-marcus/scripts/tests/test_prepare_irene_pass2_handoff.py` (cluster template plan coverage)
- Current bridge behavior:
  - writes optional `cluster_template_plan` block into `pass2-envelope.json` when clustered heads are present
  - promotes selected template IDs into first-class clustered slide rows as `selected_template_id`
  - exposes top-level `selected_template_ids_by_cluster` mapping in `cluster_template_plan` for deterministic lookups
  - remains advisory/non-blocking (handoff prep continues if selector advisory fails, with warning)
- Remaining to complete story:
  - pass1-time integration of selected template IDs into cluster planning outputs
  - production-run evaluation loop for signal/weight refinement (C1-M1 and beyond)

## Slice 3 Template-Influence Wiring Notes

- Elevated selected templates from passive tags to behavior-shaping metadata in handoff prep:
  - `cluster_template_plan` now includes:
    - `selected_template_ids_by_cluster`
    - `expected_interstitial_sequence`
    - `expected_interstitial_count`
    - `template_constraints`
- Pass2 prep now hydrates clustered slide rows from selected template contracts (defaults-first):
  - fills missing `cluster_position`, `interstitial_type`, `develop_type`, `parent_slide_id`
  - sets default `double_dispatch_eligible=false` for interstitial rows when unspecified
  - emits warnings (without overwriting) when authored values conflict with template expectations
- Preserved expanded cluster fields from Gary payload normalization to keep authored Pass1 metadata intact.
- Validation evidence for this slice:
  - Seam gate (`cluster_template_*` + `test_prepare_irene_pass2_handoff`): `40 passed`
  - Wave guardrail pack (`narration schemas`, `validate_irene_pass2_handoff`, `generate_storyboard`, `redispatch` tests): `158 passed`

## Slice 4 Fail-Closed Alignment Gate

- Converted template-sequence alignment from warning-only to blocking in Pass2 prep:
  - `prepare-irene-pass2-handoff.py` now validates clustered row alignment against template expectations and returns `status: fail` on mismatch.
- Blocking checks include:
  - clustered row `selected_template_id` consistency with `cluster_template_plan`
  - interstitial count vs `expected_interstitial_count`
  - ordered sequence match for `cluster_position`, `interstitial_type`, and `develop_type` vs template sequence
- Hydration remains defaults-first and non-destructive, but conflicting authored values now fail closure instead of silently proceeding.
- Additional evidence:
  - seam gate rerun after fail-closed conversion: `40 passed`
  - full Wave guardrail regression pack: `158 passed`

## Slice 5 C1-M1 Comparative Scaffold

- Added offline comparative evaluator script:
  - `skills/bmad-agent-marcus/scripts/evaluate_cluster_template_selection.py`
- Added focused tests:
  - `skills/bmad-agent-marcus/scripts/tests/test_evaluate_cluster_template_selection.py`
- Evaluator purpose:
  - compare baseline vs candidate bundle metrics for template-selection regressions before live HIL runs
  - emit decision (`pass|warn|fail`) and persisted artifact
- Default artifact output:
  - `_bmad-output/test-artifacts/20c-2-eval/c1-m1-comparative-eval.json`

## Dev Notes

### Iteration Expected

This is the story most likely to go through multiple refinement cycles. The content signal extraction (Task 1) is where the intelligence lives, and it will sharpen with each production run. Expect to revisit signal weights and template scoring after every 2-3 runs.

### LLM vs. Heuristic

Content signal extraction could be:
- **Heuristic:** keyword scanning, structure detection (tables, bullet counts, etc.)
- **LLM-driven:** Irene's LLM judgment during Pass 1 (more flexible, harder to debug)
- **Hybrid:** heuristic pre-scoring + LLM final selection (recommended starting point)

### Scope Boundary

This story handles template SELECTION. Template DEFINITION is 20c-1. Template EXECUTION (turning a template into actual interstitial briefs) is handled by existing 20b-1 logic, extended to read template sequences instead of ad-hoc assembly.

## References

- [20c-1-cluster-structure-template-library.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-1-cluster-structure-template-library.md)
- [cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-decision-criteria.md)
- [operator-directives mechanism](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-density-controls.md)
