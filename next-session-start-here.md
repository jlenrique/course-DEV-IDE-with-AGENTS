# Next Session Start Here

## Immediate Next Action

**Implement Story 3.2 (Content Creator Agent + Quality Reviewer Agent) via `bmad-dev-story`.**

Content is KING. Scripts must exist before slides can be narrated. Story 3.2 was moved up from the old Story 3.4 position because the production pipeline demands it:
```
Content Creator (scripts) → Gary (slides) → ElevenLabs (narration) → Assembly → Quality Reviewer
```

The Content Creator ("Instructional Architect") judiciously delegates to BMad writers for top-notch prose:
- **Paige** (Tech Writer) — for structured explanatory content (procedures, protocols)
- **Sophia** (Storyteller) — for narratives (case studies, patient vignettes, first-person explainers)
- **Caravaggio** (Presentation Expert) — for slide narrative design and visual flow advice

Follow the Gary pattern: Party Mode coaching → bmad-agent-builder → agent creation → interaction testing → Party Mode validation.

```
1. Party Mode coaching — produce coached bmad-agent-builder discovery answers
   for Content Creator + Quality Reviewer (model on party-mode-coaching-gamma-specialist.md)
2. bmad-agent-builder with coached answers (invoke twice — one per agent)
3. Build reference templates for all 6 output artifact types
4. Test invocations: verify both agents respond in character
5. Run bmad-code-review for Story 3.2
```

**Then Story 3.3 (Kling Video Specialist — API client + video production agent, human review)**
**Then Story 3.4 (ElevenLabs — expanded scope with timestamps, pronunciation, SFX, music, dialogue)**

**Branch**: `epic3-core-tool-agents`

## Current Status — STORY 3.1 COMPLETE, EPIC 3 RE-SEQUENCED

- **Story 3.1 (Gary — Gamma Specialist)**: DONE — Agent built (10 files), mastery skill built (6 files), GammaClient fixed, 29 tests pass, L1+L2 woodshed PASSED, quality scan (0 critical, 2 high repo-completeness resolved), Party Mode validated, interaction test guide created
- **Epic 3 re-sequenced (March 26)**: Content Creator moved to 3.2 (was 3.4), ElevenLabs expanded to 3.3 (was 3.2), Canvas renumbered to 3.4 (was 3.3), Canva downgraded to design guidance (API cannot edit elements)
- **ElevenLabs brainstorm completed**: 12 artifact types identified, P0-P3 prioritized, evaluator design specified — see `_bmad-output/brainstorming/party-mode-elevenlabs-capability-audit.md`
- **Canva API assessed**: Cannot add captions, apply templates, or edit elements programmatically. Import/export only. Downgraded to design guidance agent.
- **Epic 2**: COMPLETE (6/6 stories, 55 tests)
- **Epic 1**: COMPLETE (11/11 stories, 117 tests)

### Gary Agent — What's Built

| Component | Location | Status |
|-----------|----------|--------|
| Agent SKILL.md | `skills/bmad-agent-gamma/SKILL.md` | Complete (118 lines, 7 internal caps, 3 external skills) |
| References (9) | `skills/bmad-agent-gamma/references/` | Complete (parameter-recommendation, style-guide-integration, quality-assessment, exemplar-study, content-type-mapping, context-envelope-schema, memory-system, init, save-memory) |
| Mastery Skill | `skills/gamma-api-mastery/SKILL.md` | Complete (SKILL.md + 3 refs + 2 scripts) |
| GammaEvaluator | `skills/gamma-api-mastery/scripts/gamma_evaluator.py` | Complete (extends BaseEvaluator) |
| Tests (29) | `skills/gamma-api-mastery/scripts/tests/` | 17 evaluator + 12 operations, all passing |
| Memory Sidecar | `_bmad/memory/gamma-specialist-sidecar/` | Active (index.md, patterns.md, chronology.md, access-boundaries.md) |
| Quality Scan | `skills/reports/bmad-agent-gamma/quality-scan/` | 0 critical, overall Good |
| Interaction Tests | `tests/agents/bmad-agent-gamma/interaction-test-guide.md` | 12 scenarios |
| Woodshed L1 | `resources/exemplars/gamma/L1-two-processes-one-mind/reproductions/` | PASSED (25KB PDF) |
| Woodshed L2 | `resources/exemplars/gamma/L2-diagnosis-innovation/reproductions/` | PASSED (8KB PDF) |

### Key Lessons from Story 3.1 Debugging (Apply to ALL Epic 3 Stories)

1. **Guide the tool, don't suppress it.** Rich `additionalInstructions` describing the desired outcome >> restrictive "don't add anything" constraints. Each tool has a core creative strength.
2. **The evaluator must compare actual output** — extract text/audio/image from the produced artifact and compare against the source. "Did a file download?" is not a quality check.
3. **Score on content coverage, not exact match.** Tool enhancements (sub-descriptions, visual accents) are usually beneficial. Only flag changes that alter meaning.
4. **`inputText` (or equivalent) should communicate intent.** Include contextual framing, not just bare content. Keep descriptive context that shouldn't appear in the output inside `additionalInstructions`.
5. **Woodshed is training; production is different.** Woodshed compares against exemplars. Production QA compares against Marcus's context envelope requirements. Never confuse them.
6. **Default export to PNG for production** (visual assets for video/embed). PDF for review. PPTX for editing.
7. **Memory sidecar `patterns.md` grows from user checkpoint reviews** — not from woodshed scores.

### Key Architectural Decisions (Story 3.1)

- **Agent name: Gary** (Slide Architect 🎨) — user-selected
- **Template generation** support added (`POST /generations/from-template` with `gammaId` + `prompt`)
- **Template registry** in `state/config/style_guide.yaml` → `tool_parameters.gamma.templates` for scope-based template resolution
- **Context envelope schema** formalized with required/optional fields, golden examples, and `parameters_ready` expert fast-path flag
- **GammaClient** backward-incompatible fix: `topic` → `inputText`, added `textMode`, `exportAs`, `additionalInstructions`, all optional params
- **API response** uses `generationId` not `id` — handled in gamma_operations.py
- **Cross-skill imports** via `importlib.util.spec_from_file_location` for hyphenated directory names
- **pyproject.toml** added `pythonpath = ["."]` for project-root imports in skill tests

## What's Working Right Now

### MCP Servers (in Cursor agent chat)
- **Gamma**: 2 tools — generate content, browse themes
- **Canvas LMS**: 54 tools — full course/module/assignment management
- **Notion**: 22 tools — pages, databases, comments, search
- **Playwright**: 22 tools — browser automation (user-level)
- **Ref**: 2 tools — doc search and URL reading (user-level)

### API Access (via scripts, not MCP)
- **ElevenLabs**: `node scripts/smoke_elevenlabs.mjs` — 45 voices
- **Qualtrics**: `node scripts/smoke_qualtrics.mjs` — surveys, questions, distributions
- **All tools**: `node scripts/heartbeat_check.mjs` — full heartbeat

## Hot-Start Context

### Key File Paths
- Gary SKILL.md: `skills/bmad-agent-gamma/SKILL.md`
- Gary Sidecar: `_bmad/memory/gamma-specialist-sidecar/`
- Gary Quality Scan: `skills/reports/bmad-agent-gamma/quality-scan/2026-03-26_200831/quality-report.md`
- Gary Interaction Tests: `tests/agents/bmad-agent-gamma/interaction-test-guide.md`
- Gary Coaching Doc: `_bmad-output/brainstorming/party-mode-coaching-gamma-specialist.md`
- ElevenLabs Capability Audit: `_bmad-output/brainstorming/party-mode-elevenlabs-capability-audit.md`
- Marcus SKILL.md: `skills/bmad-agent-marcus/SKILL.md`
- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Epics: `_bmad-output/planning-artifacts/epics.md`

### Epic 3 Story Sequence (re-sequenced March 27, 2026 — 9 stories)
| Story | Agent | Validation | Status |
|-------|-------|------------|--------|
| 3.1 | Gary (Gamma Specialist) | Exemplar + Woodshed | DONE |
| 3.2 | Content Creator + Quality Reviewer | Human review (sample artifacts) | NEXT |
| 3.3 | Kling Video Specialist (NEW) | Human review (sample videos) | Backlog |
| 3.4 | ElevenLabs Specialist (expanded) | Exemplar + Woodshed | Backlog |
| 3.5 | Canvas Specialist | Exemplar + Woodshed | Backlog |
| 3.6 | Qualtrics Specialist | Exemplar + Woodshed | Backlog |
| 3.7 | Canva Specialist (manual-tool pattern) | Human review (instructions) | Backlog |
| 3.8 | Source Wrangler (Notion + Box) | Functional testing | Backlog |
| 3.9 | Tech Spec Wrangler | Functional testing | Backlog |

### Gotchas
- PowerShell doesn't support `&&` chaining — use `;` instead
- `.venv` is set up with Python 3.13 — activate with `.venv\Scripts\activate`
- Run tests with `.venv\Scripts\python -m pytest tests/ -v`
- Skill tests run separately: `.venv\Scripts\python -m pytest skills/gamma-api-mastery/scripts/tests/ -v`
- Gamma API returns `generationId` not `id` in POST response
- Cursor MCP `env` field does NOT resolve `${VAR}` from .env files — wrapper script exists
- Cross-skill Python imports use `importlib.util` loader pattern due to hyphenated directory names
