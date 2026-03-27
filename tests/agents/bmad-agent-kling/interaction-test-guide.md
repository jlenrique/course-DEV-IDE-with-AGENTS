# Interaction Test Guide — Kira (Kling Specialist, Video Director ??)

## Purpose
Verify Kira activates correctly, routes video requests through the `kling-video` skill, honors live-tested Kling API constraints, and returns structured output to Marcus.

## Prerequisites
- Kira's SKILL.md loaded in Cursor agent chat
- `scripts/api_clients/kling_client.py` present and authenticated
- `skills/kling-video/` built
- `resources/style-bible/` present

---

## Scenario 1: Interactive Activation
**Trigger:** "Talk to Kira" or "I need the Video Director"
**Expected:**
- [ ] Kira greets briefly and contextually
- [ ] References Kling pipeline as live and tested
- [ ] Offers clip-type exploration (B-roll, concept animation, transition, lip-sync)
- [ ] Does NOT dump a menu or generic media-tool list

## Scenario 2: Headless Delegation from Marcus
**Trigger:** Provide context envelope with `production_run_id`, `video_type`, `instructional_purpose`, `learning_objectives`
**Expected:**
- [ ] Parses envelope successfully
- [ ] Chooses correct video operation
- [ ] Routes execution through `kling-video`
- [ ] Returns structured output including `artifact_paths`, `generation_choices`, and `quality_assessment`

## Scenario 3: API Reality Awareness
**Trigger:** Ask Kira what Kling parameters matter most
**Expected:**
- [ ] References `model_name`, not `model`
- [ ] References `std` / `pro`, not standard/professional
- [ ] References type-specific status endpoint behavior
- [ ] References mandatory download of MP4 outputs

## Scenario 4: Cost-Aware Model Selection
**Trigger:** "Generate simple hospital B-roll for validation"
**Expected:**
- [ ] Recommends cheap baseline (`kling-v2-6`, `std`, `5s`) unless quality need justifies more
- [ ] Explains cost/quality tradeoff concisely

## Scenario 5: Pipeline Reuse
**Trigger:** Provide Gary slide PNG or mention it in source assets
**Expected:**
- [ ] Prefers image-to-video over regenerating the visual from text
- [ ] Explicitly notes reuse of Gary's output

## Scenario 6: Degradation Handling — Missing Asset
**Trigger:** Ask for lip-sync without audio or face/video asset
**Expected:**
- [ ] Returns `plan_only` or structured missing-asset guidance
- [ ] Does NOT hallucinate completion

## Scenario 7: No Woodshed Confusion
**Trigger:** Ask how Kira is validated
**Expected:**
- [ ] Says validation is by human review of sample videos
- [ ] Does NOT reference exemplar reproduction or woodshed scoring

## Scenario 8: Wrong-Agent Redirect
**Trigger:** "Create slides for this lesson"
**Expected:**
- [ ] Redirects to Gary / Marcus appropriately
- [ ] Does not attempt the wrong task
