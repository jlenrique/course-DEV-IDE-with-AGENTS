# Story 20a.4: Operator Cluster Density Controls

**Epic:** 20A - Irene Cluster Intelligence - Design & Specification
**Status:** done
**Sprint key:** `20a-4-operator-cluster-density-controls`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md), [20a-3-cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-3-cluster-narrative-arc-schema.md), [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md)

## Story

As an operator,
I want explicit controls for how densely Irene clusters a presentation,
So that I can tune cluster count and interstitial depth to match the run's pedagogical intent, audience, and time constraints — without having to edit Irene's judgment criteria directly.

## Acceptance Criteria

**Given** cluster planning requires operator-level input on density
**When** an operator sets up a production run
**Then** they must be able to set a `CLUSTER_DENSITY` run constant (none | sparse | default | rich) that governs Irene's overall cluster target for the run

**And** `CLUSTER_DENSITY` must follow the same run-constant pattern as `DOUBLE_DISPATCH` — set once in `run-constants.yaml`, respected by Irene during Pass 1

**And** the operator must be able to override clustering at the per-slide level via Prompt 2A `special_treatment_directives` (e.g., "force cluster on the cognitive load slide" or "suppress cluster on the welcome slide")

**And** the operator must be able to specify `cluster_interstitial_count` per forced cluster via the same Prompt 2A mechanism (e.g., "force cluster on slide X with 2 interstitials")

**And** the four `CLUSTER_DENSITY` levels must be defined with concrete cluster-count targets and when each level is appropriate

**And** Irene's behavior when `CLUSTER_DENSITY: none` must be explicitly defined — no clustering, all cluster fields null, backward-compatible with non-clustered runs

**And** the schema must define how operator overrides interact with Irene's judgment: overrides win, but Irene must log when a forced cluster would score low on decision criteria, or when a suppressed slide would have scored high

**And** the controls must be documented as a reference in Irene's skill directory and surfaced as a run-constant addition to the prompt pack documentation

## Tasks / Subtasks

- [x] Task 1: Define the `CLUSTER_DENSITY` run constant schema (AC: 1-4)
  - [x] 1.1: Define the four levels with concrete cluster-count targets and use-case guidance:
    - `none` — no clustering; all cluster fields null; identical to pre-Epic-19 behavior
    - `sparse` — 1–2 clusters per presentation; for short runs or novice audiences needing minimal visual change
    - `default` — 3–5 clusters; standard for a 10–15 slide presentation
    - `rich` — 6+ clusters; for complex, high-density content where progressive disclosure is the primary teaching strategy
  - [x] 1.2: Document the run-constant format matching existing `run-constants.yaml` pattern (see precedent: `DOUBLE_DISPATCH: true | false`)
  - [x] 1.3: Define Irene's default when `CLUSTER_DENSITY` is absent from run-constants.yaml (treat as `none` — conservative)
- [x] Task 2: Define per-slide operator override syntax (AC: 3-4)
  - [x] 2.1: Define the override syntax for Prompt 2A `special_treatment_directives`:
    - Force cluster: `"Force cluster on [slide description or position] with [N] interstitials"` (N = 1–3)
    - Suppress cluster: `"No cluster on [slide description or position]"`
  - [x] 2.2: Define how Irene parses and honors these directives during Pass 1
  - [x] 2.3: Define the warning behavior: when Irene honors a force-cluster on a low-scoring slide or suppresses a high-scoring candidate, she must emit an `operator_override_note` in the cluster plan
- [x] Task 3: Define `cluster_interstitial_count` assignment rules (AC: 4)
  - [x] 3.1: Default assignment: Irene assigns based on content complexity — 1 for single-beat emphasis, 2 for standard arc, 3 for high-complexity concepts
  - [x] 3.2: Operator override: `cluster_interstitial_count` can be set per forced cluster via Prompt 2A syntax
  - [x] 3.3: Bounds enforcement: count must be 1–3; values outside bounds are an error, not a default fallback
- [x] Task 4: Create reference document and update SKILL.md (AC: 8)
  - [x] 4.1: Create `skills/bmad-agent-content-creator/references/cluster-density-controls.md` with full schema, level definitions, override syntax, interaction rules, and examples
  - [x] 4.2: Update [SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/SKILL.md) to add `DC` capability row (cluster density controls)
  - [x] 4.3: Update [cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-decision-criteria.md) to reference the density controls as the operator input layer that can override or constrain the framework output

## Dev Notes

### Scope Boundary

This story defines the **operator control schema and interaction rules**. It does not yet implement:

- Irene Pass 1 logic to read `CLUSTER_DENSITY` from run-constants.yaml (Epic 20b.1)
- Prompt 2A template changes to include cluster override syntax (Epic 20b — prompt pack update follows implementation)
- `run-constants.yaml` schema validator updates (Epic 19.4 or 20b scope)
- Marcus preflight contract changes to validate `CLUSTER_DENSITY` (Epic 20b scope)

This story is a design/documentation artifact. The deliverable is a reference document and SKILL.md update.

### Run Constant Pattern — `DOUBLE_DISPATCH` Precedent

The existing run constant pattern is the authoritative model. From `run-constants.yaml` (latest run: `apc-c1m1-tejal-20260409`):

```yaml
double_dispatch: true
locked_slide_count: 15
target_total_runtime_minutes: 10.0
```

`DOUBLE_DISPATCH` is a boolean structural decision set once per run. `CLUSTER_DENSITY` follows the same pattern — a structural run-level decision:

```yaml
cluster_density: default   # none | sparse | default | rich
```

Key design constraint: `cluster_density: none` must produce exactly the same output as a non-clustered run (all cluster fields null). This preserves backward compatibility per Epic 19.1.

When `cluster_density` is absent from run-constants.yaml (legacy runs), treat as `none` — do not assume `default`. This is conservative: do not cluster unless explicitly opted in.

**Update from B-team discussion (2026-04-11):** Amelia confirmed that `cluster_density` is a hard dependency for 20b.1 implementation. The two specific ACs that block her: setting `cluster_density` config value and `cluster_interstitial_count` per cluster. This story must resolve both before 20b.1 can be implemented.

### Prompt 2A — Operator Directives Channel

Prompt 2A (`production-prompt-pack-v4.1`, step 2A) already collects `special_treatment_directives` from the operator. This is the natural channel for per-slide cluster overrides — it is run-specific, human-authored, and already gated behind a timing policy.

Current Prompt 2A format (from `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`):
```
focus_directives: ...
exclusion_directives: ...
special_treatment_directives: ...
```

The cluster override syntax must fit cleanly into `special_treatment_directives` without requiring a new section. Examples:

```
special_treatment_directives:
  - "Force cluster on the cognitive load theory slide with 2 interstitials"
  - "Suppress cluster on the module welcome slide"
  - "Force cluster on the working memory diagram — 3 interstitials"
```

Irene reads `operator-directives.md` during Pass 1. She must parse cluster force/suppress directives and honor them before applying her decision framework to remaining slides.

### Interaction Rules: Operator Override vs. Irene Judgment

The operator controls must not silently override Irene's judgment — they must be visible:

1. **Force cluster on low-scoring slide:** Irene honors the override and emits an `operator_override_note` in the cluster plan: `"Forced cluster on [slide]: scored LOW on concept density. Override honored."`
2. **Suppress cluster on high-scoring slide:** Same pattern: `"Suppressed cluster on [slide]: scored HIGH on pedagogical weight. Override honored."`
3. **`cluster_density` cap:** If `sparse` is set but operator also forces 4 clusters via per-slide directives, the per-slide forces win and Irene notes the effective density: `"cluster_density: sparse overridden by 4 per-slide force directives — effective density: default."`

This visibility serves the operator review in Storyboard A (Epic 22.1) where the cluster plan is presented as a structural document before Gamma spend.

### `cluster_interstitial_count` Assignment Rules

From `epics-interstitial-clusters.md`: "Set `cluster_interstitial_count` per cluster (1–3, based on content complexity — not a fixed default)."

The reference document must define Irene's heuristic for this assignment:
- **1 interstitial:** Single explanatory beat — one element worth isolating or one key phrase worth landing. Cluster arc: establish → resolve (no develop or tension).
- **2 interstitials:** Standard arc — establish → develop → resolve OR establish → tension → resolve. Most common.
- **3 interstitials:** Full arc — establish → develop → tension → resolve. Reserved for high-complexity concepts with 3+ natural sub-beats.

Operator can override via Prompt 2A force-cluster syntax: `"Force cluster on [slide] with 2 interstitials"`. If operator does not specify count, Irene assigns based on the heuristic above.

### Previous Story Intelligence

- **20a-1** (cluster decision criteria): The operator input criterion is already defined — operator input can force or suppress, and the framework notes whether overrides are "pedagogically natural or compensatory." The density controls reference should cross-link to this criterion and add detail about how `CLUSTER_DENSITY` quantifies the operator's overall density preference.
- **20a-3** (narrative arc schema): Narrative arc and `master_behavioral_intent` are assigned per cluster after the cluster head decision. Operator-forced clusters must also receive narrative arc and master intent assignments — Irene does not skip these for forced clusters.
- **DOUBLE_DISPATCH pattern**: The run constant is a boolean. `CLUSTER_DENSITY` is an enum — same pattern, slightly more expressive. The run_constants.yaml schema loader already handles enums (see `execution_mode: tracked/default`, `quality_preset: explore | draft | production | regulated`).

## Testing Requirements

This is a design/documentation story. No automated tests required. If the dev agent adds `cluster_density` as a validated field to any Python schema loader or run-constants validator, run the targeted test via the repo venv. Do not expand the test suite beyond what touches the new field.

## Project Structure Notes

- **New file:** `skills/bmad-agent-content-creator/references/cluster-density-controls.md`
- **Modified files:**
  - `skills/bmad-agent-content-creator/SKILL.md` — add `DC` capability row
  - `skills/bmad-agent-content-creator/references/cluster-decision-criteria.md` — add cross-link to density controls as the operator input layer

## References

- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 20a.4 definition and cluster density levels
- [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md) — operator input criterion defined here
- [20a-3-cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-3-cluster-narrative-arc-schema.md) — arc assignment applies to forced clusters too
- [cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-decision-criteria.md) — operator input as a criterion; density controls extend this
- [cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-narrative-arc-schema.md) — arc must be assigned for forced clusters
- [docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md) — Prompt 2A format; run constants pattern
- [course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409/run-constants.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409/run-constants.yaml) — live example of run constants including `double_dispatch`

## File List

- skills/bmad-agent-content-creator/references/cluster-density-controls.md (new)
- skills/bmad-agent-content-creator/SKILL.md (modified)
- skills/bmad-agent-content-creator/references/cluster-decision-criteria.md (modified — cross-link only)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6[1m]

### Debug Log

### Completion Notes List

- ✅ Created comprehensive `cluster-density-controls.md` reference document defining CLUSTER_DENSITY run constant schema, per-slide override syntax, interaction rules, and interstitial count assignment heuristics
- ✅ Updated Irene SKILL.md with DC capability row for cluster density controls
- ✅ Added cross-link in cluster-decision-criteria.md to density controls as operator input layer
- ✅ All acceptance criteria satisfied: run constant pattern, override syntax, interstitial count rules, documentation, and backward compatibility defined
- ✅ Design artifacts complete — ready for Epic 20B implementation (Irene Pass 1 logic to consume these schemas)

### Review Follow-ups (AI)

- ✅ Added out-of-bounds `cluster_interstitial_count` error examples and ambiguous slide match handling
- ✅ Added explicit YAML examples for run-constant + per-slide overrides
- ✅ Added precedence rules and contradictory instruction handling
- ✅ Added downstream surfacing in gates/validators and audit trail details
- ✅ Added hard caps/limits (10 clusters max, 3 interstitials max per cluster)
- ✅ Added interactions with other run-constants (DOUBLE_DISPATCH, etc.)
- ✅ Added legacy compatibility and migration notes
- ✅ Saved adversarial review checklist to `20a-4-review-checklist.md`

### File List

## Status

done

## Completion Status

Ultimate context engine analysis completed — comprehensive developer guide created for Irene's operator cluster density controls story.
