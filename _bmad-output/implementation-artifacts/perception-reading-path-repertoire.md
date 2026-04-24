# Story: Perception Reading-Path Repertoire

**Epic:** cross-cutting (Irene Pass 2 authoring surface + Marcus perception handoff)
**Status:** ratified-stub
**Sprint key:** `perception-reading-path-repertoire`
**Added:** 2026-04-24
**Points:** ~6 (stub estimate; expand at create-story)
**Depends on:** 7-1 Irene Pass 2 Authoring Template (done) — extends the segment-manifest schema and authoring template it shipped.
**Blocks:** nothing; unlocks non-Z-biased artifacts (hero graphics, infographics, multi-column handouts, quadrant matrices) for coherent narration.

## Story

As the perception-producing role (Marcus during source intake; Marcus + Irene during slide/video perception),
I want to classify each artifact with a **reading-path pattern** drawn from a closed repertoire and emit its perception scan *in that pattern's order*,
So that Irene's narration traces the natural reading path of the artifact rather than forcing a Z-scan onto sources where Z-flow doesn't exist (centered hero graphics, top-down spines, multi-column layouts, 2×2 matrices, etc.).

## Background

Trial C1-M1-PRES-20260419B established the on-the-fly convention that Marcus tags each slide/source with `narration_directive: z-pattern-literal-scan`, and Irene narrates in Z-scan order. The approach produced high-quality narration on Z-friendly artifacts but **struggled on artifacts whose visual or verbal structure did not match a Z-scan**.

Audit state (2026-04-24):
- The directive lives as a **free-text string** in the Pass-2 envelope — no enum, no schema validation ([pass-2-authoring-template.md:39](../../skills/bmad-agent-content-creator/references/pass-2-authoring-template.md#L39) explicitly permits unconstrained values).
- Four trial fixtures pinned the `z-pattern-literal-scan` value as golden ([trial_c1m1_canonical.yaml:21](../../tests/fixtures/7-1-irene-pass-2-authoring-template/pass_2_emissions/trial_c1m1_canonical.yaml#L21) and three malformed siblings) — byte-identical regression now protects Z-pattern success for those inputs.
- No code in Marcus, Irene, or the pass-2 emission lint binds narration shape to the directive value.

This story **promotes the convention to a contract** and extends it with a repertoire that covers the non-Z cases the trial surfaced.

## Repertoire (v1 closed enum)

| Pattern | When it applies | Canonical scan shape |
|---|---|---|
| `z_pattern` | Current default; quadrant-balanced slides with headline/body/visual/CTA | top-left → top-right → bottom-left → bottom-right |
| `f_pattern` | Text-heavy handouts, reference docs, dense prose columns | left-column top-down → selective right-side scan on evidence markers |
| `center_out` | Hero graphic with orbital annotations; central concept with radial supports | establish-hero → orbit-annotations clockwise → return-to-hero |
| `top_down` | Vertical spine; ordered lists; process ladders | single sweep top-to-bottom following spine |
| `multi_column` | 2–4 column layouts where each column is self-contained | column-major: each column top-to-bottom before advancing right |
| `grid_quadrant` | 2×2 or 3×3 matrices (comparison frameworks, decision grids) | declared sweep order (row-major default; column-major if axis labels demand) |
| `sequence_numbered` | Explicit ordinal markers (1→2→3, Step A → Step B) override spatial inference | follow ordinal order, ignore spatial layout |

Closed enum in v1. Extensibility via enum registry, not free-text. `custom` reserved but fail-closed.

## Acceptance Criteria (Stub Level)

- **AC-1:** Pass-2 envelope field `narration_directive` becomes an enum-constrained slot backed by a new `reading_path` sub-object: `reading_path: { pattern: <enum>, confidence: 0.0–1.0, evidence: {structured-details}, fallback: bool }`. Existing free-text `z-pattern-literal-scan` string normalized to `reading_path.pattern = "z_pattern"` with `fallback: false` at the lint layer.
- **AC-2:** Classifier step emits `{pattern, confidence, evidence}` during Marcus's perception handoff (source intake) and Irene's slide perception (Pass 2). Below confidence threshold (configurable; default 0.6), `pattern` falls back to `z_pattern` with `fallback: true`. Preserves current behavior as the floor.
- **AC-3:** Per-pattern ordered-scan emission: the perception artifact lists tokens in the order the declared pattern prescribes, each tagged `{position_in_path, role_hint, content}`. Irene consumes this sequence pattern-agnostically — the contract shape is stable across all patterns; only ordering logic differs.
- **AC-4:** [pass-2-authoring-template.md](../../skills/bmad-agent-content-creator/references/pass-2-authoring-template.md) extended with one narration-grammar rider per pattern (7 total: existing Z-pattern guidance preserved verbatim + 6 new riders). Each rider specifies the expected narration cadence, bridge phrasing, and connective tissue for that pattern.
- **AC-5:** [segment-manifest.schema.json](../../state/config/schemas/segment-manifest.schema.json) gains required `reading_path.pattern` enum validation at Pass-2 envelope and per-segment level. Template §39 "additive-permissive at envelope level" clause updated to reflect the narrower constraint.
- **AC-6:** [pass_2_emission_lint.py](../../scripts/validators/pass_2_emission_lint.py) gains pattern-aware shape checks (**warning-level, not fail-closed** in v1 — learn the edge cases before hard-gating):
  - `grid_quadrant` narration should contain compare/contrast connectives
  - `multi_column` narration should contain column-boundary bridges
  - `sequence_numbered` narration should contain ordinal markers
  - `center_out` narration should return to hero near end of scan
  - `top_down` narration should show cadence at spine-item boundaries
  - `f_pattern` narration should show drill-down on evidence markers
  - `z_pattern` narration preserves existing four-beat sweep (current behavior, now explicit)
- **AC-7:** Fixture set expanded — existing C1-M1 Z-pattern fixtures remain golden (regression proof); **5 new fixtures** added, one per non-Z pattern, with paired `as_emitted` + `canonical` + one malformed variant each. Fixture authoring uses the same trial-harvest rigor as 7-1.
- **AC-8:** **Byte-identical regression:** when Marcus/Irene process the existing C1-M1 trial artifacts and the classifier resolves to `z_pattern`, the output must be byte-identical to the pinned 7-1 canonical fixtures (modulo the new structured `reading_path` block being present; pinning updated to reflect normalization of the free-text directive).
- **AC-9:** **Portability guard (AST contract test):** this story must not import `marcus.orchestrator.*`, must not write to `lesson_plan.log`, and must not emit orchestrator events. Perception + authoring surface only. Guards the LangGraph-portability property.
- **AC-10:** User-memory reconciliation: the memory entry ["Z-pattern narration alignment"](../../../.claude/projects/...) (Marcus writes `z_pattern_literal_scan` for every slide before delegating; Irene narrates in Z-scan order) is superseded by this story. Memory update task at close: replace with "reading-path pattern classification — see reading-path-repertoire reference."
- **AC-11:** Lockstep check passes. No pytest regressions.

## File Impact (Preliminary)

- `state/config/schemas/segment-manifest.schema.json` — add `reading_path` sub-object + enum constraint (EXTEND existing schema from 7-1)
- `state/config/schemas/reading-path.schema.json` — **new** structured sub-schema for the `reading_path` block
- `state/config/reading-path-patterns.yaml` — **new** enum registry with per-pattern canonical-scan description + evidence-field schema
- `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md` — 6 new per-pattern narration-grammar riders + Z-pattern rider made explicit
- `skills/bmad-agent-marcus/scripts/classify_reading_path.py` — **new** classifier (Marcus-side, pre-delegation)
- `skills/bmad-agent-content-creator/scripts/classify_reading_path.py` — **new** classifier (Irene Pass-2-side, per-slide)
  - (Architecture decision at create-story time: one shared module under `scripts/` vs. two agent-owned wrappers. Winston call.)
- `scripts/validators/pass_2_emission_lint.py` — extend with 7 pattern-aware shape checks (warning-level)
- `tests/fixtures/perception_reading_path/` — **new** fixture directory; 5 non-Z fixtures + paired canonical/malformed variants
- `tests/irene/test_reading_path_classifier.py` — **new**
- `tests/irene/test_pass_2_emission_lint_reading_path.py` — **new**
- `tests/contracts/test_reading_path_portability_guard.py` — **new** AST contract test for AC-9
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — schema v1.2 entry (reading_path sub-object added)

## Notes for Create-Story

- **Classifier architecture decision (Winston):** vision-model call vs. heuristic layout parser vs. hybrid. Vision-model call is most flexible but introduces LLM dependency in perception critical path — weigh against determinism cost.
- **Confidence threshold (Murat):** 0.6 default is a placeholder. Story should define the empirical tuning protocol (trial → classification accuracy → threshold adjustment).
- **Irene grammar riders (Paige):** six new riders is on the edge of cognitive load. Consider whether `f_pattern` and `top_down` collapse in practice (both have vertical cadence). Audit at story close whether any pair should merge for v1.
- **LangGraph portability (operator):** AC-9 AST guard is load-bearing. This story is explicitly shaped to be a LangGraph-friendly leaf capability — classifier node in, perception-with-pattern out, Irene authoring against a stable contract. Anything that drags in orchestrator primitives is out of scope.
- **Do NOT expand repertoire in v1.** Six patterns + Z is v1. Add/merge only after one trial confirms which patterns actually fire. Extensibility is the enum registry itself, not free-text.
- **Relationship to 7-1 fixtures:** the 4 committed 7-1 fixtures are authoritative regression evidence. AC-8 byte-identical is non-negotiable — a failure there means the story broke Sprint 1 work.

## Party Input Expected at Create-Story

- **Winston** — classifier architecture (shared module vs. per-agent); schema-extension shape
- **Amelia** — dev-story task breakdown; K-floor (expect ~14-18 given the 11 ACs); dual-gate vs single-gate designation
- **Murat** — confidence-threshold empirical protocol; AC-8 byte-identical regression gate; AC-9 AST guard
- **Paige** — authoring-template rider quality; rider-count consolidation check; docs discoverability
- **Sally** — operator UX on classifier-confidence display; manual override path when classifier fires `fallback: true`

## Open Questions for Party-Mode

1. Should classifier output be operator-overridable at the Pass-2 envelope level (HIL affordance), or strictly automated? Default posture: auto with manual-override escape hatch, logged when used.
2. Lint warnings vs. fail-closed in v1 — is warning-level the right floor, or should `sequence_numbered` (the most structural) be fail-closed from the start?
3. Does this story precede or follow the Wondercraft specialist story in Sprint 2 sequencing? Reading-path-repertoire touches Irene's narration contract; Wondercraft is independent of Irene. Suggestion: parallel-safe.
