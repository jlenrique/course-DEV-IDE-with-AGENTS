# Story 20c-3: Source-to-Density Intelligence

**Epic:** 20c - Cluster Intelligence Expansion & Iteration
**Status:** ready-for-dev
**Sprint key:** `20c-3-source-to-density-intelligence`
**Added:** 2026-04-12
**Depends on:** [20c-2-content-aware-template-selection-logic.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-2-content-aware-template-selection-logic.md), [20b-1-irene-pass1-cluster-planning-implementation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20b-1-irene-pass1-cluster-planning-implementation.md)

## Story

As Irene,
I want content-aware density mapping that reads the source material structure and determines which sections deserve deep cluster treatment, which get light treatment, and which stay flat,
So that cluster density is driven by pedagogical importance and content complexity — not a uniform config knob.

## Context

Currently `cluster_density` is a presentation-level config (sparse/default/rich). This is a blunt instrument. Real presentations have sections of varying importance: a foundational framework might deserve a 3-interstitial deep-dive, while a quick transition topic deserves nothing. This story makes density mapping intelligent.

## Acceptance Criteria

**AC-1: Source Material Analysis**
Irene reads the source bundle and identifies per-section:
- **Concept centrality:** Is this a core concept (LO-anchored) or supporting material?
- **Complexity gradient:** How much unpacking does this section need?
- **Prerequisite chains:** Does understanding this section depend on understanding a prior one?
- **Novelty level:** Is this new to the audience (expert vs. novice distinction from course context)?
- **Assessment alignment:** Is this section tested/assessed? (Higher weight if yes)

**AC-2: Density Distribution**
Instead of uniform density, produce a per-slide density recommendation:
- `cluster_depth: none` — flat slide, no clustering
- `cluster_depth: light` — 1 interstitial (quick-punch or cognitive-reset)
- `cluster_depth: moderate` — 2 interstitials (most templates)
- `cluster_depth: deep` — 3 interstitials (deep-dive, evidence-build, data-walkthrough)

**AC-3: Density Budget**
- Total cluster budget respects operator's overall density preference (sparse/default/rich) as a constraint
- Within that budget, the distribution is content-driven
- Example: `default` density might allow 3-5 clusters, but the system decides WHICH 3-5 topics deserve them
- High-centrality, high-complexity topics get deep treatment first; budget allocation works downward

**AC-4: Source Structure Signals**
Parse source material for structural signals:
- Heading hierarchy (H2 = major section, H3 = subsection)
- Bullet count and nesting (dense bullets = high complexity)
- Image/diagram references (visual content = visual decomposition opportunity)
- Definition lists / glossary terms (terminology density)
- Citation density (research-heavy sections)
- Explicit emphasis markers (bold, callout boxes in source)

**AC-5: Learning Objective Weighting**
- Slides that directly serve a stated learning objective get density priority
- Slides that are contextual or transitional get lower priority
- LO coverage from Irene's existing Pass 1 analysis feeds into density decisions

**AC-6: Output Integration**
- Per-slide density recommendation included in the cluster plan (G1.5 reviewable)
- Operator can override any individual recommendation
- Density recommendations feed into template selection (20c-2): deep → complex templates, light → simple templates

## Tasks / Subtasks

- [ ] Task 1: Implement source material analysis
  - [ ] 1.1: Read source bundle and extract per-section structure
  - [ ] 1.2: Score concept centrality from LO mapping
  - [ ] 1.3: Score complexity from structural signals (bullet depth, definition density, citation count)
  - [ ] 1.4: Score novelty from audience assumption (course_context.yaml)
  - [ ] 1.5: Score assessment alignment from source or PRD

- [ ] Task 2: Implement density distribution algorithm
  - [ ] 2.1: Rank slides by composite score (centrality + complexity + novelty + assessment)
  - [ ] 2.2: Allocate density budget top-down (highest-scoring slides get deepest treatment)
  - [ ] 2.3: Apply operator overall density constraint as budget cap
  - [ ] 2.4: Output per-slide cluster_depth recommendation

- [ ] Task 3: Integrate with existing cluster planning
  - [ ] 3.1: Replace uniform cluster_density config with per-slide cluster_depth
  - [ ] 3.2: Feed cluster_depth into template selection (20c-2)
  - [ ] 3.3: Include density rationale in cluster plan for G1.5 review

- [ ] Task 4: Testing and iteration
  - [ ] 4.1: Run against C1-M1 source content — evaluate density distribution
  - [ ] 4.2: Compare content-driven density vs. uniform density output
  - [ ] 4.3: Validate LO-weighted density prioritizes the right topics

## Dev Notes

### Iteration Expected

The scoring weights (how much centrality matters vs. complexity vs. novelty) will need tuning across multiple runs. Start with equal weights, then adjust based on operator feedback.

### Backward Compatibility

The global `cluster_density` config (sparse/default/rich) becomes the **budget constraint**, not the per-slide decision. Existing behavior preserved: if per-slide intelligence is disabled, fall back to uniform density.

## References

- [course_context.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/state/config/course_context.yaml) — Audience/course metadata
- [cluster-density-controls.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/cluster-density-controls.md) — Current density controls
