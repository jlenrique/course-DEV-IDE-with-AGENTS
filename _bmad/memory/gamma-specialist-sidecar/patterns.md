# Gary — Learned Patterns

Append-only in default mode. Read-only in ad-hoc mode.
Periodically condense when entries exceed ~200 or ~5000 words.

## Parameter Effectiveness

### 2026-03-27 — Woodshed L1+L2 calibration (founding patterns)

**Rich visual instructions outperform suppression constraints.**
- `additionalInstructions` should DESCRIBE the desired visual outcome ("Create a visually striking two-column parallel comparison with clean icons for each column header") — not SUPPRESS Gamma ("Do not add content beyond what is provided").
- Suppression produces bare, visually poor output (8KB). Rich guidance produces professionally designed slides (40-187KB).
- Gamma is a visual design engine; constraining it to text-only defeats the purpose.

**`textMode: preserve` + rich `additionalInstructions` is the sweet spot.**
- `preserve` keeps the source text intact. `generate` rewrites it.
- Rich `additionalInstructions` guides the visual treatment of the preserved text.
- This combination gives text fidelity WITH visual richness.
- `generate` mode should only be used when the user provides an outline that Gamma should expand into full content.

**`imageOptions.source` should usually be left at default (not `noImages`).**
- `noImages` strips all visual accents, backgrounds, and imagery — producing bare text cards.
- Default lets Gamma add thematic accents that make slides look professional.
- Only suppress images when the content is a pure data visualization where Gamma imagery would distract.

**File size is a quality signal.**
- 8-15KB = bare text, no visual treatment (bad)
- 25-40KB = moderate visual treatment (acceptable)
- 50KB+ = rich visual treatment with imagery/accents (good)
- 150KB+ = full visual design with AI-generated or sourced imagery (excellent for impact slides)

**`inputText` should communicate intent, not just bare content.**
- Include contextual framing: "This slide compares two parallel processes to show they share the same cognitive pattern."
- Include structural cues: "Unifying insight:" prefix signals Gamma to treat that text as a synthesis statement.
- Keep descriptive context that you DON'T want on the slide in `additionalInstructions`, not `inputText` — Gamma preserves everything in `inputText` when using preserve mode.

## Embellishment Control

### 2026-03-27 — Calibrated from woodshed iterations

**Gamma WILL embellish in preserve mode — and that's usually fine.**
- Gamma adds sub-descriptions under brief bullet points (e.g., "History & Physical" becomes "History & Physical — Gather patient data through observation").
- This is beneficial for educational slides — it adds context for the learner.
- Only flag as a problem when Gamma adds WRONG content or changes the meaning.

**Targeted constraints work better than blanket suppression.**
- BAD: "Output ONLY the provided text. Do not add content." → kills visual treatment
- GOOD: "Keep bullet text concise — short phrases, not full sentences." → constrains text density without killing visuals
- GOOD: Describe the LAYOUT you want and let Gamma figure out the visual details

**Emojis are a judgment call.**
- Gamma sometimes adds emojis (🩺, 💡, 🔗) as visual accents
- For medical education: occasionally acceptable (🩺 for clinical, 💡 for innovation) but not preferred for formal content
- If emojis are unwanted: add "Do not use emoji icons" to `additionalInstructions`

## Theme Pairings

_No theme-specific pairings recorded yet. Will populate as production runs with specific themes complete._

## Content Type Insights

### 2026-03-27 — From L1+L2 exemplar work

**Parallel comparison (two-column):** Rich `additionalInstructions` describing column headers, step lists, and unifying statement produces excellent results. Gamma naturally creates balanced two-column layouts when given clear structural description.

**Bold headline (single-focus):** Minimal `inputText` with a strong title + short body paragraph. `additionalInstructions` should request "bold, impactful, dominant title." Gamma excels at this — high visual impact with minimal content. Let Gamma add a background image for impact.
