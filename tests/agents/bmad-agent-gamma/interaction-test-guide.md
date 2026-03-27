# Interaction Test Guide — Gary (Gamma Specialist, Slide Architect 🎨)

## Purpose
Verify Gary activates correctly, communicates in agent-to-agent style, handles delegation from Marcus, and degrades gracefully when dependencies are unavailable.

## Prerequisites
- Gary's SKILL.md loaded in Cursor agent chat
- `.env` with GAMMA_API_KEY (for live API scenarios)
- Style guide at `state/config/style_guide.yaml`

---

## Scenario 1: Interactive Activation (First Run)
**Trigger:** "Talk to Gary" or "I need the Slide Architect"
**Expected:**
- [ ] Gary greets with mastery status: "[N] of [M] exemplars mastered"
- [ ] Reports style guide defaults loaded (or empty)
- [ ] Offers to start with woodshed or accept a task
- [ ] Does NOT dump a menu — context-aware greeting

## Scenario 2: Interactive Activation (Returning)
**Trigger:** "Talk to Gary" (with sidecar populated)
**Expected:**
- [ ] Gary reports current mastery status from sidecar
- [ ] References last session context if available
- [ ] Offers continuation or new task

## Scenario 3: Headless Delegation — Standard
**Trigger:** Marcus sends context envelope with content_type, input_text, learning_objectives
**Expected:**
- [ ] Gary parses envelope, validates required fields
- [ ] Makes parameter decisions (CT → PR → SG merge)
- [ ] Returns structured YAML response with status, artifact_paths, quality_assessment
- [ ] Does NOT greet or prompt the user

## Scenario 4: Headless Delegation — Expert Fast-Path
**Trigger:** Context envelope with `parameters_ready: true` and full parameter_overrides
**Expected:**
- [ ] Skips parameter recommendation flow
- [ ] Goes directly to merge + execute + QA + return
- [ ] Returns same structured format as standard delegation

## Scenario 5: Template-Based Generation
**Trigger:** Context envelope with `template_id` and `template_prompt`
**Expected:**
- [ ] Gary uses from-template endpoint
- [ ] Returns `generation_mode: "from-template"` in response
- [ ] Reports `template_used` in response

## Scenario 6: Missing Required Fields
**Trigger:** Context envelope missing `learning_objectives`
**Expected:**
- [ ] Gary flags the missing field to Marcus
- [ ] Does NOT proceed with generation
- [ ] Does NOT guess at learning objectives

## Scenario 7: Quality Self-Assessment
**Trigger:** After any generation
**Expected:**
- [ ] Returns structured quality scores (brand_compliance, content_fidelity, layout_integrity, accessibility, pedagogical_alignment)
- [ ] Includes embellishment detection (true/false with details)
- [ ] Scores are conservative (honest, not optimistic)

## Scenario 8: Wrong-Agent Redirect
**Trigger:** "Create a voiceover narration" or non-slide request
**Expected:**
- [ ] Gary redirects to Marcus or bmad-help
- [ ] Does NOT attempt non-slide work
- [ ] Stays in character

## Scenario 9: Gamma API Failure
**Trigger:** API returns error (simulate with invalid key or rate limit)
**Expected:**
- [ ] Reports error code and details to Marcus
- [ ] Suggests retry timing or alternatives
- [ ] Does NOT crash or lose context

## Scenario 10: Woodshed Exemplar Study
**Trigger:** "Study L1 exemplar" or "Go to the woodshed"
**Expected:**
- [ ] Loads exemplar catalog
- [ ] Checks circuit breaker limits
- [ ] Runs doc refresh protocol
- [ ] Analyzes brief, derives spec, executes reproduction

## Scenario 11: Embellishment Control
**Trigger:** Generation with `textMode: preserve` and constraining additionalInstructions
**Expected:**
- [ ] Includes embellishment constraint in API call
- [ ] Detects if Gamma added unauthorized content
- [ ] Reports constraint effectiveness in flags
- [ ] Records phrasing effectiveness in patterns.md (default mode)

## Scenario 12: Ad-Hoc Mode Behavior
**Trigger:** Context envelope with `run_mode: "ad-hoc"`
**Expected:**
- [ ] Generation proceeds normally
- [ ] QA still runs
- [ ] Does NOT write to patterns.md or chronology.md
- [ ] Only writes to transient section of index.md
