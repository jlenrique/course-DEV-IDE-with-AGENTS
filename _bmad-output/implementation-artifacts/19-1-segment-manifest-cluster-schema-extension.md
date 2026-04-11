# Story 19.1: Segment Manifest Cluster Schema Extension

**Epic:** 19 - Interstitial Slide Cluster Schema & Manifest Foundation
**Status:** ready-for-dev
**Sprint key:** `19-1-segment-manifest-cluster-schema-extension`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [interstitial-cluster-mvp-c1m1-storyboard-a.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/interstitial-cluster-mvp-c1m1-storyboard-a.md), existing segment-manifest contract from Stories 13.3 and 14.2

## Story

As a production orchestrator,
I want the segment manifest to express clustered slide structure without breaking existing flat runs,
So that Irene, Gary, validators, and storyboard review can carry a three-cluster C1M1 presentation through the pipeline in a backward-compatible way.

## Acceptance Criteria

**Given** the current Pass 2 manifest schema is the SSOT for narrated-slide production  
**When** clustered presentations are introduced  
**Then** each manifest segment may include these additive fields:

- `cluster_id` (string, nullable; `null` for non-clustered runs)
- `cluster_role` enum: `head | interstitial`
- `cluster_position` enum: `establish | develop | tension | resolve`
- `develop_type` enum (optional when `cluster_position == develop`): `deepen | reframe | exemplify`
- `parent_slide_id` (string, nullable; set on interstitials and references the head slide)
- `interstitial_type` enum: `reveal | emphasis-shift | bridge-text | simplification | pace-reset`
- `isolation_target` (string; specific element surfaced from the head slide)
- `narrative_arc` (string; one-sentence cluster arc, typically set on the head and inherited conceptually by cluster members)
- `cluster_interstitial_count` (integer; recommended count for the cluster, 1-3)
- `double_dispatch_eligible` (boolean; default `true`, set `false` for interstitials in the MVP)

**And** all cluster fields remain optional or nullable so existing non-clustered manifests remain valid  
**And** the canonical manifest template is updated with field descriptions and one clustered example snippet  
**And** migration notes make clear that this story adds representational capacity only; Story 19.3 owns gate contract changes and Story 19.4 owns cluster-aware validator enforcement  
**And** current manifest consumers continue to load non-clustered and clustered manifests without breaking on the new fields

## Tasks / Subtasks

- [x] Task 1: Extend the canonical manifest schema reference (AC: 1-4)
   - [x] 1.1: Add the cluster fields to [template-segment-manifest.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/template-segment-manifest.md)
   - [x] 1.2: Document field semantics, nullability, and default expectations
   - [x] 1.3: Add a small clustered example snippet showing one head and one interstitial row
- [x] Task 2: Preserve backward compatibility explicitly (AC: 2, 5)
   - [x] 2.1: Confirm the manifest template still reads cleanly for current non-clustered narrated and motion workflows
   - [x] 2.2: Add migration notes stating that old manifests remain valid with all cluster fields absent
- [x] Task 3: Check current consumers for tolerance of additive fields (AC: 5)
   - [x] 3.1: Review [validate-irene-pass2-handoff.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py) for assumptions that would reject unknown manifest keys
   - [x] 3.2: Review [generate-storyboard.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/generate-storyboard.py) for assumptions that would break when clustered manifests appear
   - [x] 3.3: Review any manifest round-trip helpers or inspection-pack scripts for silent field stripping
- [x] Task 4: Add regression coverage for additive schema tolerance (AC: 5)
   - [x] 4.1: Add or extend tests proving existing manifest-loading paths tolerate the new cluster fields without failure
   - [x] 4.2: Add one regression fixture covering a clustered manifest row and one covering an unchanged flat manifest row

## Dev Notes

### Scope Boundary

This story is **schema foundation only**. Do not prematurely implement:

- cluster-aware G4 narration rules
- Storyboard A grouping behavior
- Storyboard B hydration changes
- clustered assembly or ElevenLabs behavior
- interstitial re-dispatch or retry policy

Those belong to later stories in Epics 19, 22, 23, and 24.

### Existing Infrastructure To Reuse

- [template-segment-manifest.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/template-segment-manifest.md) is the manifest SSOT and must remain the canonical schema reference.
- Story 13.3 already extended the manifest with `visual_references[]`; Story 14.2 extended it with motion fields. Follow the same additive-extension pattern rather than inventing a parallel cluster schema.
- [validate-irene-pass2-handoff.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py) currently validates content completeness and motion alignment. This story should preserve compatibility; stricter cluster enforcement lands in 19.4.
- [generate-storyboard.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/generate-storyboard.py) already reads manifest segments opportunistically. Do not force Storyboard A cluster rendering here; just make sure clustered manifests do not break current extraction paths.

### Field Semantics Guardrails

- `cluster_role` is about membership role in the cluster: `head` or `interstitial`.
- `cluster_position` is about narrative position in the cluster arc: `establish`, `develop`, `tension`, `resolve`.
- `develop_type` is only valid when `cluster_position == develop`.
- `parent_slide_id` should point back to the head slide identifier for interstitial rows.
- `double_dispatch_eligible` defaults to `true` for backward compatibility; clustered MVP interstitial rows will later set it to `false`.
- `cluster_interstitial_count` is the planned count for the cluster, not a computed count from realized rows.

### C1M1 MVP Context

The immediate target is the three-cluster Storyboard-A MVP captured in [interstitial-cluster-mvp-c1m1-storyboard-a.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/interstitial-cluster-mvp-c1m1-storyboard-a.md). This schema must support:

- exactly 3 clusters in one C1M1 presentation
- one head plus 1-3 interstitials per cluster
- explicit beginning, middle, and end structure
- Storyboard-A-only evaluation before any Storyboard B work begins

### Previous Story Intelligence

Relevant precedents:

- [13-3-segment-manifest-visual-references.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/13-3-segment-manifest-visual-references.md): use the same additive manifest-extension style and preserve downstream traceability rather than creating a detached side schema.
- [14-2-segment-manifest-motion-extensions.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/14-2-segment-manifest-motion-extensions.md): motion fields established the pattern for optional workflow-specific manifest fields. Cluster fields should follow that precedent exactly: additive, nullable, and backward-compatible.

### Recent Git Intelligence

Recent commits show active doc and workflow refinement rather than a schema refactor. Keep this story narrow and avoid dragging in unrelated prompt-pack edits:

- `9453855` `fix: correct typographical errors in course content agent guidelines`
- `22e34f9` `docs: BMAD session wrapup - handoff, next-session, agent env, project context`
- `4dec804` `feat: add Desmond specialist, prompt 14.5, and APP handoff docs`

## Testing Requirements

- Preserve behavior for current non-clustered manifests.
- Add one clustered-manifest fixture exercising the new fields.
- If tests are added to Marcus manifest consumers, run them through the repo venv:

```powershell
.\.venv\Scripts\python.exe -m pytest skills/bmad-agent-marcus/scripts/tests
```

- If no direct parser tests exist for a touched consumer, create the smallest targeted regression test instead of relying on manual inspection.

## Project Structure Notes

- Primary schema reference to modify:
  - [template-segment-manifest.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/template-segment-manifest.md)
- Likely consumer tolerance checks:
  - [validate-irene-pass2-handoff.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py)
  - [generate-storyboard.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/generate-storyboard.py)
  - [build-pass2-inspection-pack.py](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-marcus/scripts/build-pass2-inspection-pack.py)

## References

- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md)
- [interstitial-cluster-mvp-c1m1-storyboard-a.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/interstitial-cluster-mvp-c1m1-storyboard-a.md)
- [13-3-segment-manifest-visual-references.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/13-3-segment-manifest-visual-references.md)
- [14-2-segment-manifest-motion-extensions.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/14-2-segment-manifest-motion-extensions.md)
- [template-segment-manifest.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/template-segment-manifest.md)

## Dev Agent Record

### Debug Log

- 2026-04-11: Started implementation of 19-1
- 2026-04-11: Added cluster fields to template-segment-manifest.md schema
- 2026-04-11: Added field reference table and migration notes
- 2026-04-11: Added UC8 clustered presentation example
- 2026-04-11: Reviewed consumer scripts for tolerance - all use yaml.safe_load and ignore unknown fields
- 2026-04-11: Marked all tasks complete
- 2026-04-11: Code review round 1 — fixed YAML parse error in workflow-templates.yaml, updated file list
- 2026-04-11: Code review round 2 — fixed cluster test KeyError (segments on disk not in payload), renamed test-validate-irene-pass2-handoff.py to underscores for pytest collection (surfaced 36 previously uncollected tests), 120 tests pass

### Completion Notes

Successfully extended the canonical segment manifest schema with cluster fields. All fields are additive and nullable, preserving backward compatibility. Added comprehensive field documentation, migration notes, and a clustered example. Verified that existing manifest consumers tolerate unknown fields without breaking.

### File List

- skills/bmad-agent-content-creator/references/template-segment-manifest.md (modified)
- skills/bmad-agent-marcus/SKILL.md (modified)
- skills/bmad-agent-marcus/references/workflow-templates.yaml (modified)
- skills/bmad-agent-marcus/references/cluster-manifest-reference.md (new)
- skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py (renamed + modified — cluster regression tests + KeyError fix)

### Change Log

- feat: extend segment manifest schema with cluster fields (2026-04-11)
- fix: repair cluster regression test KeyError and rename test file for pytest collection (2026-04-11)

### Review Findings

- [x] [Review][Patch] YAML parse failure in workflow-templates.yaml — indentation mismatch on gate-4 and new cluster template [workflow-templates.yaml:318]
- [x] [Review][Patch] Story File List incomplete — missing Marcus SKILL.md, workflow-templates.yaml, cluster-manifest-reference.md
- [x] [Review][Patch] Cluster regression test KeyError: 'segments' — payload dict lacks segments key, must load from disk manifest [test_validate_irene_pass2_handoff.py:1717]
- [x] [Review][Defer] Hyphenated test filename not collected in directory scan — renamed to underscores, surfaced 36 previously uncollected tests

## Status

done

## Completion Status

Ultimate context engine analysis completed - comprehensive developer guide created for the first interstitial-cluster foundation story.
