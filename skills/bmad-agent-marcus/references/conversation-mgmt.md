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
| Narrated lesson (full pipeline) | `content-creator` (Irene) | `gamma-specialist` (Gary), `elevenlabs-specialist`, `kling-specialist` (Kira), `compositor`, `quality-reviewer` | Marcus -> Irene P1 -> Marcus/[Gate 1] -> Gary -> Marcus/[Gate 2] -> Irene P2 -> Marcus/[Gate 3] -> ElevenLabs -> Marcus -> Kira -> Marcus -> Quinn-R pre-comp -> Compositor -> Descript -> Quinn-R post-comp -> Marcus/[Gate 4] |
| Lecture slides only | `gamma-specialist` (Gary) | `content-creator` (slide brief), `quality-reviewer` | Marcus -> Irene slide brief -> Marcus/[Gate 1] -> Gary -> Marcus/[Gate 2] -> approve |
| Narrated slides (no video) | `content-creator` (Irene), `elevenlabs-specialist` | `gamma-specialist`, `compositor`, `quality-reviewer` | Marcus -> Irene P1 -> Marcus -> Gary -> Marcus/[Gate 2] -> Irene P2 -> Marcus/[Gate 3] -> ElevenLabs -> Marcus -> Quinn-R pre-comp -> Descript -> Marcus/[Gate 4] |
| Case study | `content-creator` | `quality-reviewer` | Draft → review → approve |
| Assessment / quiz | `content-creator` | `canvas-specialist`, `quality-reviewer` | Draft → alignment check → review → LMS publish |
| Discussion prompt | `content-creator` | `canvas-specialist` | Draft → review → LMS publish |
| Voiceover narration | `elevenlabs-specialist` | `content-creator` (script), `quality-reviewer` | Script → voice synthesis → review → approve |
| Video clip (B-roll / concept) | `kling-specialist` (Kira) | `content-creator` (brief), `quality-reviewer` | Brief → generation → download → review |
| Infographic | `canva-specialist` (Story 3.8) | `content-creator` (copy), `quality-reviewer` | Copy → design guidance → user executes in Canva → review |
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
5. **Receive results** — Specialist returns a mediated result payload: one or more artifact paths, quality assessment, parameter decisions, any specialist-specific payload fields, and explicit downstream routing notes.
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
status: completed|blocked|failed
artifact_paths:
  - "course-content/staging/..."
primary_artifact: "course-content/staging/..."
artifact_type: lesson_plan|slide_brief|narration_script|segment_manifest|slide_deck|audio_bundle|assembly_guide
quality_assessment:
  passed: true|false
  score: 0.0-1.0
  notes: ["...", "..."]
parameter_decisions:
  - key: "gamma.style"
    value: "professional-medical"
    rationale: "Matched style bible visual identity"
specialist_payload:
  gary_slide_output: []        # Gary -> Marcus -> Irene Pass 2
  segment_manifest: null       # Irene -> Marcus -> ElevenLabs/Kira/Compositor
  narration_outputs: []        # ElevenLabs -> Marcus -> Quinn-R/Compositor
recommendations: ["...", "..."]
downstream_routing:
  next_specialist: "content-creator"
  requires_hil_gate: true
  next_input_artifacts: ["course-content/staging/..."]
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

## Full Pipeline Dependency Graph (Narrated Lesson)

```
User notes + guidance
    │
    ▼
Marcus -> Irene Pass 1: Lesson Plan + Slide Brief
    │
    ▼  [HIL Gate 1 via Marcus: Review lesson plan]
    │
Marcus -> Gary: Gamma slide deck -> PNGs
    │  (Gary reads Irene's slide brief from Marcus's envelope; theme/template options routed back through Marcus)
    ▼  [HIL Gate 2 via Marcus: Review slides — CRITICAL: narration cannot start until approved]
    │
Marcus -> Irene Pass 2: Narration Script + Segment Manifest
    │  (Irene reads Gary's actual PNGs via Marcus-carried gary_slide_output)
    ▼  [HIL Gate 3 via Marcus: Review script & manifest]
    │
Marcus -> ElevenLabs Agent: narration MP3 + VTT + SFX + music
    │  (reads manifest for narration_text, sfx, music cues, voice selection)
    │  (writes narration_duration, narration_file, narration_vtt back to manifest)
    ▼
Marcus -> Kira: silent video clips
    │  (runs only after Marcus has received narration_duration from ElevenLabs)
    │  (reads manifest for visual_source, visual_mode, narration_duration)
    │  (writes visual_file, visual_duration back to manifest)
    ▼
Marcus -> Quinn-R: pre-composition validation
    │
    ▼
Marcus -> Compositor Skill: generate Descript Assembly Guide from completed manifest
    │
    ▼  [Human: assembles + tweaks in Descript -> exports MP4 + VTT]
    │
    ▼
Marcus -> Quinn-R: post-composition validation
    │
    ▼  [HIL Gate 4 via Marcus: Final video review]
    │
Done: asset ready for Canvas deployment
```

**Marcus orchestrates this entire flow.** Key invariants:
- No user-visible specialist-to-specialist communication. Specialists may depend on prior specialist artifacts, but Marcus always receives, validates, and re-packs those artifacts before the next delegation.
- Gary before Irene Pass 2 (narration complements actual slides)
- ElevenLabs before Kira (Kira needs `narration_duration` to set clip duration)
- Both before compositor (compositor needs complete manifest)
- Quinn-R pre-composition before Descript handoff
- Quinn-R post-composition before Gate 4

## Irene Two-Pass Delegation

Marcus must invoke Irene **twice** for full lesson builds:

**First delegation (Pass 1):**
```yaml
envelope:
  production_run_id: {id}
  content_type: "lesson-plan"
  module_lesson: {module}/{lesson}
  learning_objectives: [{...}]
  pass: 1
```

**Second delegation (Pass 2 — after Gate 2 approval):**
```yaml
envelope:
  production_run_id: {id}
  content_type: "narration-script"
  module_lesson: {module}/{lesson}
  learning_objectives: [{...}]
  pass: 2
  gary_slide_output:
    - slide_id: "slide-01"
      file_path: "course-content/staging/{lesson_id}/slides/card-01.png"
      card_number: 1
      visual_description: "{Gary's description of what's on the slide}"
    # ... one entry per Gary PNG
```

## Compositor Delegation

The Compositor skill (Story 3.5 — planned) generates a Descript Assembly Guide from a completed manifest. When available, Marcus invokes it after Quinn-R's pre-composition pass:

```yaml
envelope:
  production_run_id: {id}
  segment_manifest: "course-content/staging/{lesson_id}/manifest.yaml"
  output_path: "course-content/staging/{lesson_id}/descript-assembly-guide.md"
```

Until Story 3.5 is implemented, Marcus presents the completed manifest to the user and guides manual Descript assembly using the composition architecture decision record as reference.

## Descript Manual-Tool Handoff

Descript is the sole composition platform — a Tier 3 manual-tool. Marcus hands off to the user with:
1. The Descript Assembly Guide (from Compositor, or manually composed from manifest)
2. All asset file paths (narration MP3s, VTT, video clips, slide PNGs, SFX, music)
3. Track assignment instructions (V1: video/images, A1: narration, A2: music, A3: SFX)
4. Timing table (segment start times from manifest narration_duration values)
5. Music cue instructions (duck/swell/out timestamps)
6. Transition specs per segment

## Asset-Lesson Pairing Enforcement

Every educational artifact produced must be paired with instructional context. Before marking any production step complete, verify:
- The asset has a parent lesson in the course hierarchy
- Learning objectives are documented and traceable
- Assessment alignment is explicit (if applicable)

If pairing cannot be established, halt and surface the gap to the user. This invariant is never waived.
