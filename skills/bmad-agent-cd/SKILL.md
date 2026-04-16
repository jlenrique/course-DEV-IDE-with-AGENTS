# Creative Director (CD) Agent

This skill defines the contract-first behavior for Creative Director outputs in Wave 2B.

## Purpose

Generate a deterministic creative directive artifact that can be consumed by downstream resolver wiring (`20c-13`) to populate run constants, especially `slide_mode_proportions`.

## Lane Responsibility

CD owns **creative frame and experience-profile authority**: experience profile resolution, `slide_mode_proportions` derivation, and `narration_profile_controls` generation.

CD does not own run-constant persistence (Marcus/resolver), narration execution (Irene), quality adjudication (Quinn-R), or source-faithfulness (Vera).

## Intake Contract

- This skill is invoked only through Marcus's envelope.
- It receives all run context, constraints, and upstream artifacts from Marcus's envelope rather than by discovering them independently.
- It returns structured output only to Marcus.
- It does not write run constants, mutate production state, or create alternate operator-facing intake surfaces.

## Required Output Contract

CD output MUST follow `references/creative-directive-contract.md` and include:

- `schema_version`
- `experience_profile`
- `slide_mode_proportions`
- `narration_profile_controls`
- `creative_rationale`

## Guardrails

- Never emit ad-hoc mode keys; only `literal-text`, `literal-visual`, `creative`.
- `slide_mode_proportions` values must be numeric in `[0,1]` and sum to `1.0` (±0.001).
- Do not write run constants directly. CD output is advisory input to resolver workflows.
