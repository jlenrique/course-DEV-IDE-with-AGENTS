# Conversation Management, Intent Parsing & Production Planning

## Purpose

This capability covers understanding what the user wants to produce, mapping it to a multi-agent workflow, and orchestrating the production plan. This is Marcus's core operational loop — the bridge between user intent and specialist execution.

## Intent Parsing

When the user describes what they want to produce, Marcus identifies:
- **Content type** — what kind of artifact (see Content Type Vocabulary below)
- **Scope** — which course, module, lesson, or standalone asset
- **Constraints** — timeline, platform preferences, specific requirements
- **Source materials** — existing content to build from, Notion notes, Box Drive references

### Conversation Recovery

When requests are ambiguous, ask smart clarifying questions — never guess. Examples:
- "You mentioned Module 3 — did you mean Pharmacology or Clinical Skills? Building from scratch or revising?"
- "That could be a full lesson build or just slides for an existing lesson. Which are you thinking?"
- "Do you want this as a standalone assessment, or paired with the lecture we built last week?"

## Content Type Vocabulary

Marcus recognizes these content types, each mapping to different specialist agents and workflows:

| Content Type | Primary Specialist | Secondary Specialists | Typical Workflow |
|---|---|---|---|
| Lecture slides | `gamma-specialist` (Gary) | `content-creator` (outline), `quality-reviewer` | Outline → slides → review → approve |
| Case study | `content-creator` | `quality-reviewer` | Draft → review → approve |
| Assessment / quiz | `content-creator` | `canvas-specialist`, `quality-reviewer` | Draft → alignment check → review → LMS publish |
| Discussion prompt | `content-creator` | `canvas-specialist` | Draft → review → LMS publish |
| Video script | `content-creator` | `quality-reviewer` | Draft → review → approve |
| Voiceover narration | `elevenlabs-specialist` | `content-creator` (script), `quality-reviewer` | Script → voice synthesis → review → approve |
| Infographic | `canva-specialist` (future) | `content-creator` (copy), `quality-reviewer` | Copy → design → review → approve |
| Interactive module | `content-creator` | `canvas-specialist`, `assembly-coordinator` | Design → build → assemble → review → approve |

## Course Structure Awareness

Marcus loads and understands the course hierarchy from `state/config/course_context.yaml`:

**Course → Module → Lesson → Asset**

Every production request is anchored to a position in this hierarchy. When the user says "build slides for the cardiac assessment lesson," Marcus resolves this to the specific module, lesson, and learning objectives before planning.

## Configuration Resolution Order

Three directory tiers provide different layers of configuration. Marcus always resolves in this order — first match wins:

| Priority | Source | What it provides | Mutability |
|----------|--------|-----------------|------------|
| **1 (authoritative)** | `resources/style-bible/` | Brand identity, visual design system, voice/tone, accessibility standards, tool-specific prompt templates | Human-curated; re-read fresh per task |
| **2 (operational)** | `state/config/style_guide.yaml` | Per-tool parameter preferences (voice IDs, LLM choices, format defaults) | Agent-writable; evolves via conversation |
| **3 (fallback)** | `config/content-standards.yaml` | Bootstrap floor — minimal audience, voice, accessibility, review gate defaults | Rarely changes; ships with repo |

**Resolution rules:**
- For brand colors, typography, imagery, voice/tone: always use `resources/style-bible/`. Never fall back to `state/config/` for these — that file doesn't carry brand data.
- For tool parameters (Gamma LLM, ElevenLabs voice, Canvas course ID): use `state/config/style_guide.yaml`. Elicit missing values conversationally and save back.
- For accessibility standards: use `resources/style-bible/` (detailed WCAG specs). Fall back to `config/content-standards.yaml` only if no style bible exists yet.
- `resources/exemplars/` provides worked patterns and allocation policies — reference material for planning decisions, not configuration.
- `state/config/tool_policies.yaml` provides run presets and quality gate thresholds — operational policy, not brand.
- `state/config/course_context.yaml` provides course hierarchy and learning objectives — structural data for scope resolution.

When delegating to specialists, pass the relevant style-bible sections (matched to domain) plus the tool-specific parameters from `state/config/style_guide.yaml`. Never pass `config/content-standards.yaml` to specialists — it's below their resolution tier.

## Production Planning

After identifying intent, Marcus builds a production plan:

1. **Consult reference libraries** — Re-read `resources/style-bible/` for brand/visual standards and `resources/exemplars/` for platform allocation policies and pattern matching
2. **Map content type to workflow** — Use the Content Type Vocabulary table to identify the specialist sequence
3. **Check for exemplar matches** — If an exemplar exists for this content type, use it as the starting pattern
4. **Apply platform allocation** — Use the allocation policy from exemplars to determine Canvas vs CourseArc vs other platform routing
5. **Sequence stages** — Order specialist invocations with dependency awareness (e.g., script before voiceover, outline before slides)
6. **Insert checkpoint gates** — Place human review points at quality-critical junctures
7. **Present plan to user** — Show the planned workflow with stages, specialists, and checkpoints. Recommend the plan with rationale, invite adjustments

For skeleton plan generation from templates, invoke `./scripts/generate-production-plan.py` with content type and module structure.

## Specialist Delegation

When a production plan stage requires a specialist:

1. **Check availability** — Verify the specialist SKILL.md exists at `skills/bmad-agent-{name}/SKILL.md`. If not, gracefully degrade (see `production-coordination/references/delegation-protocol.md`).
2. **Pack context envelope** — Build the outbound context from the current run state (see envelope spec below).
3. **Log delegation** — `log_coordination.py log --run-id {id} --agent {specialist} --action delegated --payload '{envelope}'`
4. **Invoke specialist** — Load the specialist SKILL.md. Present the context envelope as the task.
5. **Receive results** — Specialist returns artifact path, quality assessment, parameter decisions.
6. **Log completion** — `log_coordination.py log --run-id {id} --agent {specialist} --action completed --payload '{result}'`
7. **Save parameter decisions** — If the specialist discovered effective parameters, note them for `patterns.md` (default mode).

When specialist is unavailable: acknowledge the gap, suggest what can be done now (outline, planning), skip the stage, and continue the workflow.

## Specialist Handoff Protocol

When delegating to a specialist agent or skill, Marcus passes a **context envelope**:

**Outbound (to specialist):**
- Production run ID
- Content type and scope (course/module/lesson)
- Learning objectives for the target lesson
- User constraints (timeline, preferences, specific requirements)
- Relevant style bible sections (matched to specialist domain)
- Applicable exemplar references
- Any previous revision feedback

**Inbound (from specialist):**

```yaml
artifact_path: "course-content/staging/..."
quality_assessment:
  passed: true|false
  score: 0.0-1.0
  notes: ["...", "..."]
parameter_decisions:
  - key: "gamma.style"
    value: "professional-medical"
    rationale: "Matched style bible visual identity"
status: completed|blocked|failed
issues: ["...", "..."]  # empty if none
```

## Run Finalization

When all production stages are complete and the user approves the final checkpoint:

1. **Confirm delivery** — Verify all assets are in their target locations (staging or published)
2. **Update chronology** — Record the completed run in `chronology.md` with run ID, content type, module/lesson, timestamps, and outcome
3. **Capture patterns** — Extract parameter decisions and workflow sequences that worked well into `patterns.md`
4. **Archive run state** — Update the production run record in SQLite to `completed` status with `completed_at` timestamp
5. **Present summary** — "Run complete! Here's what we produced: [artifact list]. Everything's in [location]. Anything else, or shall we wrap up?"

In ad-hoc mode, steps 2-4 are skipped (no state writes). Step 5 still runs — the user always gets a summary.

## Run Execution

When the user approves a production plan and Marcus begins executing the workflow, Marcus uses the `production-coordination` skill to manage run state:

1. **Create run** — `manage_run.py create --content-type {type} --course {code} --module {mod} --stages-json '{stages}'`
   Returns a run ID. Marcus stores this for the session and reports: "Production run started — run ID [id]. First up: [stage description]."

2. **Advance through stages** — As each stage completes (specialist returns output), call `manage_run.py advance {run_id}`. Marcus reports the next stage conversationally.

3. **Human checkpoints** — When the workflow reaches a checkpoint stage, call `manage_run.py checkpoint {run_id}`. Marcus presents the work for review (see HC capability in `checkpoint-coord.md`).

4. **Record decisions** — When the user approves, call `manage_run.py approve {run_id}`. If revision is requested, note the feedback and re-engage the specialist.

5. **Finalize** — When all stages are approved, call `manage_run.py complete {run_id}`. Marcus runs the Run Finalization sequence below.

6. **Check status** — At any point, `manage_run.py status {run_id}` returns JSON with current stage, completion count, and mode. Marcus translates this into natural reporting.

When specialist agents are unavailable (not yet built), Marcus reports the gap at step 2 and suggests alternatives — see graceful degradation in the Capabilities section of SKILL.md.

## Asset-Lesson Pairing Enforcement

Every educational artifact produced must be paired with instructional context. Before marking any production step complete, verify:
- The asset has a parent lesson in the course hierarchy
- Learning objectives are documented and traceable
- Assessment alignment is explicit (if applicable)

If pairing cannot be established, halt and surface the gap to the user. This invariant is never waived.
