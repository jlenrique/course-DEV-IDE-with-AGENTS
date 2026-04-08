# Project Context: Multi-Agent Course Content Production System

**Project Name:** course-DEV-IDE-with-AGENTS  
**Phase:** 4-Implementation (all planned epics complete)
**Architecture Status:** 14 Epics complete, **91 FRs**, Complete Architecture - Recast for BMad Agent + Cursor Plugin + APP Fidelity Assurance + Agent Governance Architecture
**2026-04-05 Update:** Epics 13 and 14 are now complete, tested, and internally reviewed. Production prompt packs now split by workflow template: `production-prompt-pack-v4.1-narrated-deck-video-export.md` for standard narrated runs and `production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` for motion-enabled narrated runs. `DOUBLE_DISPATCH` remains an inline branch in either pack.
**2026-04-08 Update:** Storyboard B and downstream motion contracts are now explicit. Motion segments keep the approved still slide in `visual_file`, the approved MP4 in `motion_asset_path`, Storyboard B renders both for review, and motion-first narration should orient briefly to the slide and then speak primarily to the visible action in the approved clip. First complete motion-enabled production run `C1-M1-PRES-20260406` has been executed through all 15 prompts of prompt pack v4.2, with assembly bundle fully packaged for Descript composition.
**Current Implementation Status:** Use the dated update above as the source of truth for epic completion and prompt-pack naming; the detailed historical implementation notes below remain as project chronology.
**Implementation Status:** Epics 1-14 + SB all COMPLETE. Epic 13 visual-aware Irene Pass 2 and Epic 14 motion workflow are implemented, tested, and internally reviewed. Production prompt packs now split by workflow template: `production-prompt-pack-v4.1-narrated-deck-video-export.md` for standard narrated runs and `production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` for motion-enabled narrated runs.

## Purpose

Build a persistent collaborative intelligence infrastructure for systematically scaling creative expertise in online course content production. A custom master orchestrator agent (created via `bmad-agent-builder`) provides a conversational interface ("general contractor" experience) coordinating specialist agents that manipulate professional media tools through skills backed by Python scripts for API calls, while systematically capturing creative decision-making patterns in BMad memory sidecars for iterative refinement and reuse.

## Critical Implementation Model

**Agents are skill directories** created through `bmad-agent-builder` six-phase conversational discovery process, following BMad SKILL.md standard. They live under `skills/bmad-agent-{name}/` and are discovered through the skills layer.

**Skills are SKILL.md directories** providing tool-specific capabilities with progressive disclosure (`references/`), Python code execution (`scripts/`), and output templates (`assets/`).

**Python infrastructure** provides supporting code for API clients, state management, and file operations - invoked from agent skills when code execution is required.

**Cursor plugin packaging** via `.cursor-plugin/plugin.json` enables native IDE integration with auto-discovery of skills, rules, commands, hooks, and MCP servers.

**BMad memory sidecars** provide persistent agent learning through `_bmad/memory/{skillName}-sidecar/` with index.md (context), patterns.md (learned preferences), chronology.md (history), and access-boundaries.md (scope control).

## Key Decisions From Planning

### Agent Architecture (Confirmed)
- **Custom Master Orchestrator agent** (.md file created via `bmad-agent-builder`) as single conversational point of contact
- **Custom specialist agents** (.md files created via `bmad-agent-builder`) for tool mastery (Gamma, ElevenLabs, Canvas, etc.)
- **Custom skills** (SKILL.md + references/ + scripts/) for tool expertise, parameter intelligence, coordination
- **Reuse existing BMad agents** for writing, editing, review, documentation
- **Python infrastructure** in scripts/ for API clients, state management, file operations

### Cursor Plugin Architecture (Confirmed)
- `.cursor-plugin/plugin.json` manifest with auto-discovery of skills/, rules/
- `.mcp.json` for tool server definitions bundled in plugin
- `hooks/hooks.json` for event-driven automation (sessionStart → pre-flight, afterFileEdit → quality, sessionEnd → reporting)
- `rules/*.mdc` for persistent agent behavior guidance
- `commands/*.md` for agent-executable actions

### BMad Memory System (Confirmed)
- Agent memory sidecars at `_bmad/memory/{skillName}-sidecar/`
- `index.md` for essential context loaded on activation
- `patterns.md` for systematic expertise crystallization (append-only, periodically condensed)
- `chronology.md` for session and production run history
- `access-boundaries.md` for agent scope control (read/write/deny zones)

### Operational Model (Confirmed)
- **Run presets**: `explore`, `draft`, `production`, `regulated` with parameter overrides
- **Asset-lesson pairing invariant**: every educational artifact paired with instructional context
- **Tool parameter mastery**: Specialty agents master complete API parameter spaces, preferences stored in style guide YAML
- **Exemplar-driven development**: Each specialist agent proves competence by reproducing real exemplar artifacts programmatically via API/MCP, scored against a structured rubric. Exemplars serve as both design aids and acceptance tests. See `resources/exemplars/_shared/woodshed-workflow.md`
- **Woodshed skill**: Shared skill (`skills/woodshed/`) provides study → reproduce → compare → reflect → register workflow with detailed run logging, downloaded artifact retention for every attempt (pass/fail), mandatory reflection between failed attempts, and circuit breaker give-up protocol (3/session, 7 total)
- **Two woodshed modes**: Faithful (exact reproduction proving tool control) must be mastered before Creative (enhanced reproduction proving creative judgment) is unlocked per exemplar
- **Progressive mastery**: L1-L4 single artifacts → L5 multi-artifact sets. L-levels with dot extensions. Levels provisional — agents may propose changes. Regression runs ensure mastered exemplars stay mastered
- **Export and download**: All reproductions must download production-quality artifacts (PNG for production, PDF for review, PPTX for editing, MP3 for audio) — screenshots supplementary only
- **Evaluator design requirements** (from Story 3.1): Guide the tool's intelligence (never suppress), extract and compare actual output (not just process compliance), score on content coverage (not exact match), use cheap quality signals per medium, separate woodshed training from production QA, capture know-how from user checkpoint reviews. See `skills/woodshed/SKILL.md` for full reference
- **HIL gates**: human checkpoints at every stage with rubrics and signoff tracking
- **Pre-flight checks**: Hook-driven MCP/API connectivity verification + tool documentation scanning
- **Production run reporting**: Comprehensive effectiveness analysis with learning capture in agent memory

### State Management (Confirmed)
- **YAML files**: Course context, style guides, policies (human-readable, git-versioned) in `state/config/`
- **SQLite database**: Runtime coordination state, production run tracking in `state/runtime/`
- **BMad memory sidecars**: Agent learning, expertise patterns, session history in `_bmad/memory/`

### Repository Contract (Confirmed)
```
.cursor-plugin/   # Cursor plugin manifest
skills/           # SKILL.md directories with references/ + scripts/ (auto-discovered)
  woodshed/       # Shared exemplar mastery skill (study, reproduce, compare, regress)
rules/            # .mdc rules files for agent guidance
hooks/            # Event-driven automation triggers
commands/         # Agent-executable command files
state/            # YAML configs + SQLite runtime
_bmad/memory/     # Agent memory sidecars for persistent learning
scripts/          # Shared Python infrastructure (API clients, utilities)
tests/            # Unit + integration tests
docs/             # Architecture + agent guides + troubleshooting
resources/
  exemplars/      # Per-tool exemplar libraries with _catalog.yaml, briefs, source, reproductions
    _shared/      # Comparison rubric template, woodshed workflow protocol
    gamma/        # Gamma exemplars (slides/presentations)
    elevenlabs/   # ElevenLabs exemplars (audio/voiceover)
    canvas/       # Canvas exemplars (LMS deployment)
    qualtrics/    # Qualtrics exemplars (surveys/assessments)
    canva/        # Canva exemplars (visual design)
  style-bible/    # Authoritative brand reference
  tool-inventory/ # Tool access matrix
```

## Tool Universe (Researched March 26, 2026)

17 tools classified by programmatic access. Full details in `resources/tool-inventory/tool-access-matrix.md`.

| Tier | Tools | Access |
|------|-------|--------|
| **Tier 1: API + MCP** | Gamma, ElevenLabs, Canvas LMS, Qualtrics, Canva, Notion | Platform capability: REST API and published MCP server |
| **Tier 2: API Only** | Botpress, Wondercraft, Kling, Panopto | REST API, no MCP server |
| **Tier 3: Limited API** | Descript, Midjourney, CapCut | Early access / third-party only |
| **Tier 4: Manual Only** | Vyond, CourseArc, Articulate (Storyline/Rise) | No usable programmatic access for this repo setup |
| **Local FS** | Box Drive | Local filesystem via desktop sync client, no API needed |

- **Live Cursor-verified MCP servers** in `.mcp.json` / `.cursor/mcp.json`: Gamma, Canvas LMS
- **API-verified but MCP-deferred platforms**: ElevenLabs, Qualtrics
- **Documented but currently deferred MCPs**: ElevenLabs (Cursor tool-name filtering), Canva (OAuth redirect rejection), Qualtrics (GitHub-only build step), Fetch (no usable surfaced tools in this setup), Brave Search (not enabled by default)
- **User-level MCPs** already available: Playwright (browser automation), Ref (doc search/reading)
- **API keys** documented in `docs/admin-guide.md`: Tier 1-3 tools with documentation links; values live in local `.env` only
- **Manual tools** require agent-guided workflows where agents provide specs and users execute in tool UI

## Current State

- [x] Repository scaffolded with directory structure, local `.env` pattern, content standards
- [x] BMad Method installed (BMM, Core, CIS modules)
- [x] **BRAINSTORMING COMPLETED**: 10 comprehensive epics defined
- [x] **PRD COMPLETED**: 70 FRs across 11 capability domains (recast for agent .md approach)
- [x] **ARCHITECTURE COMPLETED**: BMad Agent + Cursor Plugin architecture validated (recast)
- [x] **EPICS RECAST**: All 10 epics updated to reflect bmad-agent-builder creation approach
- [x] **Strategic Decisions**: Party Mode team validated and recast for agent .md patterns
- [x] **STORY CREATION COMPLETED**: 31 stories across 10 epics, 100% FR coverage validated
- [x] **API-FIRST SEQUENCING**: API/MCP clients (Gamma, ElevenLabs, Canvas) built in Epic 1 before agent creation
- [x] **TOOL UNIVERSE AUDIT**: 15 tools researched and classified (Tier 1-4), MCP servers configured, credentials documented for local `.env`
- [x] **EPIC 1 COMPLETE**: All 11 stories implemented, tested with live APIs, validated by Party Mode review team
- [x] **STORY 1.1**: Cursor plugin foundation — plugin.json, .mcp.json, hooks, directory structure
- [x] **STORY 1.2**: Python infrastructure — BaseAPIClient with retry/pagination/binary, utilities, venv
- [x] **STORY 1.3**: State management — SQLite (3 tables), YAML configs (3 files), BMad memory sidecars (5 agents)
- [x] **STORY 1.4**: Pre-flight check skill — SKILL.md + Python runner + doc scanner + 3 reference docs
- [x] **STORIES 1.5-1.11**: Testing framework + 5 full-featured API clients (Gamma, ElevenLabs, Canvas, Qualtrics, Panopto) + Canva MCP config
- [x] **LIVE API VALIDATION**: 117 tests pass against real services (Gamma, ElevenLabs, Canvas, Qualtrics), 3 skipped (Panopto — no creds)
- [x] **FR EXPANSION (Party Mode)**: 10 new FRs (FR71-FR80) added for Source Wrangling + Run Mode Management
- [x] **TOOLS EXPANSION**: Notion (API + MCP, source wrangling) and Box Drive (local FS) added to tool universe (17 tools total)
- [x] **SOURCE WRANGLER**: New architectural component for pulling reference materials from Notion/Box into production context; agent vs. skill design decision deferred to story creation
- [x] **AD-HOC MODE**: Binary ad-hoc/default mode switch for Master Orchestrator; ad-hoc routes assets to scratch/staging, suppresses state tracking; QA always runs; future per-level modality matrix deferred
- [x] **STORY 2.1 (Marcus Orchestrator)**: Agent built via bmad-agent-builder (6-phase discovery with Party Mode coaching), quality scan passed (0 critical), 12 interaction test scenarios passed, Party Mode team validation complete. 13 files: SKILL.md + 8 references + 2 scripts + 2 test files. Memory sidecar active with 4 files. First production plan staged (C1-M1-P2S1-VID-001).
- [x] **EPIC 2 COMPLETE**: Stories 2.2–2.6 all done. Production-coordination skill (4 scripts, 4 refs, 40 tests). Marcus references updated for workflow management, delegation, parameter intelligence, pre-flight, and mode management.
- [x] **EXEMPLAR-DRIVEN DEVELOPMENT**: Woodshed skill created (`skills/woodshed/`), exemplar library scaffolded (`resources/exemplars/` per tool), comparison rubric, run logging, reflection protocol, circuit breaker, two-mode woodshed (faithful + creative), doc refresh protocol, and L-level difficulty system all in place. 5 Gamma exemplars provided (L1-L4.2). Smoke test validated: Gamma API produces single-card output, PDF export/download works (205KB), 5 credits/card. GammaClient needs parameter name updates (inputText, textMode, exportAs). Epic 3 stories updated with exemplar reproduction as acceptance criteria.
- [x] **STORY 3.3.1 (Composition Architecture Harmonization + Gary Deck)**: DONE — Party Mode composition decisions implemented: segment manifest as Irene artifact, two-pass Irene model, Irene/Quinn-R/Kira/Marcus/Gary all updated, architecture.md updated with pipeline graph, tool inventory updated (Descript as sole composition platform), Gary deck mode + theme/template preview (TP capability), gary_slide_output return field, GammaClient.list_themes() live-tested (10 themes). Epic 3 re-sequenced to 11 stories: Compositor added as 3.5, Canvas→3.6, Qualtrics→3.7, Canva→3.8, Source Wrangler→3.9, Tech Spec Wrangler→3.10.
- [x] **PROMPT 7 DISPATCH HARDENING (2026-03-30)**: Canonical `gamma_operations.py` generate path now enforces fail-fast for metadata-only slide payloads, supports explicit merge of `gary-fidelity-slides.json` + `gary-slide-content.json`, and keeps placeholder content behind debug-only override (`--allow-placeholder-content`). Regression tests added to prevent recurrence of intent-placeholder slide outputs while preserving parameter, theme-handshake, and export reliability gains.
- [x] **Epic 2A: Fidelity Assurance & APP Intelligence Infrastructure** (9/9 stories DONE — Vera agent covering G0-G5, sensory bridges, perception protocol, source_ref resolver, cumulative drift tracking, fidelity-control vocabulary, maturity audit skill. GOLD document: `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md`)
- [x] Epic 3: Core Tool Specialist Agents & Mastery Skills (11/11 stories DONE — Stories 3.1-3.11 complete, including Story 3.8 Canva specialist.)

## APP Design Principles & Fidelity Architecture (Added 2026-03-28)

See `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md` (GOLD document) for full analysis.

- **Agentic Production Platform (APP):** Formal naming — the IDE is the runtime environment for a network of specialized agents. The platform gets smarter over time as LLMs improve and agent memory accumulates.
- **Three-Layer Intelligence Model:** L1 deterministic contracts (invariant standards), L2 agentic evaluation (evolves with LLM capability), L3 learning memory (compound improvement via sidecars). Applies to every APP capability.
- **Hourglass Model:** Wide cognitive top (synthesis) → narrow deterministic neck (schema/parameter binding) → wide cognitive bottom (creative execution). Intelligence must not enforce constraints that can be deterministic.
- **Leaky Neck Diagnostic:** Any point where agentic judgment enforces a deterministic constraint is a design defect.
- **Sensory Horizon:** Agents cannot verify what they cannot perceive. Sensory bridges (image, audio, PDF, video) with mandatory confirmation protocol.
- **Fidelity Assessor:** New forensic agent distinct from Quinn-R. Produces Fidelity Trace Reports (Omissions/Inventions/Alterations). Circuit breaker on failure. Runs before quality review.
- **Provenance Protocol:** Mandatory `source_ref` fields in all artifact schemas for traceable provenance chains.
- **Current maturity:** Upgraded from Level 0 — Vera covers G0-G5 with 30 L1 criteria, perception bridges for all modalities, cumulative drift tracking, source_ref resolver, fidelity-control vocabulary enforcement in merge_parameters(). G6 (composition) remains future.
- **Epic 2A** COMPLETE (9/9 stories). Story 3.11 mixed-fidelity system COMPLETE with `execute_generation()` production entry point.

## Roadmap Rebaseline (2026-03-28)

Party Mode consensus + parallel GPT-5.4 architectural review identified significant overlap between completed Epics 1-3/2A work and downstream epic scope. Rebaseline applied:

- **Epic 4A** (Agent Governance, Quality Optimization & APP Observability): **6 stories** — run baton, lane matrix, envelope governance, agent QA gate, perception caching + observability (**`run_mode` tagging; ad-hoc excluded from course-progress metrics**), **ad-hoc ledger & learning enforcement (4A-6, FR91)**. Must complete before Epic 4. FRs FR81–FR91 on PRD.
- **Epic 4 updated**: Dependency on 4A. Stories 4.2 (Quality Gates) and 4.4 (Reporting) updated to assume governance layer + Vera fidelity checks.
- **Epic 5 trimmed**: Story 5.2 (Assembly Coordination) dropped — compositor skill delivers this. Story 5.3 (Style Orchestration) merged into governance. Story 5.4 edited — Panopto and Kling already done. Story 5.1 and 5.4 are now complete.
- **Epic 6 trimmed**: Story 6.2 (Enhanced Canvas) merged into Story 3.6 (Canvas Specialist). Story 6.1 completed.
- **Epics 7, 8, 9 collapsed** into Epic G (Governance Synthesis & Intelligence Optimization): **3 stories** — platform allocation (G.1), tool/doc synthesis (G.2), **APP session readiness & health monitoring** (G.3, 2026-03-30: SQLite/`state`/imports + report; composes with pre-flight-check). Epic G is now complete.
- **2026-04-03:** `scripts.utilities.run_constants` loads frozen **`run-constants.yaml`** per bundle; wired into `app_session_readiness --bundle-dir` and `validate-source-bundle-confidence` when the file exists (contract v1.2).
- **2026-04-03:** Prompt 3 hardening pass added `scripts.utilities.validate_source_bundle_confidence` as stable CLI wrapper, normalized validator parsing for heading/ingestion format variants, and centralized hyphenated skill loading in `scripts.utilities.skill_module_loader`.
- **Epic 10**: Predictive optimization requires Epic 4 + Epic G telemetry. Story 10.1 is now complete.

**Net: 11 epics → 9 epics, 46 stories → 40 stories** (historical rebaseline); **+Story 4A-6 → 41 stories** (2026-03-29); **+Story G.3 → 42 stories** (2026-03-30). Architecture updated with governance section.

## Composition Architecture (Added 2026-03-27)

See `_bmad-output/brainstorming/party-mode-composition-architecture.md` for full decision record.

- **Silent Video + Smart Audio:** Kling always `sound-off`. ElevenLabs owns all audio (narration, SFX, music).
- **Segment manifest:** YAML file produced by Irene Pass 2. Single source of truth. All downstream agents read/write.
- **G4 anti-drift rule:** The G4 fidelity contract references both the narration script template and the segment manifest template so Pass 2 changes cannot drift out of validation coverage.
- **Narration-paced video:** ElevenLabs generates first; narration_duration becomes clip duration target for Kira.
- **Descript:** Sole composition platform (manual-tool pattern). Compositor skill (Story 3.5) generates Descript Assembly Guide and can **`sync-visuals`** to copy Gate-approved stills into the assembly bundle (`visuals/`) next to audio, captions, and summaries.
- **Four HIL gates:** Lesson plan → slides → script+manifest → final video.
- **Quinn-R two-pass:** Pre-composition (asset quality) + post-composition (final export).
- **Irene two-pass:** Pass 1 (lesson plan + slide brief before Gary); Pass 2 (narration script + segment manifest after Gary + HIL Gate 2).
- **2026-04-03 anti-drift hardening:** Prompt 6B now requires literal-visual operator packet + readiness confirmation before Gary dispatch side effects; Storyboard A (post-Gary) and Storyboard B (post-Irene Pass 2) are explicit approval checkpoints before advancing to subsequent pipeline spend.
- **2026-04-05 literal-visual rendering policy:** literal-visual slides are enforced as full-slide image-only at dispatch input. Supporting prose is moved to Irene Pass 2 narration/script, and Gate 2 preflight validation fails on non-URL literal-visual payload content.
- **2026-04-05 literal-visual reliability fix:** Anti-fade prompt ("full opacity, not as background, not faded") + initial attempt plus one retry (`_MAX_TEMPLATE_RETRIES = 2`) + composite fallback (preintegration PNG or URL download). Gamma classifies images as accent/background by content — not API-controllable. `visual_fill_validator` enhanced with variance-based content detection (`content_stddev`). Provenance tracked via `literal_visual_source` field.
- **2026-04-08 motion review contract:** Storyboard B shows both the approved still and the approved motion clip for motion segments. Downstream contracts preserve the still in `visual_file` and the playback asset in `motion_asset_path`; motion-first narration is the expected design when `visual_mode: video`.
- **Gary deck enhancement:** Deck mode (numCards by content type), theme/template preview (TP capability), gary_slide_output return field.
- **Seven instructional use cases:** Narrated deck, dialogue, walkthrough, case study, assessment prompt, concept explainer, module bumper — all one pipeline.

## Key Files

- `_bmad-output/planning-artifacts/prd.md` - Complete PRD (70 FRs, recast)
- `_bmad-output/planning-artifacts/architecture.md` - Complete architecture (recast)
- `_bmad-output/planning-artifacts/epics.md` - Epic breakdown with requirements (recast)
- `_bmad-output/strategic-decisions-collaborative-intelligence.md` - Strategic decisions
- `_bmad-output/brainstorming/brainstorming-session-20260325-150802.md` - Brainstorming session
- `_bmad-output/brainstorming/party-mode-coaching-marcus-orchestrator.md` - Marcus coaching doc
- `_bmad-output/brainstorming/party-mode-composition-architecture.md` - **Composition architecture decisions (2026-03-27)**
- `_bmad-output/implementation-artifacts/3-3-1-composition-architecture-harmonization.md` - **Story 3.3.1 (DONE)**
- `skills/bmad-agent-marcus/SKILL.md` - **Marcus orchestrator agent (Story 2.1 DONE)**
- `skills/reports/bmad-agent-marcus/quality-scan/2026-03-26_152243/quality-report.md` - Marcus quality scan
- `tests/agents/bmad-agent-marcus/interaction-test-guide.md` - Marcus interaction tests
- `resources/tool-inventory/tool-access-matrix.md` - **Tool universe access matrix (17 tools)**
- `scripts/heartbeat_check.mjs` - Baseline read-only API heartbeat across configured tools
- `scripts/smoke_elevenlabs.mjs` - Focused ElevenLabs API smoke check
- `scripts/smoke_qualtrics.mjs` - Focused Qualtrics API smoke check
- `skills/woodshed/SKILL.md` - **Shared exemplar mastery skill (study, reproduce, compare, regress)**
- `resources/exemplars/_shared/woodshed-workflow.md` - **Complete woodshed workflow protocol (logging, reflection, circuit breaker)**
- `resources/exemplars/_shared/comparison-rubric-template.md` - **Rubric for scoring exemplar reproductions**
- `resources/exemplars/gamma/_catalog.yaml` - **Gamma exemplar registry**
- `docs/agent-environment.md` - Agent/MCP guidance  
- `docs/operations-context.md` - Compact operations-only context for production sessions
- `docs/workflow/human-in-the-loop.md` - HIL procedure
- `.cursor/rules/course-content-agents.mdc` - Cursor agent rules
