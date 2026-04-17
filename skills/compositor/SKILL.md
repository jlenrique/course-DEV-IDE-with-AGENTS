---
name: compositor
description: Generate a Descript Assembly Guide from a completed segment manifest so humans can assemble narrated lesson media consistently. Use when the user asks to talk to Mike, invokes the compositor, or when Marcus needs an assembly guide generated after Quinn-R's pre-composition pass.
---

# Mike (Compositor)

## Purpose

Mike provides the composition-planning skill layer for the narrated lesson pipeline. He reads a completed segment manifest and produces a Descript Assembly Guide that tells a human exactly how to assemble the lesson in Descript: asset order, track assignment, timing, transitions, music cues, and intent-preserving edit notes.

This is a **skill**, not a specialist agent in the LLM-persona sense — Mike is the operator-persona handle for the compositor skill. It runs deterministically via `scripts/compositor_operations.py`. Marcus invokes it after Quinn-R's pre-composition pass.

## Lane Responsibility

Mike owns **composition planning execution quality**: deterministic manifest interpretation and clear assembly instructions for human execution in Descript.

Downstream, **`bmad-agent-desmond` (Desmond)** produces **`DESMOND-OPERATOR-BRIEF.md`** (prompt pack **14.5**): run-tailored Descript vocabulary and a mandatory **Automation Advisory** — it does not replace this guide’s segment order or asset inventory.

Mike does not own instructional design decisions, source-faithfulness adjudication, or quality gate authority.

## Key Paths

| Path | Purpose |
|------|---------|
| `./references/assembly-guide-format.md` | Canonical structure of the generated Descript Assembly Guide |
| `./references/manifest-interpretation.md` | Rules for interpreting manifest fields into assembly instructions |
| `./scripts/compositor_operations.py` | Manifest parser, `sync-visuals`, assembly-guide generator |

## Operating Rules

- Read only completed manifests with audio and visual write-back fields populated.
- Treat `behavioral_intent` as a first-class assembly cue.
- Preserve `bridge_type` when present so explicit learner-facing intros/outros are not edited out accidentally.
- Generate guidance that a non-technical human can follow in Descript without guesswork.
- Never rewrite the manifest’s pedagogical meaning during composition; preserve the approved intent.

*Naming note: "Compositor" remains the lane/skill name used in contracts, lane-matrix, and scripts. "Mike" is the persona/conversation handle. References to "compositor" in contracts and scripts are not renamed — they denote the skill, which Mike operates.*

## Assembly bundle: localize approved visuals

When a **completed assembly bundle** is ready (audio, captions, ElevenLabs summary, Descript Assembly Guide, and manifest in one folder), **copy** Gate‑2‑approved stills out of the Gary/Gamma export tree into that bundle so humans and Descript see a single directory.

1. Run `sync-visuals` (updates `visual_file` paths in the manifest in place, preserving YAML layout):

   `.\.venv\Scripts\python.exe skills/compositor/scripts/compositor_operations.py sync-visuals path/to/manifest.yaml`

   Stills land in `path/to/visuals/` (override with `--subdir`).

2. Regenerate the assembly guide so paths point at the localized copies:

   `.\.venv\Scripts\python.exe skills/compositor/scripts/compositor_operations.py guide path/to/manifest.yaml path/to/DESCRIPT-ASSEMBLY-GUIDE.md`
