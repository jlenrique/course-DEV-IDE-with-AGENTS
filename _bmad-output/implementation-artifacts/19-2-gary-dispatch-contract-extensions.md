# Story 19-2: Gary Dispatch Contract Extensions

**Epic:** 19 - Cluster Schema & Manifest Foundation
**Status:** ready-for-dev
**Sprint key:** `19-2-gary-dispatch-contract-extensions`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [19-1-segment-manifest-cluster-schema-extension.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/19-1-segment-manifest-cluster-schema-extension.md)

## Story

As Gary,
I want my machine artifact outputs to carry cluster metadata,
So that downstream agents (Irene Pass 2, Compositor, Fidelity Assessor) can reconstruct cluster structure without re-parsing the segment manifest.

## Acceptance Criteria

**Given** Gary dispatches slides for clustered presentations
**When** Gary produces machine artifacts
**Then** all artifacts must carry cluster metadata for downstream reconstruction

**And** `gary-slide-content.json` must include per-slide cluster fields:
- `cluster_id` (string, nullable)
- `cluster_role` (enum: head | interstitial)
- `parent_slide_id` (string, nullable — set for interstitials)

**And** `gary-fidelity-slides.json` must include `cluster_role` per slide, with interstitials inheriting the head's fidelity classification

**And** `gary-outbound-envelope.yaml` must include a `clusters[]` section with per-cluster metadata:
- `cluster_id`
- `interstitial_count` (integer 1-3)
- `narrative_arc` (string)

**And** `gary-diagram-cards.json` must exclude diagram cards for interstitial slides (carve-out)

**And** all extensions must be backward-compatible — non-clustered runs produce identical artifacts

**And** Gary's SKILL.md must be updated to document the cluster metadata extensions

## Tasks / Subtasks

- [ ] Task 1: Extend gary-slide-content.json schema
  - [ ] 1.1: Add cluster_id, cluster_role, parent_slide_id fields to slide entry schema
  - [ ] 1.2: Update Gary prompt templates to emit cluster metadata in JSON output
  - [ ] 1.3: Test backward compatibility — non-clustered runs unchanged

- [ ] Task 2: Extend gary-fidelity-slides.json schema
  - [ ] 2.1: Add cluster_role field to slide entry schema
  - [ ] 2.2: Implement inheritance logic: interstitials copy head's fidelity classification
  - [ ] 2.3: Update fidelity classification prompt to handle cluster roles

- [ ] Task 3: Extend gary-outbound-envelope.yaml schema
  - [ ] 3.1: Add clusters[] array with cluster metadata fields
  - [ ] 3.2: Update envelope generation to aggregate cluster data from slide brief
  - [ ] 3.3: Validate envelope schema against cluster manifest

- [ ] Task 4: Implement diagram cards carve-out
  - [ ] 4.1: Modify diagram card generation to skip interstitial slides
  - [ ] 4.2: Update diagram card schema documentation
  - [ ] 4.3: Test that heads still receive diagram cards normally

- [ ] Task 5: Update Gary SKILL.md and references
  - [ ] 5.1: Document cluster metadata extensions in SKILL.md
  - [ ] 5.2: Update reference documents with new schema fields
  - [ ] 5.3: Add backward compatibility notes

## Dev Notes

### Scope Boundary

This story extends **Gary's output contracts only**. It does not implement:

- Irene Pass 1 cluster planning (Epic 20b)
- Cluster-aware prompt engineering (Epic 21)
- Downstream consumption of cluster metadata (Irene Pass 2, Compositor, Fidelity Assessor)

This is pure schema extension work — the foundation for downstream stories.

### Dependency on 19-1

19-1 defines the segment manifest cluster schema. This story assumes that schema exists and Gary can read cluster metadata from the slide brief input.

### Backward Compatibility

All cluster fields are nullable/optional. Non-clustered runs must produce identical artifacts to pre-Epic-19 behavior.

### Cluster Metadata Flow

```
Slide Brief (from Irene) → Gary Dispatch → Machine Artifacts (with cluster metadata)
                                      ↓
                            Downstream Agents (Irene P2, Compositor, Fidelity)
```

### Risk: Fidelity Classification Inheritance

Interstitials inheriting head fidelity is a design decision. If interstitials need independent classification (e.g., for visual-only slides), this may need revision in Epic 21.

### Testing

- Regression test: C1-M1 non-clustered run produces identical artifacts
- Forward test: Clustered run includes all cluster metadata fields
- Schema validation: All artifacts pass JSON/YAML schema checks

## Project Structure Notes

- **Modified files:**
  - `skills/bmad-agent-gamma/SKILL.md` — document extensions
  - `skills/bmad-agent-gamma/references/` — update schema docs
  - Gary prompt templates (location TBD)

## References

- [19-1-segment-manifest-cluster-schema-extension.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/19-1-segment-manifest-cluster-schema-extension.md) — defines cluster schema Gary extends
- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 19.2 definition
- [skills/bmad-agent-gamma/SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-gamma/SKILL.md) — current Gary contracts

## File List

- _bmad-output/implementation-artifacts/19-2-gary-dispatch-contract-extensions.md (this file)
- skills/bmad-agent-gamma/SKILL.md (modified)
- skills/bmad-agent-gamma/references/ (modified schema docs)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6[1m]

### Debug Log

### Completion Notes List

- ✅ Story file created with AC, tasks, dev notes
- ✅ Dependencies and scope boundaries defined
- ✅ Backward compatibility requirements specified
- ✅ Risk assessment for fidelity inheritance

### File List

## Status

ready-for-dev

## Completion Status

Story 19-2 ready for development — Gary dispatch contract extensions planned and documented.