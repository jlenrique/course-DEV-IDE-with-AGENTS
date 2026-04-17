# Story 20a.3: Cluster Narrative Arc Schema

**Epic:** 20A - Irene Cluster Intelligence - Design & Specification
**Status:** done
**Sprint key:** `20a-3-cluster-narrative-arc-schema`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md), [20a-2-interstitial-brief-specification-standard.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-2-interstitial-brief-specification-standard.md), [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md)

## Story

As Irene,
I want a schema for the `narrative_arc` field and `master_behavioral_intent` per cluster,
So that every cluster I plan has a coherent emotional journey that guides position assignment, develop sub-typing, and downstream narration.

## Acceptance Criteria

**Given** cluster planning requires each cluster to form a coherent narrative unit
**When** Irene assigns a `narrative_arc` to a cluster head
**Then** the arc must be a single sentence capturing the emotional journey from establish to resolve

**And** the arc sentence must follow Sophia's four-beat framework: orient -> complicate -> illuminate -> resolve, mapped to cluster positions establish -> tension -> develop -> resolve

**And** each cluster must carry a `master_behavioral_intent`, a single concise directive that all segment-level `behavioral_intent` values within the cluster must serve

**And** Irene must assign develop sub-types (`deepen` | `reframe` | `exemplify`) explicitly to every `develop`-position interstitial, with no two `develop` interstitials in the same cluster sharing the same sub-type

**And** the schema must specify quality bars and failure examples for both `narrative_arc` sentences and `master_behavioral_intent` values

**And** the resulting reference must document how cluster positions map to Sophia's narrative beats and show the relationship between `master_behavioral_intent` and per-segment `behavioral_intent`

**And** the reference must be positioned as the authoritative contract that Irene Pass 1 (Epic 20B), Pass 2 narration (Epic 23), and Storyboard rendering (Epic 22) must honor

## Tasks / Subtasks

- [x] Task 1: Define the `narrative_arc` field schema
- [x] Task 2: Define `master_behavioral_intent`
- [x] Task 3: Define develop sub-type assignment rules
- [x] Task 4: Create reference document and update SKILL.md

## Dev Notes

### Scope Boundary

This story defines the **narrative arc design schema and rules**. It does not yet implement:

- Irene Pass 1 generation logic for `narrative_arc` values
- Narration alignment validation
- Storyboard cluster rendering

This story is a design/documentation artifact. The deliverable is a reference document that makes the rules explicit before implementation begins.

### Field Status in the Segment Manifest

The segment manifest template already carries the relevant cluster fields:

```yaml
narrative_arc: string | null
master_behavioral_intent: enum | null
develop_type: enum | null
```

This story defines the value rules for those fields. No additional schema change is required before Epic 20B consumes them.

### Canonical Beat Mapping

When all four beats are present, the canonical beat order is:

`establish -> tension -> develop -> resolve`

Shorter clusters may collapse one middle beat for a 2-interstitial structure, but `develop` should not be documented as the default beat before `tension`.

### Quality Guardrails

The reference must make these rules explicit:

1. Arc sentences must be specific, include a mechanism, and be usable by downstream narration and review.
2. `master_behavioral_intent` must use the existing enumerated vocabulary, not free-form prose.
3. `develop_type` assignments must be non-redundant within a cluster.
4. A grounded C1M1 example must show arc, master intent, and segment-level behavior alignment together.

## Testing Requirements

This is a design/reference story. For this closure pass, run the targeted sprint ledger regression test in the repo venv because the story status and contract references were reconciled alongside the sprint tracker.

## Project Structure Notes

- New reference: `skills/bmad-agent-content-creator/references/cluster-narrative-arc-schema.md`
- Modified support files:
  - `skills/bmad-agent-content-creator/SKILL.md`
  - `skills/bmad-agent-content-creator/references/cluster-decision-criteria.md`
  - `skills/bmad-agent-content-creator/references/template-segment-manifest.md`

## References

- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md)
- [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md)
- [20a-2-interstitial-brief-specification-standard.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-2-interstitial-brief-specification-standard.md)
- [cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-decision-criteria.md)
- [interstitial-brief-specification.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/interstitial-brief-specification.md)
- [template-segment-manifest.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/template-segment-manifest.md)

## File List

- `skills/bmad-agent-content-creator/references/cluster-narrative-arc-schema.md`
- `skills/bmad-agent-content-creator/SKILL.md`
- `skills/bmad-agent-content-creator/references/cluster-decision-criteria.md`
- `skills/bmad-agent-content-creator/references/template-segment-manifest.md`

## Dev Agent Record

### Completion Notes List

Defined the narrative arc schema, clarified canonical beat order, aligned the story with the manifest template's existing `master_behavioral_intent` field, and closed the review lane as part of the 20A checkpoint reconciliation.

## Status

done
