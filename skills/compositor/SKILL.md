---
name: compositor
description: Generate a Descript Assembly Guide from a completed segment manifest so humans can assemble narrated lesson media consistently.
---

# Compositor

## Purpose

Provides the composition-planning skill layer for the narrated lesson pipeline. The compositor reads a completed segment manifest and produces a Descript Assembly Guide that tells a human exactly how to assemble the lesson in Descript: asset order, track assignment, timing, transitions, music cues, and intent-preserving edit notes.

This is a **skill**, not a specialist agent. Marcus invokes it after Quinn-R's pre-composition pass.

## Key Paths

| Path | Purpose |
|------|---------|
| `./references/assembly-guide-format.md` | Canonical structure of the generated Descript Assembly Guide |
| `./references/manifest-interpretation.md` | Rules for interpreting manifest fields into assembly instructions |
| `./scripts/compositor_operations.py` | Manifest parser + assembly-guide generator |

## Operating Rules

- Read only completed manifests with audio and visual write-back fields populated.
- Treat `behavioral_intent` as a first-class assembly cue.
- Generate guidance that a non-technical human can follow in Descript without guesswork.
- Never rewrite the manifest’s pedagogical meaning during composition; preserve the approved intent.
