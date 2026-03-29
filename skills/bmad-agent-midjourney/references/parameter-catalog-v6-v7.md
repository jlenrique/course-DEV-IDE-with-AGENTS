# Midjourney v6/v7 Parameter Catalog

Core parameters to tune in prompt specs:

- --ar (aspect ratio)
- --style (style strength)
- --chaos (variation spread)
- --stylize (stylization intensity)
- --seed (repeatability)
- --no (hard exclusions)
- --sref (style reference)
- --cref (character reference)

Parameter baseline guidance:

- `--ar`: match destination first (16:9 for slides/video plates, 1:1 for icon systems).
- `--stylize`: start low-to-mid for clinical fidelity; increase only after structure is validated.
- `--chaos`: keep low for production candidates, raise only during exploration passes.
- `--seed`: lock once candidate direction is approved to support reproducibility.
- `--no`: include explicit artifact deny-list (watermarks, labels, extra digits, distorted anatomy).
- `--sref` and `--cref`: apply only when style/character consistency is required across a set.

Version decision guidance:

- Prefer v6 when anatomical consistency and deterministic revision loops are primary.
- Prefer v7 when composition creativity is needed after structure is already validated.
- Do not switch model versions mid-run unless documenting rationale and resetting baseline comparisons.

Practical guardrails:

- Start `--chaos` low (for example 0-20) for instructional assets.
- Increase `--stylize` gradually and only after factual structure passes review.
- Keep one fixed seed during convergence; change seed only for intentional diversification.

Guidance:

1. Use fixed seed for iterative review loops.
2. Use --no aggressively for prohibited artifacts (watermarks, labels, extra hands, etc.).
3. Use conservative chaos for medical visuals that require structure.
4. For comparative batches, vary one parameter at a time.
5. Capture every accepted or rejected iteration with `run_id`, `seed`, `parameter_delta`, and rationale.
6. Record model version (`v6` or `v7`) in every iteration entry.

## Iteration Protocol

1. Baseline run: one prompt, one seed, default-safe parameters.
2. Exploration run: vary one control (for example `--stylize`) and compare outcomes.
3. Convergence run: lock chosen settings and test a final quality pass.
4. Final package: return prompt text, full parameter string, seed, selected candidate references, and known caveats.
