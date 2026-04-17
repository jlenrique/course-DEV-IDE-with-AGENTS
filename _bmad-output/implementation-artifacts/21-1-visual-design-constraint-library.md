# Story 21-1: Visual Design Constraint Library

**Epic:** 21 - Gary Cluster Dispatch — Gamma Interpretation
**Status:** ready-for-dev
**Sprint key:** `21-1-visual-design-constraint-library`
**Added:** 2026-04-11
**Validated:** 2026-04-11
**Depends on:** [20a-2-interstitial-brief-specification-standard.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/20a-2-interstitial-brief-specification-standard.md), [19-2-gary-dispatch-contract-extensions.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/implementation-artifacts/19-2-gary-dispatch-contract-extensions.md)

## Story

As Gary,
I want a constraint library defining locked Gamma prompt parameters per interstitial type,
So that I can produce visually coherent interstitials that inherit the head slide's DNA and never introduce decorative drift — constraining Gamma's generation rather than hoping it follows vague instructions.

## Acceptance Criteria

**Given** Gary receives an interstitial brief with one of the five canonical types  
**When** Gary constructs the Gamma API prompt for that interstitial  
**Then** the prompt parameters must follow the locked constraints for that interstitial type, not Gary's general parameter recommendation flow

**And** the constraint library must define per-type rules for:
- What to INHERIT from the head slide (palette, accent color, background treatment)
- What to INCLUDE (element count caps, layout rules, typography guidance)
- What CANNOT be included (explicit prohibitions per type)

**And** each interstitial type must specify:
- `reveal`: inherit head palette + accent color, single element focus, max 2 visual elements
- `emphasis-shift`: inherit head accent color, isolate one text block, suppress all others
- `bridge-text`: inherit head atmospheric background, single phrase in large type, no imagery
- `simplification`: inherit head palette, disable multi-column layout, one data series only
- `pace-reset`: minimal chrome, icon or whitespace only, head palette undertone

**And** the library must be stored as a reference document in Gary's skill directory accessible during prompt construction

**And** Gary's SKILL.md must be updated to add a `VC` capability row (visual constraint library) that loads the new reference

## Tasks / Subtasks

- [ ] Task 1: Define constraint rules per interstitial type (AC: 1-3)
  - [ ] 1.1: Define `reveal` constraints — inheritance, inclusion, and prohibition rules
  - [ ] 1.2: Define `emphasis-shift` constraints
  - [ ] 1.3: Define `bridge-text` constraints
  - [ ] 1.4: Define `simplification` constraints
  - [ ] 1.5: Define `pace-reset` constraints
  - [ ] 1.6: For each type, define explicit "CANNOT include" rules (what Gamma must NOT generate)

- [ ] Task 2: Map constraints to Gamma API parameters (AC: 1)
  - [ ] 2.1: For each type, specify the locked `textMode` value (preserve | auto | custom)
  - [ ] 2.2: For each type, specify locked `additionalInstructions` templates that enforce constraints
  - [ ] 2.3: For each type, specify element count caps that map to `numCards` and visual density guidance
  - [ ] 2.4: Document which Gamma parameters are locked (not overridable) vs. inherited from head

- [ ] Task 3: Create reference document and update Gary SKILL.md (AC: 4-5)
  - [ ] 3.1: Create `skills/bmad-agent-gamma/references/interstitial-visual-constraints.md` with the full library
  - [ ] 3.2: Update [Gary SKILL.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-gamma/SKILL.md) to add `VC` capability row (visual constraint library for cluster interstitials)

## Dev Notes

### Scope Boundary

This story defines the **constraint reference document only**. It does not implement:
- Prompt template generation (Story 21-2)
- Dispatch sequencing (Story 21-3)
- Coherence validation (Story 21-4)

The constraint library is consumed by Story 21-2 when Gary constructs actual Gamma prompts.

### Interstitial Type Vocabulary

Use the canonical five-type vocabulary from `interstitial-brief-specification.md`:
- `reveal` | `emphasis-shift` | `bridge-text` | `simplification` | `pace-reset`

Do NOT use operational verbs (isolate, remove, enlarge). The constraint library keys off the type name.

### Constraint Structure Per Type

Each type entry in the reference document should follow this structure:

```markdown
## [type-name]

### Inherit from head
- [palette, accent color, background treatment, typography — what carries over]

### Include (locked parameters)
- Element count cap: [N]
- Layout: [locked layout rule]
- textMode: [preserve | auto | custom]
- additionalInstructions template: [locked prompt text]

### CANNOT include (prohibitions)
- [List of what Gamma must NOT generate for this type]
```

### Gamma API Parameter Context

Gary uses these Gamma API parameters (from `parameter-recommendation.md` and `style-guide-integration.md`):
- `textMode`: preserve (exact text), auto (Gamma decides), or custom
- `numCards`: slide count
- `additionalInstructions`: free-text prompt that augments the slide brief
- `imageOptions.source`: web | ai_generated | none
- Theme/style parameters from `gamma-style-presets.yaml`

For interstitials, the constraint library LOCKS certain parameters rather than letting Gary's normal recommendation flow decide. The locked values override the style guide defaults for that card only.

### Element Count Caps (from Epic 21-2)

The epic defines these caps:
- `reveal` / `emphasis-shift`: max 2 visual elements
- `bridge-text`: 1 element (text only)
- `simplification`: 1 data series
- `pace-reset`: 0 content elements (icon or whitespace only)

### Previous Story Intelligence

- **20a-2** defined the interstitial brief specification with 6 required fields. The constraint library complements the brief by defining what Gary does with each type — the brief says WHAT the interstitial is; the constraints say HOW Gary generates it.
- **19-2** extended Gary's output contracts to carry cluster metadata. The constraint library informs the prompt construction that happens before dispatch.
- Gary's existing `parameter-recommendation.md` handles general parameter selection. The constraint library provides interstitial-specific overrides that take precedence.

## Testing Requirements

This is a design/reference story. No automated tests required. Validate by document quality review — each type has complete inheritance, inclusion, and prohibition rules, and the Gamma parameter mappings are specific enough to implement in 21-2.

## Project Structure Notes

- **New file:** `skills/bmad-agent-gamma/references/interstitial-visual-constraints.md`
- **Modified file:** `skills/bmad-agent-gamma/SKILL.md` — add VC capability row

## References

- [epics-interstitial-clusters.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/_bmad-output/planning-artifacts/epics-interstitial-clusters.md) — Story 21.1 definition and element count caps
- [interstitial-brief-specification.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-content-creator/references/interstitial-brief-specification.md) — canonical 5-type vocabulary and brief field definitions
- [parameter-recommendation.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-gamma/references/parameter-recommendation.md) — Gary's existing parameter selection logic
- [style-guide-integration.md](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/skills/bmad-agent-gamma/references/style-guide-integration.md) — style guide defaults the constraints override
- [gamma-style-presets.yaml](C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS/state/config/gamma-style-presets.yaml) — theme/style presets

## File List

- skills/bmad-agent-gamma/references/interstitial-visual-constraints.md (new)
- skills/bmad-agent-gamma/SKILL.md (modified)

## Dev Agent Record

### Agent Model Used

claude-opus-4-6[1m]

### Debug Log

### Completion Notes List

### File List

## Status

ready-for-dev

## Completion Status

Ultimate context engine analysis completed — comprehensive developer guide created for Gary's visual design constraint library story.
