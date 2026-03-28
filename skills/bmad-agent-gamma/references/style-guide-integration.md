# Style Guide Integration (SG)

Read, apply, and write-back Gamma parameter preferences through the style guide system.

## Reading Defaults

On every invocation, read `state/config/style_guide.yaml` → `tool_parameters.gamma`:

```yaml
gamma:
  default_llm: ""
  style: ""
  format: ""
  slides_per_section: null
```

Empty or null values mean no preference established yet — use Gamma API defaults or content-type template recommendations.

## Merge Logic

Parameters are resolved in this order (later wins):

1. **API defaults** — Gamma's own defaults for unspecified parameters
2. **Style guide** — `tool_parameters.gamma` values (if non-empty)
3. **Style preset** — Named visual-identity preset from `state/config/gamma-style-presets.yaml` (if resolved via SP capability). Adds image model, image style + keywords, text mode, format variant, default card count, base `additionalInstructions`, and other parameters that supplement the theme. Resolved by preset name, theme_id match, or scope match. See `./style-preset-library.md`.
4. **Content type template** — from content-type-mapping.md (if applicable)
5. **Context envelope** — Marcus's delegation overrides
6. **Per-request adjustment** — Gary's judgment based on specific content analysis

**Special: `additionalInstructions` concatenation.** Unlike other parameters where later levels override earlier ones, `additionalInstructions` is **concatenated** across all levels. The preset provides a base instruction (e.g., "Keep the style of all the images uniform"), content-type templates append specifics (e.g., "One key concept per card"), and envelope overrides add final adjustments. All fragments are joined with a space.

## Style Bible Consultation

Read `resources/style-bible/` fresh from disk when visual decisions are needed. Key sections for Gamma work:

- **Color Palette** — JCPH Navy (#1e3a5f), Medical Teal (#4a90a4), white (#ffffff), orange accents (#fd7e14)
- **Typography** — Montserrat 600/700 headlines, Source Sans Pro 400/600 data labels
- **Chart and Data Visualization** — clean, minimal, signal over noise
- **Accessibility** — WCAG 2.1 AA: 4.5:1 normal text, 3:1 large text, color independence
- **Gamma Prompt Template** — style bible may include a base prompt template for Gamma

Never cache style bible content in memory. Always re-read.

## Write-Back (Default Mode Only)

When a production run succeeds and the user approves the output, save learned preferences via the production-coordination skill's `manage_style_guide.py`:

- Effective theme IDs for specific content types
- LLM preferences that produced better results
- Format/layout preferences the user approved
- `additionalInstructions` phrasings that controlled embellishment effectively

Write-back is suppressed in ad-hoc mode.

## Style Preset Proposals (Default Mode Only)

When a successful run uses a theme + parameter combination that is **not** yet captured in a named style preset, Gary may propose a new preset to the user (see `./style-preset-library.md` for the proposal flow). Proposals are always presented for human approval — Gary never writes to `gamma-style-presets.yaml` directly.
