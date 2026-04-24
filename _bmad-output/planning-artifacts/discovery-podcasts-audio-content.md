# Discovery — Podcasts & Audio Content

**Epic:** 18 — Additional Assets & Workflow Families
**Story:** 18-5 Discovery — Podcasts & Audio Content
**Status:** draft (awaiting sprint-level approval; implementation stories filed after approval)
**Authored:** 2026-04-24
**Sprint:** #2 "Portable Intake + Audio Production + Perception Repertoire"

## Summary

This document captures the discovery / requirements surface for adding podcast-style and audio-first content to the course-production workflow family. The target capability: operators can ask Marcus for "a podcast companion to this module" or "an audio summary of this lesson" and get a deterministically-assembled, G5-verified audio artifact without bespoke scripting.

The APP already has a **strong audio substrate** that this discovery reuses rather than reinventing:

- **ElevenLabs** (Story 3-4) — Voice Director agent with multi-voice, SFX, music, pronunciation dictionaries, and timestamp generation.
- **Wondercraft** ([scripts/api_clients/wondercraft_client.py](../../scripts/api_clients/wondercraft_client.py), 152 LOC, Story 5-4) — hardened API client wrapping the Wondercraft podcast-production surface (single-voice, conversation-mode, scripted-mode, async job polling).
- **Irene** (content-creator agent) — script authoring with Pass 1 (narrative) + Pass 2 (polished) separation.
- **Quinn-R** (quality-reviewer) — pre-composition fidelity review, already handles audio G5.
- **Vera** — G5 audio-fidelity verification gate.
- **sensory-bridges/audio_to_agent.py** — STT + transcript perception for audio artifacts.
- **compositor** — assembly-guidance pattern (reusable for audio assembly, paralleling how 24-2 Descript guide handles video post).

This discovery **builds on top** of that substrate. Implementation stories filed after approval will wrap the existing client surface into a specialist agent (Wanda, filed separately as `wondercraft-specialist-agent`) and define the workflow family.

## Goal 1 — Audio content type taxonomy

Five canonical audio content types, each with its own primary-use, length envelope, voice profile, and production tier. The taxonomy is deliberately **separable from Wanda's v1 capabilities** — Wanda may not ship all five on day one, and future audio-production agents (or an expanded ElevenLabs Voice Director) may fill in.

| Type | Primary use | Typical length | Voice profile | Prod tier |
|------|-------------|----------------|---------------|-----------|
| **Lecture podcast** | Long-form module summary or deep-dive episode; asynchronous companion to live lecture. | 12–30 minutes | Single voice, steady pacing, lecture register | Wondercraft `create_scripted_podcast` or ElevenLabs narration |
| **Interview / dialogue** | Two voices in conversation: host + guest, or two experts. Consumes dialogue-structured script. | 8–25 minutes | Two distinct voices, conversational register | Wondercraft `create_conversation_podcast` or ElevenLabs multi-voice |
| **Case discussion audio** | Two+ voices discussing a case study; scripted turn-taking with clinical reasoning beats. | 6–15 minutes | Two or three distinct voices, analytical register | Wondercraft conversation mode + ElevenLabs SFX for transition beats |
| **Audio summary / recap** | 2–4 minute wrap-up after a module or case; one voice, tight script. | 2–4 minutes | Single voice, summary register | ElevenLabs narration (lower cost than Wondercraft for short-form) |
| **Module bumper / intro** | Short branded intro (15–30 seconds) with music bed + single voice hook. | 0.25–0.5 minutes | Single voice + music bed | ElevenLabs narration + music bed |

**Rationale for keeping taxonomy separable from Wanda v1 (D5 ruling):** the taxonomy outlives Wanda — an operator may author a lecture-podcast script that Voice Director (ElevenLabs) narrates without any Wondercraft involvement. The taxonomy is a product-level description of what we ship; Wanda v1 is one (major) implementation surface.

## Goal 2 — Script structure

Three canonical script structures. Each is consumable by both Wondercraft and ElevenLabs (the difference is the API-layer encoding, which the specialist agent handles).

### Monologue

Single-voice narrative. Structure:

```text
[metadata block]
  title: <episode title>
  voice_id: <elevenlabs or wondercraft voice>
  duration_target_minutes: <int>

[body]
  <plain prose, optionally with SFX markers: [[sfx: transition_short]]>
  <pronunciation overrides: {"term": "pronounced"}>
```

### Dialogue (multi-voice)

Two or more voices, explicit speaker labels. Structure:

```text
[metadata block]
  title: <episode title>
  voices:
    host: <voice_id_A>
    guest: <voice_id_B>
  duration_target_minutes: <int>

[turns]
  - speaker: host
    text: <line>
  - speaker: guest
    text: <line>
  ...
```

### Interview (host + guest with narrative spine)

A dialogue with a narrative scaffold layered on top — intro script, question list, scripted responses, outro. Structure is a superset of Dialogue with the addition of a `scaffold` block:

```text
[scaffold]
  intro: <host opening monologue>
  outro: <host closing monologue>
  beats:
    - section: <name>
      questions: [<q1>, <q2>, ...]
[turns]
  ...
```

**Script-to-API mapping** — the Wondercraft specialist will translate these structures into the appropriate Wondercraft endpoint (`/podcast`, `/podcast/scripted`, `/podcast/convo-mode/user-scripted`). ElevenLabs narration consumes the monologue structure directly; dialogue/interview can be multi-voice-narrated through ElevenLabs with per-turn voice switching.

## Goal 3 — Agent role matrix

| Agent | Role in podcast production |
|-------|----------------------------|
| **Marcus** | Orchestrator. Operator dispatches "podcast this lesson" through Marcus; Marcus routes to Irene (script) → Wanda (production) → Quinn-R / Vera (quality) → compositor (assembly). |
| **Irene** | Script authoring (new "podcast-script" Pass 1/Pass 2 variants). Receives the approved lesson-plan artifacts and emits scripts in one of the three canonical structures above. |
| **Wanda** | New Wondercraft specialist (filed separately as `wondercraft-specialist-agent`). Owns capability cards for `podcast_episode_produce`, `podcast_dialogue_produce`, `audio_summary_produce`, `music_bed_apply`, `chapter_markers_emit`, `audio_assembly_handoff`. |
| **Voice Director (ElevenLabs)** | Narration specialist for monologue + short-form audio (audio summary, bumpers). When both ElevenLabs and Wondercraft are in play for the same lesson, Wanda consults Voice Director for voice-match consistency. |
| **Quinn-R** | Pre-composition quality review — runs the audio-aware G5 variant on the generated audio. |
| **Vera** | G5 gate — audio fidelity verification (existing Epic 2A pattern; no new gate needed — G5 is source-type agnostic for audio). |
| **Compositor** | Assembly guidance — produces the Descript assembly guide for any manual finish (paralleling 24-2 video-post pattern). Also handles RSS metadata emission for distribution. |
| **Texas** | Sources the underlying lesson material via existing directive pipeline — no new provider needed for podcast production (podcasts consume finalized lesson content, not raw sources). |
| **Tracy** | If the podcast needs enrichment research (e.g., case context), Tracy sources scite/Consensus cross-validation as with any other content pass. |

## Goal 4 — Production requirements

1. **Intro / outro templates** — project-level YAML at `state/config/audio/podcast-intro-outro.yaml` defining per-course or per-module intro/outro scripts. Wanda applies these at assembly time unless the directive overrides.
2. **Music beds** — a small library of royalty-free beds under `resources/audio/music-beds/` indexed by mood (calm / energetic / reflective / neutral). The specialist's `music_bed_apply` capability references the library by key.
3. **Chapter markers** — generated automatically from the script's `[beats]` or `[sections]` structure. Each beat/section becomes a chapter with `title` + `start_time_seconds`.
4. **Pronunciation dictionaries** — per-course pronunciation YAML lives alongside the course config, already wired for ElevenLabs; Wanda should honor the same file when producing Wondercraft audio that needs explicit pronunciations.
5. **VTT transcript generation** — every produced episode emits a `.vtt` transcript alongside the audio, for accessibility and searchability. Source: either the originating script (trivial mapping) or a post-production STT pass if the audio was regenerated.
6. **Loudness normalization** — target -16 LUFS for podcast content (standard for speech-centric distribution). Applied at assembly time; deferred to Descript if manual finish is selected.

## Goal 5 — Output formats

| Format | Use case | Who emits it |
|--------|----------|--------------|
| **MP3** (128–192 kbps) | Default distribution, maximally compatible | Wanda (default output) |
| **M4A with chapter metadata** | Enhanced podcast feeds (Apple Podcasts, Overcast) | Wanda with `chapter_markers_emit` |
| **WAV (uncompressed)** | Internal archival; master source for further production | Wanda on-demand |
| **VTT transcript** | Accessibility + SEO | Wanda (always emitted) |
| **RSS-ready metadata JSON** | Feed integration with publishing platforms | Compositor (assembly step) |
| **Descript project file** | Manual editing handoff | Compositor (assembly-guide output) |

## Goal 6 — Descript integration

**Pattern:** manual-tool (paralleling Story 24-2 for video-post). Descript is not automated — it is a handoff surface when the operator wants to polish dialogue, remove filler words, or re-cut sections.

**Deliverables from the compositor:**
1. A Descript-compatible project import (script + audio + chapter-marker list as a JSON sidecar).
2. An assembly guide document (markdown) walking the operator through the Descript project: recommended cuts, voice-match touchpoints, expected output specs.
3. Round-trip contract: when the operator finishes in Descript and exports audio, it flows back into the G5 gate the same way any other audio artifact does.

**Non-goal (explicit):** direct Descript API integration. The Descript round-trip is intentionally manual because it's a human-judgment surface (filler-word removal, pacing) that does not benefit from automation in v1.

## Goal 7 — Workflow family definition

The "podcast workflow family" is a named branch in the structural-walk manifest, activated when a lesson directive includes a `podcast` output spec. Structurally it mirrors the motion workflow family: static remains the default, podcast is additive.

### Pipeline

```text
Irene Pass 1 (lesson script)
-> Gate 2 (approve lesson script)
-> [branch: if podcast_enabled]
   -> Irene Pass 1 (podcast variant — consumes approved lesson script)
   -> Gate 2P (approve podcast script structure + voice choices)
   -> Wanda production (Wondercraft or ElevenLabs per capability card)
   -> G5 audio fidelity (Vera)
   -> Quinn-R quality review
   -> compositor audio assembly (chapter markers, RSS metadata, optional Descript handoff)
-> [rejoin main workflow]
```

### Control plane

`run-constants.yaml` gains:

```yaml
podcast_enabled: boolean                    # default false
podcast_profile: lecture | interview | case | summary | bumper
podcast_voice_policy:
  primary: <voice_id | "voice_director_auto">
  secondary: <voice_id | null>              # for dialogue / interview
podcast_budget:
  wondercraft_episodes: int                 # cap on Wondercraft API calls per run
  elevenlabs_minutes: int                   # cap on ElevenLabs minutes per run
descript_handoff: boolean                   # default false — emit Descript project
```

### Run-scoped sidecar

Podcast decisions (voice assignments, chapter plans, music bed choices) persist in a run-scoped `podcast_plan.yaml` alongside the existing `motion_plan.yaml` pattern. This is added to the manifest, not the pipeline schema.

### Gate behavior

- `Gate 2P` (podcast): approves the podcast-script-structure selection + voice-assignments before production. Parallel to `Gate 2M` for motion.
- `G5` (audio fidelity): **existing** gate — no new schema needed. G5 already treats audio artifacts source-agnostically.

### Non-goals for v1 workflow

- Video podcast (audio + simple slide track). Deferred to a follow-on; the motion workflow can produce the video companion separately if requested.
- Live-recording integration (operator records themselves and feeds in). Deferred — the v1 target is fully-synthetic audio from scripts.
- RSS publishing automation. v1 emits RSS-ready metadata JSON but does not push to a podcast host.

## Workflow family — structural-walk compatibility

The podcast family conforms to the structural-walk manifest shape locked in Sprint 1:

- A single-step addition to `state/config/pipeline-manifest.yaml` under a conditional branch (mirrors motion).
- New learning-event emitter: `Gate 2P` emits `approval` / `revision` events to the learning-events ledger (same schema as Gate 2M).
- New `block_mode_trigger_paths` entries: `state/config/audio/podcast-intro-outro.yaml`, the new Wanda capability-card files, and the `podcast_plan.yaml` schema (when promoted to `state/config/schemas/`).

No breaking changes to existing steps — static and motion workflows continue to pass without any podcast-related logic running when `podcast_enabled: false`.

## Implementation stories (filed after discovery approval)

Once this discovery is approved at sprint-level, the following implementation stories are queued to the backlog:

1. **18-5a Wanda production capability** — Wanda (wondercraft-specialist-agent) capability cards for all five audio content types. This story is partially scoped by the already-filed `wondercraft-specialist-agent` story; 18-5a may land as a follow-on iteration after Wanda-v1.
2. **18-5b Podcast script authoring (Irene extension)** — new Irene Pass 1/Pass 2 variants for podcast scripts in the three canonical structures.
3. **18-5c Gate 2P + podcast_plan.yaml** — new gate + sidecar in the structural-walk manifest.
4. **18-5d Compositor audio-assembly guide** — Descript handoff deliverable + RSS metadata emission.
5. **18-5e Audio G5 readiness check** — verify Vera's G5 handles all five audio content types at adequate fidelity; propose schema extensions if needed.

All five are filed to the deferred inventory at `_bmad-output/planning-artifacts/deferred-inventory.md` after this discovery is approved.

## Dependencies and references

- **Existing infrastructure** (reuse, do NOT rebuild):
  - Voice Director agent: [skills/bmad-agent-elevenlabs/SKILL.md](../../skills/bmad-agent-elevenlabs/SKILL.md)
  - ElevenLabs audio skill: [skills/elevenlabs-audio/](../../skills/elevenlabs-audio/)
  - ElevenLabs client: [scripts/api_clients/elevenlabs_client.py](../../scripts/api_clients/elevenlabs_client.py)
  - Wondercraft client: [scripts/api_clients/wondercraft_client.py](../../scripts/api_clients/wondercraft_client.py)
  - Compositor skill: [skills/compositor/](../../skills/compositor/)
  - Irene skill: [skills/bmad-agent-content-creator/](../../skills/bmad-agent-content-creator/)
  - Quinn-R skill: [skills/bmad-agent-quality-reviewer/](../../skills/bmad-agent-quality-reviewer/)
  - Audio bridge: [skills/sensory-bridges/scripts/audio_to_agent.py](../../skills/sensory-bridges/scripts/audio_to_agent.py)
  - G5 audio fidelity: Epic 2A (vera) — already source-type agnostic for audio.

- **Related stories:**
  - [Story 27-6 Box provider](../implementation-artifacts/27-6-box-provider.md) — Sprint 2 template
  - [Wondercraft specialist agent](../implementation-artifacts/wondercraft-specialist-agent.md) — Sprint 2 agent story (Wanda); 18-5 defines the taxonomy Wanda serves.
  - [Story 24-2 Descript guide](../implementation-artifacts/24-2-descript-assembly-guide-enhancement.md) — manual-tool precedent
  - [Story 14 Motion workflow](motion-enhanced-workflow-design.md) — workflow-family precedent

## Review checklist (AC-9)

- [ ] All seven goals addressed (Goals 1–7 above).
- [ ] Taxonomy ≥ five content types (lecture / interview / case / summary / bumper).
- [ ] Script structures define monologue, dialogue, interview.
- [ ] Agent role matrix covers ElevenLabs + Wondercraft + Irene + Quinn-R + compositor.
- [ ] Production requirements cover intro/outro, music beds, chapter markers, pronunciation, VTT.
- [ ] Output formats cover MP3 + enhanced (chapters) + transcript + RSS metadata.
- [ ] Descript integration evaluates workflow + manual-tool applicability + assembly-guide round-trip.
- [ ] Workflow family definition is structural-walk-manifest compatible.
- [ ] Implementation stories filed to deferred inventory (post-approval action).

## Party input captured (sprint green-light 2026-04-24)

- **D5 ruling:** kept standalone (rejected absorb-into-Wanda). Taxonomy outlives Wanda-v1 — a script-authoring story (18-5b) and a gate story (18-5c) will consume this taxonomy regardless of which specialist produces the audio.
- **Amelia / John:** 2 points firm (pure planning artifact). K≥2 tests: parity (all 7 goals covered) + link-validity (internal repo references resolve).
- **Paige:** discovery doc lives under `_bmad-output/planning-artifacts/` alongside sibling `motion-enhanced-workflow-design.md`, not in `docs/` — preserves the "planning vs. running docs" separation.
