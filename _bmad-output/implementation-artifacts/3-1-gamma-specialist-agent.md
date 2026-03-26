# Story 3.1: Gamma Specialist Agent & Mastery Skill

Status: ready-for-dev

## Story

As a user,
I want a Gamma specialist agent with complete tool mastery and intelligent parameter management,
So that presentation slides are created with optimal parameters matching my style preferences and validated through exemplar reproduction.

## Acceptance Criteria

1. `skills/bmad-agent-gamma/SKILL.md` exists with "Slide Architect" persona, complete Gamma parameter knowledge, and capability routing table following the Marcus SKILL.md pattern
2. `skills/gamma-api-mastery/SKILL.md` provides tool integration capability with references and scripts that route to the existing `scripts/api_clients/gamma_client.py`
3. `skills/gamma-api-mastery/references/parameter-catalog.md` documents ALL Gamma API parameters (inputText, textMode, format, numCards, themeId, additionalInstructions, textOptions, imageOptions, cardOptions, sharingOptions, exportAs, cardSplit, folderIds) with value ranges and educational content guidance
4. `skills/gamma-api-mastery/references/context-optimization.md` contains parameter templates for different content types (medical lecture, case study, module intro, assessment review, storytelling)
5. `skills/gamma-api-mastery/scripts/` contains Python scripts that import and orchestrate `GammaClient` from `scripts/api_clients/gamma_client.py`
6. The agent reads style guide preferences from `state/config/style_guide.yaml` `tool_parameters.gamma` section and applies them automatically
7. `_bmad/memory/gamma-specialist-sidecar/` is fully initialized with index.md (updated with activation context), patterns.md, chronology.md, and access-boundaries.md
8. At least one exemplar exists in `resources/exemplars/gamma/` (provided by Juan before implementation)
9. The agent successfully reproduces the exemplar via the Gamma API using the woodshed workflow (study → reproduce → compare → pass rubric)
10. The reproduction produces a detailed `run-log.yaml` capturing exact API call parameters, prompt text, response, and comparison conclusion
11. Both the reproduced artifact and the run log are retained in `reproductions/{timestamp}/`
12. Party Mode team reviews completed agent structure for accuracy and completeness

## Tasks / Subtasks

- [ ] Task 1: Create Gamma Specialist Agent via bmad-agent-builder (AC: #1)
  - [ ] 1.1 Run bmad-agent-builder six-phase discovery with the pre-built answers from epics.md Phase 1-3
  - [ ] 1.2 Output: `skills/bmad-agent-gamma/SKILL.md` with persona, communication style, principles, capability routing
  - [ ] 1.3 Follow Marcus SKILL.md pattern: Overview, Identity, Communication Style, Principles, Does Not Do, On Activation, Capabilities (Internal + External)
  - [ ] 1.4 Internal capabilities: parameter recommendation (PR), style guide interpretation (SG), output quality assessment (QA), exemplar study (ES)
  - [ ] 1.5 External skills routing: `gamma-api-mastery` for all Gamma API operations, `woodshed` for exemplar reproduction and regression

- [ ] Task 2: Create gamma-api-mastery skill (AC: #2, #3, #4, #5)
  - [ ] 2.1 Create `skills/gamma-api-mastery/SKILL.md` — skill overview, key paths, script index, reference index
  - [ ] 2.2 Create `skills/gamma-api-mastery/references/parameter-catalog.md` — ALL Gamma API parameters documented (sourced from live docs via Ref MCP, citing URLs)
  - [ ] 2.3 Create `skills/gamma-api-mastery/references/context-optimization.md` — content-type parameter templates
  - [ ] 2.4 Verify/update `skills/gamma-api-mastery/references/doc-sources.yaml` — ALREADY CREATED with 16 key page URLs, changelog, LLM-optimized endpoints
  - [ ] 2.5 Create `skills/gamma-api-mastery/scripts/gamma_operations.py` — wraps GammaClient with agent-level intelligence
  - [ ] 2.6 Create `skills/gamma-api-mastery/scripts/tests/test_gamma_operations.py` — pytest coverage

- [ ] Task 3: Style guide integration (AC: #6)
  - [ ] 3.1 Agent reads `state/config/style_guide.yaml` → `tool_parameters.gamma` on activation
  - [ ] 3.2 Default parameters applied: default_llm, style, format, slides_per_section
  - [ ] 3.3 Script loads style guide, merges with per-request overrides, passes to GammaClient

- [ ] Task 4: Memory sidecar initialization (AC: #7)
  - [ ] 4.1 Update `_bmad/memory/gamma-specialist-sidecar/index.md` with activation context and file references
  - [ ] 4.2 Create `_bmad/memory/gamma-specialist-sidecar/patterns.md` (empty, ready for learning)
  - [ ] 4.3 Create `_bmad/memory/gamma-specialist-sidecar/chronology.md` (empty, ready for history)
  - [ ] 4.4 Create `_bmad/memory/gamma-specialist-sidecar/access-boundaries.md` with read/write/deny zones

- [ ] Task 5: Create Gamma evaluator extending BaseEvaluator (AC: #9, DRY architecture)
  - [ ] 5.1 Create `skills/gamma-api-mastery/scripts/gamma_evaluator.py` extending `BaseEvaluator` from `skills/woodshed/scripts/woodshed_base.py`
  - [ ] 5.2 Implement `analyze_exemplar()` — extract slide layout pattern, content structure, pedagogical type from brief + source PDF
  - [ ] 5.3 Implement `derive_reproduction_spec()` — map analysis to Gamma API parameters (numCards, textMode, additionalInstructions, textOptions, etc.)
  - [ ] 5.4 Implement `execute_reproduction()` — call GammaClient.generate() + wait_for_generation(), return output URL + API interaction log
  - [ ] 5.5 Implement `compare_reproduction()` — Gamma-specific comparison: slide count, layout pattern match, content completeness, context alignment
  - [ ] 5.6 Implement `get_custom_rubric_weights()` — adjust weights per L-level (L1-L2: structural + parameter heavy; L3-L4: add content completeness)
  - [ ] 5.7 Create `skills/gamma-api-mastery/scripts/tests/test_gamma_evaluator.py`

- [ ] Task 6: Exemplar-driven validation — Woodshed (AC: #8, #9, #10, #11)
  - [ ] 6.1 Start with L1 (simplest): study → derive spec → reproduce → compare
  - [ ] 6.2 Progress through L2, L3, L4.1, L4.2 as each level is mastered
  - [ ] 6.3 Save all outputs + run-log.yaml to `reproductions/{timestamp}/` (retained for both pass and fail)
  - [ ] 6.4 Compare each reproduction against source using rubric, save comparison.yaml
  - [ ] 6.5 If fail: write reflection.md (root cause, predicted improvement), refine spec, retry (max 3/session)
  - [ ] 6.6 If pass: update `_catalog.yaml` status → mastered with mastered_at date
  - [ ] 6.7 Circuit breaker: 3 attempts/session, 7 total per exemplar; failure-report.yaml if tripped

- [ ] Task 7: Party Mode validation (AC: #12)
  - [ ] 7.1 Run Party Mode review of completed agent + skill + exemplar reproduction results

## Dev Notes

### Agent Pattern: Follow Marcus SKILL.md Structure

The Gamma specialist agent must follow the exact same SKILL.md structure as Marcus (`skills/bmad-agent-marcus/SKILL.md`). Key sections:

- **YAML frontmatter**: name, description
- **Overview**: One-paragraph summary of who this agent is and what it does
- **Identity**: "Slide Architect" — persona description
- **Communication Style**: How the agent communicates (visual-thinking oriented, precise about parameters)
- **Principles**: 5 numbered principles (every slide serves a learning objective, visual clarity for physician audience, etc.)
- **Does Not Do**: Clear boundaries — does NOT orchestrate other agents, manage production runs, or write to other sidecars
- **On Activation**: Load config, load sidecar memory, read style guide, greet with context
- **Capabilities**: Internal (parameter recommendation, style guide interpretation) + External (gamma-api-mastery skill, woodshed skill)

### Gamma API: Complete Parameter Space

From the official Gamma developer docs (https://developers.gamma.app):

**`POST /v1.0/generations`** — Core generation endpoint:
- `inputText` (required): Topic, outline, or long source text. Limit ~100k tokens
- `textMode` (required): `generate` | `condense` | `preserve`
- `format`: `presentation` | `document` | `webpage` | `social`
- `numCards`: 1-60 (Pro/Teams/Business), 1-75 (Ultra). Default 10
- `cardSplit`: `auto` (uses numCards) | `inputTextBreaks` (splits on `\n---\n`)
- `themeId`: From `GET /v1.0/themes`
- `additionalInstructions`: 1-5000 chars for layout, tone, structure guidance
- `folderIds`: Array of folder IDs
- `exportAs`: `pdf` | `pptx` | `png` (one per request, URLs expire ~7 days)
- `textOptions`: { amount: brief|medium|detailed|extensive, tone: string(500), audience: string(500), language: string }
- `imageOptions`: { source: aiGenerated|pexels|giphy|webFreeToUse|noImages|..., model: string, style: string(500) }
- `cardOptions`: { dimensions: fluid|16x9|4x3, headerFooter: {...} }
- `sharingOptions`: { ... }

**`POST /v1.0/generations/from-template`** — Template-based generation:
- `gammaId` + `prompt` required
- Best with single-page templates

**`GET /v1.0/generations/{id}`** — Poll for completion (status: pending|completed|failed)

**`GET /v1.0/themes`** — List themes (id, name, type, colorKeywords, toneKeywords)

**Gamma MCP tools** (3 tools via OAuth, registered in `.cursor/mcp.json`):
- `generate` — same as POST /v1.0/generations
- `get_themes` — list themes with optional name filter
- `get_folders` — list folders with optional name filter

### Existing GammaClient Methods

`scripts/api_clients/gamma_client.py` already provides:
- `__init__(api_key)` — auth via X-API-KEY header
- `list_themes(limit)` — GET /v1.0/themes
- `generate(topic, num_cards, output_format, llm, language, theme_id)` — POST /v1.0/generations
- `get_generation(generation_id)` — GET /v1.0/generations/{id}
- `wait_for_generation(generation_id, poll_interval, max_attempts)` — poll until done

**CRITICAL GAP (confirmed by smoke test 2026-03-26):** The existing client uses OLD parameter names (`topic` instead of `inputText`, no `textMode`). The current Gamma API REQUIRES `inputText` and `textMode`. The smoke test succeeded only by calling the API directly, bypassing the client.

Missing parameters in `GammaClient.generate()`:
- `inputText` (REQUIRED — currently uses `topic` which returns 400) — MUST FIX
- `textMode` (REQUIRED — generate/condense/preserve) — MUST FIX
- `cardSplit` (auto/inputTextBreaks) — needed for multi-slide narrative control
- `additionalInstructions` (1-5000 chars) — critical for constraining output
- `textOptions` (amount, tone, audience, language) — needed for density/voice control
- `imageOptions` (source, model, style) — needed for image control
- `cardOptions` (dimensions, headerFooter) — layout control
- `exportAs` (pdf/pptx/png) — REQUIRED for downloading production artifacts
- `folderIds`, `sharingOptions` — organizational features
- Template generation endpoint (`POST /generations/from-template`) — not yet supported

**Decision**: Update `GammaClient.generate()` to use correct parameter names (`inputText` not `topic`, add `textMode`) and accept all optional parameters. This is a backward-incompatible fix but the old names were wrong. Update any existing tests that reference the old parameters.

**Smoke test findings (2026-03-26):**
- Single-card generation works: `numCards: 1`, `textMode: preserve`, `format: presentation` → 201 Created
- Polling: 2-3 polls at 5s intervals → completed in ~15 seconds
- Export: `exportAs: "pdf"` → returns `exportUrl` with signed download link → 205KB PDF downloaded
- Credits: 5 per card, ~8000 remaining
- **Content embellishment**: Despite `textMode: preserve`, Gamma added a 4-step process diagram not in the input. Agent must learn to constrain via `additionalInstructions: "Output ONLY the provided text. Do not add content, steps, or diagrams beyond what is given."`
- **Image control**: `imageOptions.source: "noImages"` suppresses auto-generated images for faithful reproduction

### Style Guide Integration

`state/config/style_guide.yaml` → `tool_parameters.gamma` currently has:
```yaml
gamma:
  default_llm: ""
  style: ""
  format: ""
  slides_per_section: null
```

The agent should read these defaults, merge with per-request parameters (request overrides defaults), and pass the combined set to the API. When the agent learns effective parameters (e.g., a specific LLM works better for medical content), it can write learned preferences back via `manage_style_guide.py` from the production-coordination skill.

### Woodshed Integration & DRY Architecture

The exemplar-driven validation is a FIRST-CLASS acceptance criterion, not an afterthought.

**DRY principle**: The woodshed workflow engine (`skills/woodshed/scripts/woodshed_base.py`) provides common base classes. The Gamma-specific evaluation logic lives in a `GammaEvaluator` class that extends `BaseEvaluator`. This evaluator is what knows how to analyze slides, derive Gamma API parameters, and compare reproductions. The same pattern will be reused by ElevenLabs, Canvas, etc. — each provides its own evaluator.

**Exemplars provided** (5 single slides, L1-L4):
| ID | Level | Layout Pattern | Description |
|----|-------|----------------|-------------|
| L1-two-processes-one-mind | L1 | two-column-parallel | Clinical Diagnosis vs Design Thinking comparison |
| L2-diagnosis-innovation | L2 | title-plus-body | Bold headline + short explanatory paragraph |
| L3-deep-empathy | L3 | three-column-cards | Three professional qualities in card layout |
| L4.1-check-your-understanding | L4.1 | assessment-interactive | Comprehension check with categorization exercise |
| L4.2-youre-already-an-innovator | L4.2 | narrative-progression | Three-beat story arc (past → present → future) |

**Progression**: Master L1 first (simplest), then L2. L3, L4.1, L4.2 are post-story woodshed exercises. L5 (full slide decks with narrative/density control) comes later.

**Two woodshed modes** (faithful first, then creative):
- **Faithful**: Reproduce as closely as possible — proves tool control. `creative_status: locked` until faithful mastery achieved.
- **Creative**: Reproduce the intent with freedom to enhance — proves creative judgment. Unlocked per-exemplar after faithful mastery. Agent may propose level/scale changes.

**Narrative and density control** (for L5+ future multi-slide decks):
- `textOptions.amount`: brief/medium/detailed/extensive — words-per-slide dial
- `cardSplit: inputTextBreaks` — user controls slide breaks with `\n---\n` in input
- `numCards` + `amount: brief` = many slides, few words each (Juan's preferred pattern)
- `additionalInstructions` for density caps: "No more than 30 words per slide"
- `textOptions.tone` and `textOptions.audience` for voice control

**Export and download** (REQUIRED for all reproductions):
- Every reproduction must request `exportAs: "pdf"` (or pptx/png) and download the artifact immediately
- Export URLs are time-limited (~7 days for Gamma) — download on generation completion
- Downloaded artifacts stored in `reproductions/{timestamp}/output/` for comparison and downstream workflow assembly
- Screenshots are supplementary only — not acceptable as production artifacts

**GammaEvaluator responsibilities** (agent-specific, not in the common woodshed):
- `analyze_exemplar()`: Extract layout pattern, content structure, pedagogical type from brief + source
- `derive_reproduction_spec()`: Map analysis to Gamma API params (numCards=1, textMode, additionalInstructions for layout)
- `execute_reproduction()`: Call GammaClient.generate() + wait_for_generation()
- `compare_reproduction()`: Gamma-specific comparison — slide content, layout pattern, structural fidelity
- `get_custom_rubric_weights()`: L1-L2 weight structural fidelity highest; L3-L4 add content completeness weight

### File Structure

```
skills/
├── bmad-agent-gamma/
│   ├── SKILL.md                    # Agent definition (bmad-agent-builder output)
│   └── references/
│       └── init.md                 # First-run onboarding
├── gamma-api-mastery/
│   ├── SKILL.md                    # Skill overview + routing
│   ├── references/
│   │   ├── parameter-catalog.md    # Complete Gamma API parameter space
│   │   └── context-optimization.md # Content-type parameter templates
│   └── scripts/
│       ├── gamma_operations.py     # Agent-level API wrapper
│       ├── gamma_evaluator.py      # Extends BaseEvaluator — Gamma-specific analysis + comparison
│       └── tests/
│           ├── test_gamma_operations.py
│           └── test_gamma_evaluator.py
├── woodshed/                       # ALREADY BUILT — shared infrastructure
│   └── scripts/
│       └── woodshed_base.py        # BaseEvaluator abstract class (DO NOT DUPLICATE)

resources/exemplars/gamma/          # ALREADY POPULATED — 5 exemplars with briefs
├── _catalog.yaml
├── L1-two-processes-one-mind/      # brief.md + source/
├── L2-diagnosis-innovation/
├── L3-deep-empathy/
├── L4.1-check-your-understanding/
└── L4.2-youre-already-an-innovator/
```

### Testing Standards

- Use pytest for all script tests
- `gamma_operations.py` tests should mock the GammaClient to avoid live API calls in unit tests
- Live API smoke tests can be run separately with `--live` flag if desired
- Woodshed reproduction tests are separate — they use the real API and are gated by exemplar availability

### Anti-Patterns to Avoid

- Do NOT duplicate GammaClient logic — import and use the existing client
- Do NOT hardcode API parameters — read from style guide, allow per-request overrides
- Do NOT create a new MCP server config — Gamma MCP is already registered in `.cursor/mcp.json`
- Do NOT modify Marcus SKILL.md — Marcus already has `gamma-specialist` listed as a planned external agent
- Do NOT write to other agents' memory sidecars — Gamma agent writes only to its own sidecar

### Project Structure Notes

- Agent skill at `skills/bmad-agent-gamma/` (not `agents/` — following the project pattern where agent .md files live under `skills/`)
- Mastery skill at `skills/gamma-api-mastery/` (separate from agent skill — three-layer architecture)
- Memory sidecar at `_bmad/memory/gamma-specialist-sidecar/` (already scaffolded)
- Exemplar library at `resources/exemplars/gamma/` (already scaffolded with `_catalog.yaml`)
- Woodshed skill at `skills/woodshed/` (already built — shared infrastructure)
- Existing API client at `scripts/api_clients/gamma_client.py` (DO NOT MODIFY unless backward-compatible extension)

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Story 3.1] — Epic 3 story definition with ACs
- [Source: _bmad-output/planning-artifacts/architecture.md#Skills Implementation] — Skills as SKILL.md dirs
- [Source: skills/bmad-agent-marcus/SKILL.md] — Agent SKILL.md pattern (112 lines)
- [Source: scripts/api_clients/gamma_client.py] — Existing GammaClient (list_themes, generate, get_generation, wait_for_generation)
- [Source: state/config/style_guide.yaml#tool_parameters.gamma] — Current Gamma style guide defaults
- [Source: _bmad/memory/gamma-specialist-sidecar/index.md] — Sidecar scaffold
- [Source: resources/exemplars/_shared/woodshed-workflow.md] — Woodshed workflow protocol
- [Source: resources/exemplars/_shared/comparison-rubric-template.md] — Comparison rubric
- [Source: skills/woodshed/SKILL.md] — Shared woodshed skill
- [Source: docs/directory-responsibilities.md] — Configuration hierarchy and directory roles
- [Source: Gamma Developer Docs — https://developers.gamma.app/docs] — Official API documentation

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
