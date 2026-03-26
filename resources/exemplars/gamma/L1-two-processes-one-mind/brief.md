# Exemplar: Two Processes, One Mind

## Level: L1 (Simple)

Single slide. The simplest structural pattern — a parallel comparison layout.

## What This Is

A single Gamma slide comparing two parallel processes: Clinical Diagnosis and Design Thinking. Each process is shown as a vertical sequence of steps, with a unifying conclusion at the bottom connecting the two.

## Content

**Title**: Two Processes, One Mind

**Left column — Clinical Diagnosis:**
- History & Physical
- Form hypothesis
- Order labs & imaging
- Iterate until diagnosis

**Right column — Design Thinking:**
- Empathize with users
- Define the problem
- Ideate solutions
- Prototype & test

**Unifying statement**: Both require rapid hypothesis formation, experimentation, and iteration to find root causes.

## Why It's Good

- Clean parallel structure makes the comparison immediately visible
- Equal weight given to both sides — neither dominates
- Unifying conclusion draws the pedagogical connection
- Step sequences are concise — one phrase per step, no bloat
- The title frames the cognitive insight ("One Mind") before the evidence is shown

## Context Relationship

- Course: Applied Professional Communication / Innovation in Medicine
- Audience: Medical professionals / graduate health sciences students
- Learning objective: Students recognize that clinical reasoning and design thinking share the same cognitive process
- Pedagogical approach: Visual parallel to create an "aha" moment

## What the Agent Should Learn

1. Gamma can produce parallel-column comparison layouts from structured input
2. A single slide needs a clear title, two balanced content blocks, and a synthesis statement
3. The `additionalInstructions` parameter should specify "parallel comparison layout" or "two-column comparison"
4. `numCards: 1` for single-slide exemplars
5. Content should be concise — short phrases, not sentences

## Reproduction Notes

- The agent should reproduce this as a single Gamma card with parallel structure
- The API call should use `numCards: 1` and `textMode: generate` (or `preserve` if input is already structured)
- `additionalInstructions` should request a parallel/comparison layout
- Success = same content flow, same parallel structure, readable comparison
