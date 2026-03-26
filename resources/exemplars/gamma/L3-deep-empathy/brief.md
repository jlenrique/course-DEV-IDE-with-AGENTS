# Exemplar: Deep Empathy (Three Qualities)

## Level: L3 (Moderate)

Single slide. Three-column card layout with icon-style sections, each containing a quality name and supporting description.

## What This Is

A single Gamma slide presenting three professional qualities in a card/column layout: Deep Empathy, Intellectual Curiosity, and Resilience Under Pressure. Each quality has a name as heading and a brief supporting description.

## Content

**Section 1 — Deep Empathy:**
Understanding patient experience drives better diagnosis

**Section 2 — Intellectual Curiosity:**
Staying current with latest research and evidence

**Section 3 — Resilience Under Pressure:**
Making critical decisions in high-stakes environments

## Why It's Good

- Three-column structure is visually balanced and scannable
- Each quality follows the same pattern: name + one-line description
- Descriptions connect the quality to professional practice (not abstract definitions)
- No title card clutter — the three qualities ARE the content
- Progressive complexity: empathy (patient-facing) → curiosity (knowledge) → resilience (action)

## Context Relationship

- Course: Applied Professional Communication / Innovation in Medicine
- Audience: Medical professionals reflecting on their existing strengths
- Learning objective: Students identify three transferable qualities they already possess
- Pedagogical approach: Self-recognition — naming capabilities students already have

## What the Agent Should Learn

1. Gamma can produce three-column card layouts when instructed properly
2. Each card follows a consistent pattern: heading + one-line description
3. `additionalInstructions` should request "three-column card layout" or "three feature cards"
4. The content structure must be provided in a way that Gamma maps to cards (e.g., `\n---\n` separators or structured input)
5. More complex than L1-L2 because layout precision matters — the three cards must be visually equal

## Reproduction Notes

- `numCards: 1` (this is one slide with three internal sections, not three slides)
- `textMode: preserve` to keep exact phrasing
- `additionalInstructions`: request three-column card/feature layout
- Consider using `cardSplit: inputTextBreaks` if formatting the three sections as separate blocks
- Success = three visually balanced sections with correct headings and descriptions
