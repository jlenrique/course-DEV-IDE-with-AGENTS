# Voice Director Interaction Test Guide

## Purpose

Verify the ElevenLabs specialist activates correctly, routes audio work through `elevenlabs-audio`, respects Marcus-mediated workflow rules, and returns structured narration outputs.

## Prerequisites

- `skills/bmad-agent-elevenlabs/SKILL.md` exists
- `skills/elevenlabs-audio/` exists
- `scripts/api_clients/elevenlabs_client.py` is configured
- `state/config/style_guide.yaml` contains ElevenLabs defaults or the prompt provides a `voice_id`

## Scenario 1: Interactive Activation
**Trigger:** "Talk to the Voice Director"
**Expected:**
- [ ] Greets as an audio specialist, not a generic assistant
- [ ] References narration/timing/pronunciation strengths
- [ ] Does not claim to bypass Marcus in the normal workflow

## Scenario 2: Headless Narration Delegation
**Trigger:** Provide Marcus-style envelope with script or manifest context
**Expected:**
- [ ] Treats Marcus as sender/broker
- [ ] Uses style-guide default voice unless `voice_id` override is present
- [ ] Returns structured output with audio path, VTT path, and narration duration

## Scenario 3: Pronunciation Management
**Trigger:** Ask how the specialist handles repeated medical terms
**Expected:**
- [ ] Recommends pronunciation dictionaries over ad hoc respelling
- [ ] Mentions `.pls` workflow and dictionary locators

## Scenario 4: Continuity Awareness
**Trigger:** Ask about a multi-slide narration sequence
**Expected:**
- [ ] Mentions `previous_request_ids` / `next_request_ids`
- [ ] Frames them as continuity tools for Marcus-mediated sequencing

## Scenario 5: Segment Voice Overrides
**Trigger:** Provide a manifest with a segment-level `voice_id`
**Expected:**
- [ ] Honors the segment override
- [ ] Falls back to lesson default when `voice_id` is `null`

## Scenario 6: Wrong-Agent Redirect
**Trigger:** "Generate the slides for this lesson"
**Expected:**
- [ ] Redirects to Gary / Marcus appropriately
- [ ] Does not attempt slide generation
