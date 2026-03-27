# Interaction Test Guide — Irene (Content Creator, Instructional Architect 📐)

## Purpose
Verify Irene activates correctly, designs pedagogically grounded content, delegates writing to BMad writers with precise briefs, reviews for alignment, and assembles structured artifacts.

## Prerequisites
- Irene's SKILL.md loaded in Cursor agent chat
- `state/config/course_context.yaml` with at least one content strand
- `resources/style-bible/master-style-bible.md` present

---

## Scenario 1: Interactive Activation
**Trigger:** "Talk to Irene" or "I need the Instructional Architect"
**Expected:**
- [ ] Irene greets with content state from course_context.yaml
- [ ] References module/lesson availability
- [ ] Offers to work on content design
- [ ] Does NOT dump a capability menu

## Scenario 2: First Run (No Sidecar)
**Trigger:** Activate with no `_bmad/memory/content-creator-sidecar/` directory
**Expected:**
- [ ] Runs init.md first-run setup
- [ ] Creates sidecar structure
- [ ] Verifies course_context.yaml and style-bible exist
- [ ] Greets normally after setup

## Scenario 3: Headless Delegation from Marcus
**Trigger:** Provide a context envelope: `{production_run_id: "test-001", content_type: "narration_script", module_lesson: "C1-M1-L1", learning_objectives: ["Define innovative mindset characteristics"]}`
**Expected:**
- [ ] Parses envelope correctly
- [ ] Identifies content type → narration script
- [ ] Selects appropriate writer (should recommend Paige or Sophia based on content)
- [ ] Returns structured outbound with artifact_paths, writer_delegation_log, downstream_routing

## Scenario 4: Writer Selection Logic
**Trigger:** "I need a case study dialogue about a patient with ambiguous lab results"
**Expected:**
- [ ] Identifies content type as dialogue script
- [ ] Selects Sophia (narrative content, Analyze-level)
- [ ] Composes delegation brief with learning objective, Bloom's level, character profiles
- [ ] Does NOT attempt to write the dialogue itself

## Scenario 5: Pedagogical Quality Review
**Trigger:** Provide a prose draft and ask "Review this for pedagogical alignment"
**Expected:**
- [ ] Evaluates against learning objective fit, Bloom's level, cognitive load
- [ ] Does NOT evaluate prose quality (that's the writer's domain)
- [ ] Provides constructive feedback with specific alignment concerns
- [ ] References pedagogical-framework.md reasoning

## Scenario 6: Assessment Design (Backward Design)
**Trigger:** "Design an assessment for LO: Apply first-principles thinking to a healthcare problem"
**Expected:**
- [ ] Identifies Bloom's level as Apply
- [ ] Designs assessment BEFORE content (backward design principle)
- [ ] Produces assessment brief with distractor rationale
- [ ] Links back to learning objective

## Scenario 7: Cognitive Load Flag
**Trigger:** Request a slide brief with 15 distinct concepts in one slide
**Expected:**
- [ ] Flags cognitive load violation (7±2 rule)
- [ ] Suggests splitting into multiple slides
- [ ] References pedagogical-framework.md

## Scenario 8: Redirect (Wrong Agent)
**Trigger:** "Create slides for Module 2" or "Review quality of this narration"
**Expected:**
- [ ] Redirects: "I'm Irene — I handle instructional design. For slides talk to Gary, for quality review talk to Quinn-R, or ask Marcus."
- [ ] Does NOT attempt the task

## Scenario 9: Downstream Annotations
**Trigger:** Ask Irene to produce a narration script
**Expected:**
- [ ] Script includes downstream consumption section
- [ ] ElevenLabs voice suggestion present
- [ ] Estimated duration calculated (word count ÷ 150 wpm)
- [ ] Pronunciation guide for medical terms
- [ ] Paired slide brief reference noted

## Scenario 10: Missing Learning Objectives
**Trigger:** Provide envelope with empty `learning_objectives: []`
**Expected:**
- [ ] Does NOT invent objectives
- [ ] Reports back requesting clarification from Marcus
- [ ] References Degradation Handling protocol

---

## Scenarios Added: Story 3.3.1 (Two-Pass Model + Segment Manifest)

## Scenario 11: Two-Pass Model — Pass 1 (Before Gary)
**Trigger:** Marcus context envelope with `content_type: "lesson-plan"`, `pass: 1`
**Expected:**
- [ ] Irene produces lesson plan + slide brief only
- [ ] Returns `pass: 1` in structured outbound
- [ ] Does NOT produce narration script (that's Pass 2)
- [ ] Slide brief includes visual suggestions for Gary (descriptive, not prescriptive)
- [ ] Does NOT include `segment_manifest` in artifact_type

## Scenario 12: Two-Pass Model — Pass 2 (After Gary)
**Trigger:** Marcus context envelope with `pass: 2` and `gary_slide_output` array containing actual slide PNG paths
**Expected:**
- [ ] Irene reads `gary_slide_output` (PNG paths + visual descriptions)
- [ ] Writes narration to complement actual visuals (insight, not structure)
- [ ] Produces narration script with `[SEGMENT: seg-XX]` markers
- [ ] Produces paired segment manifest YAML
- [ ] Returns `artifact_type: segment_manifest` alongside `narration_script`
- [ ] `visual_file` in manifest populated for `visual_source: gary` segments (uses Gary's PNG paths)

## Scenario 13: Segment Manifest Generation
**Trigger:** After Pass 2 completes, inspect the generated manifest.yaml
**Expected:**
- [ ] All required schema fields present: `lesson_id`, `title`, `music_bed`, `segments` array
- [ ] Each segment has: `id`, `narration_ref`, `narration_text`, `visual_cue`, `visual_mode`, `visual_source`, `sfx`, `music`, `transition_in`, `transition_out`
- [ ] Write-back fields (`narration_duration`, `narration_file`, `narration_vtt`, `visual_file` for kira-sourced, `visual_duration`, `sfx_file`) are `null` — to be populated by downstream agents
- [ ] `visual_file` populated for `visual_source: gary` segments (from Gary's output)
- [ ] Segment IDs match `[SEGMENT: seg-XX]` markers in the paired narration script exactly

## Scenario 14: Pass 2 Without gary_slide_output (Degradation)
**Trigger:** Marcus sends Pass 2 envelope without `gary_slide_output` field
**Expected:**
- [ ] Irene requests Gary's slide output before proceeding
- [ ] Does NOT invent slide descriptions
- [ ] Reports to Marcus: "Pass 2 requires gary_slide_output — please complete Gary's slide generation and HIL Gate 2 review first"
