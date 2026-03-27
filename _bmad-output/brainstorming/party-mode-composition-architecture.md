# Party Mode Decision Record: Audio/Video Composition Architecture

**Date:** 2026-03-27
**Participants:** Marcus (Orchestrator), Irene (Instructional Architect), Gary (Gamma Specialist, standby), Kira (Video Director), Quinn-R (Quality Guardian), Winston (System Architect)
**Trigger:** Pre-Story 3.4 architectural decision — how audio, video, and visual assets are composed into final instructional media
**Status:** DECIDED

---

## Decision Summary

**Descript is the sole composition platform.** All instructional media — regardless of complexity — flows through a single assembly workflow ending in Descript. No tool routing, no composition tiers. Agents produce assets and a structured assembly guide; the human composes and tweaks in Descript.

---

## Key Decisions

### D1: Silent Video + Smart Audio Model

- **Kling always produces silent video** (`sound-off`). Kling's native audio is atmospheric and uncontrollable — unsuitable for instructional content.
- **ElevenLabs owns all intentional audio**: narration, SFX, music, dialogue. No exceptions.
- **Kling lip-sync endpoint** reserved for special cases only (single-speaker talking head). Multi-speaker lip-sync deferred as too fragile for production.

### D2: Narration-Paced Video (Audio Drives Timing)

- Narration is the **content backbone** — it carries the pedagogy (Mayer's modality principle).
- ElevenLabs generates narration first; segment durations become the **timing contract** for video clips.
- Kira generates video clips matched to narration durations, not the reverse.
- **Exception:** Use Case 6 (concept explainer with visual metaphor) may require video-first timing. Handled case-by-case in the manifest.

### D3: Segment Manifest as Single Source of Truth

Irene produces a **segment manifest** (YAML) as a formal output artifact. This manifest:
- Is the machine-readable production contract consumed by all downstream agents
- References the paired narration script (human-readable prose document)
- Is written back to by downstream agents as they complete work (durations, file paths)
- Drives composition guide generation

**Manifest schema (core fields):**
```yaml
lesson_id: string
title: string
music_bed: string | null
segments:
  - id: string
    narration_ref: string          # pointer to script section
    narration_text: string         # actual narration content
    visual_cue: string             # description of intended visual
    visual_mode: enum              # static-hold | video | text-frame
    visual_source: enum            # gary | kira | null
    sfx: string | null
    music: enum                    # duck | swell | out | continue | null
    transition: enum               # cross-dissolve | fade | cut | none
    # Written back by downstream agents:
    narration_duration: float      # seconds (ElevenLabs)
    narration_file: string         # path to MP3 (ElevenLabs)
    narration_vtt: string          # path to VTT (ElevenLabs)
    visual_file: string            # path to PNG or MP4 (Gary or Kira)
    visual_duration: float         # seconds (derived or Kira)
    sfx_file: string | null        # path to SFX clip (ElevenLabs)
```

### D4: Two-Pass Irene Model

- **Pass 1 (before Gary):** Irene produces a **Lesson Plan** — learning objectives, content outline, concept sequence, visual suggestions. Gary uses this to craft his Gamma prompt.
- **Pass 2 (after Gary):** Irene reviews Gary's actual slide PNGs, then produces the **Narration Script + Segment Manifest** — writing narration that complements the specific visuals Gary created.
- This ensures slide-narration **complementarity** (narration explains insight, not what's visually obvious) per Mayer's multimedia coherence principle.

### D5: Descript as Sole Composition Platform

- **All seven use cases** converge into Descript. No FFmpeg/DaVinci/CapCut branching.
- Descript is classified as **Tier 3 (manual-tool pattern)** in the tool inventory.
- A **composition skill** generates a **Descript Assembly Guide** — a structured document with:
  - Ordered asset list (file paths for all PNGs, MP4s, MP3s, VTT files)
  - Track assignments (V1: video/images, A1: narration, A2: music, A3: SFX)
  - Timing table (segment start times derived from narration durations)
  - Music cues (duck/swell/out with timestamps)
  - Transition specs (type + duration between segments)
- Human opens Descript, imports assets, follows the guide, tweaks to taste, exports.

### D6: Four HIL Gates

```
HIL Gate 1: Review Irene's lesson plan (content accuracy, objectives)
     |
     v
HIL Gate 2: Review Gary's slides (visual quality, brand, content)
     |
     v
HIL Gate 3: Review Irene's narration script (narration quality, slide complementarity)
     |
     v
HIL Gate 4: Review final composed video from Descript (overall quality, accessibility)
```

Quinn-R runs automated quality checks between every gate. Human review time is spent on judgment calls, not formatting errors.

---

## Seven Instructional Use Cases

| # | Use Case | Audio Profile | Visual Profile | Notes |
|---|----------|--------------|----------------|-------|
| 1 | **Narrated slide deck** | Narration drives timing | Static PNGs + optional Kira animation | Bread-and-butter, ~60-70% of volume |
| 2 | **Dialogue / debate** | Multi-voice dialogue | Conversation B-roll, angle cuts | No lip-sync (Option C — avoid uncanny valley) |
| 3 | **Step-by-step walkthrough** | Narration with pause beats | Sequential step visuals | Manifest supports `pause-beat` segments |
| 4 | **Case study narrative** | Continuous narration + music | Varied visual sequence | Music ducking critical |
| 5 | **Assessment prompt** | Sparse narration + deliberate silence | Scenario clip + text frame | `narration: null` segments for observation |
| 6 | **Concept explainer** | Tightly choreographed with visual | Visual metaphor animation | Hardest; may need `sync_points` and video-first timing |
| 7 | **Module bumper** | Title VO + music sting | Branded template | Templatized, parameterized by module |

All seven flow through the same pipeline and end in Descript.

---

## Production Pipeline (Final)

```
Irene Pass 1: Lesson Plan (objectives, outline, visual suggestions)
    |
    v  [HIL Gate 1]
    |
Gary: Gamma slide deck → PNGs
    |
    v  [HIL Gate 2]
    |
Irene Pass 2: Narration Script + Segment Manifest
    |         (references Gary's actual PNGs)
    |
    v  [HIL Gate 3]
    |
ElevenLabs Agent: narration MP3 + VTT + SFX + music
    |              (writes durations back to manifest)
    |
    v
Kira: silent video clips matched to narration durations
    |  (only for segments with visual_mode: video)
    |
    v  [Quinn-R: pre-composition validation]
    |
Composition Skill: generates Descript Assembly Guide
    |
    v
Human: assembles + tweaks in Descript → exports MP4 + VTT
    |
    v  [HIL Gate 4 + Quinn-R: final validation]
    |
Done: final asset ready for Canvas deployment
```

---

## Architectural Implications

### For ElevenLabs Agent (Story 3.4)
- Reads segment manifest for narration text, SFX cues, music cues
- Generates narration per segment with word-level VTT timestamps
- Writes back: `narration_duration`, `narration_file`, `narration_vtt`, `sfx_file` per segment
- Multi-voice support for dialogue use cases (Use Case 2)
- Does NOT need to know about composition tooling

### For Irene (existing — needs update)
- New artifact type: **Segment Manifest** (YAML) alongside narration script
- Two-pass model formalized: Pass 1 (lesson plan) and Pass 2 (script + manifest)
- Manifest includes downstream annotations for ElevenLabs, Kira, and composition

### For Kira (existing — no change needed)
- Already produces silent video clips
- Reads manifest for `visual_mode`, `visual_source`, and target duration
- No architectural change required

### For New Compositor Agent/Skill (future story)
- Reads completed manifest (all agents have written back)
- Generates Descript Assembly Guide
- Classifies nothing — one tool, one workflow
- Descript added to tool inventory as Tier 3 manual-tool pattern

### For Quinn-R (existing — needs update)
- Two validation passes: pre-composition (asset quality) and post-composition (final output)
- Validates narration against manifest (WPM 130-170, VTT monotonicity, segment coverage)
- Validates video durations against narration durations (+-0.5s tolerance)
- Validates final export (audio levels, caption sync, accessibility compliance)

### For Marcus (existing — needs update)
- Pipeline dependency graph updated with two-pass Irene model
- Four HIL gates formalized
- Composition skill added as new pipeline stage

---

## Tool Inventory Updates

| Tool | Current Tier | Change |
|------|-------------|--------|
| Descript | Tier 3 (limited API) | Add as **composition platform**, manual-tool pattern |
| DaVinci Resolve | Not listed | **Deferred** — revisit if Descript proves limiting |
| FFmpeg | Not listed | **Available as utility** but not primary composition path |
| CapCut | Tier 3 | **No role** in this architecture |

---

## Open Items

1. **Descript Assembly Guide format** — exact template TBD during compositor skill creation
2. **Manifest schema finalization** — refine during Story 3.4 (ElevenLabs) as first consumer
3. **Use Case 6 sync_points** — advanced sub-segment timing deferred until a real concept explainer lesson requires it
4. **Music sourcing** — ElevenLabs sound generation vs. licensed tracks vs. both — decide during Story 3.4
5. **Irene artifact update** — formalize two-pass model and manifest output in Irene's agent definition
