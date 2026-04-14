# Creative Director (CD) Agent

This skill defines the contract-first behavior for Creative Director outputs in Wave 2B.

## Purpose

Generate a deterministic creative directive artifact that can be consumed by downstream resolver wiring (`20c-13`) to populate run constants, especially `slide_mode_proportions`.

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
