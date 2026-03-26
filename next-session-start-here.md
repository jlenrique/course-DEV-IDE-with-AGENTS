# Next Session Start Here

## Immediate Next Action

**Implement Story 3.1 (Gamma Specialist Agent & Mastery Skill) via `bmad-dev-story`.**

Story 3.1 file is READY at `_bmad-output/implementation-artifacts/3-1-gamma-specialist-agent.md`. Five Gamma exemplars are provided (L1-L4.2). Smoke test PASSED (2026-03-26): Gamma API generates single-card presentations, PDF export/download works, 5 credits/card.

```
# In a FRESH Cursor chat session:
1. Run bmad-dev-story — say "dev story 3.1" or "implement the next story"
2. First: Fix GammaClient parameter names (inputText, textMode, exportAs)
3. Build Gamma agent via bmad-agent-builder (Task 1)
4. Build gamma-api-mastery skill with GammaEvaluator (Tasks 2, 5)
5. Woodshed: faithful reproduction of L1 + L2 exemplars with PDF export (Task 6)
6. Run bmad-code-review for Story 3.1
7. Post-story: woodshed L3, L4.1, L4.2 as progressive mastery exercises
8. Repeat cycle for Stories 3.2–3.7
```

**Branch**: `epic3-core-tool-agents`

## Current Status — EPIC 2 COMPLETE, EXEMPLAR INFRA BUILT + SMOKE TESTED, STORY 3.1 READY

- **Exemplar-Driven Development Infrastructure**: DONE — woodshed skill, exemplar libraries per tool, comparison rubric, run logging, reflection protocol, circuit breaker, two-mode woodshed (faithful + creative), doc refresh protocol, L-level difficulty system, BaseEvaluator DRY pattern
- **Gamma Smoke Test**: PASSED — single-card generation + PDF export/download validated (205KB, 5 credits, ~15s). GammaClient needs param name fixes (Story 3.1 Task 2)
- **Gamma Exemplars**: 5 slides provided (L1-L4.2) with briefs in `resources/exemplars/gamma/`
- **Story 2.1 (Master Orchestrator Agent Creation)**: DONE — Marcus built, quality scanned, interaction tested, Party Mode validated
- **Story 2.2 (Conversational Workflow Management)**: DONE — production-coordination skill, manage_run.py (17 tests)
- **Story 2.3 (Agent Coordination Protocols)**: DONE — delegation-protocol.md, log_coordination.py (6 tests)
- **Story 2.4 (Parameter Intelligence)**: DONE — manage_style_guide.py (10 tests)
- **Story 2.5 (Pre-Flight Check Orchestration)**: DONE — preflight-integration.md
- **Story 2.6 (Run Mode Management)**: DONE — manage_mode.py (7 tests)
- **Epic 1**: COMPLETE (11/11 stories done, 117 tests pass, 3 skipped)
- **Tool Universe**: 17 tools audited and classified (added Notion + Box Drive)
- **Live MCPs**: Gamma (2 tools), Canvas LMS (54 tools), Notion (22 tools) verified in Cursor
- **API-verified**: ElevenLabs (45 voices), Qualtrics (authenticated), Wondercraft, Kling
- **PRD**: 80 FRs across 11 capability domains
- **Architecture**: Complete, recast for BMad agent + Cursor plugin approach

### Marcus Agent — What's Built

Marcus (Creative Production Orchestrator, 🎬) is fully operational at the Story 2.1 scope:

| Component | Location | Status |
|-----------|----------|--------|
| Agent SKILL.md | `skills/bmad-agent-marcus/SKILL.md` | Complete (112 lines, persona, 10 principles, capability routing) |
| References (8) | `skills/bmad-agent-marcus/references/` | Complete (conversation-mgmt, mode-management, checkpoint-coord, progress-reporting, source-prompting, memory-system, init, save-memory) |
| Scripts (2) | `skills/bmad-agent-marcus/scripts/` | Complete (`read-mode-state.py`, `generate-production-plan.py`) |
| Script Tests (15) | `skills/bmad-agent-marcus/scripts/tests/` | Complete (8 + 7 tests) |
| Memory Sidecar | `_bmad/memory/bmad-agent-marcus-sidecar/` | Active (index.md, access-boundaries.md, patterns.md, chronology.md) |
| Quality Scan | `skills/reports/bmad-agent-marcus/quality-scan/` | 0 critical, 2 high (env-only), 11 medium, 12 low |
| Interaction Tests | `tests/agents/bmad-agent-marcus/interaction-test-guide.md` | 12 scenarios, all pass |

**Marcus can**: greet in character, report mode, parse intent, plan production, manage mode switching, save memory, gracefully degrade when specialists aren't built, run pre-flight checks, offer source material assistance.

**Marcus needs** (Stories 2.2–2.6): conversational workflow execution infrastructure, multi-agent coordination protocols, parameter intelligence, pre-flight orchestration integration, run mode management infrastructure.

### Party Mode Decisions (March 26, 2026 — Sessions 1–3)

**Session 3 — Story 2.1 Validation (COMPLETE):**
Party Mode team (Winston, Mary, John, Sally, Quinn, Bob, Paige) reviewed all Story 2.1 acceptance criteria against implementation. All 9 AC items passed. Identified 4 doc harmonization tasks (sprint status, workflow status, next-session, orphaned sidecar) — all resolved in this session.

**Session 2 — Marcus Orchestrator Coaching (COMPLETE):**
Party Mode team coached through all 6 phases of the bmad-agent-builder interview. Produced `_bmad-output/brainstorming/party-mode-coaching-marcus-orchestrator.md` with copy-paste-ready answers.

**Session 1 — Three new capabilities agreed upon:**
1. Notion + Box Drive Integration (Story 3.7)
2. Run Mode Management (Story 2.6)
3. Source Wrangler architectural component

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

### Known MCP Limitations (deferred)
- ElevenLabs MCP: Cursor filters tools due to name length >60 chars
- Qualtrics MCP: Not on npm, needs local build
- Canva MCP: OAuth redirect rejected by Cursor
- Fetch MCP: No usable tools surfaced

## Hot-Start Context

### Key File Paths
- Marcus SKILL.md: `skills/bmad-agent-marcus/SKILL.md`
- Marcus Sidecar: `_bmad/memory/bmad-agent-marcus-sidecar/`
- Marcus Quality Scan: `skills/reports/bmad-agent-marcus/quality-scan/2026-03-26_152243/quality-report.md`
- Marcus Interaction Tests: `tests/agents/bmad-agent-marcus/interaction-test-guide.md`
- Sprint Status: `_bmad-output/implementation-artifacts/sprint-status.yaml`
- Epics: `_bmad-output/planning-artifacts/epics.md`
- Tool Matrix: `resources/tool-inventory/tool-access-matrix.md`
- MCP Config (live): `.cursor/mcp.json`
- Project Context: `docs/project-context.md`

### Key Tools for Next Session
- `bmad-agent-builder` — create Gamma specialist agent (Party Mode coaching first, then six-phase discovery)
- `bmad-dev-story` — implement Story 3.1
- `bmad-code-review` — review Story 3.1 implementation
- `skills/woodshed/` — exemplar study, reproduction, comparison, regression
- `skills/tech-spec-wrangler/` — planned (Story 3.8); doc refresh protocol available now via `doc-sources.yaml`

### API Keys
- `.env` has live keys for: Gamma, ElevenLabs, Canvas, Qualtrics, Botpress, Wondercraft, Kling
- `.env` is gitignored; `.env.example` is the safe template
- `.cursor/mcp.json` uses `scripts/run_mcp_from_env.cjs` to load keys at runtime (no literal secrets in config)

### Agent Creation Process (Epic 3 pattern — exemplar-driven)
For every story that creates a custom specialist agent:
1. **Juan provides exemplar(s)** in `resources/exemplars/{tool}/` with `brief.md` + `source/`
2. **Party Mode coaching** — team refines discovery answers with the user
3. **bmad-agent-builder** — six-phase discovery using the refined answers
4. **Skill co-creation** — agent's mastery skill built in the same story
5. **Woodshed validation** — agent studies exemplar, reproduces via API/MCP, passes rubric
6. **Party Mode validation** — team reviews completed agent + skill + reproduction results

**Three-layer architecture** (each independently updatable):
- **API clients** (`scripts/api_clients/`) — connectivity, retry, auth (Epic 1, DONE)
- **Skills** (`skills/{tool}/`) — tool expertise, parameter templates, execution code (Epic 3)
- **Agents** (`skills/bmad-agent-{name}/`) — judgment, decision-making, personality, memory (Epics 2-3)

**Exemplar-driven mastery** (new for Epic 3):
- **Exemplar library** (`resources/exemplars/{tool}/`) — real artifacts that agents must reproduce
- **L-level system**: L1-L4 single artifacts, L5+ multi-artifact sets, dot extensions for within-level granularity; levels are provisional
- **Woodshed skill** (`skills/woodshed/`) — study → reproduce → compare → reflect → register
- **Two modes**: Faithful (exact reproduction, proves control) → Creative (enhanced reproduction, proves judgment)
- **DRY architecture**: `BaseEvaluator` in woodshed (common process); `GammaEvaluator` in mastery skill (agent-specific analysis)
- **Export/download**: All reproductions download production artifacts (PDF/PPTX/MP3); screenshots supplementary only
- **Run logging** — every attempt logs exact API calls, prompts, responses, comparison conclusions
- **Artifact retention** — all reproduction outputs kept (pass and fail) for side-by-side review
- **Circuit breaker** — 3 attempts/session, 7 total; agent gives up with structured failure report if it can't master an exemplar
- **Doc refresh** — `doc-sources.yaml` per mastery skill; mandatory refresh via Ref MCP before woodshed cycles

### Smoke Test Results (2026-03-26)
- Gamma API: `inputText` + `textMode: preserve` + `format: presentation` + `numCards: 1` → 201 Created
- Export: `exportAs: "pdf"` → signed download URL → 205KB PDF saved locally
- Polling: 2-3 polls at 5s intervals → completed in ~15 seconds
- Credits: 5 per card, ~7990 remaining
- Finding: Gamma embellishes content even in preserve mode → agent must constrain via `additionalInstructions`
- Finding: GammaClient uses old param names (`topic` not `inputText`) → must fix in Story 3.1

### Gotchas
- PowerShell doesn't support `&&` chaining — use `;` instead
- `.venv` is set up with Python 3.13 — activate with `.venv\Scripts\activate`
- Run tests with `.venv\Scripts\python -m pytest tests/ -v`
- Cursor MCP `env` field does NOT resolve `${VAR}` from .env files — that's why the wrapper script exists
