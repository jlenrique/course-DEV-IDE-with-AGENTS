# Session Handoff — 2026-04-05 Literal-Visual Reliability Fix

## Session Mode

- Execution mode: APP code changes + live API testing
- Quality preset: production
- Branch: `phase-02/sunday-2026-04-05`
- BMad workflow: Party Mode consensus at each decision gate

## Session Summary

Investigated and fixed unreliable literal-visual slide generation when Gary dispatches to the Gamma template API (`/generations/from-template`). Used live API testing with prompt harness, Gamma developer docs (developers.gamma.app), and visual inspection to identify root causes. BMad Party Mode (Gary, Winston, Quinn, Amelia) guided all decisions.

## Root Cause Findings

1. **Gamma classifies images as accent or background by visual content** — diagrammatic/infographic images get "accent" placement (cropped/positioned), photographic/dense images get "background" (full-bleed). This classification is **not controllable via the API** (confirmed by developers.gamma.app: "Accent images are automatically placed by Gamma — they cannot be directly controlled via the API.").

2. **Background-classified images are faded by default** — Gamma applies reduced opacity when placing images as backgrounds. An explicit anti-fade prompt ("at full opacity, not as background, not faded") overrides this.

3. **Template endpoint rejects `imageOptions.source`** — HTTP 400 with "imageOptions.property source should not exist". Template `g_gior6s13mvpk8ms` uses image source: `placeholder`. The `source: noImages` parameter that works on the standard generate endpoint is invalid for templates.

4. **Image size/dimensions do not determine classification** — tested resized card-02 (1376x768, same dims as card-09): still classified as accent. Classification is content-driven.

## Completed Outcomes

1. **Anti-fade prompt**: "Replace the placeholder image with this image at full opacity (not as background, not faded). The image must be the primary visual element filling the entire card. No text overlay." Proven 3/3 reliable for background-classified images.
2. **Fail-fast strategy**: Template retries reduced from 3 to 1 — single attempt, then immediate composite fallback.
3. **Export settle delay**: Increased from 10s to 15s (matches all successful test conditions).
4. **Download-based composite fallback**: When template fails and no local preintegration PNG exists, downloads from hosted URL and composites locally. Three provenance values: `template`, `composite-preintegration`, `composite-download`.
5. **Variance-based fill validation**: `visual_fill_validator.py` enhanced with `_content_stddev()` — blank (stddev < 5), faded (< 25), real content (>= 25). Validated 17/17 correct against prompt harness results.
6. **Provenance tracking**: New `literal_visual_source` field on `gary_slide_output` records.
7. **Dev reference doc**: `literal-visual-image-optimization.md` — optimal PNG attributes for Gamma template success.
8. **Prompt harness**: `test_literal_visual_prompt_harness.py` — live API test for prompt variants (`--run-live-e2e`).
9. **Validator test suite**: `test_visual_fill_validator.py` — 18 unit tests covering edge-band, variance, and pass/fail logic.

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Anti-fade prompt wording | Live API testing: 3/3 success for card-09 with "full opacity, not as background, not faded" |
| Fail-fast 1 retry instead of 3 | Gamma's accent/background classification is deterministic per image — retrying the same image with the same prompt gets the same result |
| Composite fallback as primary safety net | `_composite_full_bleed()` is deterministic, zero-credit, zero-latency; guarantees full-bleed for accent-classified images |
| Template `g_gior6s13mvpk8ms` retained | Template still works for background-classified images; composite catches the rest |
| Variance-based validation over edge-only | Edge sampling produces false negatives on light-edged images (infographics); variance detection correctly identifies content presence |

## Lessons Learned

1. **Gamma API docs can be misleading** — `imageOptions` is listed as optional for templates but `source` sub-field triggers HTTP 400. Always validate with live API calls.
2. **Gamma's image classification is content-driven** — not size, dimensions, aspect ratio, or metadata. Dense/photographic images → background. Diagrammatic/whitespace-heavy → accent.
3. **The Gamma UI has capabilities the API lacks** — "use as background" toggle in the UI produces perfect results but cannot be replicated via API parameters.
4. **Test against real artifacts** — the prompt harness with GitHub Pages–hosted production images caught issues that mocked tests missed.

## Validation Summary

| Check | Result |
|-------|--------|
| pytest (root suite) | 238+ passed |
| test_visual_fill_validator.py | 18 passed |
| test_literal_visual_prompt_harness.py | 7 collected (live-api gated) |
| Prompt harness live run | 6 variants tested, card-09 3/3 success |
| GitHub Pages cleanup | card-02-resized.png deleted |
| git status | Clean after commits 1-4 |

## Artifact Update Checklist

| Artifact | Updated? |
|----------|----------|
| `gamma_operations.py` | Yes — anti-fade prompt, 1 retry, 15s settle, download fallback, provenance |
| `test_gamma_operations.py` | Yes — assertions, provenance, download fallback test |
| `visual_fill_validator.py` | Yes — variance detection, content_stddev |
| `test_visual_fill_validator.py` | Yes — NEW (18 tests) |
| `test_literal_visual_prompt_harness.py` | Yes — NEW (live API harness) |
| `literal-visual-image-optimization.md` | Yes — NEW (dev reference) |
| `next-session-start-here.md` | Yes — rewritten |
| `SESSION-HANDOFF.md` | Yes — this file |
| `Gary SKILL.md` | Yes — provenance, download fallback |
| `bmm-workflow-status.yaml` | Yes — key_decision entry |
| `project-context.md` | Yes — variance detection bullet |
| `.gitignore` | Yes — dispatch logs, prompt-harness-results |
