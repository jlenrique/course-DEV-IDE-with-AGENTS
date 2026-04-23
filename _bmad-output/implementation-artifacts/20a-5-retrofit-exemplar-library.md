# Story 20a.5: Retrofit Exemplar Library

**Epic:** 20A - Irene Cluster Intelligence - Design & Specification
**Status:** review
**Sprint key:** `20a-5-retrofit-exemplar-library`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [20a-1-cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-1-cluster-decision-criteria.md), [20a-2-interstitial-brief-specification-standard.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-2-interstitial-brief-specification-standard.md), [20a-3-cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-3-cluster-narrative-arc-schema.md), [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md)

> **Unblocked:** MVP gate passed (Storyboard A trial, 2026-04-11). Real cluster production data is now available from the trial run. Execute in Wave 2 iteration loop alongside Epic 20c template/intelligence work.

## Story

As Irene,
I want a library of exemplar cluster plans drawn from existing C1-M1 production slides,
So that when I begin planning clusters in Pass 1, I have concrete reference patterns — not just abstract rules — showing what strong cluster decisions, briefs, and arc assignments look like for this specific course's content and visual style.

## Acceptance Criteria

**Given** Irene needs concrete cluster patterns grounded in real C1-M1 content
**When** this story is executed after the Storyboard A gate passes
**Then** a cluster exemplar library must exist with 3–5 complete exemplar entries drawn from actual C1-M1 slide briefs

**And** each exemplar must be a complete cluster plan, including:
- The source slide (run ID, slide number, slide topic)
- Decision framework scores (concept density / visual complexity / pedagogical weight / operator input) per the 20a-1 criteria
- Rationale for why this slide is a strong cluster head
- `interstitial_type` assignments per interstitial using canonical vocabulary (`reveal | emphasis-shift | bridge-text | simplification | pace-reset`)
- Complete interstitial brief for each interstitial (all 6 fields from 20a-2 standard)
- `narrative_arc` sentence and `master_behavioral_intent` per the 20a-3 schema
- `develop_type` assignments where applicable

**And** at least one exemplar must be drawn from a post-Storyboard-A run — i.e., a cluster plan that was **actually executed through Gary and judged at review** — so the exemplar library is grounded in production reality, not pure speculation

**And** the exemplars must be stored in a reference file accessible to Irene during Pass 1 cluster planning

**And** a pointer to the exemplar library must be added to Irene's `patterns.md` sidecar if the sidecar is initialized by the time this story runs

**And** the exemplars must include at least one entry that shows a **strong candidate rejected** (a slide that scored high on criteria but was suppressed for a legitimate reason — pacing, density balance, or operator override), so Irene learns constraint as well as selection

## Tasks / Subtasks

- [x] Task 1: Analyze existing C1-M1 slide briefs for cluster candidates (AC: 1-2)
  - [x] 1.1: Load `g2-slide-brief.md` from all available C1-M1 production runs (see paths in Dev Notes)
  - [x] 1.2: If Storyboard A has already run: load cluster output artifacts from the first clustered run and prioritize those as exemplar sources
  - [x] 1.3: Apply the 20a-1 decision framework to each slide — score concept density, visual complexity, pedagogical weight
  - [x] 1.4: Identify 5-7 strong candidates, then select 3-5 for full exemplar treatment; document the full candidate list with scores
- [x] Task 2: Write complete exemplar cluster plans (AC: 2-3)
  - [x] 2.1: For each selected exemplar, write the full cluster plan using all 20a-2 brief fields and the 20a-3 arc schema (see format in Dev Notes)
  - [x] 2.2: Include at least one exemplar drawn from actual Gary output (post-run), not just the slide brief alone
  - [x] 2.3: Write one "rejected strong candidate" entry showing why a high-scoring slide was not clustered
- [x] Task 3: Store exemplars and update Irene references (AC: 4-5)
  - [x] 3.1: Create `skills/bmad-agent-content-creator/references/cluster-exemplars.md` with all exemplar entries
  - [x] 3.2: Update [SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/SKILL.md) to add `CE` capability row (cluster exemplar library)
  - [x] 3.3: If `_bmad/memory/content-creator-sidecar/` exists, append a pointer to the exemplar reference in `patterns.md`; if the sidecar does not exist, load `./references/init.md` to initialize it first, then append

## Dev Notes

### MVP Deferral — Execution Timing

Per `interstitial-cluster-mvp-c1m1-storyboard-a.md`, this story is deferred from the first Storyboard-A spike. The reason is sound: exemplars written purely from slide briefs (before any cluster has been generated and reviewed) are speculative. They show what a cluster *should* look like, but they cannot show whether the cluster *worked visually* — which is the thing that makes exemplars valuable.

**Ideal execution path:**
1. Epic 20b + Epic 21 Stories 1-2 complete → first clustered C1-M1 run through Gary
2. Storyboard A human review gate passes
3. **This story executes** — using the reviewed cluster output as the primary exemplar source, supplemented by retrospective analysis of earlier slides

If this story is executed before a cluster run exists, Task 2.2 must note that all exemplars are pre-run and should be validated against the first real cluster output.

### Source Artifacts for Analysis

Available C1-M1 production runs (most recent first):
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409/g2-slide-brief.md` — 15 slides, production quality preset, `double_dispatch: true`
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409-motion/g2-slide-brief.md` — motion-enabled variant
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260403/g2-slide-brief.md` — earlier run
- `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260406-motion/g2-slide-brief.md` — motion variant

Also check each bundle for `gary-slide-content.json` and `gary-fidelity-slides.json` — these carry mode assignments and fidelity classifications that help assess visual complexity.

**From preliminary analysis of the 20260409 run** (first 4 slides of g2-slide-brief.md):

| Slide | Topic | Preliminary Assessment |
|-------|-------|----------------------|
| 1 | Welcome & Modern Clinician's Dilemma | Likely flat — motion-first (literal-visual + video); interstitials compete with motion |
| 2 | Innovator's Hero's Journey (roadmap) | Moderate — 3 waypoints could be progressively disclosed; assess concept density |
| 3 | Lineage of Physician Innovators (2×2 grid) | **Strong candidate** — 4 distinct innovators, high visual complexity, each quadrant is a distinct sub-concept |
| 4 | Hero's Journey (visual map) | Likely flat — similar to Slide 2; may be redundant cluster |

Read the full 15-slide brief to complete the candidate analysis.

### Exemplar Format

Each entry in `cluster-exemplars.md` must follow this structure:

```markdown
## Exemplar [N]: [Slide Topic]

**Source:** RUN_ID [run_id], Slide [number]
**Cluster Decision Scores:**
- Concept Density: High/Medium/Low — [brief rationale]
- Visual Complexity: High/Medium/Low — [brief rationale]
- Pedagogical Weight: High/Medium/Low — [brief rationale]
- Operator Input: Support/Neutral/Oppose

**Decision:** [Full cluster (2-3 interstitials) | Single interstitial | Rejected — see rationale]
**Rejection Rationale:** (if rejected) [why it was not clustered despite high score]

**Cluster Plan:**
- `narrative_arc`: "[one-sentence arc]"
- `master_behavioral_intent`: [value]
- `cluster_interstitial_count`: [1-3]

**Interstitial 1:**
- `cluster_position`: develop | tension | resolve
- `develop_type`: deepen | reframe | exemplify (if develop)
- `interstitial_type`: reveal | emphasis-shift | bridge-text | simplification | pace-reset
- `isolation_target`: "[specific element from head]"
- `visual_register_constraint`: ["element to suppress/remove"]
- `content_scope`: minimal | focused | reduced
- `narration_burden`: low | medium | high
- `relationship_to_head`: zoom | isolate | simplify | reframe | rest

**Interstitial 2:** (if applicable)
[same fields]

**Production Notes:** (if post-run) [what the cluster actually looked like in Gary output; what worked or didn't]
```

### Sidecar Initialization

If `_bmad/memory/content-creator-sidecar/` does not exist when this story runs, load `skills/bmad-agent-content-creator/references/init.md` to initialize it. The sidecar structure is:
- `index.md` — active production context (create with current run context)
- `patterns.md` — learned patterns (append cluster exemplar pointer here)
- `chronology.md` — production history
- `access-boundaries.md` — access control rules

The exemplar library itself lives at `skills/bmad-agent-content-creator/references/cluster-exemplars.md` — a reference file, not a sidecar file. The sidecar `patterns.md` gets a pointer only.

### Previous Story Intelligence

- **20a-1 through 20a-4** are all done — all four frameworks (decision criteria, brief standard, arc schema, density controls) must be applied in creating these exemplars. The exemplars are the integration test of all four frameworks working together.
- **The rejected-candidate exemplar** is specifically important for 20a-1's decision quality guardrails: "A cluster candidate should have enough substance to support multiple explanatory beats... the framework must help avoid decorative interstitials."
- This story creates the only ground-truth artifact in Epic 20A — everything else defines rules; this story shows them applied.

## Testing Requirements

No automated tests. This is a research/documentation story. Validate by:
1. Each exemplar entry passes a self-consistency check: does the `interstitial_type` match what the `isolation_target` and `visual_register_constraint` are doing?
2. Each `narrative_arc` sentence follows the "From [start] to [end] through [mechanism]" format.
3. Each `narration_burden` value is consistent with the `interstitial_type` (e.g., `reveal` should be `low`, `bridge-text` should be `high`).

## Project Structure Notes

- **New file:** `skills/bmad-agent-content-creator/references/cluster-exemplars.md`
- **Modified files:**
  - `skills/bmad-agent-content-creator/SKILL.md` — add `CE` capability row
  - `_bmad/memory/content-creator-sidecar/patterns.md` — append exemplar pointer (initialize sidecar first if needed)

## References

- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 20a.5 definition
- [interstitial-cluster-mvp-c1m1-storyboard-a.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/interstitial-cluster-mvp-c1m1-storyboard-a.md) — MVP deferral rationale and Storyboard A gate criteria
- [cluster-decision-criteria.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-decision-criteria.md) — decision framework to apply retroactively
- [interstitial-brief-specification.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/interstitial-brief-specification.md) — brief field standard for exemplar entries
- [cluster-narrative-arc-schema.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-narrative-arc-schema.md) — arc and master intent schema for exemplar entries
- [cluster-density-controls.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-density-controls.md) — density controls (relevant to operator input scoring)
- [memory-system.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/memory-system.md) — sidecar structure and initialization rules
- [g2-slide-brief.md — latest run](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260409/g2-slide-brief.md) — primary source for candidate analysis

## File List

- skills/bmad-agent-content-creator/references/cluster-exemplars.md (new)
- skills/bmad-agent-content-creator/SKILL.md (modified)
- _bmad/memory/bmad-agent-content-creator/MEMORY.md (modified; sanctum pointer entry)

## Dev Agent Record

### Agent Model Used

GPT-5.3-Codex

### Debug Log

- Loaded full sprint status and selected first ready-for-dev key in order: `20a-5-retrofit-exemplar-library`.
- Ingested post-Storyboard-A run artifacts from `apc-c1m1-tejal-20260419b-motion` (`cluster-plan.yaml`, `cluster-plan-review.md`, `gary-slide-content.json`, `gary-cluster-outputs.json`).
- Ingested supporting run artifacts from `apc-c1m1-tejal-20260409`.
- Authored `cluster-exemplars.md` with 5 exemplar entries (4 selected + 1 rejected strong candidate) and a 7-slide scoring matrix.
- Added CE capability mention to Irene SKILL capability router section.
- Added exemplar pointer to Irene sanctum memory (`Cluster Patterns` section).

### Completion Notes List

- Built a concrete C1-M1 exemplar library grounded in post-run Gary outputs and cluster gate review evidence.
- Included full six-field interstitial contracts, narrative arcs, and master behavioral intents for each selected exemplar.
- Added one rejected strong-candidate exemplar to capture selection constraints and operator override dynamics.
- Completed manual consistency checks required by story testing notes:
  - interstitial type vs isolation/constraint alignment
  - narrative arc sentence format (`From ... to ... through ...`)
  - narration burden alignment (reveal=low, bridge-text=high)

### File List

- skills/bmad-agent-content-creator/references/cluster-exemplars.md (new)
- skills/bmad-agent-content-creator/SKILL.md (modified)
- _bmad/memory/bmad-agent-content-creator/MEMORY.md (modified)

## Change Log

- 2026-04-22: Implemented Story 20a.5 deliverables (retrofit exemplar library, Irene capability router update, sanctum pointer update).

## Status

review

## Completion Status

Retrofit exemplar library completed using post-Storyboard-A production artifacts and validated against story-specific documentation checks.
