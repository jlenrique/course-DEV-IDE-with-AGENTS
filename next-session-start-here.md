# Next Session Start Here

## Immediate Next Action

**Implement Story 3.2 (ElevenLabs Specialist Agent & Mastery Skill) via `bmad-dev-story`.**

Follow the Gary pattern established in Story 3.1: Party Mode coaching → bmad-agent-builder → mastery skill → evaluator → woodshed → Party Mode validation.

```
1. Party Mode coaching — produce coached bmad-agent-builder discovery answers
   for ElevenLabs specialist (model on party-mode-coaching-gamma-specialist.md)
2. bmad-agent-builder with coached answers
3. Build elevenlabs-audio mastery skill with ElevenLabsEvaluator
4. Woodshed: faithful reproduction of audio exemplar(s) with MP3 export
5. Run bmad-code-review for Story 3.2
```

**Branch**: `epic3-core-tool-agents`

## Current Status — STORY 3.1 COMPLETE, EPIC 3 IN PROGRESS

- **Story 3.1 (Gary — Gamma Specialist)**: DONE — Agent built (10 files), mastery skill built (6 files), GammaClient fixed, 29 tests pass, L1+L2 woodshed PASSED, quality scan (0 critical, 2 high repo-completeness resolved), Party Mode validated, interaction test guide created
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
- Marcus SKILL.md: `skills/bmad-agent-marcus/SKILL.md`
- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Epics: `_bmad-output/planning-artifacts/epics.md`

### Gotchas
- PowerShell doesn't support `&&` chaining — use `;` instead
- `.venv` is set up with Python 3.13 — activate with `.venv\Scripts\activate`
- Run tests with `.venv\Scripts\python -m pytest tests/ -v`
- Skill tests run separately: `.venv\Scripts\python -m pytest skills/gamma-api-mastery/scripts/tests/ -v`
- Gamma API returns `generationId` not `id` in POST response
- Cursor MCP `env` field does NOT resolve `${VAR}` from .env files — wrapper script exists
- Cross-skill Python imports use `importlib.util` loader pattern due to hyphenated directory names
