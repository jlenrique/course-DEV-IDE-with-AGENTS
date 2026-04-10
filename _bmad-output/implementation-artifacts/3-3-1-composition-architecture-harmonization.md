# Story 3.3.1: Composition Architecture Harmonization & Gary Deck Enhancement

Status: review

## Story

As a user,
I want all existing agents, plans, and documentation updated to reflect the composition architecture decisions (Party Mode 2026-03-27), and Gary enhanced with multi-slide deck generation and theme/template preview,
so that Story 3.4 (ElevenLabs) and the future Compositor story can build on a coherent, harmonized foundation.

## Context

Party Mode session (2026-03-27) established:
- **Segment manifest** as the single source of truth for multimedia production
- **Two-pass Irene model** (lesson plan before Gary, script+manifest after Gary)
- **Silent Video + Smart Audio** model (Kling silent, ElevenLabs owns all audio)
- **Descript as sole composition platform** (manual-tool pattern)
- **Narration-paced video** (audio drives visual timing)
- **Four HIL gates** front-loading human judgment
- **Seven instructional use cases** all flowing through one pipeline
- **Compositor skill** (future story) generates Descript Assembly Guides from completed manifests

Decision record: `_bmad-output/brainstorming/party-mode-composition-architecture.md`

Additionally, Gary needs enhancement:
- **Multi-slide deck generation** — woodshed only proved single slides (L1-L4); the API client already supports `num_cards` up to 60/75 but Gary's workflow doesn't exercise deck mode
- **Theme/template preview** — `GammaClient.list_themes()` exists but Gary never presents available themes/templates to the user before generation

## Acceptance Criteria

### Agent Updates

1. Irene's SKILL.md updated with two-pass workflow model (Pass 1: lesson plan, Pass 2: script + manifest after Gary's slides)
2. Irene has a new artifact type: **Segment Manifest** (YAML) with the schema from the composition architecture decision record
3. Irene's narration script template updated with segment IDs that cross-reference the manifest
4. Irene's context envelope schema updated to accept Gary's slide output as input for Pass 2
5. Irene's downstream annotations include ElevenLabs cues (`sfx`, `music`, `voice_id`) and Kira cues (`visual_mode`, `visual_source`)
6. Quinn-R's SKILL.md updated with two-pass validation model: pre-composition pass (audio/video asset quality) and post-composition pass (final Descript export)
7. Quinn-R's quality dimensions expanded to cover: narration WPM (130-170), VTT timestamp monotonicity, segment coverage, video duration match (±0.5s), audio levels (-16 LUFS narration, -30 LUFS music under speech), caption synchronization
8. Kira's SKILL.md references updated to document manifest consumption: reads `visual_mode`, `visual_source`, and `narration_duration` from segment manifest
9. Marcus's pipeline references updated with the full dependency graph (Irene Pass 1 → Gary → HIL → Irene Pass 2 → ElevenLabs → Kira → Composition → Descript → Quinn-R)
10. Marcus's checkpoint-coord reference updated with four formalized HIL gates
11. Marcus's conversation-mgmt reference updated with Compositor delegation and Descript manual-tool routing

### Gary Deck Enhancement

12. Gary's SKILL.md updated with explicit **deck generation mode** alongside single-slide mode
13. Gary's parameter-recommendation reference updated with deck-specific parameter guidance (numCards ranges per content type, cardSplit strategy, deck-level additionalInstructions)
14. Gary's content-type-mapping reference updated with multi-slide deck templates (lecture deck, case study deck, module overview deck)
15. Gary has a new reference: `theme-template-preview.md` — workflow for presenting available Gamma themes and registered templates to the user before generation
16. Gary's context envelope schema updated to support deck mode fields: `deck_mode: true`, `num_cards`, `card_split`, `theme_selection_required: true`
17. `skills/gamma-api-mastery/` updated with a `list_themes_and_templates` operation that combines `GammaClient.list_themes()` with the template registry in `style_guide.yaml`

### Documentation & Plans

18. `_bmad-output/planning-artifacts/architecture.md` production pipeline section updated with the composition architecture dependency graph, Descript as composition platform, and segment manifest as data backbone
19. `resources/tool-inventory/tool-access-matrix.md` updated: Descript entry revised to reflect its role as sole composition platform (manual-tool pattern)
20. `_bmad-output/planning-artifacts/epics.md` Epic 3 section updated: new Compositor story added as 3.5, Canvas pushed to 3.6, Qualtrics to 3.7, Canva to 3.8, Source Wrangler to 3.9, Tech Spec Wrangler to 3.10
21. `_bmad-output/implementation-artifacts/sprint-status.yaml` updated with 3.3.1 status, new Compositor story slot (3.5), and renumbered stories
22. `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` updated with composition architecture decisions and new story sequencing
23. `next-session-start-here.md` updated to reflect harmonization completion, Gary deck enhancement, new story sequence, and readiness for Story 3.4
24. `docs/project-context.md` Current State section updated with composition architecture decisions

### Validation

25. All updated agent SKILL.md files pass a self-consistency check: no dangling references, no contradictory workflow descriptions, all external skill/agent references resolve to existing files
26. The segment manifest schema example in Irene's template is consistent with the schema in the composition architecture decision record
27. Gary's theme listing works: `GammaClient.list_themes()` returns valid data (quick smoke test against live API)

## Tasks / Subtasks

- [x] Task 1: Update Irene — Two-Pass Model & Segment Manifest (AC: #1-5, #26)
  - [x] 1.1 Update `skills/bmad-agent-content-creator/SKILL.md`: add two-pass workflow description, add Segment Manifest as 7th artifact type, update internal capabilities list with MG (Segment Manifest generation)
  - [x] 1.2 Create `skills/bmad-agent-content-creator/references/template-segment-manifest.md`: YAML schema with all fields from decision record, usage examples per use case type, field descriptions, downstream consumer notes
  - [x] 1.3 Update `skills/bmad-agent-content-creator/references/template-narration-script.md`: add segment IDs that cross-reference manifest, add `[SEGMENT: seg-XX]` markers
  - [x] 1.4 Update `skills/bmad-agent-content-creator/references/template-slide-brief.md`: note that this is Pass 1 output (pre-Gary), annotated to clarify its role in the two-pass model
  - [x] 1.5 Add downstream annotation fields to Irene templates: `sfx`, `music`, `visual_mode`, `visual_source` in segment manifest template and slide brief
  - [x] 1.6 Update Irene's context envelope to accept `gary_slide_output` (list of slide PNGs with metadata) as input for Pass 2 invocation

- [x] Task 2: Update Quinn-R — Two-Pass Validation & Audio/Composition Dimensions (AC: #6-7)
  - [x] 2.1 Update `skills/bmad-agent-quality-reviewer/SKILL.md`: add two-pass validation model description (pre-composition + post-composition)
  - [x] 2.2 Add new quality dimension: **Audio Quality** (AQ) — WPM range (130-170), VTT timestamp monotonicity, pronunciation accuracy, segment narration coverage (>95% of script words)
  - [x] 2.3 Add new quality dimension: **Composition Integrity** (CI) — video duration vs narration duration (±0.5s), audio levels (narration -16 LUFS, music ducked -30 LUFS), caption sync, transition consistency
  - [x] 2.4 Update `skills/quality-control/SKILL.md` to reference the two new dimensions and two-pass model
  - [x] 2.5 Updated Quinn-R's SKILL.md to distinguish pre-composition pass (audio/video asset quality) from post-composition pass (final Descript export validation)

- [x] Task 3: Update Kira — Manifest Consumption (AC: #8)
  - [x] 3.1 Update `skills/bmad-agent-kling/SKILL.md`: add manifest consumption to workflow description — reads `visual_mode`, `visual_source`, `narration_duration` from segment manifest; writes back `visual_file`, `visual_duration`
  - [x] 3.2 Update Kira's context envelope to add `segment_manifest` as optional pipeline input field
  - [x] 3.3 Documented three Kira engagement modes from manifest in Kira's SKILL.md headless activation section

- [x] Task 4: Update Marcus — Pipeline, HIL Gates, Delegation (AC: #9-11)
  - [x] 4.1 Update `skills/bmad-agent-marcus/references/checkpoint-coord.md`: replaced with four formalized HIL gates, each with timing, review criteria, approve/revise actions, Quinn-R integration table
  - [x] 4.2 Update `skills/bmad-agent-marcus/references/conversation-mgmt.md`: added full dependency graph, Compositor delegation, Descript manual-tool handoff, two-pass Irene delegation envelopes
  - [x] 4.3 Update Marcus SKILL.md External Specialist Agents section: added Compositor (planned Story 3.5), Descript manual-tool handoff note, updated all specialist statuses and story numbers
  - [x] 4.4 Updated Marcus's content type vocabulary table with full narrated lesson pipeline and Irene two-pass delegation envelopes in conversation-mgmt.md

- [x] Task 5: Enhance Gary — Deck Mode & Theme/Template Preview (AC: #12-17, #27)
  - [x] 5.1 Update `skills/bmad-agent-gamma/SKILL.md`: added deck mode, theme/template preview (TP capability), gary_slide_output return field, pipeline output for Irene Pass 2
  - [x] 5.2 Update `skills/bmad-agent-gamma/references/parameter-recommendation.md`: added Deck Mode Parameter Guidance section with numCards ranges by content type, cardSplit strategy, deck-level additionalInstructions patterns
  - [x] 5.3 Update `skills/bmad-agent-gamma/references/content-type-mapping.md`: added four multi-slide deck templates (Lecture Deck, Case Study Deck, Module Overview Deck, Assessment Set)
  - [x] 5.4 Create `skills/bmad-agent-gamma/references/theme-template-preview.md`: full TP workflow (fetch → present → capture → proceed), recommendation logic, registration workflow
  - [x] 5.5 Update `skills/bmad-agent-gamma/references/context-envelope-schema.md`: added `deck_mode`, `num_cards`, `card_split`, `theme_selection_required` fields; added `gary_slide_output` to outbound return
  - [x] 5.6 Update `skills/gamma-api-mastery/SKILL.md`: added `list_themes_and_templates` operation combining API theme listing with registry lookup
  - [x] 5.7 Smoke test `GammaClient.list_themes()` — PASSED: returns 10 themes including institutional "2026 HIL APC (Nejal)" theme. Documented in theme-template-preview.md recommendation logic.

- [x] Task 6: Update Architecture & Tool Inventory (AC: #18-19)
  - [x] 6.1 Update `_bmad-output/planning-artifacts/architecture.md`: added "Production Composition Pipeline" section with dependency graph, segment manifest data backbone, Descript sole composition platform, seven use cases table, four HIL gates, audio architecture, Quinn-R two-pass validation
  - [x] 6.2 Update `resources/tool-inventory/tool-access-matrix.md`: Descript entry revised to COMPOSITION PLATFORM (manual-tool pattern), full rationale documented

- [x] Task 7: Update Epics, Sprint Status & Workflow Status (AC: #20-22)
  - [x] 7.1 Update `_bmad-output/planning-artifacts/epics.md`: added Story 3.3.1 entry, added Story 3.5 Compositor, renumbered Canvas→3.6, Qualtrics→3.7, Canva→3.8, Source Wrangler→3.9, Tech Spec Wrangler→3.10
  - [x] 7.2 Update `_bmad-output/implementation-artifacts/sprint-status.yaml`: added 3-3-1 (in-progress), 3-5-compositor-skill (backlog), all downstream stories renumbered
  - [x] 7.3 Update `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`: added 5 new key decisions (composition architecture, Irene two-pass, Gary deck, Compositor), updated next_workflow_step

- [x] Task 8: Update Project Context & Session File (AC: #23-24)
  - [x] 8.1 Update `next-session-start-here.md`: complete rewrite reflecting harmonization done, composition architecture resolved, Gary enhancements, new 11-story Epic 3 sequence, Story 3.4 as next
  - [x] 8.2 Update `docs/project-context.md`: added Composition Architecture section, updated Current State, updated Epic 3 story list, added key file references

- [x] Task 9: Self-Consistency Validation (AC: #25-26)
  - [x] 9.1 All SKILL.md cross-references verified: 9/9 referenced files exist and resolve correctly
  - [x] 9.2 Segment manifest schema consistency: all 19 canonical fields from decision record present in Irene's template
  - [x] 9.3 Marcus pipeline graph verified against agent SKILL.md capabilities: gary_slide_output, segment_manifest, narration_duration, silent video all confirmed in respective agents
  - [x] 9.4 Epics/sprint-status/bmm-workflow-status internal consistency: all 7 new story keys consistent across files

## Dev Notes

### Scope Discipline: Documentation & Reference Updates Only

This story is **agent reference and documentation harmonization** — no new Python scripts, no new API clients, no new test infrastructure. The only code touch is Task 5.7 (smoke test of existing `list_themes()`).

Every change is to `.md` or `.yaml` files in:
- `skills/bmad-agent-*/` (agent definitions and references)
- `skills/*/` (mastery skill references)
- `_bmad-output/` (planning and implementation artifacts)
- `docs/` (project documentation)
- `resources/` (tool inventory)
- `next-session-start-here.md`

### Two-Pass Irene Model: Design Details

**Pass 1 output** (before Gary):
- Lesson plan with learning objectives, content outline, concept sequence
- Slide brief (existing artifact) — content suggestions per slide, NOT a rigid spec
- Visual suggestions (descriptive, not prescriptive — Gary interprets these)

**Pass 2 input** (after Gary + HIL Gate 2):
- Gary's actual slide PNGs with metadata (file paths, card count, theme used)
- User's approval/revision notes from HIL Gate 2

**Pass 2 output**:
- Narration script (updated template with `[SEGMENT: seg-XX]` markers)
- Segment manifest (new YAML artifact) — the machine-readable production contract

**Critical principle:** Irene writes narration to *complement* Gary's visuals, not duplicate them. If the slide shows a three-column comparison, Irene narrates the insight, not the structure.

### Segment Manifest Schema (Canonical)

```yaml
lesson_id: string        # e.g., C1-M1-L3
title: string
music_bed: string | null  # overall music direction
segments:
  - id: string            # e.g., seg-01
    narration_ref: string  # pointer to script section (e.g., script.md#segment-1)
    narration_text: string # actual narration content
    visual_cue: string     # description of intended visual
    visual_mode: enum      # static-hold | video | text-frame | pause-beat
    visual_source: enum    # gary | kira | null
    sfx: string | null     # SFX cue name or null
    music: enum            # duck | swell | out | continue | null
    transition: enum       # cross-dissolve | fade | cut | none
    # Written back by downstream agents:
    narration_duration: float | null   # seconds (ElevenLabs writes)
    narration_file: string | null      # path to MP3 (ElevenLabs writes)
    narration_vtt: string | null       # path to VTT (ElevenLabs writes)
    visual_file: string | null         # path to PNG or MP4 (Gary or Kira writes)
    visual_duration: float | null      # seconds (derived or Kira writes)
    sfx_file: string | null            # path to SFX clip (ElevenLabs writes)
```

### Gary Deck Enhancement: Design Details

**Current state:** GammaClient supports `num_cards` (1-60 Pro, 1-75 Ultra), `list_themes()`, and `generate_from_template()`. Gary's content-type-mapping references `numCards: auto` and `numCards: 3-5` for some types. But:
- Woodshed exemplars are all L1-L4 (single slides) — deck exemplars (L5+) not yet created
- No workflow for presenting themes/templates to user before generation
- No explicit deck-vs-single-slide mode distinction in Gary's SKILL.md

**What changes:**
1. Gary's SKILL.md gets a clear "Single Slide Mode" vs "Deck Mode" distinction
2. Parameter recommendation adds deck-specific guidance (numCards ranges, cardSplit)
3. Content-type-mapping adds multi-slide templates
4. New `theme-template-preview.md` reference defines the pre-generation theme/template presentation workflow
5. Context envelope adds deck-specific fields

**Theme/template preview workflow:**
1. Before any generation, Gary checks if `theme_selection_required: true` in envelope (or always for deck mode)
2. Gary calls `list_themes()` → gets available Gamma themes with names, descriptions, thumbnails
3. Gary checks `style_guide.yaml` template registry for scope-matched templates
4. Gary presents both to user: "Here are the available themes and any registered templates. I recommend [X] because [reason]. Which would you like?"
5. User selects → Gary proceeds with `theme_id` set

**Deck-mode numCards guidance:**
| Content Type | Recommended numCards | cardSplit | Notes |
|-------------|---------------------|-----------|-------|
| Lecture deck | 5-12 | auto | One concept per card, Gamma decides breaks |
| Case study deck | 3-5 | auto | Presenting complaint → diagnosis → management |
| Module overview | 3-4 | auto | Objectives → topics → assessment preview |
| Assessment set | 2-4 | inputTextBreaks | One question per card, explicit breaks |
| Narrative arc | 4-8 | auto | Story beats, rising action |

### Re-Sequencing: New Epic 3 Story Order

| Story | Agent/Skill | Status | Change |
|-------|-------------|--------|--------|
| 3.1 | Gary (Gamma Specialist) | DONE | — |
| 3.2 | Irene (Content Creator) + Quinn-R (Quality Reviewer) | DONE | — |
| 3.3 | Kira (Kling Video Specialist) | DONE | — |
| **3.3.1** | **Composition Architecture Harmonization + Gary Deck** | **THIS STORY** | **NEW** |
| 3.4 | ElevenLabs Specialist (expanded) | Backlog | No change |
| **3.5** | **Compositor Skill (Descript Assembly Guide)** | **Backlog** | **NEW** |
| 3.6 | Canvas Specialist | Backlog | Was 3.5 |
| 3.7 | Qualtrics Specialist | Backlog | Was 3.6 |
| 3.8 | Canva Specialist (manual-tool pattern) | Backlog | Was 3.7 |
| 3.9 | Source Wrangler (Notion + Box) | Backlog | Was 3.8 |
| 3.10 | Tech Spec Wrangler | Backlog | Was 3.9 |

Epic 3 now has **11 stories** (was 9).

### Existing Infrastructure to Reuse (DO NOT REINVENT)

| Component | Location | Reuse For |
|-----------|----------|-----------|
| GammaClient.list_themes() | `scripts/api_clients/gamma_client.py:41` | Theme listing — already implemented |
| GammaClient.generate() num_cards | `scripts/api_clients/gamma_client.py:56` | Deck generation — already supported |
| GammaClient.generate_from_template() | `scripts/api_clients/gamma_client.py:119` | Template-based generation — already supported |
| Template registry pattern | `skills/bmad-agent-gamma/references/content-type-mapping.md` | Template resolution logic already documented |
| Context envelope pattern | `skills/bmad-agent-gamma/references/context-envelope-schema.md` | Extend, don't replace |
| Quality dimensions pattern | `skills/bmad-agent-quality-reviewer/SKILL.md` | Add new dimensions following existing format |
| Marcus reference pattern | `skills/bmad-agent-marcus/references/` | Update existing files, don't create new ones |
| Decision record | `_bmad-output/brainstorming/party-mode-composition-architecture.md` | Canonical source for all pipeline decisions |

### Testing Standards

- No new test files in this story (documentation-only changes)
- Exception: Task 5.7 — quick smoke test of `GammaClient.list_themes()` against live API to verify theme data is retrievable. Run interactively, not as a committed test.
- Self-consistency validation (Task 9) is manual review, not automated tests

### Anti-Patterns to Avoid

- Do NOT create new agent files — this story UPDATES existing agents only
- Do NOT write Python scripts for the segment manifest — it's a YAML template in Irene's references, consumed by future agents
- Do NOT implement the Compositor skill — that's Story 3.5. Only add the story slot and Marcus's awareness of it
- Do NOT create deck exemplars for Gary's woodshed — that's a future enhancement. Only add the deck mode capability to Gary's workflow
- Do NOT change GammaClient code — the API client already supports everything needed
- Do NOT add Descript API integration — Descript is manual-tool pattern only
- Do NOT update agent memory sidecars — those are runtime artifacts, not harmonization scope
- Do NOT renumber completed stories (3.1, 3.2, 3.3 stay as-is)

### Key Lessons from Stories 3.1-3.3 (Apply Here)

1. **Agent references are the contract.** When Marcus delegates to a specialist, the references define what's expected. If the references don't describe the manifest, the agent won't know to read it.
2. **Context envelope is the API.** Every new capability needs corresponding envelope fields. Deck mode, theme selection, and manifest input all need envelope schema updates.
3. **Templates are starting points, not rigid specs.** Gary's content-type-mapping templates should suggest numCards ranges, not mandate exact values. Gary's judgment (informed by patterns.md) decides the final value.
4. **HIL gates front-load human judgment.** The four gates are placed where changes are cheapest — before expensive audio/video generation, not after.
5. **One source of truth per decision.** The segment manifest is canonical for production. The decision record is canonical for architecture. Don't duplicate decision content across multiple documents — reference the source.

### Task Execution Order (Recommended)

Tasks can be partially parallelized but some have logical dependencies:

```
Task 1 (Irene) ─────────┐
Task 2 (Quinn-R) ────────┤
Task 3 (Kira) ───────────┼──→ Task 4 (Marcus — needs to reference updated agents)
Task 5 (Gary) ───────────┘          │
                                     ├──→ Task 6 (Architecture — needs final pipeline)
                                     │         │
                                     │         ├──→ Task 7 (Epics/Sprint — needs final scope)
                                     │         │         │
                                     │         │         ├──→ Task 8 (Context/Session — last)
                                     │         │         │         │
                                     │         │         │         ├──→ Task 9 (Validation — verify all)
```

### References

- [Source: _bmad-output/brainstorming/party-mode-composition-architecture.md] — Canonical composition architecture decisions
- [Source: skills/bmad-agent-content-creator/SKILL.md] — Irene current state
- [Source: skills/bmad-agent-quality-reviewer/SKILL.md] — Quinn-R current state
- [Source: skills/bmad-agent-kling/SKILL.md] — Kira current state
- [Source: skills/bmad-agent-marcus/SKILL.md] — Marcus current state
- [Source: skills/bmad-agent-gamma/SKILL.md] — Gary current state
- [Source: skills/bmad-agent-gamma/references/content-type-mapping.md] — Gary content types
- [Source: skills/bmad-agent-gamma/references/parameter-recommendation.md] — Gary parameter logic
- [Source: scripts/api_clients/gamma_client.py] — GammaClient with list_themes, num_cards, generate_from_template
- [Source: _bmad-output/planning-artifacts/epics.md] — Current epic/story definitions
- [Source: _bmad-output/planning-artifacts/architecture.md] — Current architecture
- [Source: resources/tool-inventory/tool-access-matrix.md] — Current tool inventory
- [Source: _bmad-output/implementation-artifacts/sprint-status.yaml] — Current sprint tracking
- [Source: _bmad-output/implementation-artifacts/bmm-workflow-status.yaml] — Current workflow status

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6[1m]

### Debug Log References

- GammaClient.list_themes() smoke test: PASSED. Returns 10 themes. Institutional theme "2026 HIL APC (Nejal)" id=njim9kuhfnljvaa present.
- All 9 cross-reference checks: PASSED
- Segment manifest schema: all 19 canonical fields present
- Internal consistency (epics/sprint/bmm): all 7 new story keys consistent

### Completion Notes List

- Story 3.3.1 complete: 27 ACs satisfied, 9 tasks, 42 subtasks
- Irene: two-pass model, segment manifest (7th artifact), MG capability, gary_slide_output in envelope, Pass 1/2 annotated in all templates
- Quinn-R: two-pass validation (pre/post-composition), AQ + CI quality dimensions added (7 total), quality-control SKILL.md updated
- Kira: manifest consumption documented (visual_source, visual_mode, narration_duration), three engagement modes, segment_manifest envelope field, silent video confirmed
- Marcus: checkpoint-coord.md rewritten with 4 HIL gates + Quinn-R integration; conversation-mgmt.md updated with full dependency graph, Compositor delegation, Descript handoff, two-pass Irene envelopes; SKILL.md updated with Compositor placeholder and story renumbering
- Gary: deck mode, TP capability, theme-template-preview.md created, parameter-recommendation.md deck guidance, content-type-mapping.md 4 new deck templates, context-envelope-schema.md deck fields + gary_slide_output, gamma-api-mastery list_themes_and_templates operation
- Architecture.md: Production Composition Pipeline section added (dependency graph, 7 use cases, 4 HIL gates, audio architecture, Quinn-R two-pass)
- Tool inventory: Descript entry updated to COMPOSITION PLATFORM (manual-tool pattern)
- Epics: 3.3.1, 3.5 Compositor added; Canvas→3.6, Qualtrics→3.7, Canva→3.8, Source Wrangler→3.9, Tech Spec Wrangler→3.10
- Sprint status: new entries added, story renumbered, 3.3.1 set in-progress
- bmm-workflow-status: 5 new key decisions, next_workflow_step updated
- next-session-start-here.md: complete rewrite, Story 3.4 as next action
- docs/project-context.md: Composition Architecture section, Current State, Key Files updated

### File List

**Modified:**
- `skills/bmad-agent-content-creator/SKILL.md`
- `skills/bmad-agent-content-creator/references/template-narration-script.md`
- `skills/bmad-agent-content-creator/references/template-slide-brief.md`
- `skills/bmad-agent-quality-reviewer/SKILL.md`
- `skills/quality-control/SKILL.md`
- `skills/bmad-agent-kling/SKILL.md`
- `skills/bmad-agent-marcus/SKILL.md`
- `skills/bmad-agent-marcus/references/checkpoint-coord.md`
- `skills/bmad-agent-marcus/references/conversation-mgmt.md`
- `skills/bmad-agent-gamma/SKILL.md`
- `skills/bmad-agent-gamma/references/parameter-recommendation.md`
- `skills/bmad-agent-gamma/references/content-type-mapping.md`
- `skills/bmad-agent-gamma/references/context-envelope-schema.md`
- `skills/gamma-api-mastery/SKILL.md`
- `_bmad-output/planning-artifacts/architecture.md`
- `_bmad-output/planning-artifacts/epics.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `resources/tool-inventory/tool-access-matrix.md`
- `next-session-start-here.md`
- `docs/project-context.md`

**Created:**
- `skills/bmad-agent-content-creator/references/template-segment-manifest.md`
- `skills/bmad-agent-gamma/references/theme-template-preview.md`
- `_bmad-output/brainstorming/party-mode-composition-architecture.md`
- `_bmad-output/implementation-artifacts/3-3-1-composition-architecture-harmonization.md` (this file)
