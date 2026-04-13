# Story 20c-5: Presentation Architect Specialist Agent

**Epic:** 20c - Cluster Intelligence Expansion & Iteration
**Status:** ready-for-dev
**Sprint key:** `20c-5-presentation-architect-agent`
**Added:** 2026-04-12
**Depends on:** [20c-1-cluster-structure-template-library.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-1-cluster-structure-template-library.md), [20c-4-master-arc-cluster-arc-composition.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20c-4-master-arc-cluster-arc-composition.md)

## Story

As Marcus (orchestrator),
I want a Presentation Architect specialist agent that Irene or Marcus can delegate to for structural presentation design decisions,
So that the complexity of template selection, arc composition, and density mapping is handled by a purpose-built agent rather than overloading Irene's already broad responsibilities.

## Context

Irene's current scope: lesson planning (Pass 1), narration writing (Pass 2), pedagogical framework, cluster planning, bridge design, source interpretation. Adding template selection, content signal analysis, master arc composition, and density intelligence to Irene risks making her prompt too broad — a "god agent" problem. 

A **Presentation Architect** agent separates STRUCTURAL design (what gets emphasized, how clusters compose, what templates fit) from CONTENT creation (what the narration says, how briefs are written). Think of it as: the Architect designs the blueprint; Irene writes the content that fills it.

## Agent Design

### Identity

| Field | Value |
|-------|-------|
| **name** | `bmad-agent-presentation-architect` |
| **displayName** | Pax |
| **title** | Presentation Structure Architect |
| **icon** | 🏛️ |
| **role** | Designs the structural blueprint of clustered presentations: template selection, density mapping, master arc composition, pacing, and cluster sequencing |

### Communication Style

Thinks in structures and patterns. Speaks in architectural metaphors — blueprints, load-bearing walls, foundations, keystones. Concise and spatial. Sees the presentation as a building to be designed, not a story to be told (that's Sophia's domain) or content to be created (that's Irene's domain).

### Principles

- Structure serves pedagogy — every structural decision has a learning rationale
- Variety is not randomness — template variation follows a design logic
- Pacing is architecture — cognitive load management is a structural concern
- The master arc is the foundation; clusters are rooms; interstitials are furniture

### Capabilities

1. **Template Selection** — analyzes content signals, scores templates, recommends per-cluster template
2. **Density Mapping** — reads source material structure, recommends per-slide cluster depth
3. **Arc Composition** — designs master arc, assigns cluster arc_roles, defines stitching intentions
4. **Pacing Design** — evaluates presentation-level timing balance, flags pacing issues
5. **Structural Review** — reviews Irene's cluster plan and suggests structural improvements

## Acceptance Criteria

**AC-1: Agent Creation**
- Agent skill directory: `skills/bmad-agent-presentation-architect/`
- SKILL.md with identity, capabilities, references, protocols
- Memory sidecar at `_bmad/memory/presentation-architect-sidecar/`

**AC-2: Delegation Protocol**
- Marcus can delegate structural design to Pax before Irene starts cluster planning
- Irene can request Pax consultation during Pass 1 for complex presentations
- Pax produces a **structural blueprint** that Irene consumes:
  - Per-slide cluster_depth recommendation
  - Per-cluster template_id recommendation
  - Master arc with cluster arc_roles
  - Stitching intentions at each boundary
  - Pacing timeline

**AC-3: Handoff Contract**
- Pax's output is a `structural-blueprint.yaml` (or .md) that Irene reads as input
- Blueprint format is machine-parseable (YAML sections) + human-reviewable (markdown narrative)
- Operator reviews the blueprint at a new structural review checkpoint (between source analysis and cluster planning)

**AC-4: Lane Matrix Integration**
- Pax added to the lane matrix (Epic 4A) with explicit boundaries:
  - CAN: structural design, template selection, density mapping, arc composition
  - CANNOT: write narration, generate slide briefs, dispatch to tools, modify fidelity contracts
  - CONSULTS: Sophia (narrative framework), Irene (content expertise), operator (preferences)

**AC-5: Learning and Iteration**
- Pax maintains a memory sidecar for structural design patterns that work/fail
- After each production run, structural review feeds into Pax's pattern library
- Pax's template scoring weights evolve based on tracked outcomes

## Tasks / Subtasks

- [ ] Task 1: Create agent infrastructure
  - [ ] 1.1: Create `skills/bmad-agent-presentation-architect/` directory
  - [ ] 1.2: Write SKILL.md with identity, capabilities, references, protocols
  - [ ] 1.3: Create memory sidecar directory and init.md
  - [ ] 1.4: Define structural-blueprint output format (YAML + markdown)

- [ ] Task 2: Implement core capabilities
  - [ ] 2.1: Template selection capability (consumes 20c-1 library, 20c-2 logic)
  - [ ] 2.2: Density mapping capability (consumes 20c-3 intelligence)
  - [ ] 2.3: Arc composition capability (consumes 20c-4 rules)
  - [ ] 2.4: Pacing design capability (new — evaluates timing balance)

- [ ] Task 3: Implement delegation protocol
  - [ ] 3.1: Marcus → Pax delegation (pre-Irene structural design)
  - [ ] 3.2: Irene → Pax consultation (mid-planning query)
  - [ ] 3.3: Structural blueprint handoff format
  - [ ] 3.4: Operator structural review checkpoint

- [ ] Task 4: Lane matrix and governance
  - [ ] 4.1: Add Pax to lane matrix
  - [ ] 4.2: Define CAN/CANNOT boundaries
  - [ ] 4.3: Define consultation protocols (Sophia, Irene, operator)

- [ ] Task 5: Testing
  - [ ] 5.1: Agent QA gate (existing 4A-4 pattern)
  - [ ] 5.2: Run Pax against C1-M1 source content — evaluate structural blueprint
  - [ ] 5.3: Compare Pax-designed structure vs. Irene ad-hoc structure

## Dev Notes

### Agent vs. Capability

The decision to make this an agent (vs. a capability within Irene's SKILL.md) depends on complexity. If structural design stays simple (3-4 heuristics), it can be a capability. If it grows to include template scoring, content signal analysis, master arc composition, pacing evaluation, and iterative learning — that's agent-level complexity. Start as a capability if the scope feels manageable; promote to agent when it outgrows Irene's prompt.

### Potential Second Agent: Cluster Design Advisor

If Pax handles macro-level structural design, there may also be a need for a **Cluster Design Advisor** that handles micro-level within-cluster design: exactly how to decompose a specific slide into interstitials, what isolation_targets to pick, how to frame the brief. This is currently Irene's job (20a-2 specification). If it becomes complex enough, it could split into its own agent. Flag for future consideration.

### Sophia Integration

Pax's arc composition work overlaps with Sophia's storytelling framework. The cleanest model: Sophia provides the narrative theory (what makes a good arc); Pax applies it to presentation structure (where to place what kind of cluster). Sophia is the dramaturg; Pax is the stage director.

## References

- [agent-manifest.csv](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad/_config/agent-manifest.csv) — Existing agent roster
- [lane-matrix governance](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/production-coordination/) — Lane boundaries
- [20c-1 through 20c-4](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/) — Capabilities this agent consumes
