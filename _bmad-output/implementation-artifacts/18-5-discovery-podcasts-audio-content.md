# Story 18.5: Content Type Discovery — Podcasts & Audio Content

**Epic:** 18 — Additional Assets & Workflow Families
**Status:** backlog
**Sprint key:** `18-5-discovery-podcasts-audio-content`
**Added:** 2026-04-06
**Depends on:** Core pipeline stability. Existing ElevenLabs specialist and audio infrastructure.

## Summary

Discovery-first story: elicit detailed requirements for podcast and audio-first content production. The APP already has a strong ElevenLabs specialist with multi-voice, timestamp, pronunciation dictionary, and SFX capabilities. The Wondercraft API client exists for enhanced podcast features. This discovery should build heavily on existing audio infrastructure rather than starting from scratch.

## Goals

1. Define audio content types: lecture podcast, interview/dialogue, case discussion audio, audio summary/recap.
2. Define script structure: monologue, dialogue with multiple voices, interview format.
3. Map agent roles leveraging existing ElevenLabs and Wondercraft infrastructure.
4. Identify production requirements: intro/outro, music beds, chapter markers, transcripts.
5. Define output formats for podcast distribution.
6. Evaluate Descript integration for editing.
7. Define the workflow family.

## Existing Infrastructure To Reuse

- `skills/bmad-agent-elevenlabs/` — Voice Director agent (Story 3.4): multi-voice narration, dialogue, SFX, music
- `skills/elevenlabs-audio/` — ElevenLabs audio skill: timestamp generation, pronunciation dictionaries, SFX packages
- `scripts/api_clients/elevenlabs_client.py` — full ElevenLabs API client (TTS, voices, pronunciation, SFX, music)
- `scripts/api_clients/wondercraft_client.py` — Wondercraft API client (Tier 2: enhanced podcast features)
- `skills/compositor/` — composition/assembly guidance pattern (reusable for audio assembly)
- `skills/bmad-agent-content-creator/` (Irene) — script writing for audio content
- `skills/bmad-agent-quality-reviewer/` (Quinn-R) — audio quality review (pre-composition pass)
- `skills/sensory-bridges/` — audio sensory bridge (STT extraction, content verification)
- Existing G5 audio fidelity verification pattern from Epic 2A

## Key Files

- `_bmad-output/planning-artifacts/discovery-podcasts-audio-content.md` — new: requirements document
- `_bmad-output/planning-artifacts/epics.md` — update: implementation stories added after approval

## Acceptance Criteria

1. Requirements document covers all seven goals above.
2. Audio content type taxonomy includes at least: lecture podcast, interview/dialogue, case discussion audio, audio summary/recap, module bumper/intro.
3. Script structure section defines: monologue, multi-voice dialogue (ElevenLabs voice assignment), interview format with host/guest roles.
4. Agent role matrix shows ElevenLabs specialist (audio production), Wondercraft (enhanced features), Irene (script), Quinn-R (quality), compositor (assembly guidance).
5. Production requirements section covers: intro/outro templates, music bed selection, chapter markers, VTT transcript generation, pronunciation dictionaries.
6. Output format section covers: MP3 (standard), enhanced podcast with chapters (M4A), transcript + VTT, RSS-ready metadata.
7. Descript integration section evaluates: editing workflow, manual-tool pattern applicability, assembly guide compatibility.
8. Workflow family definition compatible with structural-walk manifest pattern.
9. Document reviewed and approved before implementation stories are created.
