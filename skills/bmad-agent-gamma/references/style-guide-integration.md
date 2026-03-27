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
3. **Content type template** — from content-type-mapping.md (if applicable)
4. **Context envelope** — Marcus's delegation overrides
5. **Per-request adjustment** — Gary's judgment based on specific content analysis

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
