# Story 20c-1: Cluster Structure Template Library

**Epic:** 20c - Cluster Intelligence Expansion & Iteration
**Status:** done
**Sprint key:** `20c-1-cluster-structure-template-library`
**Added:** 2026-04-12
**Depends on:** [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md), [20a-2-interstitial-brief-specification-standard.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-2-interstitial-brief-specification-standard.md), [20b-1-irene-pass1-cluster-planning-implementation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-1-irene-pass1-cluster-planning-implementation.md)

## Story

As Irene,
I want a library of named cluster structure templates — each defining a specific pattern of interstitial types, positions, and pacing — beyond the current 5 raw interstitial types,
So that when I plan a cluster, I'm selecting from proven structural patterns rather than assembling individual interstitials ad hoc.

## Context

The current system defines 5 interstitial types (reveal, emphasis-shift, bridge-text, simplification, pace-reset) and 4 positions (establish, develop, tension, resolve). But the combinatorics are open — Irene can assemble any combination. This story introduces **named cluster structure templates** that package type sequences into reusable, pedagogically-grounded patterns. Think of interstitial types as individual notes; templates are chord progressions.

## Acceptance Criteria

**AC-1: Template Definition Format**
Each template must define:
- `template_id` (string, kebab-case)
- `display_name` (human-readable)
- `purpose` (one-sentence pedagogical rationale)
- `interstitial_sequence` (ordered list of {position, interstitial_type, develop_subtype?})
- `interstitial_count` (1-3, derived from sequence)
- `best_for` (content situations where this template excels)
- `avoid_when` (content situations where this template is wrong)
- `pacing_profile` (tight | measured | breathing-room)
- `head_word_range` (may override default [80,140] per template)
- `interstitial_word_ranges` (per-position word range overrides if needed)

**AC-2: Initial Template Set (8-12 templates)**
At minimum, the following structural patterns must be defined:

| Template | Sequence | Purpose |
|----------|----------|---------|
| `deep-dive` | develop(deepen) → develop(exemplify) → resolve | Progressively unpack a complex concept |
| `contrast-pair` | develop(reframe) → tension → resolve | Compare two perspectives, land a synthesis |
| `evidence-build` | develop(exemplify) → develop(exemplify) → resolve | Stack evidence before concluding |
| `quick-punch` | emphasis-shift | Single interstitial, fast impact on one key point |
| `cognitive-reset` | pace-reset | Breathing room after dense content |
| `data-walkthrough` | simplification → reveal → resolve | Strip complex data, then rebuild understanding |
| `narrative-pivot` | bridge-text → tension → resolve | Shift the story direction mid-presentation |
| `zoom-and-return` | reveal → reveal → bridge-text | Zoom into details, then pull back to big picture |
| `framework-expose` | simplification → emphasis-shift → resolve | Simplify a framework, highlight key part, land it |
| `emotional-arc` | reveal → tension → resolve | Full Sophia arc: orient → complicate → illuminate |

Additional templates may emerge during iteration. The library is extensible.

**AC-3: Storage and Access**
- Templates stored as YAML in `skills/bmad-agent-content-creator/references/cluster-templates.yaml`
- Irene loads the template library during Pass 1 cluster planning
- Gary's constraint library (21-1) can reference template-level overrides if needed
- Template library is versioned (schema_version field)

**AC-4: Template Composition Rules**
- A presentation may use different templates for different clusters
- Template selection is per-cluster, not per-presentation
- Templates can be mixed: one cluster uses `deep-dive`, the next uses `quick-punch`
- Consecutive clusters should not use the same template (variety principle)

## Tasks / Subtasks

- [x] Task 1: Design template YAML schema
  - [x] 1.1: Define template fields per AC-1
  - [x] 1.2: Define validation rules (sequence positions must be valid, types must match vocabulary)
  - [x] 1.3: Create schema version and migration path

- [x] Task 2: Author initial template set
  - [x] 2.1: Write 8-12 templates per AC-2
  - [x] 2.2: For each template: purpose, best_for, avoid_when, pacing_profile
  - [x] 2.3: Validate sequences against interstitial type vocabulary and position rules

- [x] Task 3: Integrate into Irene's reference system
  - [x] 3.1: Add cluster-templates.yaml to Irene's references directory
  - [x] 3.2: Update Irene's SKILL.md to load template library during cluster planning
  - [x] 3.3: Update cluster planning logic to select templates (not just types)

- [x] Task 4: Testing and validation
  - [x] 4.1: YAML schema validation tests
  - [x] 4.2: Validate each template produces valid manifest entries
  - [x] 4.3: Run Irene against C1-M1 with template library — compare output to ad-hoc clustering

## Slice 1 Completion Notes (Wave 2 kickoff)

- Added template library:
  - `skills/bmad-agent-content-creator/references/cluster-templates.yaml`
  - Includes schema version `1.0` and 10 required templates from AC-2.
- Added deterministic validator module:
  - `skills/bmad-agent-marcus/scripts/cluster_template_library.py`
- Added test coverage:
  - `skills/bmad-agent-marcus/scripts/tests/test_cluster_template_library.py`
- Updated Irene cluster-planning reference loading:
  - `skills/bmad-agent-content-creator/SKILL.md` now includes `cluster-templates.yaml` in CP reference set.
- Deferred to next slice:
  - Weight/signal refinement across additional profile-driven runs (follow-on under 20c-2)

## Slice 2 Completion Notes (runtime integration + C1-M1 evidence)

- Confirmed runtime template-selection integration at handoff seam:
  - `skills/bmad-agent-marcus/scripts/cluster_template_planner.py`
  - `skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py`
- Hardened comparative evaluator to read selected template IDs from pass2 envelope metadata
  (storyboard + `cluster_template_plan` sources):
  - `skills/bmad-agent-marcus/scripts/evaluate_cluster_template_selection.py`
- Added regression coverage for envelope-derived template IDs:
  - `skills/bmad-agent-marcus/scripts/tests/test_evaluate_cluster_template_selection.py`
- C1-M1 comparison artifact generated:
  - `_bmad-output/test-artifacts/20c-1-eval/c1-m1-comparative-eval.json`
- Latest C1-M1 candidate (`apc-c1m1-tejal-20260419b-motion`) now evaluates `pass`
  against ad-hoc baseline (`apc-c1m1-tejal-20260406-motion`) on minimal regression metrics.

## Dev Notes

### This Is Iterative

This story creates the initial template set. Expect the library to grow and refine across multiple production runs. The `best_for` / `avoid_when` guidance will sharpen as Irene gains experience with each template.

### Relationship to Existing Work

- 20a-1 (decision criteria) determines IF a slide clusters
- 20a-2 (brief specification) determines the quality of individual interstitial briefs
- THIS STORY determines the STRUCTURAL PATTERN of the cluster as a whole
- 20c-2 (selection logic) determines WHICH template Irene picks

## References

- [cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-decision-criteria.md)
- [interstitial-brief-specification.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/interstitial-brief-specification.md)
- [cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-narrative-arc-schema.md)
