---
stepsCompleted: [1, 2, 3, 4]
status: 'complete'
completedAt: 'March 25, 2026'
inputDocuments: [
  "_bmad-output/planning-artifacts/prd.md",
  "_bmad-output/planning-artifacts/architecture.md",
  "_bmad-output/brainstorming/brainstorming-session-20260325-150802.md"
]
---

# course-DEV-IDE-with-AGENTS - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for course-DEV-IDE-with-AGENTS, decomposing the requirements from the PRD, Architecture, and existing brainstorming epics into implementable stories for collaborative intelligence orchestration system development.

## Requirements Inventory

### Functional Requirements

**Note:** FR inventory expanded from 70 to 80 FRs (March 26, 2026 Party Mode session). Added Source Wrangling (FR71-74) and Run Mode Management (FR75-80).

**Agent Orchestration & Coordination (6 FRs):**
- FR1: Master orchestrator can coordinate multiple specialist agents through production workflows
- FR2: Agents can communicate with each other through event-driven messaging protocols  
- FR3: Agents can register their capabilities and availability in the coordination registry
- FR4: Master orchestrator can assign tasks to agents based on capability matching
- FR5: Agents can report task completion and status updates to the coordination system
- FR6: System can manage agent dependencies and handoff protocols between production stages

**Production Workflow Management (9 FRs):**
- FR7: Users can initiate production runs for course modules with context specification
- FR8: System can maintain production run state across tool failures and interruptions
- FR9: System can track workflow progress through multiple coordinated stages
- FR10: Users can review and approve work at designated human checkpoint gates
- FR11: System can manage cross-run context and memory for course consistency
- FR12: Users can access production run history and audit trails
- FR33: Users can export completed content to target platforms (Canvas, CourseArc, Panopto) with platform-specific formatting
- FR34: System can manage learning objectives alignment across all content production decisions  
- FR35: Users can configure run presets (explore, draft, production, regulated) with parameter overrides

**Tool Integration & API Management (5 FRs):**
- FR13: System can integrate with external tools through MCP and direct API connections
- FR14: System can verify API connectivity before production runs begin
- FR15: Agents can manipulate tools (Gamma, ElevenLabs, Canvas) through standardized interfaces
- FR16: System can handle tool API failures with retry mechanisms and graceful degradation
- FR17: System can manage API keys and authentication across multiple tool integrations

**Skills & Expertise Management (7 FRs):**
- FR18: System can store and evolve skills for tool-specific expertise (Gamma prompts, ElevenLabs optimization)
- FR19: Agents can access and apply skills for specialized tool interactions  
- FR20: System can capture and crystallize creative decision patterns through skills evolution
- FR21: Users can review and refine skills based on production outcomes
- FR22: System can version control skills and track effectiveness improvements
- FR42: System can analyze and recommend tool optimization strategies based on production outcome patterns
- FR43: System can detect and suggest workflow improvements through systematic experience analysis
- FR44: Users can access systematic expertise insights and creative pattern recommendations

**Quality Control & Review (7 FRs):**
- FR23: Agents can perform automated quality review at each production stage
- FR24: System can enforce quality standards through configurable validation rules
- FR25: Agents can conduct peer review of other agents' outputs against creative standards
- FR26: Users can override quality decisions when creative judgment is required
- FR27: System can maintain quality audit trails for production accountability
- FR48: System can provide comprehensive audit trails for compliance and quality assurance reporting
- FR49: Users can configure accessibility standards enforcement across all content production workflows

**Content & Asset Management (8 FRs):**
- FR28: System can manage course, module, and asset context entities throughout production
- FR29: System can track asset evolution history and creative decision rationale
- FR30: Users can define and update brand guidelines, style standards, and creative policies  
- FR31: System can ensure content accessibility and compliance with educational standards
- FR32: System can generate release manifests for final content deployment
- FR45: Agents can maintain creative consistency across multiple content types within the same course module
- FR46: System can provide creative decision rationale tracking for learning objective alignment  
- FR47: Users can access creative pattern libraries built from successful production runs

**System Infrastructure & Development (6 FRs):**
- FR36: System can manage the core entity model (Course Context, Module Context, Asset Specification entities) with version control
- FR37: System can provide real-time coordination state visibility for debugging and monitoring agent interactions
- FR38: System can backup and restore production run states for disaster recovery
- FR39: Developers can set up the development environment with automated dependency and API verification
- FR40: System can provide development mode with enhanced logging and debugging capabilities for agent coordination
- FR41: Users can validate system configuration before initiating production runs

**Production Intelligence & Reporting (3 FRs):**
- FR50: System can generate comprehensive production run reports including purpose achievement, stage effectiveness, and optimization recommendations
- FR51: Users can access comparative analysis between production runs to track workflow improvement patterns  
- FR52: System can automatically identify workflow bottlenecks and suggest optimization strategies based on run performance data

**Conversational Orchestrator Interface (8 FRs):**
- FR53: Users can initiate production runs through natural language conversation with master orchestrator
- FR54: Master orchestrator can request user input, confirmation, and direction through conversational prompts
- FR55: Users can provide information, address problems, and confirm actions through direct conversation with orchestrator
- FR56: Master orchestrator can present work products for user review and incorporate feedback through conversational interaction  
- FR57: Users can monitor and direct production run progress through continuous dialogue with orchestrator
- FR58: System can provide conversational interface for all user interactions with master orchestrator
- FR59: Master orchestrator can manage conversation flow including requests, confirmations, and reviews
- FR60: Users can access all system capabilities through natural language conversation with orchestrator

**Parameter Intelligence & Tool Mastery (5 FRs):**
- FR61: Specialty agents can master complete tool API/MCP parameter sets including all control options and value ranges
- FR62: Orchestrator can elicit tool parameters through conversational education when not previously established
- FR63: System can store parameter decisions in human-readable style guide format organized by course/project context
- FR64: Specialty agents can determine optimal parameters through runtime elicitation, style guide defaults, and prior run patterns
- FR65: Users can provide exemplar-based parameter guidance that agents apply to similar contexts with intelligent inference

**Pre-Flight Check & Tool Validation (5 FRs):**
- FR66: Users can invoke pre-flight system validation through conversational request to master orchestrator
- FR67: System can verify MCP connectivity, API authentication, and tool availability before production runs
- FR68: System can scan current tool documentation to detect API changes, new capabilities, or status modifications
- FR69: Pre-flight check can identify potential issues and provide resolution guidance before production workflow initiation
- FR70: System can update tool capability knowledge and parameter catalogs based on documentation intelligence scanning

**Source Wrangling & External Reference Integration (4 FRs):**
- FR71: System shall integrate with Notion API to read course development notes by database or page reference
- FR72: System shall support writing feedback (readiness assessments, design recommendations) back to Notion pages
- FR73: System shall read source materials from a configured local Box Drive path
- FR74: System shall provide a source wrangling capability that pulls reference materials from configured external sources (Notion, Box Drive, future sources) into the production context

**Run Mode Management (6 FRs):**
- FR75: Master Orchestrator shall support a binary ad-hoc/default mode switch, settable and reportable via natural language conversation
- FR76: In ad-hoc mode, all state-tracking writes (SQLite, YAML config, memory sidecars) shall be suppressed or redirected to scratch state
- FR77: In ad-hoc mode, all produced assets shall route to a designated scratch/staging area separate from production paths
- FR78: Quality assurance actions shall execute regardless of the current run mode
- FR79: Mode switch shall persist within a session until explicitly changed by the user
- FR80: System shall support future evolution to a per-level (course/module/lesson/asset) modality matrix with additional modes (write-only, read-only)

### Non-Functional Requirements

**Performance (7 NFRs):**
- Agent-to-agent communication handoffs complete within 5 seconds under normal conditions
- Tool API calls timeout after 30 seconds before triggering retry mechanisms
- Production run status updates provided within 10 seconds of stage completion
- Quality review checkpoints present results within 15 seconds for human decision-making
- Complete Course 1, Module 1 recreation completes within 45 minutes for standard complexity content
- Individual production stages complete within 10 minutes per asset
- System startup and environment verification complete within 2 minutes

**Integration (6 NFRs):**
- Tool API failure rate maintained below 5% during production runs
- Exponential backoff retry mechanism: 3 attempts with 2s, 4s, 8s delays before escalation
- API connectivity verification achieves 100% success rate during pre-production checks
- Critical integrations maintain 95% availability during standard business hours
- System continues production when non-critical tool integrations fail temporarily
- Integration failures logged with sufficient detail for troubleshooting and optimization

**Security (4 NFRs):**
- All API keys stored in encrypted .env files with restricted file system permissions
- API keys never logged in plain text or included in audit trails
- Production run data encrypted at rest using AES-256 encryption
- System access logs maintain 30-day retention for security audit purposes

**Accessibility (4 NFRs):**
- All generated content meets WCAG 2.1 AA compliance requirements automatically
- Visual assets include descriptive alt-text generated and validated by quality review agents
- Color contrast ratios maintain 4.5:1 minimum for normal text, 3:1 for large text
- Generated audio content includes synchronized captions and transcripts

**Reliability (4 NFRs):**
- Development environment maintains 99% availability during planned working hours
- Production run failure rate below 5% due to system issues (excluding external API failures)
- Agent coordination system recovers automatically from individual agent failures within 30 seconds
- Backup and recovery capabilities restore production run state within 5 minutes of system restart

### Additional Requirements

**Architecture Integration Requirements:**
- Hybrid multi-agent framework implementation (subagents-pydantic-ai + conversational interface + traditional Python packaging)
- Cursor IDE chat integration with terminal fallback for conversational orchestrator interface
- Hybrid execution pattern (function calls for simple tasks, events for complex workflows) through skills bridge framework
- Hybrid state management (YAML configuration files + SQLite runtime coordination) with cross-run persistence
- Parameter intelligence architecture enabling tool mastery and contextual parameter optimization

**Technical Infrastructure Requirements:**
- Python 3.10+ with asyncio-native multi-agent coordination and traditional pip packaging with virtual environment isolation
- subagents-pydantic-ai framework (v0.0.8+) with auto-mode execution, nested agents, and parent-child communication protocols
- SQLite database for runtime coordination state with ACID transactions and backup procedures
- YAML configuration files for course context, style guide, and tool policies with git version control
- MCP integration framework with standardized tool manipulation patterns and consistent error handling

### UX Design Requirements

**Conversational Interface Requirements:**
- Primary interface through Cursor IDE chat with natural language conversation flow
- Master orchestrator serves as single point of contact hiding all system complexity
- Conversational parameter elicitation with educational context and intelligent defaults
- Work product presentation through conversation with clear review and approval workflows
- Error resolution and problem-solving through conversational guidance and recovery suggestions

## Existing Epic Architecture (Recast for BMad Agent + Cursor Plugin Approach)

**Epic 1: Repository Environment & Agent Infrastructure** (FOUNDATIONAL)
Cursor plugin setup, agent/skill directory structure, Python infrastructure, SQLite + YAML state management, MCP integration, pre-flight check infrastructure, testing framework.

**Epic 2: Master Agent Architecture & Development**
Create master orchestrator agent via `bmad-agent-builder`, Cursor chat integration, memory sidecar for persistent learning, conversational workflow management, parameter intelligence, pre-flight orchestration.

**Epic 3: Core Tool Integrations** 
Create specialty agents (Gamma, ElevenLabs, Canvas) via `bmad-agent-builder`, tool mastery skills with SKILL.md + references/ + scripts/, parameter catalogs in style guide YAML.

**Epic 4: Workflow Coordination & State Infrastructure**
Cross-run persistence via BMad memory sidecars + SQLite, production run lifecycle management, quality gate coordination, production intelligence and run reporting skills.

**Epic 5: Unified Content Production Engine** 
Additional specialty agents (Vyond, Midjourney, CapCut) via `bmad-agent-builder`, multi-modal assembly skills, style orchestration with brand consistency enforcement.

**Epic 6: LMS Platform Integration & Delivery**
CourseArc specialist agent, enhanced Canvas specialist, platform deployment skills with SCORM packaging scripts.

**Epic 7: Multi-Platform Intelligence Matrix**
Platform allocation agent with four-platform decision intelligence, context-aware routing skills, handoff choreography patterns.

**Epic 8: Tool Review & Optimization Intelligence**
Tool review agent with environment scanning and documentation monitoring skills, policy crystallization via agent memory sidecars.

**Epic 9: Living Architecture Documentation System**
Documentation agent with self-improving capability using BMad memory sidecar patterns, knowledge crystallization through pattern analysis.

**Epic 10: Strategic Production Orchestration**
Enhanced master orchestrator with predictive optimization skills, evolved coordination protocols, performance monitoring and improvement recommendations.

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1-6 | Epic 2 | Agent orchestration & coordination |
| FR7-12 | Epic 4 | Production workflow management (core) |
| FR13-17 | Epic 1 + Epic 3 | Tool integration (Epic 1: API clients; Epic 3: agent mastery skills) |
| FR18-22 | Epic 3 | Skills & expertise management (foundation) |
| FR23-27 | Epic 4 | Quality control & review |
| FR28-32 | Epic 4 | Content & asset management |
| FR33-35 | Epic 4 | Production workflow (export, objectives, presets) |
| FR36-41 | Epic 1 | System infrastructure & development |
| FR42-44 | Epic 8 | Advanced expertise insights & recommendations |
| FR45-47 | Epic 5 | Creative consistency & pattern libraries |
| FR48-49 | Epic 4 | Compliance audit trails & accessibility enforcement |
| FR50-52 | Epic 4 | Production intelligence & reporting |
| FR53-60 | Epic 2 | Conversational orchestrator interface |
| FR61-65 | Epic 3 | Parameter intelligence & tool mastery |
| FR66-70 | Epic 1 | Pre-flight check & tool validation |
| FR71-74 | Epic 3 | Source wrangling & external reference integration (Notion API, Box Drive, source wrangler agent/skill) |
| FR75-80 | Epic 2 | Run mode management (ad-hoc/default switch, state suppression, scratch routing, QA always-on) |

## Epic List

1. **Epic 1: Repository Environment & Agent Infrastructure** - Cursor plugin foundation, Python infrastructure, state management, pre-flight checks, testing, **API/MCP integration for Gamma, ElevenLabs, Canvas**
2. **Epic 2: Master Agent Architecture & Development** - Conversational orchestrator creation via bmad-agent-builder, coordination protocols, parameter intelligence, **run mode management (ad-hoc/default switch)**
3. **Epic 2A: Fidelity Assurance & APP Intelligence Infrastructure** - Fidelity maturity audit, sensory bridges skill, provenance protocol, Fidelity Assessor agent, gate-by-gate verification (G0–G6), cumulative drift tracking, leaky neck remediation, APP maturity audit skill. **Implements the GOLD document architecture.**
4. **Epic 3: Core Tool Integrations** - Specialty agent creation (Gamma, ElevenLabs, Canvas) via bmad-agent-builder, tool mastery skills, **source wrangler (Notion + Box Drive)**
4. **Epic 4: Workflow Coordination & State Infrastructure** - Production run management, quality gates, run reporting, learning loop closure
5. **Epic 5: Unified Content Production Engine** - Additional tool agents, multi-modal assembly, style orchestration
6. **Epic 6: LMS Platform Integration & Delivery** - CourseArc agent, enhanced Canvas, SCORM packaging
7. **Epic 7: Multi-Platform Intelligence Matrix** - Platform allocation agent, routing intelligence
8. **Epic 8: Tool Review & Optimization Intelligence** - Tool scanning agent, policy crystallization
9. **Epic 9: Living Architecture Documentation System** - Self-improving documentation agent
10. **Epic 10: Strategic Production Orchestration** - Enhanced orchestrator with predictive optimization
11. **Epic 11: APP Trial Remediation & Run Contract Hardening** - Due-diligence findings, Gary outbound contract, Irene Pass 2 perception, theme-mapping handshake
12. **Epic SB: Storyboard & Run Visualization** - On-demand storyboard run-view with Pass 2 narration merge, related-asset rows, run-id traceability
13. **Epic 12: Double-Dispatch Gamma Slide Selection** - Per-run dual Gamma dispatch, parallel fidelity review, side-by-side selection storyboard, winner forwarding to Irene
14. **Epic 13: Visual-Aware Irene Pass 2 Scripting** - Mandatory perception contract, parameterized visual reference injection in narration, segment manifest enrichment
15. **Epic 14: Motion-Enhanced Presentation Workflow** - Motion workflow variant with Kira video + manual animation, motion decision point, motion perception, compositor motion support
16. **Epic 15: Learning & Compound Intelligence** - Learning event capture, tracked-run retrospectives, upstream-from-downstream feedback routing, synergy scorecards, pattern condensation, workflow-family learning
17. **Epic 16: Bounded Autonomy Expansion** - Autonomy evidence framework, shared governance enforcement utilities, expanded handoff validators, contract linting, Marcus autonomous routing for routine decisions
18. **Epic 17: Research & Reference Services** - Consensus + Scite.ai triangulation, related-resources list generation, inline citation injection, hypothesis/pro-con research for learning experiences, shared research skill
19. **Epic 18: Additional Assets & Workflow Families** - Discovery-first requirements for cases/scenarios, quizzes, discussions, handouts, podcasts, diagrams; reusable workflow-family implementation framework

---

## Epic 1: Repository Environment & Agent Infrastructure

**Goal**: Users can set up and validate the complete collaborative intelligence development environment with Cursor plugin structure, Python infrastructure, state management, and pre-flight checking capabilities.

**FRs covered:** FR36, FR37, FR38, FR39, FR40, FR41, FR66, FR67, FR68, FR69, FR70

### Story 1.1: Cursor Plugin Foundation & Repository Structure

As a developer,
I want the repository configured as a Cursor plugin with proper directory structure,
So that agents, skills, rules, and MCP servers are auto-discovered by the IDE.

**Acceptance Criteria:**

**Given** a fresh clone of the repository
**When** the developer opens it in Cursor IDE
**Then** Cursor discovers the plugin via `.cursor-plugin/plugin.json` manifest
**And** the `agents/`, `skills/`, `rules/`, `commands/`, `hooks/` directories exist with placeholder READMEs
**And** `.mcp.json` defines available MCP tool servers for Gamma, ElevenLabs, Canvas
**And** `hooks/hooks.json` defines event triggers for sessionStart and sessionEnd
**And** `rules/course-content-agents.mdc` provides persistent agent behavior guidance

### Story 1.2: Python Infrastructure & Environment Configuration

As a developer,
I want a Python development environment with API key management and dependency isolation,
So that agent skills can execute Python scripts for tool integration and state management.

**Acceptance Criteria:**

**Given** the Cursor plugin structure exists
**When** the developer runs environment setup
**Then** a virtual environment is created with all dependencies from `requirements.txt`
**And** `.env.example` provides a complete template with documented entries for all API-capable tools from the tools inventory:
```
# Slide Generation
GAMMA_API_KEY=
GAMMA_API_URL=

# Voice/Audio Synthesis
ELEVENLABS_API_KEY=
ELEVENLABS_API_URL=

# Canvas LMS
CANVAS_API_URL=
CANVAS_ACCESS_TOKEN=

# Video Generation & Editing
VYOND_API_KEY=
CAPCUT_API_KEY=
KLING_API_KEY=
DESCRIPT_API_KEY=

# Image Generation
MIDJOURNEY_API_KEY=

# Design
CANVA_API_KEY=

# Interactive Authoring
ARTICULATE_API_KEY=

# Chatbot
BOTPRESS_API_KEY=
BOTPRESS_BOT_ID=

# Audio Podcasting
WONDERCRAFT_API_KEY=
```
**And** `scripts/api_clients/` contains base API client patterns following canvas_api_tools conventions
**And** `scripts/utilities/` contains shared helper functions for file operations and logging
**And** automated dependency verification confirms all packages install correctly

### Story 1.3: State Management Infrastructure

As a developer,
I want SQLite database, YAML configuration files, and BMad memory sidecar directories initialized,
So that agents have persistent state for coordination, configuration, and learning.

**Acceptance Criteria:**

**Given** the Python environment is configured
**When** state infrastructure initialization script runs
**Then** `state/config/course_context.yaml` exists with course-level template structure
**And** `state/config/style_guide.yaml` exists with per-tool parameter preference sections (brand standards live in `resources/style-bible/`; see `docs/directory-responsibilities.md`)
**And** `state/config/tool_policies.yaml` exists with tool allocation policy template
**And** `state/runtime/coordination.db` SQLite database is created with production_runs, agent_coordination, and quality_gates tables
**And** `_bmad/memory/` directory exists with placeholder structure for agent sidecars
**And** backup scripts exist at `state/runtime/backup/` for disaster recovery

### Story 1.4: Pre-Flight Check Skill

As a user,
I want a pre-flight check skill that verifies all MCPs, APIs, and tool capabilities before production runs,
So that I know the system is ready before starting content creation.

**Acceptance Criteria:**

**Given** the pre-flight-check skill exists at `skills/pre-flight-check/SKILL.md`
**When** the pre-flight check skill is invoked
**Then** all configured MCP servers in `.mcp.json` and `.cursor/mcp.json` are tested for connectivity and tool discovery
**And** all API keys in `.env` are validated against their respective services with read-only test calls
**And** `scripts/heartbeat_check.mjs` is incorporated as the baseline API readiness check
**And** targeted smoke checks are run for API-primary / MCP-deferred tools, including:
  - `scripts/smoke_elevenlabs.mjs`
  - `scripts/smoke_qualtrics.mjs`
**And** current tool documentation is scanned via Ref MCP for capability or status changes
**And** a comprehensive readiness report is generated with pass/fail status per tool
**And** the readiness report classifies each tool as one of:
  - MCP-ready
  - API-ready
  - manual-only
  - blocked/deferred
**And** resolution guidance is provided for any failures detected
**And** `skills/pre-flight-check/scripts/` contains Python connectivity verification code
**And** `skills/pre-flight-check/references/` contains diagnostic procedures, tool doc scanning patterns, and a matrix explaining when pre-flight should rely on MCP checks vs API smoke checks

### Story 1.5: Testing Framework & Development Mode

As a developer,
I want testing infrastructure and development mode capabilities,
So that agent coordination and skill execution can be validated during development.

**Acceptance Criteria:**

**Given** the testing framework is configured
**When** tests are executed via `pytest`
**Then** unit tests in `tests/unit/` validate Python API client scripts
**And** unit tests validate SQLite state management operations
**And** integration tests in `tests/integration/` validate skill invocation patterns
**And** test fixtures in `tests/fixtures/` include mock API responses for Gamma, ElevenLabs, and Canvas
**And** development mode logging configuration provides enhanced agent coordination debugging output
**And** `FR40` development mode capability is satisfied with configurable log levels

### Story 1.6: Gamma API Integration & MCP Setup

As a developer,
I want a working Gamma API client and MCP configuration,
So that agents and skills can generate slides through verified, tested tool connectivity.

**Acceptance Criteria:**

**Given** the Python infrastructure and .env API keys are configured
**When** the Gamma API client is built and tested
**Then** `scripts/api_clients/gamma_client.py` provides authenticated Gamma API access
**And** slide generation can be triggered programmatically with configurable parameters (LLM choice, style, output format)
**And** exponential backoff retry logic (3 attempts: 2s, 4s, 8s) handles API failures gracefully
**And** MCP server configuration for Gamma is validated in `.mcp.json` (if Gamma MCP exists)
**And** a working integration test demonstrates end-to-end slide generation from a text prompt
**And** API response parsing extracts slide URLs, metadata, and status information
**And** error handling provides clear diagnostic messages for authentication failures, rate limits, and service outages

### Story 1.7: ElevenLabs API Integration

As a developer,
I want a working ElevenLabs API client for voice synthesis,
So that agents and skills can generate voiceover audio through verified, tested connectivity.

**Acceptance Criteria:**

**Given** the Python infrastructure and .env API keys are configured
**When** the ElevenLabs API client is built and tested
**Then** `scripts/api_clients/elevenlabs_client.py` provides authenticated ElevenLabs API access
**And** voice synthesis can be triggered with configurable parameters (voice ID, stability, clarity, style)
**And** available voices can be listed and filtered programmatically
**And** audio output is saved in standard formats (MP3, WAV) with timing metadata
**And** exponential backoff retry logic handles API failures gracefully
**And** a working integration test demonstrates end-to-end voiceover generation from text input
**And** error handling provides clear diagnostics for quota limits, voice unavailability, and service issues

### Story 1.8: Canvas API Integration

As a developer,
I want a working Canvas API client following canvas_api_tools patterns,
So that agents and skills can deploy content to Canvas LMS through verified, tested connectivity.

**Acceptance Criteria:**

**Given** the Python infrastructure and .env API keys are configured (CANVAS_API_URL, CANVAS_ACCESS_TOKEN)
**When** the Canvas API client is built and tested
**Then** `scripts/api_clients/canvas_client.py` provides authenticated Canvas REST API access following canvas_api_tools patterns
**And** module creation, page publishing, and quiz deployment operations work programmatically
**And** course and module listing operations support content deployment workflows
**And** exponential backoff retry logic and Canvas-specific rate limit handling are implemented
**And** a working integration test demonstrates module creation and page publishing against a test Canvas instance
**And** error handling provides clear diagnostics for authentication, permissions, and API rate limiting
**And** the client respects institutional API policies and scoped token permissions

### Story 1.9: Qualtrics API/MCP Integration

As a developer,
I want a working Qualtrics API connection and MCP server configured,
So that agents and skills can create and manage surveys, assessments, and data collection through verified, tested connectivity.

**Acceptance Criteria:**

**Given** the Python infrastructure and .env API keys are configured (QUALTRICS_API_TOKEN, QUALTRICS_BASE_URL)
**When** the Qualtrics integration is built and tested
**Then** `scripts/api_clients/qualtrics_client.py` provides authenticated Qualtrics REST API v3 access
**And** survey creation, question management, and response export operations work programmatically
**And** the Qualtrics MCP server (`qualtrics-mcp-server`) is validated in `.mcp.json` with correct environment variable mapping
**And** exponential backoff retry logic handles API failures gracefully
**And** a working integration test demonstrates survey listing and basic survey creation
**And** error handling provides clear diagnostics for authentication failures, quota limits, and API errors

### Story 1.10: Canva MCP Integration

As a developer,
I want the Canva MCP server configured and validated,
So that agents and skills can create, export, and manage designs through the official Canva MCP.

**Acceptance Criteria:**

**Given** the Canva remote MCP server is configured in `.mcp.json` (url: `https://mcp.canva.com/mcp`)
**When** the Canva MCP integration is validated
**Then** the Canva MCP server connects and responds to tool discovery requests
**And** OAuth authentication flow works through the MCP server's browser-based auth
**And** `create_design`, `export_design`, `get_design`, and `list_designs` tools are available
**And** a working integration test demonstrates design listing and basic design creation
**And** error handling provides clear diagnostics for auth failures and API rate limits (20 req/min)

### Story 1.11: Panopto API Integration

As a developer,
I want a working Panopto API client for video platform management,
So that agents and skills can manage video content on the institutional Panopto instance through verified, tested connectivity.

**Acceptance Criteria:**

**Given** the Python infrastructure and .env credentials are configured (PANOPTO_BASE_URL, PANOPTO_CLIENT_ID, PANOPTO_CLIENT_SECRET)
**When** the Panopto API client is built and tested
**Then** `scripts/api_clients/panopto_client.py` provides authenticated Panopto REST API access with OAuth2
**And** video listing, folder management, and metadata retrieval operations work programmatically
**And** exponential backoff retry logic handles API failures gracefully
**And** a working integration test demonstrates folder listing and video search
**And** error handling provides clear diagnostics for authentication, permissions, and API errors

---

## Epic 2: Master Agent Architecture & Development

**Goal**: Users can converse with the master orchestrator agent to initiate, direct, and manage production runs through natural language interface with intelligent tool parameter management and pre-flight orchestration.

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR53, FR54, FR55, FR56, FR57, FR58, FR59, FR60, FR75, FR76, FR77, FR78, FR79, FR80

### Story 2.1: Marcus — Master Orchestrator Agent Creation

As a user,
I want a master orchestrator agent named Marcus created via bmad-agent-builder,
So that I have a conversational "general contractor" for all production workflow interactions.

**bmad-agent-builder Discovery Answers** — Party Mode coaching COMPLETE (March 26, 2026, Session 2).
Full copy-paste-ready answers: `_bmad-output/brainstorming/party-mode-coaching-marcus-orchestrator.md`

**Agent identity:** displayName: Marcus | title: Creative Production Orchestrator | icon: 🎬 | name: `bmad-agent-marcus`

**Phase 1 - Intent Discovery:**
Build a master orchestrator agent named Marcus — a Creative Production Orchestrator who serves as the single conversational point of contact for health sciences / medical education course content production within the Cursor IDE. Marcus is the "general contractor" of a collaborative intelligence system. The user — a medical education faculty member and domain expert — tells Marcus what they want to teach, and Marcus figures out how to produce it. Marcus understands production requests, plans multi-agent workflows, delegates to specialist agents and skills, manages human checkpoint gates, enforces the asset-lesson pairing invariant, and presents work products for review. He is the accountability holder for all production outcomes. Marcus never touches APIs or tools directly — he operates at the agent layer (judgment, decisions, personality). Marcus consults two living reference libraries: `resources/style-bible/` (brand identity, visual design, voice/tone) and `resources/exemplars/` (platform allocation policies, worked patterns). He re-reads them fresh at the start of relevant tasks. Marcus operates in two modes: default (full production with state tracking) and ad-hoc (sandbox with assets routed to scratch/staging, state tracking suppressed). QA runs in both modes.

**Phase 2 - Capabilities Strategy:**
Both internal capabilities and external skills.

*Internal capabilities (7):*
- Conversation management and intent parsing
- Production planning and workflow orchestration (consults style bible + exemplars)
- Progress reporting and status summaries
- Human checkpoint coordination (review gates, approval requests)
- **Run mode management**: ad-hoc/default switch enforcement, mode state reporting, scratch routing control
- Mode-aware greeting and session continuity
- Source material prompting — proactively offer to pull Notion/Box references

*External skills (5, delegated to):*
- `pre-flight-check` — MCP/API connectivity verification and tool documentation scanning
- `production-coordination` — workflow stage management and state transitions
- `run-reporting` — production run analysis and effectiveness reports
- `parameter-intelligence` — style guide reading/writing, parameter elicitation
- **`source-wrangling`** — pull from Notion (API), read from Box Drive (local FS), write feedback to Notion

*External agents (delegates to by capability matching):*
- `gamma-specialist` — slide/presentation generation
- `elevenlabs-specialist` — voice synthesis and audio production
- `canvas-specialist` — LMS course structure, modules, assignments, quizzes
- `content-creator` — instructional design and content drafting
- `quality-reviewer` — quality assurance and standards validation (validates against style bible)
- `assembly-coordinator` — multi-modal content assembly
- Future: `qualtrics-specialist`, `canva-specialist`, `source-wrangler` (if elevated from skill to agent)

*When delegating, Marcus passes relevant style bible sections and exemplar references as context to specialists.*

*Script opportunities:* `read-mode-state.py` (mode + session state → JSON), `generate-production-plan.py` (skeleton plan from templates). Routing table stays as prompt-accessible capability table in SKILL.md.

**Phase 3 - Requirements:**
- **Identity**: Marcus — seasoned creative production orchestrator for health sciences/medical education. Veteran executive producer: calm, experienced, unflappable. Understands Bloom's taxonomy, clinical case integration, backward design, LCME/ACGME expectations. Doesn't do instructional design — understands enough to ask right questions, route to right specialists, catch misalignment. Treats user as creative director and domain expert. Knows style bible and exemplar library intimately, references them proactively.
- **Communication Style**: Clear, professional, proactive. Leads with context (not blank prompts). Presents options with recommendations. Natural progress reporting. Appropriate urgency. No unnecessary technical detail. Domain-native vocabulary (learning objectives, assessment alignment, backward design). Unambiguous mode confirmations. Cites style bible and exemplars in planning conversations.
- **Principles**: (1) User's creative vision drives all decisions. (2) Hide system complexity behind conversational ease. (3) Quality gates are non-negotiable in any mode. (4) Asset-lesson pairing invariant is inviolable. (5) Medical education rigor is a professional requirement. (6) Proactively surface decisions that need human judgment. (7) Learn from every production run (default mode). (8) Respect run mode boundary as hard enforcement line. (9) Proactively offer source material assistance. (10) Ground decisions in style bible and exemplar library — re-read live, never cache content.
- **Activation**: Interactive only (no headless v1). Load config → load sidecar index.md → read mode state → greet with mode, context, next-step offer. Four greeting patterns: active default, active ad-hoc, fresh start, pre-flight issue.
- **Memory**: Full sidecar. index.md (production context, preferences, mode, transient ad-hoc section). patterns.md (successful workflows, parameter combos, revision patterns — default mode writes only). chronology.md (run history, satisfaction signals — default mode writes only). access-boundaries.md. Ad-hoc mode: all sidecar read-only except transient section in index.md. Style bible/exemplar content NOT cached in memory — always re-read live.
- **Access Boundaries**: Read (both modes): entire project, `resources/style-bible/`, `resources/exemplars/`, state/, _bmad/memory/, course-content/, BOX_DRIVE_PATH, Notion API. Write (default): state/, own sidecar (all files), course-content/staging/, course-content/courses/ (after human approval), Notion API. Write (ad-hoc): course-content/staging/ad-hoc/ only, index.md transient section only. Deny (both): .env, .cursor-plugin/plugin.json, scripts/api_clients/, tests/, other agents' sidecars (read yes, write never).

**Phase 4-6**: See full coaching document for 10-point gap checklist (Phase 4), build verification checklist (Phase 5), and post-build steps (Phase 6).

**Acceptance Criteria:**

**Given** the bmad-agent-builder skill is invoked with the coached discovery answers
**When** the Marcus orchestrator agent is created through six-phase discovery
**Then** `agents/marcus/SKILL.md` (or builder-chosen path) exists with persona, identity, communication style, and principles as specified
**And** the agent has a capability routing table linking to all 5 external skills and 6+ specialist agents
**And** the agent's persona reflects Marcus — seasoned creative production orchestrator
**And** the agent references `resources/style-bible/` and `resources/exemplars/` in production planning and specialist delegation
**And** the agent knows how to delegate to specialty agents by capability matching, passing relevant style bible sections as context
**And** `_bmad/memory/master-orchestrator-sidecar/` is initialized with index.md, patterns.md, chronology.md, and access-boundaries.md
**And** ad-hoc mode enforces read-only sidecar access (except transient index.md section)
**And** the completed agent structure is reviewed by Party Mode team for completeness and accuracy
**And** a test invocation confirms Marcus greets in character, reports mode, offers capabilities, and handles basic conversation flow

### Story 2.2: Conversational Workflow Management

As a user,
I want the orchestrator to manage production runs through natural conversation,
So that I can initiate, direct, and review content creation by talking to one agent.

**Acceptance Criteria:**

**Given** the master orchestrator agent is activated
**When** a user says "Create the Welcome video for C1M1"
**Then** the orchestrator parses intent and identifies required content type, module, and production requirements
**And** the orchestrator creates a production plan with agent assignments and workflow stages
**And** the orchestrator requests confirmation before proceeding: "Here's my plan. Shall I proceed?"
**And** during production, the orchestrator presents work products for review at human checkpoint gates
**And** the orchestrator reports progress conversationally: "Slides complete. Ready for voiceover. Want to review?"
**And** the user can provide guidance, corrections, or approvals through natural conversation at any point

### Story 2.3: Agent Coordination Protocols

As a user,
I want the orchestrator to coordinate specialist agents seamlessly,
So that multi-agent production workflows execute without my managing individual agents.

**Acceptance Criteria:**

**Given** specialist agents exist in `agents/` directory
**When** the orchestrator needs a specialist capability (slide creation, audio generation, etc.)
**Then** the orchestrator identifies the appropriate specialist agent through capability matching
**And** the orchestrator delegates tasks with full context from the production run state
**And** specialist agent results flow back through the orchestrator for quality review
**And** the orchestrator manages dependencies between stages (slides before voiceover, etc.)
**And** coordination state is persisted in SQLite for recovery from interruptions
**And** the orchestrator's memory sidecar captures coordination patterns for future optimization

### Story 2.4: Parameter Intelligence & Style Guide Integration

As a user,
I want the orchestrator to manage tool parameters intelligently through style guides and conversation,
So that I don't have to manually configure every tool parameter for each production run.

**Acceptance Criteria:**

**Given** `state/config/style_guide.yaml` contains tool parameter preferences
**When** a production task requires tool-specific parameters (e.g., Gamma LLM choice, ElevenLabs voice)
**Then** the orchestrator first checks style guide for established preferences
**And** if parameters exist, applies them automatically with notification: "Using Claude-3 for medical content per your style guide"
**And** if parameters are missing, elicits them conversationally with educational context and recommendations
**And** newly elicited parameters are saved to the style guide with reasoning context
**And** the user can override any parameter at any time through conversation
**And** parameter effectiveness is tracked in the orchestrator's memory sidecar for future optimization

### Story 2.5: Pre-Flight Check Orchestration

As a user,
I want to invoke pre-flight system validation through conversation with the orchestrator,
So that I can confirm all tools are operational before starting a production run.

**Acceptance Criteria:**

**Given** the user says "Run pre-flight check" or "Are all tools ready?"
**When** the orchestrator invokes the pre-flight-check skill
**Then** the orchestrator presents results conversationally: "All systems green" or "Gamma API is down - here's what I suggest"
**And** tool documentation changes are highlighted: "ElevenLabs added new voice options since last check"
**And** the orchestrator recommends whether to proceed, wait, or work around issues
**And** pre-flight results are logged for production run context

### Story 2.6: Run Mode Management (Ad-Hoc / Default Switch)

As a user,
I want to switch the orchestrator between ad-hoc and default (full-throttle) mode via natural conversation,
So that I can experiment freely without impacting production state, or work in full production mode with complete state tracking.

**FRs covered:** FR75, FR76, FR77, FR78, FR79, FR80

**Acceptance Criteria:**

**Given** the user says "Let's work ad hoc until further notice" or equivalent natural language
**When** the orchestrator processes the mode switch request
**Then** the orchestrator sets a hard session-level switch to ad-hoc mode and confirms: "Switching to ad-hoc mode. Assets will go to staging scratch area. State tracking paused. QA still active. Say 'full throttle' or 'default mode' to switch back."
**And** all produced assets route to `course-content/staging/ad-hoc/` (or timestamped scratch subdirectory)
**And** all state-tracking writes (SQLite production run state, YAML config updates, memory sidecar writes) are suppressed
**And** quality assurance actions continue to execute regardless of mode, with QA results stored alongside scratch assets
**And** the mode switch persists within the session until explicitly changed by the user
**And** the orchestrator can accurately report current mode state when asked: "What mode are we in?"
**And** when the user says "Let's work full throttle" or "default mode," the orchestrator switches back and confirms
**And** assets produced during ad-hoc mode remain in the scratch/staging area for manual promotion by the user
**And** a promotion checklist fires QA gates when ad-hoc assets are promoted to production paths (future story)

**Design Note:** This story implements Phase 1 of the modality matrix (binary switch). Future evolution (FR80) will add per-level granularity (course/module/lesson/asset) and additional modes (write-only, read-only). The switch is implemented as a gate on the state management layer -- agents behave identically in both modes; the infrastructure handles routing.

---

## Epic 2A: Fidelity Assurance & APP Intelligence Infrastructure

**Goal**: The Agentic Production Platform (APP) has systematic fidelity assurance at every production gate (G0–G6), with deterministic fidelity contracts, agentic evaluation, sensory bridges for multimodal artifact perception, provenance traceability, and a dedicated Fidelity Assessor agent — so that every artifact produced by the pipeline is verified as faithful to its source of truth before quality review or human checkpoint.

**Motivation**: A Party Mode consultation (2026-03-28) and parallel independent analysis established that the APP is at **Level 0 for fidelity assurance**: zero independent fidelity evaluation at any gate, perception unconfirmed or blind for audio/video, no provenance traceability, and cumulative drift undetected. This epic implements the architecture documented in `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md` (the "GOLD document").

**Design Principles Governing This Epic:**

1. **Three-Layer Intelligence Model** — Every fidelity capability has: L1 deterministic contracts (invariant standards in YAML), L2 agentic evaluation (judgment that evolves with LLM capability), L3 learning memory (sidecars that improve over time).
2. **Hourglass Model** — Intelligence is applied broadly at synthesis (top) and creative execution (bottom), with strict deterministic contracts at the narrow neck (schema validation, parameter binding, API calls). Intelligence must not be used to enforce constraints that can be handled by deterministic code.
3. **Leaky Neck Diagnostic** — Any point where agentic judgment enforces a constraint that could be a schema rule, parameter value, or validation script is a design defect to be remediated.
4. **Sensory Horizon Principle** — An agent cannot verify the fidelity of an artifact it cannot perceive. Sensory bridges must exist for every modality the pipeline produces.

**FRs covered:** FR23, FR24, FR25, FR27, FR48 (quality/audit from original PRD). Additionally introduces fidelity-specific requirements beyond the original PRD scope — provenance traceability, multimodal perception, cumulative drift detection — documented in the GOLD document.

**Prerequisite:** Epic 2 complete (Marcus, coordination protocols, parameter intelligence, mode management all in place).

**Relationship to Epic 3:** This epic creates the fidelity infrastructure that Epic 3's tool specialists (Gary, Irene, ElevenLabs, etc.) operate within. Story 3.11 (Mixed-Fidelity Gamma Generation) is on hold pending this epic's foundational stories. After this epic's G2-G3 stories are complete, Story 3.11 should be revisited to incorporate the fidelity verification it currently lacks.

---

### Story 2A-1: APP Fidelity Maturity Audit & L1 Contract Definitions

As an APP architect,
I want a formalized fidelity maturity audit of the current pipeline with explicit L1 fidelity contracts defined for all production gates,
So that we have a measured baseline, testable acceptance criteria for fidelity at every gate, and a repeatable audit methodology.

**Acceptance Criteria:**

**Given** the current APP pipeline with agents Marcus, Irene, Gary, Quinn-R, Kira, ElevenLabs Voice Director, and the Compositor skill
**When** the fidelity maturity audit is executed
**Then** an audit report is produced covering all 7 gates (G0–G6) evaluated against four pillars: L1 Contracts, L2 Evaluation, L3 Memory, Perception
**And** each gate receives a maturity score (ABSENT / WEAK / PARTIAL / GOOD / STRONG) per pillar with evidence
**And** a Leaky Neck report identifies all points where agentic judgment currently enforces deterministic constraints
**And** L1 fidelity contracts are defined in YAML for gates G0 through G6:
  - G0 (Source Bundle): extraction completeness criteria — section coverage, media capture, metadata preservation
  - G1 (Lesson Plan): LO coverage of source themes, Bloom's alignment, content structure completeness
  - G2 (Slide Brief): LO traceability per slide, fidelity classification accuracy, content item completeness
  - G3 (Generated Slides): text preservation for literal slides, content coverage for creative slides, image placement for literal-visual slides
  - G4 (Narration Script): script-to-slide correspondence, assessment reference accuracy, terminology consistency
  - G5 (Audio): spoken text match to script, pronunciation accuracy, timing/WPM compliance
  - G6 (Composition): segment order, audio-visual sync, assembly completeness against manifest
**And** the L1 contracts are stored in `state/config/fidelity-contracts/` as versioned, human-reviewable YAML files
**And** the Hourglass Model and Leaky Neck diagnostic are documented as architectural references in `docs/`
**And** the Three-Layer Intelligence Model is documented as an architectural reference in `docs/`

**Design Note:** This story produces the contracts and baseline that every subsequent story in this epic builds upon. The audit methodology itself becomes a skill in Story 2A-9.

---

### Story 2A-2: Sensory Bridges Skill

As any agent in the APP pipeline,
I want shared sensory bridge scripts that convert multimodal artifacts (images, audio, PDF, video) into structured agent-interpretable representations,
So that I can perceive and verify artifacts I could not otherwise interpret.

**Acceptance Criteria:**

**Given** a production pipeline that produces PNG slides, MP3/WAV narration, PDF exports, and MP4 video
**When** an agent needs to interpret a non-text artifact
**Then** a shared `sensory-bridges` skill exists at `skills/sensory-bridges/` with SKILL.md, references, and scripts

**Image bridge (`scripts/png_to_agent.py`):**
**Given** a PNG or JPG file path
**When** the image bridge is invoked
**Then** it produces a structured output containing: full text extraction (OCR), layout description (columns, sections, headers, images), visual element inventory, and a confidence score
**And** the output format is JSON with fields: `extracted_text`, `layout_description`, `visual_elements[]`, `confidence` (HIGH/MEDIUM/LOW)
**And** unit tests verify extraction accuracy against known slide PNGs from Trial Run 1 or 2

**Audio bridge (`scripts/audio_to_agent.py`):**
**Given** an MP3 or WAV file path
**When** the audio bridge is invoked
**Then** it produces a timestamped transcript using ElevenLabs STT or local Whisper
**And** the output includes: `transcript_text`, `timestamped_words[]` (word + start_ms + end_ms), `total_duration_ms`, `wpm`, `confidence`
**And** unit tests verify transcription accuracy against known narration files from Trial Run 1

**PDF bridge (`scripts/pdf_to_agent.py`):**
**Given** a PDF file path
**When** the PDF bridge is invoked
**Then** it extracts text content page-by-page and any embedded images as separate PNG files
**And** the output includes: `pages[]` (page_number + text + image_paths[]), `total_pages`, `confidence`

**Canonical Perception Schema:**
**Given** the need for a machine-readable contract between agents and sensory bridges
**When** the sensory bridges skill is built
**Then** a canonical request/response JSON schema is defined at `skills/sensory-bridges/references/perception-schema.md` specifying:
  - **Request schema:** `{ artifact_path, modality (image|audio|pdf|video), gate, requesting_agent, purpose }`
  - **Response schema:** `{ modality, artifact_path, extracted_content (modality-specific fields), confidence (HIGH|MEDIUM|LOW), confidence_rationale, perception_timestamp }`
**And** image response includes: `extracted_text`, `layout_description`, `visual_elements[]`, `slide_title`, `text_blocks[]`
**And** audio response includes: `transcript_text`, `timestamped_words[]`, `total_duration_ms`, `wpm`, `pronunciation_flags[]`
**And** all sensory bridge scripts accept and return this schema — no free-form output
**And** the schema is referenced in `context-envelope-schema.md` as the standard perception artifact format for agent-to-agent handoff of multimodal interpretations

**Confidence Calibration Rubric:**
**Given** that HIGH, MEDIUM, and LOW confidence have no operational definition
**When** the perception protocol is documented
**Then** a modality-specific calibration rubric is defined at `skills/sensory-bridges/references/confidence-rubric.md` specifying:
  - **Image HIGH:** All text blocks extracted with ≥95% OCR confidence; layout unambiguous; all visual elements identifiable
  - **Image MEDIUM:** Text extraction ≥80% confidence OR layout ambiguous (e.g., overlapping elements) OR ≥1 visual element unidentifiable
  - **Image LOW:** Text extraction <80% confidence OR layout unparseable OR image corrupt/blank
  - **Audio HIGH:** Transcript word-error-rate <5% estimated; no unintelligible segments; medical terms recognized
  - **Audio MEDIUM:** WER 5-15% estimated OR ≥1 unintelligible segment <3s OR ≥1 medical term unrecognized
  - **Audio LOW:** WER >15% OR unintelligible segments >3s OR heavy background noise
  - **PDF HIGH:** All pages extracted with text; no OCR-only pages detected
  - **PDF MEDIUM:** ≥1 page is OCR-only (scanned) but text extracted; embedded images detected
  - **PDF LOW:** ≥1 page completely unreadable; scanned without OCR; corrupt
**And** thresholds are configurable per production mode (ad-hoc may accept MEDIUM where production requires HIGH)
**And** the rubric is calibrated empirically during early production runs and updated in the sidecar

**Universal Perception Protocol:**
**Given** any agent consuming a multimodal artifact
**When** the agent receives the artifact
**Then** it follows the five-step protocol: Receive → Perceive (invoke bridge) → Confirm (state interpretation with confidence per rubric) → Proceed (if confidence ≥ gate threshold) → Escalate (if confidence < threshold)
**And** the protocol is documented as a skill reference at `skills/sensory-bridges/references/perception-protocol.md`
**And** the protocol reference is consumable by all agents via standard skill reference loading

**Validator Integration:**
**Given** Quinn-R already has deterministic validators (`accessibility_checker.py`, `brand_validator.py`) and reserves audio/composition validators
**When** sensory bridges produce structured output
**Then** the bridge output format is designed to be consumable by BOTH the Fidelity Assessor (source traceability checks) AND Quinn-R's existing validators (quality checks)
**And** sensory bridge outputs feed into the existing validation stack — they do not create a second parallel validation infrastructure
**And** the handoff between perception outputs and validators is specified in `skills/sensory-bridges/references/validator-handoff.md`

**Design Note:** Video bridge (`video_to_agent.py` using ffmpeg + STT) is deferred to Story 2A-7 when G6 comes into scope. Image and audio bridges are the immediate priorities for G3 and G5 verification.

---

### Story 2A-3: Provenance Protocol — Source Reference Traceability

As the Fidelity Assessor (and any reviewing agent),
I want every pedagogical content field in every artifact schema to carry a `source_ref` citation linking it to its upstream origin,
So that I can trace any content item backward through the pipeline to the original SME material without full-document search.

**Acceptance Criteria:**

**Given** the artifact schemas used across the production pipeline
**When** the Provenance Protocol is implemented
**Then** the following schemas are updated with mandatory `source_ref` fields:

**Lesson plan template** (`skills/bmad-agent-content-creator/references/template-lesson-plan.md`):
- Each learning objective includes `source_ref` citing the section/page of the source bundle it derives from
- Each content block includes `source_ref` citing its origin in the source bundle

**Slide brief template** (`skills/bmad-agent-content-creator/references/template-slide-brief.md`):
- Each slide's `content_items[]` include `source_ref` citing the lesson plan LO or content block
- Fidelity classification rationale includes `source_ref` to the source material signal that triggered the classification

**Context envelope schema** (`skills/bmad-agent-gamma/references/context-envelope-schema.md`):
- `source_ref` fields pass through from slide brief to Gary's input, enabling provenance in the return envelope
- Provenance manifest in the return envelope maps each generated card to its `source_ref` chain

**Narration script template** (new or extended):
- Each narration segment includes `source_ref` citing the lesson plan section and the slide number it complements

**Segment manifest** (existing, extended):
- Each segment definition includes `source_ref` linking to narration script segment and slide brief slide

**And** a provenance chain can be traversed from any downstream artifact (e.g., narration segment) back to the original source bundle section in no more than 3 hops

**Source_ref Grammar and Resolver:**
**And** `source_ref` format is specified as a formal grammar (not just examples):
  - Format: `{filename}#{path_expression}`
  - `filename`: relative path from project root (e.g., `course-content/staging/ad-hoc/source-bundles/trial2-macro-trends/extracted.md`)
  - `path_expression`: `>` delimited section path (e.g., `Chapter 2 > Knowledge Check > Item 3`) OR line range (e.g., `L45-L62`) OR heading anchor (e.g., `## Macro Trends Overview`)
  - Resolver rules: path expression is matched top-down (first `>` segment is top-level heading, second is sub-section, etc.); line ranges are stable within a versioned artifact; heading anchors use markdown heading text
**And** a resolver function `resolve_source_ref(source_ref_string, base_path) → (file_content_slice, confidence)` is specified (implementation in Story 2A-8 for drift tracking; specification here)
**And** evidence retention: when the Fidelity Assessor resolves a `source_ref`, the resolved content slice is captured in the Fidelity Trace Report as `source_evidence` alongside the `output_evidence` — creating a self-contained, auditable comparison record

**And** Irene's SKILL.md and delegation protocol are updated to instruct her to populate `source_ref` fields when producing artifacts
**And** a validation function `validate_source_refs(artifact_path) → (valid_refs[], broken_refs[])` is specified to check that all `source_ref` citations in an artifact resolve to existing content (implementation in Story 2A-4)

**Design Note:** This is primarily a schema and specification story — it establishes the traceability grammar, resolver spec, and evidence retention rules that the Fidelity Assessor (Story 2A-4) and drift tracking (Story 2A-8) implement. The live template modifications (adding `source_ref` fields to lesson plan, slide brief, narration script, segment manifest) are the concrete changes. Note: these templates currently have NO `source_ref` fields — only objective and pairing references exist.

---

### Story 2A-4: Fidelity Assessor Agent — Foundation (G2-G3)

As a course content producer,
I want an independent Fidelity Assessor agent that verifies whether production artifacts are faithful to their source of truth at each gate,
So that fidelity failures are caught automatically before quality review or human checkpoint — and the system's fidelity evaluation improves over time as LLM capabilities advance.

**Acceptance Criteria:**

**Agent creation (via bmad-agent-builder):**
**Given** the GOLD document's Fidelity Assessor specification and the Three-Layer Intelligence Model
**When** the Fidelity Assessor agent is created through six-phase discovery
**Then** `skills/bmad-agent-fidelity-assessor/SKILL.md` exists with persona, identity, communication style, and principles
**And** the agent's role is strictly forensic: "Is this output faithful to its source of truth?"
**And** the agent is distinct from Quinn-R (quality) in role, mandate, and assessment criteria
**And** the agent has a memory sidecar at `_bmad/memory/fidelity-assessor-sidecar/` with index.md, patterns.md, chronology.md, access-boundaries.md

**Three-layer architecture:**
**And** L1 contracts are loaded from `state/config/fidelity-contracts/` (produced in Story 2A-1)
**And** L2 evaluation logic is in the agent's judgment layer — starts with structural comparison and keyword/item coverage, designed to evolve with LLM capability
**And** L3 memory captures fidelity assessment outcomes, drift patterns, user corrections, and gate-specific learnings in the sidecar

**Fidelity Trace Report (standard output):**
**And** every assessment produces a Fidelity Trace Report with findings categorized as Omissions, Inventions, or Alterations
**And** each finding includes: gate, artifact location, severity (critical/high/medium), source reference, output reference, suggested remediation
**And** the report includes a gate-level pass/fail verdict with overall fidelity score

**G2 coverage (slide brief vs. lesson plan):**
**Given** Irene produces a slide brief with `source_ref` annotations
**When** the Fidelity Assessor evaluates G2
**Then** it verifies every lesson plan LO is covered by at least one slide
**And** it verifies fidelity classifications (`literal-text`, `literal-visual`, `creative`) are appropriate based on source material signals
**And** it verifies `content_items` trace to lesson plan sections via `source_ref`
**And** Omissions (missing LOs), Inventions (slides without LO traceability), and Alterations (misclassified fidelity) are reported

**G3 coverage (generated slides vs. slide brief):**
**Given** Gary produces slides and downloads PNGs
**When** the Fidelity Assessor evaluates G3
**Then** it invokes the image sensory bridge (`png_to_agent.py`) on each PNG
**And** it confirms perception of each slide with confidence level before evaluating
**And** for `literal-text` slides: verifies all `content_items` from the slide brief appear verbatim in the extracted text
**And** for `literal-visual` slides: verifies the specified image is present and text is preserved
**And** for `creative` slides: verifies content coverage — all `content_items` themes are represented even if creatively enhanced
**And** Omissions, Inventions, and Alterations are reported per slide with slide number and content item references

**Circuit breaker and operating policy:**
**And** a fidelity failure triggers the response defined in the Fidelity Trace Report operating policy (from `docs/fidelity-gate-map.md`, produced in Story 2A-1):
  - **Critical finding:** Immediate circuit break — pipeline halts, artifact returned to producing agent, Marcus notified with full Fidelity Trace Report. No retry without human review.
  - **High finding:** Circuit break — producing agent receives report and may retry once with specific remediation guidance. Second failure escalates to Marcus + human.
  - **Medium finding:** Warning — logged in report, artifact proceeds to Quinn-R and human checkpoint with findings attached. No circuit break.
  - **Remediation owner:** The producing agent for that gate (Irene at G1/G2, Gary at G3, ElevenLabs at G5). Marcus is the escalation path. Human is the waiver authority.
  - **Maximum retries:** 2 per gate per production run before mandatory human escalation.
  - **Waiver:** Only the human (via Marcus) can waive a critical or high finding. Waivers are logged in the Fidelity Trace Report with rationale.

**Marcus integration:**
**And** Marcus's delegation flow is updated to invoke the Fidelity Assessor after each producing agent returns results at G2 and G3
**And** Marcus's conversation management reference documents the fidelity checkpoint workflow
**And** the Fidelity Assessor runs BEFORE Quinn-R at each gate — fidelity is a precondition for quality

**Design Note:** This is the most substantial story in the epic. It may need decomposition during sprint planning. The agent creation via bmad-agent-builder should be a separate task from the G2/G3 integration and circuit breaker implementation.

---

### Story 2A-5: G0-G1 Fidelity — Source Bundle & Lesson Plan Verification

As a course content producer,
I want the Fidelity Assessor to verify source bundle extraction completeness (G0) and lesson plan faithfulness to the source material (G1),
So that the entire downstream pipeline inherits a faithful baseline from the very first step.

**Acceptance Criteria:**

**G0 (Source Bundle — extracted.md vs. original SME materials):**
**Given** the source wrangler produces `extracted.md` from SME materials (Notion, Box, PDFs, URLs)
**When** the Fidelity Assessor evaluates G0
**Then** it compares the extracted bundle against available source material metadata (section count, heading structure, page count for PDFs)
**And** it identifies potential extraction gaps: sections present in the original but absent in the extraction
**And** for PDF sources, it invokes the PDF sensory bridge to verify text extraction quality
**And** Omissions (missing sections), Inventions (content not in source), and Alterations (structural changes) are reported
**And** extraction confidence is scored and reported to Marcus
**And** if source materials include scanned/OCR PDFs (detected by the PDF sensory bridge's confidence rubric), the Fidelity Assessor flags a `degraded_source` warning identifying affected pages. The source wrangler currently excludes scanned PDFs from text extraction — this means G0 fidelity cannot be fully assured for scanned inputs. The warning is surfaced to Marcus so the human can provide manual transcription or alternative source material before the pipeline proceeds on an incomplete baseline.

**G1 (Lesson Plan — LOs vs. source bundle themes):**
**Given** Irene produces a lesson plan with `source_ref` annotations
**When** the Fidelity Assessor evaluates G1
**Then** it verifies that every major theme in the source bundle is represented in at least one learning objective
**And** it verifies `source_ref` links are valid — the cited section exists in the source bundle
**And** it verifies Bloom's level assignments are consistent with the pedagogical activity described
**And** Omissions (source themes not covered by any LO), Inventions (LOs without source material basis), and Alterations (source themes misrepresented) are reported

**Marcus integration:**
**And** Marcus's delegation flow invokes the Fidelity Assessor at G0 (after source wrangling) and G1 (after Irene Pass 1 lesson plan)
**And** fidelity failures at G0 route back to the source wrangler for re-extraction
**And** fidelity failures at G1 route back to Irene for revision

---

### Story 2A-6: Existing Agent Perception Upgrades

As Irene, Gary, and Quinn-R,
We want to adopt the universal perception protocol with sensory bridges when we consume multimodal artifacts,
So that we confirm our interpretation of non-text artifacts before acting on them — eliminating silent misperception.

**Acceptance Criteria:**

**Irene (Pass 2 — writing narration for actual slides):**
**Given** Gary has generated slides and downloaded PNGs
**When** Irene begins Pass 2 (narration script + segment manifest)
**Then** Irene receives PNG file paths in her context envelope
**And** Irene invokes the image sensory bridge on each PNG
**And** Irene confirms her interpretation of each slide: "I see Slide N shows [description]. Confidence: HIGH/MEDIUM/LOW."
**And** Irene writes narration that accurately describes and complements the actual visual content she confirmed seeing
**And** if confidence is LOW for any slide, Irene flags it to Marcus for human clarification before writing narration

**Gary→Irene handoff normalization:**
**And** the `gary_slide_output[].visual_description` free-text field in the context envelope is supplemented (not replaced) by the canonical perception schema output from the image sensory bridge. Irene's Pass 2 envelope receives BOTH:
  - `gary_slide_output[]` (Gary's editorial descriptions — useful for creative context)
  - `perception_artifacts[]` (normalized sensory bridge output per slide — auditable, structured, confidence-scored)
**And** Irene's narration decisions reference the normalized `perception_artifacts[]` as the ground truth for what is visually on screen, not the free-text `visual_description`
**And** the Fidelity Assessor at G4 can audit Irene's narration against the same `perception_artifacts[]` — creating a closed, auditable loop

**Gary (self-assessment of generated output):**
**Given** Gary has generated slides and downloaded PNGs
**When** Gary performs self-assessment
**Then** Gary invokes the image sensory bridge on each PNG
**And** Gary confirms his perception before scoring: "I see [description]. Checking against slide brief..."
**And** Gary's self-assessment scores are based on confirmed perception, not assumed output

**Quinn-R (quality review of multimodal artifacts):**
**Given** Quinn-R receives artifacts for quality review
**When** the artifacts include PNGs, audio files, or other non-text assets
**Then** Quinn-R invokes the appropriate sensory bridge
**And** Quinn-R confirms interpretation before scoring quality dimensions
**And** quality scores are based on confirmed perception

**And** all three agents' SKILL.md files and relevant references are updated to include the perception protocol
**And** the perception confirmation is visible in the agent's output (not silent)

---

### Story 2A-7: G4-G5 Fidelity — Script & Audio Verification

As a course content producer,
I want the Fidelity Assessor to verify narration script fidelity against the actual slides (G4) and audio fidelity against the narration script (G5),
So that what the learner hears accurately matches what they see, and what was spoken matches what was written.

**Acceptance Criteria:**

**G4 (Narration Script — script vs. lesson plan + actual slide PNGs):**
**Given** Irene produces a narration script with `source_ref` annotations after confirming slide perception
**When** the Fidelity Assessor evaluates G4
**Then** it verifies each narration segment references an existing slide by number
**And** it invokes the image sensory bridge on referenced slides and verifies the narration describes content actually visible on the slide
**And** it verifies assessment references in narration match the lesson plan's assessment items exactly
**And** it verifies medical/clinical terminology is consistent between narration and slides
**And** Omissions (slides without narration), Inventions (narration describing content not on slides), and Alterations (terminology inconsistencies) are reported

**G5 (Audio — spoken narration vs. narration script):**
**Given** ElevenLabs generates audio from the narration script
**When** the Fidelity Assessor evaluates G5
**Then** it invokes the audio sensory bridge (`audio_to_agent.py`) to produce a timestamped transcript
**And** it compares the transcript against the narration script text
**And** it checks WPM against the target range (130–170 for instructional narration)
**And** it checks pronunciation of medical terms against the pronunciation guide in the narration script
**And** Omissions (script words not spoken), Inventions (spoken words not in script — hallucinated audio), and Alterations (pronunciation errors changing meaning) are reported

**Video bridge (deferred scope):**
**And** `video_to_agent.py` is created for future G6 use: ffmpeg-based keyframe extraction + audio channel transcription via STT
**And** G6 fidelity assessment is documented as a future story (manual Descript composition requires export before verification)

---

### Story 2A-8: Cumulative Drift Tracking & Leaky Neck Remediation

As a course content producer,
I want the Fidelity Assessor to track cumulative fidelity drift across the entire pipeline and I want all leaky necks in the pipeline remediated,
So that small per-gate fidelity losses don't compound into large divergence from SME intent, and all deterministic constraints are enforced deterministically.

**Acceptance Criteria:**

**Cumulative drift tracking:**
**Given** the Provenance Protocol provides `source_ref` chains from any artifact back to G0
**When** the Fidelity Assessor evaluates G3 or later
**Then** it performs both a **local** check (this gate's output vs. this gate's input) and a **global** check (this gate's output vs. the original source bundle at G0)
**And** global fidelity is scored as a percentage of source themes still faithfully represented
**And** drift thresholds are configurable per production mode:
  - Ad-hoc: global drift warning at 20%, failure at 40%
  - Production: global drift warning at 10%, failure at 20%
  - Regulated: global drift warning at 5%, failure at 10%
**And** drift warnings and failures are reported to Marcus in the Fidelity Trace Report
**And** the Fidelity Assessor's memory sidecar captures drift patterns: which types of content drift most, at which gates, and under which conditions

**Source_ref resolver implementation:**
**Given** the resolver grammar specified in Story 2A-3
**When** the Fidelity Assessor performs global drift checks
**Then** a `resolve_source_ref()` function implements the grammar: parses `{filename}#{path_expression}`, locates the file, extracts the content slice matching the path expression (heading hierarchy via `>`, line range via `L{n}-L{m}`, heading anchor via `## text`)
**And** resolved content is cached per production run to avoid redundant file reads during multi-gate assessment
**And** evidence retention: every global drift check captures `{ source_ref, resolved_source_slice, output_slice, comparison_result, gate }` as a self-contained evidence record in the Fidelity Trace Report — enabling audit without re-resolving references
**And** targeted lookup: the resolver uses `source_ref` path expressions for direct section extraction rather than full-document re-read — making global drift checks proportional to the number of references, not the size of the source bundle

**Leaky Neck remediation:**
**Given** the Leaky Neck report from Story 2A-1 identified points where agentic judgment enforces deterministic constraints
**When** each identified leak is remediated
**Then** the enforcement is moved from natural-language agent instructions to schema rules, parameter bindings, or validation scripts

**Fidelity-control vocabulary (replacing free-text constraint channels):**
**And** specifically, the `additionalInstructions` free-text field in the slide brief and context envelope is replaced (for fidelity-relevant constraints) with a finite, deterministic **fidelity-control vocabulary**:
  - `text_treatment`: `generate` | `preserve` | `preserve-strict` (maps to Gamma `textMode` parameter)
  - `image_treatment`: `ai-generated` | `no-images` | `theme-accent` | `user-provided` (maps to Gamma `imageOptions.source` parameter)
  - `layout_constraint`: `single-column` | `two-column` | `full-bleed-image` | `data-table` | `unconstrained` (maps to structured `additionalInstructions` templates, not free text)
  - `content_scope`: `exact-input-only` | `guided-enhancement` | `creative-freedom` (controls Gamma's embellishment behavior)
**And** the `additionalInstructions` field remains available for creative guidance on `creative`-class slides ONLY — it is prohibited for `literal-text` and `literal-visual` slides where deterministic controls must apply
**And** the Fidelity Assessor verifies at G2 that `literal-text` and `literal-visual` slides use vocabulary controls, not free-text constraints

**And** each remediation is documented with before/after evidence
**And** the Leaky Neck report is updated to reflect resolved items
**And** a regression test confirms the deterministic enforcement produces correct results

---

### Story 2A-9: APP Maturity Audit Skill

As an APP maintainer,
I want a repeatable skill that audits the APP pipeline against the Three-Layer Model, Hourglass Model, and Sensory Horizon principle,
So that I can re-evaluate APP maturity after any architectural change and track improvement over time.

**Acceptance Criteria:**

**Given** the fidelity infrastructure from Stories 2A-1 through 2A-8 is in place
**When** the `app-maturity-audit` skill is invoked
**Then** it produces:
  - A **four-pillar heat map** (L1 Contracts, L2 Evaluation, L3 Memory, Perception) for all gates (G0–G6)
  - A **Leaky Neck report** identifying remaining points where intelligence enforces deterministic constraints
  - A **Sensory Horizon report** listing all artifact modalities and their bridge coverage status
  - A **cumulative drift summary** from the most recent production run
  - A **maturity delta** comparing current scores against the previous audit
**And** the skill is stored at `skills/app-maturity-audit/SKILL.md`
**And** the skill can be invoked by Marcus, by the user directly, or as part of a session startup protocol
**And** audit results are stored in `_bmad-output/implementation-artifacts/` with timestamps for historical comparison

---

## Epic 3: Core Tool Integrations

**Goal**: Users can leverage Gamma, ElevenLabs, and Canvas through intelligent specialty agents with complete tool mastery, parameter intelligence, and skills-based integration. Each agent proves its competence through **exemplar-driven development**: studying real exemplar artifacts, reproducing them programmatically via API/MCP, and passing structured comparison against the originals. The shared **woodshed skill** (`skills/woodshed/`) provides the study → reproduce → compare → reflect → register workflow with detailed run logging, artifact retention, reflection protocols, and circuit breaker safeguards.

**FRs covered:** FR13, FR14, FR15, FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR61, FR62, FR63, FR64, FR65, FR71, FR72, FR73, FR74

**Exemplar-Driven Acceptance Model**: For every specialist agent in this epic, the definition of "tool mastery" includes:
1. Juan provides exemplar artifact(s) in `resources/exemplars/{tool}/{id}/`
2. The agent studies the exemplar (brief + source) and derives a reproduction spec
3. The agent reproduces the exemplar programmatically through the tool's API/MCP
4. The reproduction is compared against the original using the rubric in `resources/exemplars/_shared/comparison-rubric-template.md`
5. Passing the rubric = the agent has demonstrated real competence, not just API connectivity
6. All reproduction attempts (pass and fail) are retained with detailed run logs for audit and improvement
7. Between failed attempts, the agent reflects on root causes and predicts improvements before retrying
8. If the agent cannot master an exemplar after the circuit breaker limit (7 total attempts), it produces a structured failure report for human review

**Evaluator Design Requirements (from Story 3.1 — Gary/Gamma)**: Every specialist evaluator MUST:
1. **Guide the tool's intelligence — never suppress it.** Rich instructions describing the desired outcome outperform restrictive constraints. Each creative tool has a core strength; suppressing it produces worse output than guiding it. (E.g., telling Gamma "no images, no additions" produces bare text; telling it "two-column comparison with medical icons" produces professional slides.)
2. **Extract and compare actual output.** Medium-specific output extraction (PDF text, audio speech-to-text, image OCR, survey JSON parsing) — not just "did a file download?" A rubber-stamp evaluator that checks process compliance gives false confidence.
3. **Score based on content coverage — not exact text match.** Source key words and phrases should appear in the reproduction, but tool enhancements (sub-descriptions, visual accents, structural formatting) are usually beneficial. Only flag additions that change meaning or violate the professional aesthetic.
4. **Use a cheap quality signal.** File size (slides: 8KB=bad, 50KB+=good), audio duration vs word count, image dimensions, question count vs objectives — instant proxies appropriate to each medium.
5. **Separate woodshed from production QA.** Woodshed compares against a source exemplar (tool control training). Production QA compares against the context envelope from Marcus (did the agent produce what was asked for). Same rubric dimensions, different reference point. Woodshed never appears in production runs.
6. **Capture know-how from production feedback.** The memory sidecar's `patterns.md` grows from user checkpoint reviews, not woodshed scores. The most valuable patterns come from the user saying "excellent" or "fix the density."

See `skills/woodshed/SKILL.md` → "Evaluator Design Requirements" for the full reference with per-tool examples.

### Story 3.1: Gamma Specialist Agent & Mastery Skill

As a user,
I want a Gamma specialist agent with complete tool mastery and intelligent parameter management,
So that presentation slides are created with optimal parameters matching my style preferences.

**bmad-agent-builder Discovery Answers:**

**Phase 1 - Intent**: Build a Gamma specialist agent that has complete mastery of Gamma's AI slide generation capabilities. It knows every API parameter, understands which settings produce the best results for different content types (medical presentations, storytelling, data visualization), and learns from each production run what works best.

**Phase 2 - Capabilities**: External skills primarily. Internal: parameter recommendation, style guide interpretation, output quality assessment. External skills: gamma-api-mastery skill with scripts that call the working Gamma API client from Epic 1. No need for own API code - orchestrates existing `scripts/api_clients/gamma_client.py`.

**Phase 3 - Requirements:**
- **Identity**: "Slide Architect" - a visual communication expert who knows Gamma inside and out
- **Communication Style**: Precise, visual-thinking oriented. Explains slide design choices. Recommends parameter combinations with reasoning. Concise but thorough on technical detail when asked.
- **Principles**: (1) Every slide serves a learning objective. (2) Visual clarity for physician audience above flashiness. (3) Style guide preferences are baseline, always applied. (4) Learn what parameter combinations produce excellent results. (5) Professional medical aesthetic unless explicitly overridden.
- **Memory**: Sidecar with patterns.md tracking successful parameter combinations, content type → parameter mappings, quality outcomes per configuration.
- **Access Boundaries**: Read: `state/config/`, `scripts/api_clients/`, skill references. Write: `_bmad/memory/gamma-specialist-sidecar/`, production output directories. Deny: `.env`, other agent sidecars.

**Acceptance Criteria:**

**Given** the Gamma API client from Story 1.6 is working and `bmad-agent-builder` is invoked with discovery answers above
**When** the Gamma specialist agent is created through six-phase discovery
**Then** `agents/gamma-specialist.md` exists with "Slide Architect" persona and complete Gamma parameter knowledge
**And** `skills/gamma-api-mastery/SKILL.md` provides tool integration capability routing to the existing API client
**And** `skills/gamma-api-mastery/references/parameter-catalog.md` documents all Gamma API parameters with value ranges
**And** `skills/gamma-api-mastery/references/context-optimization.md` contains parameter templates for different content types (medical presentations, assessments, storytelling)
**And** `skills/gamma-api-mastery/scripts/` imports and orchestrates the shared `scripts/api_clients/gamma_client.py`
**And** the agent reads style guide preferences from `state/config/style_guide.yaml` and applies them automatically
**And** `_bmad/memory/gamma-specialist-sidecar/` is initialized with index.md, patterns.md, and access-boundaries.md
**And** Party Mode team reviews completed agent structure for accuracy and completeness
**And** at least one exemplar exists in `resources/exemplars/gamma/` (provided by Juan)
**And** the agent successfully reproduces the exemplar via the Gamma API using the woodshed workflow (study → reproduce → compare → pass rubric)
**And** the reproduction attempt produces a detailed `run-log.yaml` capturing exact API call, prompt, response, and comparison conclusion
**And** both the reproduced artifact and the run log are retained in `reproductions/{timestamp}/`

### Story 3.2: Content Creator Agent & Quality Reviewer Agent

As a user,
I want content creation and quality review specialist agents,
So that instructional content is pedagogically designed by a specialist who delegates writing to expert BMad agents, and all production outputs are systematically validated for quality.

**Dependency rationale:** Content is king in higher education. Written content (narration scripts, dialogue scripts, slide briefs, lesson plans) is the prerequisite for all downstream production. The pipeline is: Content Creator (scripts/lesson plans) → Gary (slides) → ElevenLabs (narration) → Kling (video) → Assembly → Quality Reviewer. This story must precede all tool-specialist work.

**Validation model:** No exemplars. No woodshed. The Content Creator produces one sample of each output artifact type on a designated topic, staged in `course-content/staging/`. Acceptance = human review (Juan) confirms instructional soundness and prose quality. This is appropriate because the Content Creator produces *written content*, not API-generated artifacts.

**bmad-agent-builder Discovery Answers (Content Creator):**

**Phase 1 - Intent**: Build an instructional design agent ("Instructional Architect") whose unique value is **pedagogical expertise** — Bloom's taxonomy, cognitive load theory, learning objective alignment, content sequencing, assessment design. The agent does NOT write prose itself; it is the **instructional design director** who tells expert writers *what* to write, *why*, and *how it fits the learning arc*. It delegates all writing to three BMad specialist agents who are better prose craftspeople, reviews their output for pedagogical soundness, and assembles the final structured artifacts for downstream production.

**Content is KING — Instructional Design Director Model:**
The Content Creator's unique contribution is **instructional design chops**. It is the pedagogical authority that directs the writing team:
- **Paige (Tech Writer)** — delegated for precise, structured explanatory content (procedures, protocols, technical descriptions, data-driven explanations)
- **Sophia (Storyteller)** — delegated for compelling narratives (case study dialogues, patient vignettes, first-person clinical explainers, emotional engagement pieces)
- **Caravaggio (Presentation Expert)** — delegated for slide narrative design (visual hierarchy advice, slide-script pairing, presentation flow, audience attention sequencing)
- **Editorial review agents** (`bmad-editorial-review-prose`, `bmad-editorial-review-structure`) — for polishing all written output before downstream handoff

The Content Creator provides each writer with: learning objectives, target Bloom's level, cognitive load constraints, audience profile, and pedagogical intent. The writers produce beautiful prose. The Content Creator reviews for pedagogical alignment, assembles into structured artifact templates, and hands off to downstream specialists (Gary, ElevenLabs, Kling, Qualtrics).

**Phase 2 - Capabilities**: Primarily instructional design expertise with strategic delegation. Internal: instructional analysis, learning objective decomposition, Bloom's taxonomy application, cognitive load management, content sequencing, assessment alignment, quality review of delegated prose for pedagogical soundness. External: delegates writing to Paige (technical), Sophia (narrative), Caravaggio (slide design), editorial review agents (polish).

**Phase 3 - Requirements:**
- **Identity**: "Instructional Architect" - a pedagogical expert who designs content for maximum learning impact and directs writing specialists
- **Communication Style**: Educational, precise about learning science. Explains structural decisions with pedagogical reasoning. Collaborative with the human instructor's vision. Clear about what to delegate and why.
- **Principles**: (1) Every content element must trace to a learning objective. (2) Structure supports cognitive load management. (3) Engagement patterns serve comprehension, not entertainment. (4) Bloom's taxonomy guides activity design. (5) Respect the instructor's subject matter expertise. (6) Own the pedagogy, delegate the prose — the best instructional design + the best writing = the best content.
- **Memory**: Sidecar tracking content patterns, effective structures, learning objective mapping approaches, script-to-slide pairing patterns, which BMad writers produce best results for which content types.
- **Access Boundaries**: Read: `state/config/`, course content, learning objectives, style bible. Write: `_bmad/memory/content-creator-sidecar/`, staging content. Deny: `.env`, tool API code.

**Output Artifacts:**
1. **Lesson Plans** — structured outlines with learning objectives, content blocks, assessment hooks
2. **Narration Scripts** — per-slide scripts with stage directions (tone, pacing, emphasis) for ElevenLabs (writing delegated to Paige or Sophia based on content type)
3. **Dialogue Scripts** — multi-speaker scripts with character labels and tone direction for case study scenarios (writing delegated to Sophia)
4. **Slide Briefs** — per-slide content specifications (text, key visuals, layout hints) for Gary/Gamma (visual flow delegated to Caravaggio)
5. **Assessment Briefs** — question/answer specs for Qualtrics integration
6. **First-Person Explainers** — expert-voice content (clinical reasoning walkthrough, procedure narration) (writing delegated to Sophia)

**bmad-agent-builder Discovery Answers (Quality Reviewer):**

**Phase 1 - Intent**: Build a quality validation agent that systematically reviews all production outputs against style guide standards, accessibility requirements, learning objective alignment, and brand consistency. It provides structured pass/fail assessment with improvement suggestions.

**Phase 2 - Capabilities**: Both internal and external. Internal: quality assessment, compliance checking, feedback generation. External skills: quality-control skill with scripts for automated accessibility scanning and brand validation.

**Phase 3 - Requirements:**
- **Identity**: "Quality Guardian" - a meticulous reviewer who ensures every output meets professional standards
- **Communication Style**: Precise, structured, constructive. Reports findings with severity levels. Always provides actionable improvement suggestions. Never just identifies problems without solutions.
- **Principles**: (1) Accessibility compliance is non-negotiable. (2) Brand consistency protects professional credibility. (3) Learning objective alignment validates instructional purpose. (4) Quality feedback must be actionable. (5) Track quality patterns to improve upstream processes.
- **Memory**: Sidecar tracking quality patterns, common issues, effective standards, calibration with human reviewer preferences.
- **Access Boundaries**: Read: entire project (needs to review everything). Write: `_bmad/memory/quality-reviewer-sidecar/`, quality audit trail. Deny: `.env`.

**Acceptance Criteria:**

**Given** `bmad-agent-builder` is invoked twice with the discovery answers above
**When** the content creator and quality reviewer agents are created through six-phase discovery
**Then** `skills/bmad-agent-content-creator/SKILL.md` exists with "Instructional Architect" persona whose core expertise is instructional design, not prose writing
**And** the content creator delegates writing to BMad specialists: Paige (technical content), Sophia (narratives/dialogues/first-person), Caravaggio (slide narrative design)
**And** the content creator provides each writer with learning objectives, Bloom's level, cognitive load constraints, and pedagogical intent
**And** the content creator reviews delegated writing for pedagogical alignment before assembling final artifacts
**And** the agent produces one sample of each output artifact type (lesson plan, narration script, dialogue script, slide brief, assessment brief, first-person explainer) on a designated topic
**And** sample artifacts are staged in `course-content/staging/` for human review
**And** output artifacts follow structured templates in `skills/bmad-agent-content-creator/references/`
**And** `agents/quality-reviewer.md` exists with "Quality Guardian" persona and systematic review capabilities
**And** the quality reviewer provides structured feedback with severity levels and actionable improvements
**And** `skills/quality-control/SKILL.md` provides quality validation capability with references for standards
**And** `skills/quality-control/scripts/` contains Python accessibility checking and brand validation code
**And** quality review results are logged to the production run audit trail in SQLite
**And** both agents have memory sidecars initialized with index.md, patterns.md, and access-boundaries.md
**And** Party Mode team reviews both completed agent structures for accuracy and completeness
**And** human review (Juan) confirms sample artifacts meet quality standards for instructional soundness and prose quality

### Story 3.3: Kling Video Specialist Agent & API Client

As a user,
I want a Kling video production specialist agent with AI video generation mastery,
So that professional B-roll, concept visualizations, slide-to-video transitions, and educational video clips are generated programmatically for course content.

**Validation model:** No exemplars. No woodshed. The agent produces sample videos of each type it supports (B-roll, concept visualization, image-to-video transition, lip-sync overlay) as small examples. Acceptance = human review (Juan) confirms video quality and educational appropriateness. This mirrors the Content Creator validation model — the agent demonstrates capability through sample production, not exemplar reproduction.

**API Client (built within this story):**
A `scripts/api_clients/kling_client.py` is created extending `BaseAPIClient`, covering:
- `text_to_video()` — generate video from text prompt (5s or 10s, 720p/1080p, aspect ratios)
- `image_to_video()` — generate video from image (single frame or first+last frame)
- `get_task_status()` — poll async task completion
- `download_video()` — retrieve completed video file
- `extend_video()` — extend existing video duration
- `lip_sync()` — apply lip-sync to video with audio

**Auth:** `KLING_ACCESS_KEY` + `KLING_SECRET_KEY` in `.env` (already templated in `.env.example`)

**bmad-agent-builder Discovery Answers:**

**Phase 1 - Intent**: Build a Kling specialist agent ("Video Director") that masters AI video generation for medical education content. It understands text-to-video and image-to-video generation, model selection (O1 for quality, 2.6 Pro for audio, 2.5 Turbo for speed), aspect ratio and resolution choices, motion control, lip-sync, and prompt engineering for educational video. The agent produces B-roll, concept visualizations, transition sequences, and talking-head overlays that integrate into the content production pipeline.

**Phase 2 - Capabilities**: External skills primarily. Internal: video prompt engineering, shot composition for educational context, motion direction, model selection based on content requirements. External skills: kling-video skill with scripts that call the Kling API client built in this story.

**Phase 3 - Requirements:**
- **Identity**: "Video Director" — a video production expert specializing in AI-generated educational video
- **Communication Style**: Visually descriptive, explains shot choices with educational impact reasoning. Concise about technical parameters, expressive about creative direction. Thinks in sequences and transitions.
- **Principles**: (1) Every video clip must serve an instructional purpose. (2) Visual clarity for medical content over cinematic flash. (3) B-roll supports the narration, never distracts from it. (4) Model selection balances quality vs. speed vs. cost for each use case. (5) Lip-sync quality must be natural enough for professional presentation. (6) Learn which prompt patterns and model configurations produce the best results for different content types.
- **Memory**: Sidecar tracking effective prompts per content type, model performance comparisons, successful visual patterns for medical education.
- **Access Boundaries**: Read: `state/config/`, `scripts/api_clients/`, skill references. Write: `_bmad/memory/kling-specialist-sidecar/`, video output directories. Deny: `.env`, other agent sidecars.

**Video Types for Medical Education:**
1. **B-roll** — ambient establishing shots (hospital corridors, lab environments, clinical settings) via text-to-video
2. **Concept Visualizations** — abstract medical concepts made visual (cellular processes, drug mechanisms) via text-to-video with detailed prompts
3. **Image-to-Video Transitions** — slide images animated into motion sequences for dynamic presentations via image-to-video
4. **Talking-Head Overlays** — lip-synced presenter clips synchronized with narration audio via lip-sync API
5. **Transition Sequences** — smooth visual bridges between content sections

**Acceptance Criteria:**

**Given** `KLING_ACCESS_KEY` and `KLING_SECRET_KEY` are configured in `.env`
**When** the Kling API client and specialist agent are built
**Then** `scripts/api_clients/kling_client.py` extends `BaseAPIClient` with text-to-video, image-to-video, task polling, download, extend, and lip-sync methods
**And** the client handles Kling's async task model (submit → poll → download)
**And** `skills/bmad-agent-kling/SKILL.md` exists with "Video Director" persona and Kling API parameter mastery
**And** `skills/kling-video/SKILL.md` provides video generation capability routing to the API client
**And** `skills/kling-video/references/prompt-patterns.md` documents effective prompts for educational video types
**And** `skills/kling-video/references/model-selection.md` documents model tradeoffs (O1 vs 2.6 Pro vs 2.5 Turbo)
**And** `skills/kling-video/scripts/` imports and orchestrates `scripts/api_clients/kling_client.py`
**And** the agent produces sample videos of each type (B-roll, concept viz, image-to-video, lip-sync) for human review
**And** sample videos are staged in `course-content/staging/` for human review
**And** `_bmad/memory/kling-specialist-sidecar/` is initialized with index.md, patterns.md, and access-boundaries.md
**And** Party Mode team reviews completed agent structure for accuracy and completeness
**And** human review (Juan) confirms sample videos meet quality standards for educational video production

**Note:** Kling API client was originally planned for Story 5.4 (Tier 2 integrations). Pulling it forward to this story since the BaseAPIClient infrastructure is well established and the video production capability is high-priority for the content pipeline.

### Story 3.3.1: Composition Architecture Harmonization & Gary Deck Enhancement

As a developer,
I want all existing agents, plans, and documentation updated to reflect the composition architecture decisions (Party Mode 2026-03-27), and Gary enhanced with multi-slide deck generation and theme/template preview,
So that Story 3.4 (ElevenLabs) and the future Compositor story can build on a coherent, harmonized foundation.

**Decision Reference:** `_bmad-output/brainstorming/party-mode-composition-architecture.md`

**Key changes:**
- Irene: two-pass model, segment manifest as 7th artifact type, downstream annotations for ElevenLabs/Kira
- Quinn-R: two-pass validation, audio quality + composition integrity dimensions
- Kira: manifest consumption references (visual_source, visual_mode, narration_duration)
- Marcus: pipeline dependency graph, four HIL gates, Compositor delegation, Descript handoff
- Gary: deck mode, theme/template preview (TP capability), deck parameter guidance, gary_slide_output return field
- Architecture doc: Production Composition Pipeline section added
- Tool inventory: Descript entry updated to sole composition platform
- Story renumbering: Compositor added as 3.5, Canvas→3.6, Qualtrics→3.7, Canva→3.8, Source Wrangler→3.9, Tech Spec Wrangler→3.10

**Story file:** `_bmad-output/implementation-artifacts/3-3-1-composition-architecture-harmonization.md`

---

### Story 3.4: ElevenLabs Specialist Agent & Mastery Skill

As a user,
I want an ElevenLabs specialist agent with comprehensive audio production mastery covering narration, pronunciation, sound design, and multi-speaker dialogue,
So that professional audio artifacts are generated with optimal parameters for medical education content.

**Dependency:** Requires narration scripts from Content Creator agent (Story 3.2) or interim scripts from existing BMad agents.

**bmad-agent-builder Discovery Answers:**

**Phase 1 - Intent**: Build an ElevenLabs specialist agent that masters the FULL ElevenLabs API surface for medical education content. Beyond basic TTS, the agent commands: timestamp-synced narration (for VTT subtitle generation and slide synchronization), pronunciation dictionaries (critical for medical terminology), request stitching for multi-slide continuity, sound effects generation, music generation, and multi-speaker dialogue. The agent understands which voices and settings work best for authoritative yet warm medical narration and learns optimal configurations for different content types.

**Phase 2 - Capabilities**: External skills primarily. Internal: voice selection recommendation, pronunciation optimization for medical terminology, timing estimation, audio quality assessment. External skills: elevenlabs-audio skill with scripts that call the working ElevenLabs API client from Epic 1 (expanded with new API methods).

**Phase 3 - Requirements:**
- **Identity**: "Voice Director" - an audio production expert specializing in educational narration and sound design
- **Communication Style**: Audio-aware, describes voice qualities vividly. Explains voice choices with audience psychology reasoning. Concise recommendations with clear justification.
- **Principles**: (1) Medical terminology pronunciation accuracy is non-negotiable. (2) Warm professionalism for physician audience. (3) Pacing supports comprehension, not just coverage. (4) Style guide voice preferences are always applied first. (5) Timestamps are a first-class output, not an afterthought — every narration includes VTT timing data. (6) Request stitching maintains natural flow across multi-slide sequences. (7) Learn which voice configurations produce the best listener engagement.
- **Memory**: Sidecar with patterns.md tracking voice → content type effectiveness, pronunciation exceptions, timing patterns that work, voice parameter combinations per content type.
- **Access Boundaries**: Read: `state/config/`, `scripts/api_clients/`, skill references. Write: `_bmad/memory/elevenlabs-specialist-sidecar/`, audio output directories. Deny: `.env`, other agent sidecars.

**API Client Expansion (from Story 1.7 base):**
The existing `elevenlabs_client.py` must be expanded with:
- `text_to_speech_with_timestamps()` — returns audio + word-level timing JSON
- `create_pronunciation_dictionary()` / `add_pronunciation_rules()` — medical terminology management
- `text_to_sound_effect()` — sound design generation (duration, looping, prompt influence)
- `text_to_dialogue()` — multi-speaker audio generation (P1 stretch)
- `generate_music()` — background music (P2 stretch)
- `get_pronunciation_dictionaries()` / `list_pronunciation_dictionaries()` — dictionary management

**Priority Tiers (from Party Mode brainstorm — March 26, 2026):**
- **P0 (Must-have):** Slide narration with timestamps + VTT, pronunciation dictionaries, multi-slide request stitching
- **P1 (MVP stretch):** Case study dialogue (multi-speaker), sound effects package, background music
- **P2 (Deferred):** Voice cloning, audio annotations, podcast summaries
- **P3 (Future):** Dubbing/translation, conversational AI tutors, interactive audio quizzes

**Acceptance Criteria:**

**Given** the ElevenLabs API client from Story 1.7 is working (expanded per above) and `bmad-agent-builder` is invoked with discovery answers above
**When** the ElevenLabs specialist agent is created through six-phase discovery
**Then** `skills/bmad-agent-elevenlabs/SKILL.md` exists with "Voice Director" persona and complete ElevenLabs parameter knowledge across all API capabilities
**And** `skills/elevenlabs-audio/SKILL.md` provides audio generation capability routing to the expanded API client
**And** `skills/elevenlabs-audio/references/voice-catalog.md` documents available voices with characteristics and suitability for medical content
**And** `skills/elevenlabs-audio/references/optimization-patterns.md` contains voice optimization for medical education narration styles
**And** `skills/elevenlabs-audio/references/pronunciation-management.md` documents pronunciation dictionary workflow for medical terminology
**And** `skills/elevenlabs-audio/references/sound-design-patterns.md` documents SFX and music generation patterns for instructional content
**And** `skills/elevenlabs-audio/scripts/` imports and orchestrates the expanded `scripts/api_clients/elevenlabs_client.py`
**And** the expanded API client includes methods for timestamps, pronunciation dictionaries, sound effects, and (stub) dialogue/music
**And** the agent reads style guide voice preferences and applies them automatically
**And** generated narration includes word-level timestamp JSON and paired VTT subtitle track
**And** the agent uses `previous_request_ids`/`next_request_ids` for multi-slide narration continuity
**And** a pronunciation dictionary with at least 10 medical terms is created and verified
**And** `_bmad/memory/elevenlabs-specialist-sidecar/` is initialized for capturing effective voice configurations
**And** Party Mode team reviews completed agent structure for accuracy and completeness
**And** at least one exemplar exists in `resources/exemplars/elevenlabs/` (provided by Juan)
**And** the agent successfully reproduces the exemplar via the ElevenLabs API using the woodshed workflow
**And** the reproduction produces a detailed `run-log.yaml` and both artifact and log are retained

**Exemplar L-Level Progression:**
- L1: Single-slide narration → script in, MP3 + VTT out, timing verified
- L2: Multi-slide narration with request stitching (3-5 slides, continuity across segments)
- L3: Narration + pronunciation dictionary (medical terms pronounced correctly)
- L4: Case study dialogue (multi-speaker clinical scenario) — P1 stretch
- L5: Complete slide deck narration suite (full production output set) — future

**ElevenLabsEvaluator Design Requirements:**
- Extract audio duration + speech-to-text from downloaded MP3
- Compare STT transcript against source script (word coverage >95%)
- Score on pronunciation accuracy (medical terms), pacing (130-170 WPM for educational), tone quality
- Use duration-vs-word-count as cheap quality signal (~150 WPM expected)
- Verify timestamp completeness and monotonicity when timestamps are used
- File size sanity check (~1MB/min at 128kbps MP3)

**Brainstorm Reference:** `_bmad-output/brainstorming/party-mode-elevenlabs-capability-audit.md`

### Story 3.5: Compositor Skill (Descript Assembly Guide)

As a user,
I want a Compositor skill that reads a completed segment manifest and generates a Descript Assembly Guide,
So that assembling the final lesson video in Descript is fast, accurate, and reproducible — not manual guesswork.

**Dependency:** Requires a completed segment manifest (all agent write-back fields populated) from a production run with ElevenLabs (Story 3.4) and Kira outputs.

**Design Reference:** `_bmad-output/brainstorming/party-mode-composition-architecture.md`

**Scope:**
- New skill: `skills/compositor/SKILL.md` — reads completed manifest, generates Descript Assembly Guide
- Descript Assembly Guide format: ordered asset list (file paths), track assignments (V1/A1/A2/A3), timing table (segment start times from narration_duration), music cue instructions (duck/swell/out timestamps), transition specs per segment
- Marcus integration: Marcus invokes Compositor after Quinn-R pre-composition pass; presents guide + asset paths to user
- Proof of concept: Execute end-to-end on a real C1-M1 lesson: Irene manifest → ElevenLabs audio → Kira video → Compositor guide → human assembles in Descript → final video

**Acceptance Criteria:**

**Given** a completed segment manifest with all narration_duration, narration_file, visual_file fields populated
**When** the Compositor skill is invoked with the manifest path
**Then** `skills/compositor/SKILL.md` exists with clear generation workflow
**And** a Descript Assembly Guide is generated at `course-content/staging/{lesson_id}/descript-assembly-guide.md`
**And** the guide includes: ordered asset list, track assignments, timing table, music cues, transition specs
**And** the guide is human-executable — a non-technical user can follow it in Descript without interpretation
**And** Marcus references the Compositor in its delegation protocol
**And** a real C1-M1 lesson is assembled end-to-end as proof of concept
**And** Party Mode team reviews the completed Compositor and proof-of-concept output

---

### Story 3.6: Canvas Specialist Agent & Mastery Skill

As a user,
I want a Canvas specialist agent with LMS deployment mastery,
So that completed content is deployed to Canvas with proper module structure and accessibility compliance.

**bmad-agent-builder Discovery Answers:**

**Phase 1 - Intent**: Build a Canvas specialist agent that masters Canvas LMS deployment for course content. It knows Canvas REST API deeply (following canvas_api_tools patterns), understands institutional deployment requirements, and ensures all content meets accessibility and compliance standards before going live.

**Phase 2 - Capabilities**: External skills primarily. Internal: deployment planning, accessibility pre-check, module structure verification. External skills: canvas-deployment skill with scripts that call the working Canvas API client from Epic 1.

**Phase 3 - Requirements:**
- **Identity**: "Deployment Director" - an LMS integration expert who ensures flawless content delivery
- **Communication Style**: Precise, compliance-aware. Confirms deployment targets clearly. Reports results with verification links. Flags accessibility issues before they reach students.
- **Principles**: (1) Never deploy content that fails accessibility checks. (2) Module structure must support student navigation. (3) Grading integration must be verified before live deployment. (4) Always provide confirmation URLs for human verification. (5) Respect institutional API policies and token scoping.
- **Memory**: Sidecar with patterns.md tracking institutional requirements, successful deployment patterns, common Canvas API issues and resolutions.
- **Access Boundaries**: Read: `state/config/`, `scripts/api_clients/`, skill references, production output. Write: `_bmad/memory/canvas-specialist-sidecar/`. Deny: `.env`, other agent sidecars.

**Acceptance Criteria:**

**Given** the Canvas API client from Story 1.8 is working and `bmad-agent-builder` is invoked with discovery answers above
**When** the Canvas specialist agent is created through six-phase discovery
**Then** `agents/canvas-specialist.md` exists with "Deployment Director" persona and Canvas REST API mastery
**And** `skills/canvas-deployment/SKILL.md` provides deployment capability routing to the existing API client
**And** `skills/canvas-deployment/references/deployment-workflows.md` contains workflows for different content types (pages, quizzes, discussions, modules)
**And** `skills/canvas-deployment/references/institutional-requirements.md` documents Canvas-specific policies and compliance requirements
**And** `skills/canvas-deployment/scripts/` imports and orchestrates the shared `scripts/api_clients/canvas_client.py`
**And** the agent validates accessibility compliance before deployment
**And** deployment results include confirmation URLs and Canvas module structure verification
**And** `_bmad/memory/canvas-specialist-sidecar/` is initialized for capturing deployment patterns
**And** Party Mode team reviews completed agent structure for accuracy and completeness
**And** at least one exemplar exists in `resources/exemplars/canvas/` (provided by Juan)
**And** the agent successfully reproduces the exemplar via the Canvas API using the woodshed workflow
**And** the reproduction produces a detailed `run-log.yaml` and both artifact and log are retained

### Story 3.7: Qualtrics Specialist Agent & Mastery Skill

As a user,
I want a Qualtrics specialist agent with survey design mastery and assessment intelligence,
So that course assessments, polls, and surveys are created with optimal parameters matching instructional objectives.

**bmad-agent-builder Discovery Answers:**

**Phase 1 - Intent**: Build a Qualtrics specialist agent that masters survey and assessment creation for educational contexts. It knows every Qualtrics API parameter, understands which question types and flow logic work best for different assessment scenarios (knowledge checks, course evaluations, learning outcome measurement), and learns optimal configurations from each production run.

**Phase 3 - Requirements:**
- **Identity**: "Assessment Architect" — a survey design expert who understands educational measurement
- **Communication Style**: Precise, assessment-literate. Explains question design with pedagogical reasoning. Recommends survey structures aligned with learning objectives.
- **Principles**: (1) Every assessment item must trace to a learning objective. (2) Question design supports valid measurement, not trick questions. (3) Style guide assessment preferences are baseline. (4) Learn which question configurations produce the best learner engagement and measurement validity.
- **Memory**: Sidecar tracking effective question types, assessment-to-objective mappings, response quality patterns.
- **Access Boundaries**: Read: `state/config/`, `scripts/api_clients/`, skill references. Write: `_bmad/memory/qualtrics-specialist-sidecar/`, assessment output. Deny: `.env`, other agent sidecars.

**Acceptance Criteria:**

**Given** the Qualtrics API client from Story 1.9 is working and `bmad-agent-builder` is invoked with discovery answers above
**When** the Qualtrics specialist agent is created through six-phase discovery
**Then** `agents/qualtrics-specialist.md` exists with "Assessment Architect" persona and Qualtrics parameter knowledge
**And** `skills/qualtrics-assessment/SKILL.md` provides assessment creation capability routing to the existing API client
**And** `skills/qualtrics-assessment/references/question-catalog.md` documents question types with educational assessment suitability
**And** `skills/qualtrics-assessment/scripts/` imports and orchestrates the shared `scripts/api_clients/qualtrics_client.py`
**And** the agent reads style guide assessment preferences and applies them automatically
**And** `_bmad/memory/qualtrics-specialist-sidecar/` is initialized for capturing assessment patterns
**And** at least one exemplar exists in `resources/exemplars/qualtrics/` (provided by Juan)
**And** the agent successfully reproduces the exemplar via the Qualtrics API using the woodshed workflow
**And** the reproduction produces a detailed `run-log.yaml` and both artifact and log are retained

### Story 3.8: Canva Specialist Agent (Manual-Tool Agent Pattern)

As a user,
I want a Canva specialist agent with design creation guidance and import/export capabilities,
So that course graphics, infographics, and visual assets are managed with professional design quality matching brand standards.

**API Value Assessment (March 26, 2026):**
The Canva Connect API at `api.canva.com/rest/v1` has been thoroughly researched. **The API cannot edit individual design elements** — there is no endpoint to add text, move elements, add captions, or apply a template/style to existing content. What it *can* do:
- Create blank designs (presentation, doc, custom dimensions) — any plan
- Import PPTX (e.g., Gary/Gamma export → Canva for manual enhancement) — any plan
- Export designs to PNG/PDF/MP4 — any plan
- Upload/manage image assets — any plan
- Autofill brand template fields — **Enterprise plan only**

**Implication:** Canva's programmatic value for this project is limited to an **import/export gateway** (not a design manipulation tool). The most useful path is: Gary generates PPTX → Canva imports it → user manually enhances in Canva editor → Canva exports. This does not warrant building an OAuth token manager or API client at this stage.

**Manual-Tool Agent Pattern:**
This story establishes the **manual-tool agent pattern** — reused for Vyond and Articulate in later epics. Agents for tools without programmatic control are structurally identical to every other agent (same bmad-agent-builder creation, same memory sidecar, same deep tool knowledge). The differences are operational:
- **Marcus polls them** during production planning: "What can you contribute to this production cycle?" The agent responds based on deep knowledge of what the tool can do.
- **When pulled into a production sequence**, the agent provides **detailed, step-by-step instructions** the user executes at the keyboard on the agent's behalf.
- **No API skill layer** — no `scripts/` directory, no API client. The agent's skill layer is knowledge-only (references with tool capability catalogs, workflow templates, best-practice guides).
- **No woodshed** — the tool isn't programmatically controlled, so there's no automated reproduction to evaluate.
- **Validation**: Human review of the agent's guidance quality — does it provide accurate, actionable instructions that produce good results when the user follows them?

**bmad-agent-builder Discovery Answers:**

**Phase 1 - Intent**: Build a Canva specialist agent that has deep expertise in Canva's full capabilities, design patterns, templates, and brand consistency requirements. The agent is polled by Marcus to confirm what it can contribute to any production cycle. When assigned tasks, it produces detailed, step-by-step instructions that the user executes in Canva's editor. It understands the PPTX import path for Gamma → Canva handoff workflows.

**Phase 2 - Capabilities**: Internal capabilities only (no external API/MCP). Internal: design specification creation, template recommendation, brand consistency guidance, step-by-step instruction generation, PPTX import workflow guidance, accessibility compliance checking for visual designs.

**Phase 3 - Requirements:**
- **Identity**: "Visual Designer" — a graphic design expert who creates professional educational visuals
- **Communication Style**: Visually oriented, describes design choices with clarity. Recommends templates and styles with brand reasoning. Provides detailed step-by-step Canva instructions the user can follow. When polled by Marcus, clearly states what Canva can and cannot contribute.
- **Principles**: (1) Every visual must serve instructional clarity. (2) Brand consistency across all course materials. (3) Accessibility standards (contrast, alt-text) are non-negotiable. (4) Style guide design preferences are always applied. (5) When providing instructions, be specific enough that the user can execute without guesswork. (6) Learn which design patterns resonate with the target audience.
- **Memory**: Sidecar tracking successful design patterns, brand application approaches, template effectiveness, user feedback on instruction clarity.
- **Access Boundaries**: Read: `state/config/`, skill references. Write: `_bmad/memory/canva-specialist-sidecar/`, design specs output. Deny: `.env`, other agent sidecars.

**Acceptance Criteria:**

**Given** `bmad-agent-builder` is invoked with discovery answers above
**When** the Canva specialist agent is created through six-phase discovery
**Then** `skills/bmad-agent-canva/SKILL.md` exists with "Visual Designer" persona and deep Canva capability knowledge
**And** `skills/canva-design/SKILL.md` provides design guidance capability (knowledge-only, no scripts/)
**And** `skills/canva-design/references/capability-catalog.md` documents everything Canva can do, organized by use case
**And** `skills/canva-design/references/template-catalog.md` documents Canva templates suited for educational content
**And** `skills/canva-design/references/pptx-import-workflow.md` documents the Gamma PPTX → Canva import → manual enhancement → export path
**And** the agent can be polled by Marcus and accurately report what it can contribute to a given production cycle
**And** when assigned tasks, the agent provides step-by-step instructions detailed enough for the user to execute without guesswork
**And** the agent reads style guide brand preferences and applies them to all design specifications
**And** `_bmad/memory/canva-specialist-sidecar/` is initialized for capturing design pattern effectiveness
**And** Party Mode team reviews completed agent structure for accuracy and completeness
**And** human review (Juan) confirms the agent produces accurate, actionable Canva instructions

**Future upgrade path:** If Canva Enterprise Autofill API or element-level manipulation API becomes available, upgrade to programmatic integration with a `canva_client.py` API client and OAuth token management.

**Reusable pattern:** This manual-tool agent pattern applies to Vyond (Story 5.1) and Articulate (Epic 6). See those stories for tool-specific adaptations.

### Story 3.9: Source Wrangler — Notion & Box Drive Integration

As a user,
I want a source wrangling capability that pulls course development notes from Notion and reference materials from my local Box Drive into the production context,
So that agents have access to my existing course planning materials without manual copy-paste.

**FRs covered:** FR71, FR72, FR73, FR74

**Design Decision (to be resolved during story creation):** Whether the source wrangler is implemented as a dedicated agent (via `bmad-agent-builder`) or as a skill (SKILL.md + scripts/). Factors: an agent brings its own persona, memory sidecar, and judgment about what to pull; a skill is lighter-weight and can be invoked by the orchestrator or any specialist. The Party Mode team recommends starting as a **skill** and evolving to a dedicated agent if the complexity warrants it.

**Acceptance Criteria:**

**Given** `NOTION_API_KEY` and `NOTION_ROOT_PAGE_ID` are configured in `.env`
**When** the source wrangler is invoked (by orchestrator or directly) with a course/module reference
**Then** the wrangler queries Notion API for matching course development notes and returns structured content
**And** a `NotionClient` exists in `scripts/api_clients/` following the `BaseAPIClient` pattern with retry logic
**And** the wrangler can read files from the configured `BOX_DRIVE_PATH` and surface relevant materials by course/module
**And** retrieved materials are made available to the production context for other agents to reference
**And** the wrangler can write feedback (readiness assessments, design tips) back to Notion pages
**And** pre-flight checks verify Notion API connectivity and Box Drive path accessibility
**And** a test demonstrates: wrangler invoked → pulls from Notion → reads from Box → materials available to orchestrator

### Story 3.10: Tech Spec Wrangler Skill

As a specialist agent,
I want a shared tech spec wrangler skill that finds, validates, and delivers current tool documentation, working examples, and how-to guides,
So that I always have authoritative, up-to-date API knowledge before production work and woodshed cycles.

**FRs covered:** FR14 (API connectivity verification), FR18 (tool-specific expertise), FR22 (skills version control and effectiveness)

**Design Decision:** Implemented as a shared **skill** (SKILL.md + scripts/), not a dedicated agent. Any specialist agent or the orchestrator can invoke it. The skill delegates to available MCPs: Ref MCP (primary — `ref_search_documentation`, `ref_read_url`) for reading known docs, and optionally a research MCP (e.g., Perplexity) for discovering unknown docs, examples, and community patterns. May be promoted to a full agent if judgment/proactive-monitoring needs emerge.

**Acceptance Criteria:**

**Given** a specialist agent needs current documentation for its tool (e.g., Gamma, ElevenLabs, Canvas)
**When** the tech spec wrangler skill is invoked with a tool name and optional query
**Then** it loads `doc-sources.yaml` from the requesting agent's mastery skill references
**And** it checks the tool's changelog for changes since `last_refreshed` date via Ref MCP
**And** if changes are found, it reads affected doc pages via Ref MCP (`ref_read_url`) and identifies new parameters, deprecations, or breaking changes
**And** it can perform targeted research queries (e.g., "Gamma API charts best practices") via Ref MCP or research MCP
**And** it returns a structured update report: what changed, what's new, what was deprecated, with source URLs cited
**And** it updates `last_refreshed` and `refresh_notes` in the requesting skill's `doc-sources.yaml`
**And** it logs discoveries to the requesting agent's memory sidecar (`patterns.md`)
**And** for tools with LLM-optimized docs (e.g., Gamma's `llms.txt`), it uses those endpoints for efficient scanning
**And** `skills/tech-spec-wrangler/SKILL.md` exists with references and scripts
**And** unit tests cover changelog detection, doc comparison, and report generation

### Story 3.11: Mixed-Fidelity Gamma Generation System

As a course content producer,
I want the production pipeline to handle slides with different fidelity requirements within a single deck — creative enhancement for most slides, literal text preservation for assessment-linked slides, and faithful reproduction of SME-provided technical visuals,
So that every slide gets the right treatment and learners never see content that misrepresents what they'll be tested on or misrepresents technical diagrams provided by subject matter experts.

**FRs covered:** FR15 (tool manipulation through standardized interfaces), FR34 (learning objectives alignment), FR10 (human checkpoint gates)

**Origin:** Trial Run 2 fidelity audit (2026-03-28). Party Mode consensus + parallel research team validation.

**Three fidelity classes:** `creative` (default — Gamma `generate` mode), `literal-text` (Gamma `preserve` mode with strict constraints), `literal-visual` (Gamma `preserve` mode + user-rebranded image via inline URL).

**Acceptance Criteria:**

**Given** Irene produces a slide brief with mixed fidelity requirements
**When** the brief includes slides tagged `fidelity: literal-text` or `fidelity: literal-visual`
**Then** Gary partitions the slides into creative and literal groups
**And** Gary runs two separate Gamma API calls: `generate` mode for creative slides, `preserve` mode for literal slides
**And** for `literal-visual` slides, Gary embeds user-provided image URLs inline in the inputText
**And** for `literal-visual` slides, Gary sets `imageOptions.source: noImages` to prevent competing AI visuals
**And** Gary reassembles all PNGs in original slide order with a provenance manifest documenting source call and fidelity class per slide
**And** the unified `gary_slide_output` array is indistinguishable from a single-call generation for downstream consumers
**And** when all slides are `creative` (default), Gary runs exactly one API call — no regression from pre-story behavior
**And** Marcus surfaces `literal-visual` slides to the user for Imagine processing before Gary runs
**And** Marcus validates all image URLs are HTTPS-accessible before unblocking Gary
**And** the Quality Reviewer applies fidelity-appropriate review criteria per the provenance manifest

---

## Epic 4: Workflow Coordination & State Infrastructure

**Goal**: Users can execute persistent, recoverable production workflows with comprehensive run intelligence, quality gate coordination (including Vera fidelity checks before Quinn-R quality review at every gate), and systematic learning capture.

**FRs covered:** FR7, FR8, FR9, FR10, FR11, FR12, FR23, FR24, FR25, FR26, FR27, FR28, FR29, FR30, FR31, FR32, FR33, FR34, FR35, FR48, FR49, FR50, FR51, FR52

**Dependency:** Epic 4A (Agent Governance & Observability) MUST be completed before Epic 4. Story 4.2 (Quality Gate Coordination) depends on the run baton, lane matrix, and envelope governance extensions from Epic 4A. Story 4.4 (Production Intelligence) depends on the observability hooks from Epic 4A.

### Story 4.1: Production Run Lifecycle Management

As a user,
I want complete production run lifecycle management with state persistence,
So that production runs are tracked, recoverable, and provide context for quality and reporting.

**Acceptance Criteria:**

**Given** a production run is initiated through the orchestrator
**When** the production coordination skill manages the run lifecycle
**Then** `skills/production-coordination/scripts/` creates a production run record in SQLite with run ID, purpose, context, and status
**And** YAML run context entities (course, module, asset specifications) are created in `state/config/`
**And** each workflow stage completion updates the run state with timestamps and results
**And** if a run is interrupted, it can be resumed from the last successful checkpoint
**And** cross-run context links the current run to previous runs for the same course/module
**And** run presets (explore, draft, production, regulated) configure quality gate strictness

### Story 4.2: Quality Gate Coordination

As a user,
I want systematic quality gates with agent peer review and human checkpoints,
So that content quality is validated at every production stage before proceeding.

**Acceptance Criteria:**

**Given** a production stage completes (slides created, audio generated, etc.)
**When** the quality gate is triggered
**Then** the quality reviewer agent validates output against style guide and quality standards
**And** automated accessibility checks run via `skills/quality-control/scripts/`
**And** if quality threshold is met, the workflow proceeds with notification to user
**And** if quality threshold is not met, the orchestrator presents issues conversationally with options
**And** human review checkpoints are triggered at designated decision points (creative direction, final approval)
**And** all quality decisions are logged to the production run audit trail with reasoning context
**And** the user can override quality decisions when creative judgment is required

### Story 4.3: Content Entity Management & Learning Objective Alignment

As a user,
I want course, module, and asset entities managed throughout production with learning objective tracking,
So that all content serves defined educational goals and maintains cross-module consistency.

**Acceptance Criteria:**

**Given** a production run has course and module context loaded
**When** content is created or modified during the run
**Then** asset evolution history is tracked with creative decision rationale in SQLite
**And** learning objective alignment is validated against course/module objectives at each stage
**And** brand guidelines from `resources/style-bible/` and tool parameters from `state/config/style_guide.yaml` are enforced (see `docs/directory-responsibilities.md` for separation)
**And** release manifests are generated for final content deployment with quality certification
**And** the user can update brand guidelines and creative policies through conversation with orchestrator

### Story 4.4: Production Intelligence & Run Reporting

As a user,
I want comprehensive production run reports that capture effectiveness, bottlenecks, and optimization insights,
So that the system learns and improves from each production run.

**Acceptance Criteria:**

**Given** a production run completes (successfully or with issues)
**When** the run reporting skill generates the production report
**Then** the report includes: run purpose, completion status, time per stage, quality gate results
**And** stage-by-stage effectiveness analysis identifies what worked well and what didn't
**And** bottleneck identification highlights stages that took longest or required most rework
**And** optimization recommendations are generated based on run analysis
**And** comparative analysis against previous runs shows improvement trends
**And** production intelligence rollups and trend comparisons **exclude** `run_mode: ad-hoc` (using `run_mode` tags from Story 4A-5 observability) so sandbox runs never skew course/module building progress metrics
**And** the orchestrator presents the report conversationally: "Here's how the run went..."
**And** learning insights are captured in agent memory sidecars for future workflow optimization

### Story 4.5: Export & Platform Deployment Coordination

As a user,
I want completed content exported to target platforms with proper formatting,
So that finished course assets reach Canvas, CourseArc, or other platforms ready for student access.

**Acceptance Criteria:**

**Given** content passes final quality review and user approval
**When** export is initiated through the orchestrator
**Then** the appropriate platform specialist agent handles deployment with platform-specific formatting
**And** accessibility compliance is verified one final time before deployment
**And** deployment confirmation includes platform URLs and module structure verification
**And** the production run record is updated with deployment details and final status
**And** the orchestrator confirms completion: "Module deployed to Canvas. Here's the link to verify."

---

## Epic 4A: Agent Governance, Quality Optimization & APP Observability (Added 2026-03-28)

**Goal**: Establish the authority model, lane boundaries, and observability infrastructure that constrain how agents interact within production runs — preventing judgment overlap, enabling governance-aware delegation, and making agent quality a release gate.

**FRs covered:** FR81, FR82, FR83, FR84, FR85, FR86, FR87, FR88, FR89, FR90, FR91

**Dependency:** Epic 2A (Fidelity Assurance) must be complete. Epic 4A must complete before Epic 4 (Workflow Coordination).

**Design source:** Party Mode consensus session (2026-03-28) + parallel GPT-5.4 architectural review. Architecture section: `architecture.md#Agent Governance & Authority Architecture`.

### Story 4A-1: Run Baton & Authority Contract

As a production user,
I want an explicit authority contract for every active production run that agents check before acting,
So that specialist agents operate within a clear delegation hierarchy and users can seamlessly switch between orchestrated production and standalone consultation.

**Acceptance Criteria:**

**Given** Marcus creates a production run
**When** the run baton is initialized
**Then** the baton contains `run_id`, `orchestrator`, `current_gate`, `invocation_mode`, `allowed_delegates`, `escalation_target`, and `blocking_authority`
**And** the baton is persisted in a location accessible to all agents within the session
**And** Marcus updates `current_gate` as the pipeline progresses through fidelity and quality gates

**Given** a user directly invokes a specialist agent while Marcus holds an active baton
**When** the specialist checks the baton
**Then** the specialist redirects to Marcus by default: "Marcus is running [run_id], currently at [gate]. Redirect, or enter standalone consult mode?"
**And** if the user explicitly requests standalone consult mode, the specialist operates outside the production flow with no baton authority
**And** the standalone session does not affect the active production run state

**Given** a production run completes or is cancelled
**When** Marcus closes the run
**Then** the baton is cleared — specialists no longer redirect

**Design Note:** The baton is a lightweight YAML/JSON structure, not a database record. It can live in the session context or as a transient file in `state/runtime/`. It does NOT require new Python infrastructure — it's a coordination contract enforced by agent markdown, similar to how `run_mode` is currently enforced.

---

### Story 4A-2: Lane Matrix & Judgment Boundary Cleanup

As a system architect,
I want a single authoritative lane matrix defining which agent owns which judgment dimension,
So that no two agents produce conflicting authoritative assessments on the same dimension.

**Acceptance Criteria:**

**Given** the APP has multiple assessment agents (Vera, Quinn-R, producing agents)
**When** the lane matrix is published
**Then** `docs/lane-matrix.md` exists with one row per judgment dimension, one owner per row, and a "NOT Owned By" column for clarity
**And** the matrix covers: orchestration, instructional design, tool execution quality, perception, source fidelity, quality standards, content accuracy (flag only), and platform deployment
**And** no dimension is claimed by more than one agent

**Given** the lane matrix is published
**When** existing agent SKILL.md files are audited
**Then** Gary's self-assessment scope is narrowed to execution quality only (layout integrity, parameter confidence, embellishment risk) — pedagogical alignment commentary is removed
**And** Irene's delegation protocol clarifies that she reviews delegated prose for behavioral intent achievement, not as a quality gate
**And** Quinn-R's "intent fidelity" dimension is clarified as a quality dimension about learner effect, not source-faithfulness (which is Vera's lane)
**And** each specialist's SKILL.md briefly restates their lane from the central matrix

**Design Note:** The lane matrix extends `docs/fidelity-gate-map.md` (which already covers Vera vs Quinn-R) to ALL agents. It should be compatible with the role matrix — not a replacement.

---

### Story 4A-3: Envelope Governance Extensions

As a specialist agent,
I want every context envelope to carry explicit governance fields so I know my scope and authority,
So that I never exceed my delegated responsibilities or produce outputs outside my allowed scope.

**Acceptance Criteria:**

**Given** Marcus delegates work to any specialist
**When** the context envelope is constructed
**Then** it includes a `governance` block with: `invocation_mode` (delegated/standalone), `current_gate`, `authority_chain`, `decision_scope`, and `allowed_outputs`
**And** the governance block is documented in Marcus's conversation-mgmt.md envelope specification

**Given** a specialist receives an envelope with governance fields
**When** the specialist processes the request
**Then** the specialist validates that its planned outputs are within `allowed_outputs`
**And** the specialist validates that its judgment stays within `decision_scope`
**And** any work outside scope is flagged and returned to the `authority_chain` for routing

**And** all existing context envelope schemas (Gary, Irene, Kira, ElevenLabs, Vera, Quinn-R) are updated to include the governance block

---

### Story 4A-4: Agent QA Release Gate

As a system maintainer,
I want every agent revision to pass a mandatory quality scan before acceptance,
So that structural defects, prompt craft issues, and lane violations are caught before they become runtime drift.

**Acceptance Criteria:**

**Given** a new agent or agent revision is proposed
**When** the quality gate runs
**Then** `bmad-agent-builder` quality optimizer scans for: structure compliance, prompt craft quality, cohesion, execution efficiency, and script opportunities
**And** pass/fail criteria are defined per scan dimension
**And** failures block acceptance — the agent must be revised and re-scanned

**Given** the release gate process is defined
**When** an agent passes the quality scan
**Then** the scan results are archived in `skills/reports/bmad-agent-{name}/quality-scan/` with timestamp

**And** the dev-story workflow and create-story workflow reference the agent QA gate as a required step for agent-creation stories
**And** the process is documented in a shared reference accessible to all developers

**Design Note:** This does not require new tooling — `bmad-agent-builder` already has the quality optimizer. This story formalizes it as a release gate in the workflow.

---

### Story 4A-5: Perception Caching & Observability Foundation

As a production user,
I want sensory bridge perception results cached within a run and governance metrics captured for reporting,
So that agents don't waste resources re-perceiving artifacts and I can track governance health over time.

**Acceptance Criteria:**

**Given** a sensory bridge is invoked during a production run
**When** the perception result is generated
**Then** the result is cached with key `(artifact_path, modality)` within the run scope
**And** subsequent requests for the same artifact and modality return the cached result without re-invoking the bridge
**And** the caching mechanism is documented in `skills/sensory-bridges/references/validator-handoff.md`

**Given** production gates are evaluated during a run
**When** gate results are recorded
**Then** observability hooks capture: gate pass rates, fidelity scores (O/I/A counts per gate), quality dimension scores, and agent performance metrics
**And** every observability record emitted by this story carries `run_mode` (`default` | `ad-hoc`) and sufficient run identity (`run_id` or explicit sandbox sentinel) so downstream aggregations can filter correctly
**And** aggregation rules for course/module building progress (and any Epic 4 production intelligence rollups) **exclude** `run_mode: ad-hoc` — sandbox runs never feed course progress metrics
**And** these metrics feed into Story 4.4 (Production Intelligence) when Epic 4 is implemented

**And** lane boundary violations detected during runs are logged as governance findings with agent, dimension, and context
**And** governance findings are included in run completion reports

**Design Note:** The perception caching may require a simple Python utility in `skills/sensory-bridges/scripts/` to manage the cache. The observability hooks are initially captured in the Fidelity Trace Report and quality review report — formal aggregation happens in Epic 4.

---

### Story 4A-6: Ad-Hoc Mode Ledger & Learning Boundary (Enforcement)

As a production user,
I want ad-hoc mode to be enforced as a hard boundary on persistence and learning,
So that I can complete end-to-end runs in a sandbox without those runs advancing the course/module ledger or training long-lived platform memory.

**Acceptance Criteria:**

**Given** the system is in ad-hoc mode (`state/runtime/mode_state.json` and/or run `context.mode`)
**When** coordination scripts or agents would persist production state
**Then** SQLite writes that imply production run history, coordination audit trails, or quality-gate persistence for the institutional record are **refused or no-op** with a clear machine-readable reason (or an equivalent fail-closed policy documented in code)
**And** Marcus sidecar updates are limited to the **transient ad-hoc session section** of `index.md` only — no writes to `patterns.md` or `chronology.md` driven by ad-hoc runs
**And** run finalization behavior matches `skills/bmad-agent-marcus/references/conversation-mgmt.md` (ad-hoc skips durable finalization steps; user still receives a summary)

**Given** `manage_run.py` (or successor run lifecycle tooling) is invoked
**When** mode is ad-hoc
**Then** behavior is aligned with `skills/bmad-agent-marcus/references/mode-management.md` — no accidental “tracked run with an ad-hoc flag” that still mutates the production ledger

**Given** quality-control or specialist scripts write to SQLite
**When** mode is ad-hoc
**Then** persistence matches agent contracts (e.g. quality review executes but **does not** log to SQLite in ad-hoc where specified)

**And** unit or integration tests lock the boundary (at minimum: mode detection + representative forbidden write paths)
**And** a short normative contract doc exists (e.g. `docs/ad-hoc-contract.md`) listing invariants and pointing to this story

**Design Note:** Story 4A-5 ensures observability is **tagged** so sandbox work is filterable; this story ensures the **platform does not learn or accrue course progress** from ad-hoc runs at the persistence layer. Epic 4 Story 4.4 must consume `run_mode` when building comparative/course progress reports.

---

## Epic 5: Tool Capability Expansion (Rebaselined 2026-03-28)

**Goal**: Expand the APP's tool ecosystem with specialist agents for remaining creative tools. Narrowed from "Unified Content Production Engine" — compositor, source wrangler, and tech-spec-wrangler capabilities originally planned here are already delivered.

**FRs covered:** FR45, FR46, FR47 (partially — assembly coordination FR45 is complete via compositor)

**Rebaseline rationale:** Story 5.2 (Multi-Modal Assembly) is fully delivered by the compositor skill (Story 3.5). Story 5.3 (Style Orchestration) is partially delivered by Quinn-R + style guide infrastructure. Story 5.4 needs editing (Panopto already done, Kling pulled forward).

### Story 5.1: Expanded Tool Specialist Agents (Vyond, Midjourney, Articulate)

As a user,
I want specialist agents for the remaining manual-tool creative platforms,
So that Marcus can consult them for step-by-step instructions when production plans involve tools without API access.

**Acceptance Criteria:**

**Given** bmad-agent-builder creates agents for each manual tool
**When** expanded tool specialists are available
**Then** `skills/bmad-agent-vyond/SKILL.md` exists with storyboard specs, scene construction, timing, and Vyond Studio step-by-step guidance
**And** `skills/bmad-agent-midjourney/SKILL.md` exists with v6/v7 parameter mastery, medical/scientific visualization prompting, and Discord/web workflow guidance
**And** `skills/bmad-agent-articulate/SKILL.md` exists with Storyline/Rise specs, branching scenario design, SCORM packaging, and review guidance
**And** all agents follow the manual-tool pattern established by Canva specialist (Story 3.8): knowledge-only, no API skills, no woodshed, human-reviewed instruction quality
**And** all agents have memory sidecars and interaction test guides
**And** Marcus's specialist registry includes all new agents with appropriate content type routing

**Design Note:** CapCut specialist is deferred until API access matures. Midjourney official API may become available — upgrade path documented in agent.

---

### Story 5.4: Remaining Tier 2 API Integrations (Botpress, Wondercraft)

As a developer,
I want API clients for the remaining Tier 2 tools with genuine unbuilt integrations,
So that chatbot and podcast production capabilities are available to the APP.

**Acceptance Criteria:**

**Given** Python infrastructure and `.env` keys
**When** API clients are built
**Then** `scripts/api_clients/botpress_client.py` exists with conversation management, NLU, and bot deployment capabilities
**And** `scripts/api_clients/wondercraft_client.py` exists with podcast generation, voice synthesis, and episode management
**And** both clients extend `BaseAPIClient` with retry, pagination, and error handling
**And** integration tests verify API connectivity

**Design Note:** Panopto client is already built (Story 1.11). Kling client is already built (Story 3.3). This story covers only genuinely unbuilt Tier 2 integrations. Specialist agents for these tools would be separate stories if needed.

---

## Epic 6: LMS Platform Integration & Delivery (Rebaselined 2026-03-28)

**Goal**: Deploy content seamlessly to educational platforms with automated formatting, compliance, and integration.

**Rebaseline rationale:** Epic 6.2 (Enhanced Canvas) merged into Story 3.6 (Canvas Specialist) — foundational Canvas API client is already built (Story 1.8). The Canvas specialist story becomes a two-phase effort: basic specialist (3.6) then enhanced grading/analytics (phase 2 within 3.6).

### Story 6.1: CourseArc Specialist Agent & LTI Integration

As a user,
I want a CourseArc specialist agent with LTI 1.3 compliance knowledge,
So that interactive content is deployed to CourseArc with proper embedding in Canvas.

**Acceptance Criteria:**

**Given** `skills/bmad-agent-coursearc/SKILL.md` is created via bmad-agent-builder
**When** CourseArc deployment is needed
**Then** the agent provides LTI 1.3 integration guidance for Canvas-CourseArc embedding
**And** SCORM packaging specifications for portable content
**And** interactive content block guidance (sorting activities, flip cards, virtual patient drills)
**And** WCAG 2.1 AA compliance verification for interactive elements
**And** the agent follows the manual-tool pattern (no API — CourseArc is LTI/SCORM only)

---

## Epic G: Governance Synthesis & Intelligence Optimization (Replaces Epics 7, 8, 9 — Rebaselined 2026-03-28)

**Goal**: Consolidate platform allocation intelligence, tool ecosystem monitoring, and documentation synthesis into Marcus intelligence extensions and shared governance infrastructure — not standalone agents.

**Rebaseline rationale:** Original Epics 7 (Platform Allocation Agent), 8 (Tool Review Agent), and 9 (Self-Improving Documentation Agent) were designed before the APP had shared-skill infrastructure (tech-spec-wrangler, woodshed, sensory bridges, memory sidecars). Most of their planned capabilities now exist as shared skills or agent memory patterns. What remains is synthesis and governance, not new standalone agents.

### Story G.1: Platform Allocation Intelligence (Replaces Epic 7)

As a user,
I want Marcus to recommend optimal platform placement for each content piece,
So that slides, videos, assessments, and interactive modules land on the platform best suited for their instructional purpose.

**Acceptance Criteria:**

**Given** Marcus loads allocation policies from `resources/exemplars/` and course context from `state/config/course_context.yaml`
**When** a production plan includes platform deployment
**Then** Marcus analyzes content type, grading requirements, interactivity level, and accessibility needs
**And** recommends platform allocation (Canvas, CourseArc, Panopto, direct embed) with reasoning
**And** the user can accept, modify, or override recommendations conversationally
**And** allocation decisions are captured in Marcus's memory sidecar for pattern learning

**Design Note:** This is a Marcus intelligence extension, not a standalone agent. The allocation matrix lives in `resources/exemplars/` — the same location it already occupies.

---

### Story G.2: Tool Ecosystem Monitoring & Documentation Synthesis (Replaces Epics 8 + 9)

As a system maintainer,
I want periodic synthesis of tool capability changes, agent learning patterns, and production outcomes into actionable reports,
So that the APP stays current with tool evolution and accumulated intelligence is accessible without reading every sidecar file.

**Acceptance Criteria:**

**Given** tech-spec-wrangler already monitors tool API documentation for changes
**When** a periodic review is requested (or triggered by run reporting)
**Then** tool capability changes detected by tech-spec-wrangler are surfaced in a synthesis report
**And** agent memory sidecar patterns are summarized across all specialists — recurring issues, calibration trends, effective parameter patterns
**And** governance health metrics (lane violations, baton redirects, perception cache hit rates) are aggregated
**And** the synthesis report is written to `docs/` or `_bmad-output/` for human review
**And** actionable recommendations (doc updates, agent revisions, contract changes) are prioritized

**Design Note:** This is a periodic synthesis process, not a persistent agent. It leverages existing infrastructure: tech-spec-wrangler for tool monitoring, memory sidecars for agent learning, and production run records for metrics. Could be implemented as a Marcus capability or a standalone skill.

---

### Story G.3: APP Session Readiness & Health Monitoring Service (Added 2026-03-30)

As a production operator,
I want a single designed health-check and monitoring path that validates APP runtime infrastructure (not only external tools) and produces an accompanying report at session start or on demand,
So that real default-mode production work fails fast with diagnosable evidence before long multi-agent runs.

**Acceptance Criteria:**

**Given** Epic 4 coordination and observability infrastructure exists (`coordination.db`, `state/runtime/`, production-coordination scripts, pre-flight-check skill)
**When** the session readiness service runs (CLI, optional Cursor `sessionStart` hook, or Marcus conversational invoke)
**Then** it verifies at minimum: SQLite coordination database presence and basic schema/table sanity (or idempotent init path); critical `state/` paths exist and are writable; `mode_state.json` readable when present; Python import sanity for production-coordination / observability modules used by reporting
**And** it composes with existing `skills/pre-flight-check/` (MCP config, `heartbeat_check.mjs`, Notion, Box Drive, smokes) without duplicating tool logic — either orchestrates the existing runner or documents a two-phase “runtime then tools” invocation
**And** outputs a **structured report** (JSON and human-readable summary) with per-check pass/fail/skip, error detail, and resolution hints aligned with `docs/admin-guide.md` / `docs/app-logging-channels.md`
**And** **pytest** covers happy path, missing DB, missing `state/` subtree, and simulated observability/reporting import failure
**And** Marcus `SKILL.md` and/or `docs/user-guide.md` document how to invoke readiness before production runs

**Dependency:** Epic 4 complete (provides DB and scripts under test). May proceed in parallel with G.1 and G.2.

**Design Note:** This closes the gap between “tools are up” and “APP persistence layer is up.” Optional follow-on: wire `hooks/scripts/session-start.mjs` when hook contract is ready; keep hook behavior non-blocking or configurable to avoid breaking Cursor sessions on strict CI machines.

---

## Epic 10: Strategic Production Orchestration (Deferred — Rebaselined 2026-03-28)

**Goal**: Master orchestrator evolves with predictive optimization and sophisticated coordination capabilities based on accumulated production intelligence.

**Dependency:** Requires Epic 4 (run lifecycle, reporting) and Epic G (governance synthesis) to provide sufficient telemetry data. Deferred until governance and observability infrastructure matures.

### Story 10.1: Predictive Workflow Optimization

As a user,
I want the orchestrator to predict optimal workflows based on accumulated production intelligence,
So that each new production run is more efficient than the last.

**Acceptance Criteria:**

**Given** the orchestrator has memory from multiple production runs
**When** a new production run is initiated
**Then** the orchestrator suggests optimized workflow sequences based on similar past runs
**And** predicted bottlenecks are identified with preemptive mitigation recommendations
**And** resource allocation suggestions optimize tool usage and timing
**And** the user can accept, modify, or override predictive recommendations through conversation

---

## Epic 11: APP Trial Remediation & Run Contract Hardening (Added 2026-03-30)

**Goal**: Convert ad-hoc trial findings into enforceable run controls while preserving the demonstrated success path (mixed-fidelity slide generation with nuanced card mapping and exports).

**Execution guardrail:** This epic explicitly starts only after confirming all prior APP epics remain complete/done in BMAD control docs.

### Phase 1 (Mandatory): Due Diligence

Analyze trial logs/artifacts against expected contracts and produce finding-linked mitigation requirements before coding changes.

### Story 11.1: Trial Due Diligence & Findings Matrix

As a production operator,
I want a formal evidence review of trial artifacts against expected APP contracts,
So that mitigation work is traceable, severity-ranked, and non-regressive.

**Acceptance Criteria:**

**Given** trial run artifacts, envelope files, dispatch logs, and handoff prompts
**When** due diligence is executed
**Then** a findings matrix is produced with: finding ID, severity, evidence path, expected behavior, actual behavior, and owner
**And** findings include both strengths to preserve and gaps to remediate
**And** each mitigation requirement references one or more finding IDs

### Story 11.2: Gary Outbound Contract Completeness & Validation Gate

As Marcus/Gary pipeline maintainers,
I want Gary outbound payloads to include all required contract fields with pre-dispatch and post-dispatch validation,
So that downstream agents receive complete execution-quality evidence.

**Acceptance Criteria:**

**Given** Gary dispatch preparation and run result assembly
**When** contract validation runs
**Then** outbound artifacts include `gary_slide_output`, `quality_assessment`, `parameter_decisions`, `recommendations`, and `flags`
**And** missing required fields block progression with targeted remediation guidance
**And** validation output is logged in run artifacts for auditability

### Story 11.3: Irene Pass 2 Perception Grounding Enforcement

As an instructional production pipeline owner,
I want Irene Pass 2 to require canonical perception artifacts in addition to slide outputs,
So that narration uses auditable visual ground truth rather than inferred visuals.

**Acceptance Criteria:**

**Given** Irene Pass 2 handoff construction
**When** required inputs are validated
**Then** both `gary_slide_output` and `perception_artifacts` are required
**And** missing perception artifacts block Pass 2 delegation with explicit missing-field diagnostics
**And** handoff docs and checks clearly distinguish supplementary creative descriptions from perception ground truth

### Story 11.4: Theme Selection -> Parameter Mapping Handshake Enforcement

As a production operator,
I want theme selection and mapped parameter set confirmation to be explicit and user-confirmed before Gary dispatch,
So that standard slides are generated with the intended visual system and parameter controls.

**Acceptance Criteria:**

**Given** standard-slide generation planning
**When** pre-dispatch validation executes
**Then** user-approved theme selection and resolved parameter-set mapping are required and recorded
**And** mismatch or missing mapping triggers a stop-and-clarify flow
**And** run artifacts include a durable theme-resolution record consumed by downstream gates

---

### Story 5.1: Expanded Tool Specialist Agents (Vyond, Midjourney, CapCut, Articulate)

As a user,
I want specialist agents for Vyond, Midjourney, CapCut, and Articulate,
So that the full creative tool ecosystem is available for multi-modal content production.

**Manual-Tool Agent Pattern (Vyond, Midjourney, Articulate):**
Vyond (Enterprise API required, not available), Midjourney (no official API — third-party wrappers are unofficial and unreliable), and Articulate (no content creation API) follow the **manual-tool agent pattern** established in Story 3.7 (Canva). These agents have deep tool knowledge, get polled by Marcus during production planning, and provide detailed step-by-step instructions the user executes at the keyboard. No API skills, no woodshed. See Story 3.7 for the full pattern description.

- **Vyond agent**: Animation production expert. Provides detailed storyboards, scene descriptions, character specifications, timing, and step-by-step Vyond Studio instructions. The user builds in Vyond's web editor following the agent's guidance. The agent coordinates the exported video with other production assets downstream.
- **Midjourney agent**: Bespoke image generation expert. Deep mastery of Midjourney prompt syntax (v6/v7 parameters: `--ar`, `--style`, `--chaos`, `--no`, `--sref`, `--cref`, etc.), style references, image composition, and medical/scientific visualization. Essential for creating highly bespoke images where generic stock imagery won't suffice — anatomical illustrations, clinical scenario visualizations, branded concept art, data-informed infographics. Provides ready-to-paste prompts with parameter recommendations, iteration guidance, and upscale/variation strategies. The user pastes prompts into Midjourney's Discord bot or web interface. Future upgrade path: if a reliable official or third-party API becomes available, the agent can be upgraded to programmatic integration.
- **Articulate agent**: Interactive authoring expert (Storyline 360 / Rise 360). Provides detailed interaction specifications, branching logic, storyboards, and step-by-step build instructions. The user builds in Storyline/Rise following the agent's guidance. The agent can review exported SCORM packages for structural completeness.

**API-Based Agents (CapCut):**
CapCut may have API access (status unclear — see tool-access-matrix.md). If viable, follows the standard agent pattern with API skills and woodshed validation.

**Acceptance Criteria:**

**Given** bmad-agent-builder creates agents for each tool
**When** expanded tool specialists are available
**Then** `agents/vyond-specialist.md` provides animation production mastery following the manual-tool agent pattern (knowledge-only skill layer, step-by-step instructions, no API)
**And** `agents/midjourney-specialist.md` provides bespoke image generation mastery following the manual-tool agent pattern (prompt engineering expertise, ready-to-paste prompts, no API)
**And** `agents/articulate-specialist.md` provides interactive authoring mastery following the manual-tool agent pattern (knowledge-only skill layer, step-by-step instructions, no API)
**And** `agents/capcut-specialist.md` provides video assembly mastery (API-based where available, manual-tool pattern as fallback)
**And** each agent has corresponding skill directory with SKILL.md and references/
**And** manual-tool agents have knowledge-only skill layers (no scripts/); API-based agents have scripts/ calling API clients
**And** each agent has a memory sidecar for learning effective patterns
**And** style guide includes parameter/preference sections for each new tool
**And** all manual-tool agents are validated by human review of instruction/prompt quality

### Story 5.2: Multi-Modal Assembly Coordination

As a user,
I want an assembly coordinator agent that combines outputs from multiple tools into finished content,
So that slides, voiceover, animations, and b-roll are assembled into professional presentations.

**Acceptance Criteria:**

**Given** individual content components exist (slides, audio, video, images)
**When** the assembly coordinator manages final production
**Then** `agents/assembly-coordinator.md` coordinates component integration with proper sequencing
**And** the coordinator manages format translation between tool outputs (Gamma → Descript, etc.)
**And** timing synchronization aligns audio with visual elements
**And** the final assembly is export-ready for Descript or CapCut with all components organized
**And** brand consistency is validated across all assembled components

### Story 5.3: Style Orchestration & Brand Consistency

As a user,
I want systematic brand consistency enforcement across all tools and content types,
So that every content piece maintains professional standards regardless of which tools created it.

**Acceptance Criteria:**

**Given** `resources/style-bible/` contains brand standards with tool-specific prompt translations and `state/config/style_guide.yaml` contains per-tool parameter preferences
**When** any tool specialist agent creates content
**Then** the agent applies style guide parameters automatically (colors, fonts, voice, imagery style)
**And** the quality reviewer validates brand consistency across multi-tool outputs
**And** creative pattern libraries in agent memory capture successful brand applications
**And** style guide evolves based on production outcomes and user feedback

### Story 5.4: Tier 2 API Integrations (Botpress, Wondercraft, Panopto)

> Legacy note (non-authoritative): this block predates the 2026-03-28 rebaseline. Use the rebaselined Epic 5 section above as the source of truth for active implementation scope.

As a developer,
I want API clients and specialist agents for the remaining Tier 2 tools in the tool universe,
So that the full creative tool ecosystem is available for multi-modal content production.

**Acceptance Criteria:**

**Given** the Python infrastructure and .env API keys are configured for each Tier 2 tool
**When** API clients are built and tested for each tool
**Then** `scripts/api_clients/botpress_client.py` provides chatbot creation and management capabilities
**And** `scripts/api_clients/wondercraft_client.py` provides AI podcast/audio generation capabilities
**And** `scripts/api_clients/panopto_client.py` provides video platform management (if not completed in Story 1.11)
**And** each client has exponential backoff retry logic and clear error diagnostics
**And** integration tests demonstrate basic connectivity and operations for each tool
**And** specialist agents are created via bmad-agent-builder for tools with sufficient API surface

**Note:** Kling API client and agent were pulled forward to Story 3.3. Vyond uses the manual-tool agent pattern (no API client needed — Enterprise plan only). Descript (early access), Midjourney (third-party only), and CapCut (unclear API) are deferred until their API access matures.

---

## Epic 6: LMS Platform Integration & Delivery

> Legacy note (non-authoritative): this block predates the 2026-03-28 rebaseline. Use the rebaselined Epic 6 section above as the source of truth for active implementation scope.

**Goal**: Users can deploy content seamlessly to multiple educational platforms with automated formatting, compliance, and integration.

### Story 6.1: CourseArc Specialist Agent & LTI Integration

As a user,
I want a CourseArc specialist agent with LTI 1.3 compliance knowledge,
So that interactive content is deployed to CourseArc with proper embedding in Canvas.

**Acceptance Criteria:**

**Given** bmad-agent-builder creates `agents/coursearc-specialist.md`
**When** content requires CourseArc deployment
**Then** the agent manages LTI 1.3 integration with Canvas for seamless embedding
**And** SCORM packaging scripts handle content export formatting
**And** interactive content blocks (sorting, flip cards, drills) deploy correctly
**And** WCAG 2.1 AA compliance is verified for all CourseArc content

### Story 6.2: Enhanced Canvas Integration

As a user,
I want advanced Canvas integration with grading passback and analytics,
So that assessments, discussion boards, and graded activities deploy with full LMS functionality.

**Acceptance Criteria:**

**Given** the Canvas specialist agent is enhanced
**When** complex content types are deployed (quizzes with answer-level feedback, graded discussions)
**Then** Canvas gradebook integration works with proper point values and rubrics
**And** SpeedGrader compatibility is verified for all assessment types
**And** analytics data flows correctly from Canvas to production reporting

---

## Epic 7: Multi-Platform Intelligence Matrix

**Goal**: Users benefit from intelligent content routing to optimal platforms based on content type, learning objectives, and platform strengths.

### Story 7.1: Platform Allocation Agent

As a user,
I want a platform allocation agent that recommends optimal placement across Canvas, CourseArc, Playbook, and Qualtrics,
So that each content piece lands on the platform best suited for its instructional purpose.

**Acceptance Criteria:**

**Given** bmad-agent-builder creates a platform allocation specialist
**When** content requires platform placement decisions
**Then** the agent analyzes content type, grading requirements, interactivity needs, and accessibility requirements
**And** recommendations reference the platform allocation matrix with reasoning
**And** the orchestrator presents allocation decisions conversationally for user confirmation
**And** allocation patterns are captured in agent memory for consistency

---

## Epic 8: Tool Review & Optimization Intelligence

**Goal**: Users benefit from systematic tool environment monitoring and adaptive optimization recommendations.

### Story 8.1: Tool Review Agent & Environment Scanning

As a user,
I want a tool review agent that monitors the tool ecosystem for changes and optimization opportunities,
So that the system stays current with tool capabilities and identifies better approaches.

**Acceptance Criteria:**

**Given** bmad-agent-builder creates a tool review specialist
**When** periodic tool review is triggered or user requests optimization analysis
**Then** the agent scans tool documentation for API changes, new features, and capability updates
**And** cost-benefit analysis identifies optimization opportunities across the tool stack
**And** policy crystallization captures effective tool allocation strategies in style guide YAML
**And** the orchestrator presents findings conversationally with actionable recommendations

---

## Epic 9: Living Architecture Documentation System

**Goal**: System documentation evolves automatically from production experience, capturing institutional knowledge.

### Story 9.1: Self-Improving Documentation Agent

As a user,
I want documentation that improves automatically based on production outcomes,
So that operational knowledge is preserved and grows without manual documentation effort.

**Acceptance Criteria:**

**Given** bmad-agent-builder creates a documentation specialist
**When** production runs complete and generate learning insights
**Then** the agent analyzes patterns across production memory sidecars
**And** documentation updates are proposed based on discovered patterns and optimizations
**And** troubleshooting guides evolve based on actual issues encountered and resolved
**And** agent capability documentation reflects current system state

---

## Epic 10: Strategic Production Orchestration

**Goal**: Master orchestrator evolves with predictive optimization and sophisticated coordination capabilities.

### Story 10.1: Predictive Workflow Optimization

As a user,
I want the orchestrator to predict optimal workflows based on accumulated production intelligence,
So that each new production run is more efficient than the last.

**Acceptance Criteria:**

**Given** the orchestrator has memory from multiple production runs
**When** a new production run is initiated
**Then** the orchestrator suggests optimized workflow sequences based on similar past runs
**And** predicted bottlenecks are identified with preemptive mitigation recommendations
**And** resource allocation suggestions optimize tool usage and timing
**And** the user can accept, modify, or override predictive recommendations through conversation

---

## Epic 12: Double-Dispatch Gamma Slide Selection

**Goal**: When enabled via a per-run flag, produce two independent visual treatments per slide so the user can choose the strongest version for each position, raising presentation quality without re-running the full pipeline.

**Depends on**: All existing epics complete. Extends `gamma_operations.py`, storyboard run-view (SB.1), Gary/Vera/Quinn-R contracts.

**Party Mode consensus decisions (2026-04-05)**:
- Double-dispatch is a **per-run flag** (not per-slide)
- Both variants are fidelity-reviewed **before** user selection
- Irene receives only the selected winner slides — losing variants archived with full provenance
- Exactly one winner per slide position (no "keep both" option)
- Full-deck sequential preview after individual selections for visual flow check

### Story 12.1: Dual-Dispatch Infrastructure

As a production operator,
I want gamma_operations.py to support a double_dispatch mode that executes two independent Gamma generate calls per slide position,
So that I get two meaningfully different visual treatments to choose from.

**Acceptance Criteria:**

**Given** `run-constants.yaml` contains `double_dispatch: true`
**When** `execute_generation()` processes a slide
**Then** two independent Gamma API calls are made per slide position (separate calls, not retries)
**And** both exports are downloaded with variant labeling: `{slide_id}_variant_A.png`, `{slide_id}_variant_B.png`
**And** `gary_slide_output` records gain `dispatch_variant: "A" | "B"` field
**And** provenance (`literal_visual_source`) is tracked independently per variant
**And** when `double_dispatch: false` (default), behavior is identical to current single-dispatch — zero regression
**And** unit tests cover dual-dispatch path with mocked API responses

### Story 12.2: Parallel Fidelity & Quality Review for Variant Pairs

As a production operator,
I want both slide variants to pass independently through Vera fidelity assessment and Quinn-R quality review before I see them,
So that my selection is between two pre-qualified options.

**Acceptance Criteria:**

**Given** two variant PNGs exist for a slide position
**When** fidelity and quality review runs
**Then** Vera runs G2-G3 fidelity checks on each variant independently
**And** Quinn-R scores each variant independently against the slide brief
**And** quality scores are attached to each variant record: `{variant, vera_score, quinn_score, findings[]}`
**And** variants that fail fidelity thresholds are flagged but still presented (user may override)
**And** if both variants fail, the pair is flagged as "needs re-dispatch or manual intervention"
**And** no new fidelity gates are introduced — existing G2-G3 logic is extended, not duplicated

### Story 12.3: Selection Storyboard

As a production operator,
I want to see both variants side-by-side with quality scores and select the winner for each slide position,
So that I can make informed visual choices for the final presentation.

**Acceptance Criteria:**

**Given** two fidelity-reviewed variants exist per slide position
**When** the selection storyboard is presented
**Then** paired variants (A/B) are displayed side-by-side per slide position at legible scale
**And** quality scores (Vera + Quinn-R) are visible per variant
**And** user selects exactly one winner per position (all positions must be selected before confirmation)
**And** running tally shows selection progress ("Selected: 7/12")
**And** after all selections, a full-deck sequential preview shows chosen slides in presentation order for visual flow check
**And** user can revise selections during preview before final confirmation
**And** selection metadata is persisted: `{slide_id, selected_variant, rejected_variant, selection_timestamp}`

### Story 12.4: Winner Forwarding & Provenance Archive

As a production operator,
I want selected winners promoted into the canonical gary_slide_output and rejected variants archived,
So that the downstream pipeline receives clean, confirmed slides with full audit trail.

**Acceptance Criteria:**

**Given** the user has confirmed all slide selections
**When** the selection is finalized
**Then** `gary_slide_output` contains only winner slides with `selected: true`
**And** rejected variants are moved to `{run_dir}/archived_variants/` with full metadata
**And** the context envelope for Irene Pass 2 contains only selected slides — no variant A/B distinction visible to Irene
**And** `perception_artifacts` are generated only for winning slides (no wasted sensory bridge calls on rejected variants)
**And** archive includes: variant PNGs, quality scores, selection metadata, timestamps
**And** storyboard archive section shows selection history for audit trail

### Story 12.5: Marcus Run Mode Integration for Double-Dispatch

As a production operator,
I want Marcus to recognize and orchestrate double-dispatch runs end to end,
So that the dual-dispatch workflow is seamlessly integrated into the production pipeline.

**Acceptance Criteria:**

**Given** `double_dispatch: true` in run-constants.yaml
**When** Marcus orchestrates the run
**Then** Marcus adjusts the workflow: Gary dispatches 2x → parallel review → selection storyboard gate → then Irene Pass 2
**And** run progress reporting accounts for dual-dispatch timing (estimated 2x generation time)
**And** run cost estimate reflects 2x Gamma credits when double-dispatch is active
**And** pre-flight check validates double-dispatch compatibility (sufficient API credits, template supports re-dispatch)
**And** ad-hoc mode supports double-dispatch (same flag, same workflow)

---

## Epic 13: Visual-Aware Irene Pass 2 Scripting

**Goal**: Irene's Pass 2 narration scripts explicitly reference specific visual elements perceived on each slide, transforming generic commentary into guided learning narration that speaks pointedly to what's on screen.

**Depends on**: Epic 12 (soft — enhanced by double-dispatch winner slides, but functions with single-dispatch). Hard dependency on existing sensory bridges skill (Epic 2A).

**Party Mode consensus decisions (2026-04-05)**:
- Perception is **mandatory** for Irene Pass 2 (no longer optional)
- LOW-confidence perception escalation goes to **Marcus** (not user)
- Visual references are natural language integrated into narration flow — not bolted-on annotations
- `visual_references_per_slide` parameter default: 2 (±1 tolerance)

### Story 13.1: Mandatory Perception Contract for Irene Pass 2

As a content architect,
I want Irene's Pass 2 to require perception artifacts as first-class input,
So that every narration script is grounded in confirmed visual understanding of the slides.

**Acceptance Criteria:**

**Given** Irene Pass 2 is invoked with a context envelope
**When** activation begins
**Then** Irene validates `perception_artifacts` presence in the context envelope
**And** if absent, Irene invokes image sensory bridge on each slide PNG in `gary_slide_output` and generates `perception_artifacts` inline
**And** perception confirmation is logged per slide: "I see Slide N shows [description]. Confidence: HIGH/MEDIUM/LOW"
**And** LOW-confidence slides trigger automatic re-perception (one retry with different bridge parameters)
**And** if still LOW after retry, Irene flags to Marcus for decision (proceed with caveated narration or escalate to user)
**And** perception is confirmed before any narration writing begins

### Story 13.2: Visual Reference Injection in Narration Scripts

As a content architect,
I want narration scripts to explicitly reference specific visual elements on each slide,
So that learners are guided through the visuals rather than hearing generic commentary.

**Acceptance Criteria:**

**Given** confirmed `perception_artifacts` exist for all slides
**When** Irene writes narration for a slide
**Then** `run-constants.yaml` parameter `visual_references_per_slide: int` (default: 2) controls reference count
**And** narration includes exactly `visual_references_per_slide` explicit references to perceived visual elements (±1 tolerance)
**And** references are natural language integrated into narration flow ("As you can see in the comparison chart on the right..." not "Reference 1: comparison chart")
**And** each reference is grounded in a specific element from `perception_artifacts` — traceable
**And** references complement (not duplicate) slide content — narrate the insight, reference the visual
**And** narration script template is updated with `visual_references[]` metadata per segment
**And** unit tests validate reference count compliance and traceability to perception artifacts

### Story 13.3: Segment Manifest Visual Reference Enrichment & Downstream QA

As a quality reviewer,
I want each segment in the manifest to carry structured visual references linking narration cues to perceived visual elements,
So that downstream fidelity verification can confirm narration-to-visual alignment.

**Acceptance Criteria:**

**Given** Irene has produced narration with visual references
**When** the segment manifest is generated
**Then** each segment gains `visual_references: [{element, location_on_slide, narration_cue, perception_source}]`
**And** `element` identifies what is referenced (e.g., "comparison timeline")
**And** `location_on_slide` provides spatial description (e.g., "left panel")
**And** `narration_cue` contains the exact narration phrase that references it
**And** `perception_source` references the perception artifact entry
**And** Vera G4 (narration vs slides) is extended to validate visual references correspond to perceived elements
**And** Quinn-R can flag narration referencing visual elements not found in perception artifacts
**And** Compositor assembly guide includes visual reference cues for human assemblers

---

## Epic 14: Motion-Enhanced Presentation Workflow

**Goal**: Add motion — AI-generated video clips (Kira/Kling) and hand-crafted animations — to specific slides in a presentation, with narration that speaks to the motion content, creating richer educational experiences without breaking the existing static pipeline.

**Depends on**: Epic 13 (hard — visual reference injection for motion content uses Epic 13 mechanism). Epic 12 (soft — compatible but independent).

**Party Mode consensus decisions (2026-04-05)**:
- Motion Decision Point is a **separate HIL gate (Gate 2M)**, not an extension of Gate 2
- Gate 2M is skipped entirely when `motion_enabled: false`
- Motion is **additive** — most slides stay static, specific slides get motion companions
- Kira uses image-to-video (preferred) or text-to-video based on brief complexity
- Budget guardrails: `motion_budget` with max_credits and model_preference, auto-downgrade on ceiling
- Manual animation guidance is tool-agnostic by default (Vyond-specific only when user specifies)

### Story 14.1: Motion Workflow Design & Contract Specification

As a system architect,
I want a formal workflow design document specifying the motion-enhanced pipeline variant,
So that all agents, contracts, and gates are defined before implementation begins.

**Acceptance Criteria:**

**Given** the motion-enhanced pipeline variant needs formal specification
**When** the design is complete
**Then** a workflow design document exists in `_bmad-output/planning-artifacts/` specifying:
  - Motion-enhanced pipeline stages (Gate 2 → Gate 2M → Kira/manual → Motion Gate → Irene Pass 2)
  - Motion Decision Point (HIL Gate 2M) as a new stage between Gate 2 and Irene Pass 2
  - HIL Motion Gate: user reviews Kira clips and imported animations before Irene
  - Agent role matrix: Marcus orchestrates motion routing, Kira generates video, Vyond specialist generates animation guidance
  - Segment manifest schema extensions (motion fields)
  - Run-constants.yaml extensions: `motion_enabled: boolean`, `motion_budget: {max_credits, model_preference}`
  - Workflow variant selection logic in Marcus
**And** architecture doc is updated with motion pipeline stage diagram
**And** Party Mode team consensus is recorded on the design

### Story 14.2: Segment Manifest Motion Extensions

As a system architect,
I want the segment manifest schema extended with motion designation fields,
So that every segment can declare its motion type and track motion asset lifecycle.

**Acceptance Criteria:**

**Given** the motion workflow design is approved
**When** the manifest schema is updated
**Then** new fields per segment: `motion_type: "static" | "video" | "animation"` (default: "static")
**And** `motion_asset_path: string | null` — path to video MP4 or animation file
**And** `motion_source: "kling" | "manual" | null` — provenance of motion asset
**And** `motion_duration_seconds: float | null` — duration of motion asset
**And** `motion_brief: string | null` — intent/description of the motion
**And** `motion_status: "pending" | "generated" | "imported" | "approved" | null` — lifecycle tracking
**And** backward compatible: existing manifests with all-static segments work unchanged
**And** template updated: `skills/bmad-agent-content-creator/references/template-segment-manifest.md`
**And** validation: `motion_type != "static"` requires `motion_asset_path` populated before Irene Pass 2

### Story 14.3: Motion Decision Point & Designation UI

As a production operator,
I want to designate each approved slide as static, video, or animation after Gate 2,
So that the pipeline knows which slides need motion assets before Irene scripts for them.

**Acceptance Criteria:**

**Given** Gary's slides are approved at HIL Gate 2 and `motion_enabled: true`
**When** HIL Gate 2M is presented
**Then** storyboard view shows all approved slides with motion designation controls
**And** per-slide options: Static (default), Video (Kira), Animation (manual)
**And** video designation allows optional motion brief (what should the video depict)
**And** animation designation allows optional guidance notes
**And** designation summary displayed: "12 slides: 8 static, 3 video (Kira), 1 animation (manual)"
**And** cost estimate shown for Kira video designations (based on model/mode/duration defaults from `motion_budget`)
**And** designations written to segment manifest `motion_type` fields
**And** Marcus routes: static slides proceed directly, video slides to Kira, animation slides to guidance skill

### Story 14.4: Kira Pipeline Integration

As a production operator,
I want Kira to receive designated slides and produce video clips within the motion-enhanced pipeline,
So that AI-generated motion is available for narration scripting.

**Acceptance Criteria:**

**Given** slides are designated as `motion_type: "video"` at Gate 2M
**When** Marcus routes them to Kira
**Then** Kira receives context envelope containing: slide PNG, motion brief, narration intent (from Irene Pass 1), duration target, budget constraints
**And** Kira uses image-to-video (preferred) or text-to-video based on brief complexity
**And** model selection respects `motion_budget.model_preference` (std/pro)
**And** each generated MP4 is downloaded immediately to `{run_dir}/motion/` as `{slide_id}_motion.mp4`
**And** Kira returns structured results: `{slide_id, mp4_path, model_used, duration_seconds, credits_consumed, self_assessment}`
**And** running cost tally updated after each generation
**And** if budget ceiling hit, Marcus pauses and downgrades remaining clips to `std` (or flags if already `std`)
**And** segment manifest updated: `motion_asset_path`, `motion_source: "kling"`, `motion_duration_seconds`, `motion_status: "generated"`

### Story 14.5: Manual Animation Guidance Skill

As a production operator,
I want detailed step-by-step animation creation instructions for slides designated as manual animation,
So that I can create animations in my tool of choice with clear direction from the app.

**Acceptance Criteria:**

**Given** slides are designated as `motion_type: "animation"` at Gate 2M
**When** the animation guidance skill runs
**Then** an Animation Guidance Document is produced per slide containing:
  - Visual description of what the animation should depict (from motion brief + slide content)
  - Suggested duration and pacing
  - Key frames / state descriptions (start, middle, end)
  - Alignment with narration intent from Irene Pass 1 lesson plan
  - Tool-agnostic instructions (no tool-specific jargon unless user specifies tool)
**And** Vyond specialist (`bmad-agent-vyond`) can optionally produce Vyond-specific instructions if requested
**And** user imports completed animation file to `{run_dir}/motion/` as `{slide_id}_motion.{ext}`
**And** import validation: file exists, is a supported video format, duration within expected range
**And** segment manifest updated: `motion_asset_path`, `motion_source: "manual"`, `motion_duration_seconds`, `motion_status: "imported"`

### Story 14.6: Motion Perception & Irene Pass 2 Integration

As a content architect,
I want Irene to perceive motion assets and write narration that speaks to both static slides and motion content,
So that narration scripts are synchronized with all visual assets the learner will experience.

**Acceptance Criteria:**

**Given** motion assets (video clips + animations) are approved at HIL Motion Gate
**When** Irene Pass 2 runs
**Then** Irene receives both `gary_slide_output` (static slides) and motion assets in her context envelope
**And** for motion-designated segments, Irene invokes video sensory bridge on the motion asset
**And** perception logged: "Slide N has motion (video/animation): I see [description]. Confidence: HIGH/MEDIUM/LOW"
**And** narration for motion segments references the motion content specifically (using visual reference injection from Epic 13)
**And** `visual_references_per_slide` parameter applies to both static and motion segments
**And** narration script includes timing cues for motion segments: "[as the animation plays]", "[during the transition]"
**And** segment manifest correctly distinguishes static narration timing from motion narration timing

### Story 14.7: End-to-End Motion Pipeline Orchestration & Compositor Update

As a production operator,
I want Marcus to orchestrate the complete motion-enhanced workflow and the compositor to include motion assets in assembly guides,
So that a motion-enhanced lesson can be produced end-to-end through the APP.

**Acceptance Criteria:**

**Given** `motion_enabled: true` in run-constants.yaml
**When** Marcus orchestrates the run
**Then** the motion pipeline activates: Gate 2 → Gate 2M → Kira/manual → Motion Gate → Irene Pass 2
**And** `motion_enabled: false` runs the existing static pipeline with zero behavioral change
**And** Compositor assembly guide includes motion assets: "At Slide 5, play `slide_05_motion.mp4` (8s) on video track, timed to narration segment 5"
**And** `sync-visuals` is extended to also copy motion assets into the assembly bundle
**And** run reporting includes motion metrics: clips generated, animations imported, total motion duration, Kira credits consumed
**And** pre-flight check extended: verify Kling API connectivity when `motion_enabled: true`
**And** end-to-end integration test: a 3-slide mini-run with 1 static + 1 video (Kira) + 1 animation (manual) produces correct manifest, narration with motion references, and assembly guide

---

## Epic 15: Learning & Compound Intelligence (Added 2026-04-06)

**Goal**: Convert the APP from a well-governed multi-agent pipeline into a compound-learning production system where tracked runs, gate decisions, human corrections, and cross-agent outcomes accumulate into reusable organizational intelligence — so each serious production run makes the platform measurably smarter.

**Depends on**: At least one tracked trial run completed (hard — learning schema needs real operational evidence to validate). Epic 2A sensory bridges and Vera fidelity infrastructure (existing, satisfied). Epic 4A governance and observability hooks (existing, satisfied).

**Seed document**: `_bmad-output/implementation-artifacts/app-three-layer-optimization-plans-2026-04-06.md`, Plan 3 (primary), plus `_bmad-output/implementation-artifacts/app-optimization-map-and-baseline-audit-2026-04-05.md` Priority 0 and Priority 3.

**Design guardrails**:
- Only capture learning that changes future decisions
- Distinguish clearly between: deterministic policy candidate, specialist calibration note, workflow-family heuristic, one-off exception
- Do not let memory become a dumping ground — periodic condensation is mandatory
- Preserve specialist intelligence; do not flatten judgment into brittle automation

### Story 15.1: Learning Event Schema & Capture Infrastructure

As a system architect,
I want a canonical learning-event format that captures every meaningful production event (gate approval, revision, waiver, circuit break, quality failure, fidelity failure, first-pass approval, manual override),
So that the system stops losing its most valuable feedback.

**Acceptance Criteria:**

**Given** a tracked production run reaches any gate decision
**When** a human or agent decision is recorded
**Then** a structured learning event is persisted containing: `run_id`, `gate`, `artifact_type`, `producing_specialist`, `reviewing_specialist` (if applicable), `human_decision`, `root_cause_classification`, `accepted_remediation`, `learning_targets[]`
**And** the learning-event schema is defined in `state/config/learning-event-schema.yaml`
**And** events are appended to a per-run learning ledger at `{run_dir}/learning-events.yaml`
**And** capture hooks integrate with the existing gate coordinator and quality gate infrastructure
**And** ad-hoc runs capture events to their ad-hoc ledger (existing FR91 boundary respected)
**And** schema is extensible for future event types without breaking existing consumers
**And** unit tests validate schema compliance and append behavior

### Story 15.2: Tracked-Run Retrospective Artifact

As a production operator,
I want an automated post-run retrospective generated after each tracked/default production run,
So that the system produces structured learning from every serious run.

**Acceptance Criteria:**

**Given** a tracked production run completes (all gates closed or run explicitly ended)
**When** Marcus initiates the retrospective step
**Then** a structured retrospective artifact is generated containing:
  - what worked unusually well (first-pass approvals, clean handoffs)
  - what failed (revisions, waivers, circuit breaks)
  - where each failure originated (upstream specialist) vs where detected (downstream gate)
  - what correction fixed each issue
  - which agents should learn what (per-specialist learning recommendations)
  - whether each finding should become deterministic policy, specialist guidance, or one-off note
**And** retrospective is saved to `{run_dir}/retrospective.md`
**And** learning events from Story 15.1 are the primary input
**And** retrospective template exists at `state/config/retrospective-template.md`
**And** Marcus references the retrospective in the run's final report

### Story 15.3: Upstream-From-Downstream Feedback Routing

As a system architect,
I want every downstream failure mapped to the earliest upstream point that could have prevented it,
So that the system learns causally, not only descriptively.

**Acceptance Criteria:**

**Given** a learning event records a failure at any gate
**When** the feedback routing logic runs (during retrospective generation)
**Then** the system applies a causal attribution taxonomy:
  - Quinn-R flags weak learner-effect → feeds back to Irene
  - Vera flags source drift in slides → feeds back to Irene brief + Gary execution pattern
  - composition issue from manifest ambiguity → feeds back to Irene and compositor
  - repeated human revisions at Gate 2 → feeds back to Gary and Marcus planning
**And** the routing taxonomy is defined in `state/config/feedback-routing-rules.yaml`
**And** routed feedback is appended to the target specialist's sidecar `patterns.md` in structured format
**And** sidecar writes respect existing `access-boundaries.md` constraints
**And** attribution is evidence-based (linked to specific learning events), not guessed
**And** new routing rules can be added without code changes (YAML-driven)

### Story 15.4: Synergy Scorecard

As a production operator,
I want measurable health indicators for handoff quality across the core pipeline,
So that "synergy" becomes an operationally visible property, not just a design aspiration.

**Acceptance Criteria:**

**Given** one or more tracked runs have completed with learning events captured
**When** the synergy scorecard is generated
**Then** it scores each core handoff on:
  - handoff completeness rate
  - downstream usability rate (did the receiver need to request corrections?)
  - first-pass acceptance of upstream artifacts
  - correction locality (good: caught near source; bad: caught 2-3 stages later)
  - repeated cross-agent friction signatures
**And** handoffs scored: Marcus→Irene, Irene→Gary, Gary→Irene Pass 2, Irene→Vera, Vera→Quinn-R, Quinn-R→Marcus/Human, manifest→compositor
**And** scorecard is saved to `reports/synergy/scorecard-{date}.md`
**And** scorecard can be run on-demand or as part of retrospective
**And** trend comparison is supported when multiple scorecards exist
**And** Marcus can reference the scorecard when planning subsequent runs

### Story 15.5: Multi-Agent Pattern Condensation

As a system architect,
I want a periodic condensation process that distills accumulated sidecar patterns into high-signal summaries,
So that agent memory stays useful without becoming bloated or contradictory.

**Acceptance Criteria:**

**Given** specialist sidecars have accumulated patterns from multiple tracked runs
**When** the condensation process runs
**Then** it produces per-specialist summaries:
  - top recurring success patterns
  - top recurring failure patterns
  - patterns that should be promoted to deterministic policy
  - patterns that should remain specialist calibration
  - patterns that should be archived as one-off
**And** condensation output is written to `{sidecar}/condensation-{date}.md`
**And** the process identifies and flags contradictory local lessons across agents
**And** duplicated learnings across multiple agents are deduplicated
**And** condensation does not delete original chronology entries (append-only archive)
**And** a policy-promotion review section highlights candidates for deterministic hardening

### Story 15.6: Workflow-Family Learning Ledger

As a production operator,
I want learning tracked not only per-agent but per-workflow family (narrated deck, motion-enabled lesson, assessment generation, etc.),
So that the platform gets smarter at the level the user actually experiences.

**Acceptance Criteria:**

**Given** tracked runs are tagged with their workflow family
**When** the workflow-family learning ledger is generated or updated
**Then** it tracks per workflow family:
  - frequent failure modes
  - expensive stages (time, credits, revision cycles)
  - best escalation points
  - best preset/mode combinations
  - common human preferences and overrides
**And** ledger is saved to `state/config/workflow-family-learning/{family-name}.yaml`
**And** Marcus can consult workflow-family heuristics when planning a new run
**And** the ledger grows from real run data (not pre-populated with guesses)
**And** new workflow families are automatically created when a run uses an unrecognized family tag

### Story 15.7: Agent Judgment Calibration Harness (autoresearch-inspired)

As a system architect,
I want an automated calibration harness that iteratively refines individual agent judgment criteria against human-labeled ground truth,
So that specialist agents (Quinn-R, Vera, Gary, Irene) get measurably better at their specific judgment tasks through structured experimentation rather than ad-hoc prompt tuning.

**Design inspiration**: Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) methodology — hypothesis → modify → run → evaluate → persist improvements — adapted from ML training loops to agent prompt/criteria calibration against labeled exemplar corpora.

**Acceptance Criteria:**

**Given** a labeled corpus exists for a specialist agent's judgment task (e.g., 20 slides labeled good/bad/marginal by a human reviewer)
**When** the calibration harness runs
**Then** it loads the agent's current evaluation criteria (from SKILL.md references, fidelity contracts, or quality rubrics)
**And** runs the agent's judgment against the full corpus, scoring agreement with human labels
**And** proposes a criteria modification (add a check, adjust severity, refine wording, reweight dimensions)
**And** re-runs and compares agreement rate
**And** if improved, persists the refinement to the agent's sidecar `patterns.md` with evidence (corpus size, before/after agreement rate, specific changes)
**And** if not improved, reverts and tries an alternative direction
**And** iterates up to a configurable max cycles (default: 10) or until convergence (agreement rate delta < threshold)
**And** produces a calibration report: `{agent, corpus_size, initial_agreement, final_agreement, refinements_accepted, refinements_rejected, cycles_run}`
**And** the harness extends the existing woodshed skill pattern rather than replacing it
**And** labeled corpus data derives from tracked-run learning events (Story 15.1) and human gate decisions
**And** unit tests cover the calibration loop, scoring, persistence, and revert logic

**Target agents and judgment tasks:**
- Quinn-R: slide quality discrimination (good vs. bad vs. marginal)
- Vera: fidelity assessment accuracy (omission/invention/alteration detection)
- Gary: parameter-to-outcome mapping (which Gamma parameters produce human-preferred results)
- Irene: pedagogical structure quality (which patterns get first-pass approval)

---

## Epic 16: Bounded Autonomy Expansion (Added 2026-04-06)

**Goal**: Expand the scope of what Marcus and specialist agents can do independently — reducing operator friction for routine decisions and low-risk operations — without weakening governance, gate authority, specialist lanes, or human checkpoint control where they matter.

**Depends on**: Epic 15 (hard — autonomy decisions must be informed by learning data, not design theory alone). At least 3-5 tracked runs completed (recommended — enough evidence to distinguish routine from risky decisions).

**Seed documents**: `_bmad-output/implementation-artifacts/app-three-layer-optimization-plans-2026-04-06.md` Plans 1 and 2, plus `_bmad-output/implementation-artifacts/app-optimization-map-and-baseline-audit-2026-04-05.md` Priorities 1, 2, and 4.

**Design guardrails**:
- Autonomy is earned, not assumed — expansion is gated by evidence from tracked runs
- Preserve specialist intelligence; do not replace pedagogy, visual reasoning, or evaluator judgment with cheap automation
- Human checkpoint authority is never reduced — only the friction of low-risk routine decisions is reduced
- Every autonomy expansion must have a rollback mechanism (deterministic fallback to operator-confirmed mode)

### Story 16.1: Autonomy Evidence Baseline & Decision Framework

As a system architect,
I want a structured framework for identifying which decisions can safely be automated based on tracked-run evidence,
So that autonomy expansion is data-driven, not speculative.

**Acceptance Criteria:**

**Given** learning events and retrospectives exist from tracked runs
**When** the autonomy evidence baseline is generated
**Then** it classifies each recurring decision point as:
  - `always-confirm`: high-risk or high-cost, must remain human-gated
  - `confirm-unless-routine`: low-risk when pattern matches prior approvals, can be auto-approved with notification
  - `auto-with-audit`: consistently approved without revision, can be fully automated with audit trail
**And** the classification is documented in `state/config/autonomy-framework.yaml`
**And** each classification cites specific run evidence (run IDs, approval rates, revision counts)
**And** Marcus can read the framework to adjust his checkpoint behavior
**And** the framework is reviewed and updated after each condensation cycle (Story 15.5)
**And** any decision can be manually reclassified by the operator at any time

### Story 16.2: Shared Governance Enforcement Utilities

As a developer,
I want reusable code-level middleware that validates governance constraints (allowed_outputs, decision_scope, authority_chain) across all specialists,
So that governance validation is consistent, machine-checkable, and no longer duplicated in agent prose.

**Acceptance Criteria:**

**Given** multiple specialists enforce governance boundaries in their instructions
**When** the shared governance module is implemented
**Then** a `scripts/utilities/governance_validator.py` module provides:
  - `validate_allowed_outputs(agent, outputs)` — checks output against agent's `governance.allowed_outputs`
  - `validate_decision_scope(agent, dimensions)` — checks owned vs. not-owned dimensions
  - `validate_authority_chain(envelope)` — confirms baton, route_to, and delegation fields
  - `validate_required_envelope_fields(agent, envelope)` — per-specialist required field check
**And** shared module is used by Marcus dispatch helpers, Gary, Irene, Vera, Quinn-R
**And** scope violations produce consistent, machine-readable `scope_violation` outputs
**And** existing agent SKILL.md governance prose can reference the shared validators instead of re-implementing
**And** unit tests cover each validation function with pass/fail cases per specialist
**And** the module does not replace specialist judgment — only enforces invariant boundaries

### Story 16.3: Expanded Handoff Validators for Late-Stage Transitions

As a production operator,
I want deterministic gatekeeper scripts for all high-cost pipeline transitions (not just Gary/Irene),
So that expensive downstream failures are caught before they happen.

**Acceptance Criteria:**

**Given** the core pipeline has validator coverage strongest around Gary and Irene
**When** validators are expanded
**Then** new validators cover:
  - Irene Pass 1 output bundle integrity (lesson plan + slide brief completeness)
  - Quinn-R pre-composition input completeness (all segments reviewed, all assets present)
  - ElevenLabs write-back completeness and path integrity (audio files exist, timestamps valid, VTT monotonic)
  - compositor manifest readiness (all write-back fields populated, all assets downloadable)
  - final composition bundle completeness (assembly guide + all referenced assets present)
**And** each validator is a standalone Python function in `scripts/utilities/`
**And** validators integrate with the existing gate coordinator
**And** validators are fail-closed: missing or invalid inputs block the transition
**And** validators produce structured reports (not just pass/fail) listing specific missing or invalid fields
**And** unit tests cover each validator with realistic pass and fail scenarios

### Story 16.4: Contract Linting & Drift Protection

As a system architect,
I want a repeatable contract-validation routine that detects structural drift in YAML contracts, schemas, and templates,
So that contracts remain operational assets, not only architectural documents.

**Acceptance Criteria:**

**Given** fidelity contracts, schemas, and templates are core invariants
**When** the contract lint command runs
**Then** it validates:
  - fidelity contract YAML structure against canonical schema
  - schema field consistency across related contracts
  - template references in contracts resolve to existing files
  - perception modality references match sensory bridge capabilities
  - gate names and ownership match lane-matrix definitions
**And** lint command is callable via `python -m scripts.utilities.contract_lint`
**And** lint runs on contract edits, in pre-merge checks, and during APP maturity audits
**And** output is structured: `{file, issue_type, severity, description, suggested_fix}`
**And** zero-finding runs produce a clean bill of health report
**And** the linter is extensible (new rule types can be added via YAML configuration)

### Story 16.5: Marcus Autonomous Routing for Routine Decisions

As a production operator,
I want Marcus to handle routine, low-risk decisions autonomously (with notification) based on the autonomy framework,
So that I spend my attention on decisions that actually need human judgment.

**Acceptance Criteria:**

**Given** the autonomy framework (Story 16.1) classifies certain decisions as `confirm-unless-routine` or `auto-with-audit`
**When** Marcus encounters a classified decision during a production run
**Then** for `confirm-unless-routine`: Marcus proceeds automatically if the current context matches a prior-approved pattern, and notifies the operator with a brief summary ("Auto-approved Gate 1 — matches pattern from runs X, Y, Z")
**And** for `auto-with-audit`: Marcus proceeds automatically and logs the decision to the audit trail without interrupting the operator
**And** for `always-confirm`: Marcus pauses and requests explicit operator confirmation (unchanged behavior)
**And** operator can override any auto-decision within the run by saying "stop auto-approving [gate/decision]"
**And** a per-run autonomy log tracks all auto-approved decisions with pattern citations
**And** if an auto-approved decision leads to a downstream failure, the retrospective (Story 15.2) flags it for reclassification
**And** autonomy behavior is disabled entirely when `run_preset: regulated`

---

## Epic 17: Research & Reference Services (Added 2026-04-06)

**Goal**: Provide agent-consumable research and citation services that enrich course content with academically credible, triangulated references — from supplemental "Related Resources" lists through inline citation injection to hypothesis-driven learning experience research.

**Depends on**: Epic 3 source wrangler and tech-spec-wrangler (existing, satisfied). Consensus API and Scite.ai API access (new integration requirement). Existing agent infrastructure (Marcus, Irene, source wrangler as consumers).

**Design principles**:
- Triangulation is core: findings from Consensus and Scite.ai are cross-validated, not taken at face value from a single source
- Output modes are composable: related-resources, inline citation, and hypothesis research can be used independently or combined
- Services are agent-consumable: any agent (source wrangler, Irene, Marcus) can invoke research services, not just a single consumer
- Academic credibility is paramount: citation quality, recency, and relevance are explicitly scored

### Story 17.1: Research Service Foundation & API Integration

As a developer,
I want API clients for Consensus and Scite.ai with triangulation logic,
So that the APP can programmatically retrieve and cross-validate academic research findings.

**Acceptance Criteria:**

**Given** Consensus and Scite.ai API credentials are configured in `.env`
**When** the research service is initialized
**Then** `scripts/api_clients/consensus_client.py` provides: search by query, filter by recency/field/type, retrieve paper metadata and key findings
**And** `scripts/api_clients/scite_client.py` provides: search by query or DOI, retrieve citation context (supporting/contrasting/mentioning), smart citation counts
**And** a `scripts/utilities/research_triangulator.py` module cross-validates findings:
  - papers found in both sources score higher
  - contradictory citation contexts are flagged
  - recency, citation count, and journal quality contribute to a composite reliability score
**And** triangulated results are returned in a canonical format: `{query, findings[], reliability_scores, contradictions[], metadata}`
**And** pre-flight check is extended to verify Consensus and Scite.ai API connectivity
**And** unit tests cover each client with mocked responses and triangulation logic with synthetic data
**And** live integration tests (behind `--run-live` flag) validate real API connectivity

### Story 17.2: Related Resources List Generation

As a production operator,
I want the research service to generate a "Related Resources" list from a presentation script or lesson notes,
So that learners get credible supplemental references for further study.

**Acceptance Criteria:**

**Given** a completed narration script or lesson notes (Irene Pass 2 output)
**When** the related-resources generator runs
**Then** key themes and claims are extracted from the source text
**And** each theme/claim is researched via the triangulation service (Story 17.1)
**And** results are filtered and ranked by: relevance to the source claim, reliability score, recency, accessibility (open-access preferred)
**And** output is a structured "Related Resources" document containing:
  - resource title, authors, publication year, DOI/URL
  - one-sentence relevance summary per resource
  - reliability indicator (triangulated / single-source)
  - grouped by theme or section of the source material
**And** configurable output count: default 5-10 resources, adjustable per run
**And** output formats: Markdown (standalone document), slide-ready format (for last-slide embed), YAML (for downstream agent consumption)
**And** the generator can be invoked by Marcus, Irene, or source wrangler via a shared function interface

### Story 17.3: Inline Citation Injection Mode

As a production operator,
I want the research service to enrich a script or notes with inline citations to supporting research,
So that content gains academic depth and credibility without requiring manual research.

**Acceptance Criteria:**

**Given** a narration script or lesson notes and `citation_mode: inline` is specified
**When** the citation injector runs
**Then** claims, statistics, and assertions in the source text are identified
**And** each identified claim is researched via the triangulation service
**And** matching citations are inserted naturally into the text flow (e.g., "(Smith et al., 2024)" or "Research from [University] confirms...")
**And** a bibliography/references section is appended with full citation details
**And** citation density is configurable: `light` (key claims only), `moderate` (most substantive claims), `thorough` (all supportable assertions)
**And** the injector preserves the original voice and flow of the text — citations augment, not disrupt
**And** claims where no credible research is found are left unchanged (no fabricated citations)
**And** output includes a citation map: `{claim_text, citation, reliability_score, source_api}`
**And** Irene can invoke this mode during Pass 2 narration scripting when requested

### Story 17.4: Hypothesis & Learning Experience Research Mode

As an instructional designer (Irene),
I want the research service to find pro/con research for claims or themes in course content,
So that I can design learning experiences like debates, critical analysis exercises, and evidence-evaluation activities.

**Acceptance Criteria:**

**Given** a theme, claim, or hypothesis extracted from lesson content and `research_mode: hypothesis` is specified
**When** the hypothesis research service runs
**Then** Scite.ai citation contexts are used to identify: supporting evidence, contrasting evidence, and mentioning-only references
**And** Consensus findings are categorized by stance: supports, challenges, nuances
**And** output is a structured hypothesis research package:
  - claim/hypothesis statement
  - supporting evidence summary with citations
  - contrasting evidence summary with citations
  - nuances and qualifications
  - suggested learning activities (e.g., "Have students compare Smith 2023 and Jones 2024 for opposing conclusions")
  - evidence strength assessment per side
**And** the package can be consumed by Irene for designing discussion prompts, debate scaffolds, or critical thinking exercises
**And** Marcus can request hypothesis research as part of run planning when the lesson content involves controversial or multi-perspective topics
**And** output includes an academic integrity note flagging any findings with low reliability or limited triangulation

### Story 17.5: Research Service Agent Integration & Skill Packaging

As a system architect,
I want the research services packaged as a shared skill consumable by any agent in the APP,
So that research capabilities are reusable across workflows and agents.

**Acceptance Criteria:**

**Given** Stories 17.1-17.4 provide the research service functions
**When** the skill is packaged
**Then** a `skills/research-services/` skill directory is created with SKILL.md, references, and scripts
**And** the skill exposes three modes: `related-resources`, `inline-citation`, `hypothesis`
**And** Marcus can delegate research tasks to the skill as part of production planning
**And** Irene can invoke research during Pass 1 (lesson planning) or Pass 2 (narration scripting)
**And** source wrangler can invoke research when enriching source bundles
**And** the skill respects run-constants: `research_enabled: boolean`, `research_mode: related | citation | hypothesis | all`, `research_depth: light | moderate | thorough`
**And** research results are cached per-run to avoid redundant API calls for the same queries
**And** run reporting includes research metrics: queries made, citations found, triangulation rate, API credits consumed
**And** the skill's governance block defines its lane: research retrieval and formatting only, no pedagogical or visual judgment

---

## Epic 18: Additional Assets & Workflow Families (Added 2026-04-06)

**Goal**: Expand the APP's production capabilities beyond narrated slide decks to cover the full range of instructional content types — cases/scenarios, quizzes, discussions, review activities, handouts, podcasts, instructional diagrams, and more — with new workflow families or pipeline variants and tool integrations as needed.

**Depends on**: Core pipeline stability (Epics 1-14 complete, satisfied). At least one successful tracked trial run of the narrated-deck workflow (recommended — proves the pipeline model before extending it). Epic 15 learning infrastructure (soft — new workflows should capture learning from day one).

**Design principles**:
- Discovery-first: each new content type starts with a dedicated requirements elicitation story before implementation
- Workflow families, not one-offs: each content type gets a named workflow family that the learning ledger (Story 15.6) can track
- Reuse the pipeline model: where possible, new content types reuse existing agents (Irene for pedagogy, Quinn-R for quality) with new specialist skills, not new agents
- Human-in-the-loop by default: new content types inherit the HIL gate pattern; gate count and placement are determined per content type during discovery

### Story 18.1: Content Type Discovery & Requirements Elicitation — Cases & Scenarios

As a product owner,
I want detailed requirements for case study and scenario-based learning content production,
So that the APP can produce pedagogically sound cases with the right workflow, agents, and tools.

**Acceptance Criteria:**

**Given** cases/scenarios are identified as a target content type
**When** the discovery process completes
**Then** a requirements document exists in `_bmad-output/planning-artifacts/` covering:
  - content structure (narrative arc, decision points, branching vs. linear, debriefing)
  - source material requirements (real-world data, anonymization needs, domain expertise)
  - agent roles (Irene for pedagogy, new specialist for scenario logic, Quinn-R for quality)
  - tool requirements (Gamma for visuals? Botpress for interactive branching? New tools?)
  - output formats (document, slide-embedded, LMS-native, interactive web)
  - HIL gates (how many, where placed, what the human reviews)
  - workflow family definition: named stages, handoff contracts, acceptance criteria
**And** the discovery document is reviewed by the operator before implementation stories are created
**And** implementation stories for cases/scenarios are added to this epic after approval

### Story 18.2: Content Type Discovery & Requirements Elicitation — Quizzes & Assessments

As a product owner,
I want detailed requirements for quiz and assessment content production,
So that the APP can produce valid, aligned assessments integrated with the existing Qualtrics and Canvas tooling.

**Acceptance Criteria:**

**Given** quizzes/assessments are identified as a target content type
**When** the discovery process completes
**Then** a requirements document exists covering:
  - assessment types (formative, summative, diagnostic, self-check, peer review prompt)
  - item types (multiple choice, short answer, matching, essay prompt, scenario-based)
  - alignment requirements (Bloom's taxonomy mapping, learning objective traceability)
  - agent roles (Irene for alignment, Qualtrics specialist for survey-type items, Canvas specialist for LMS-native quizzes)
  - quality review requirements (distractor analysis, difficulty calibration, bias review)
  - output formats (Qualtrics survey, Canvas quiz, standalone document, question bank)
  - workflow family definition
**And** the discovery document is reviewed before implementation stories are created

### Story 18.3: Content Type Discovery & Requirements Elicitation — Discussions & Review Activities

As a product owner,
I want detailed requirements for discussion prompt and review activity production,
So that the APP can produce engaging, pedagogically grounded collaborative learning experiences.

**Acceptance Criteria:**

**Given** discussions and review activities are identified as target content types
**When** the discovery process completes
**Then** a requirements document exists covering:
  - discussion types (open-ended, structured debate, case discussion, peer review, reflection)
  - review activity types (peer critique, self-assessment rubric, portfolio review prompt)
  - scaffolding requirements (discussion rubrics, response templates, moderation guidance)
  - agent roles (Irene for pedagogy, Canvas specialist for LMS discussion setup)
  - research integration (Epic 17 hypothesis mode for debate scaffolds)
  - output formats (Canvas discussion topic, standalone prompt document, rubric)
  - workflow family definition
**And** the discovery document is reviewed before implementation stories are created

### Story 18.4: Content Type Discovery & Requirements Elicitation — Handouts & Reference Materials

As a product owner,
I want detailed requirements for handout and reference material production,
So that the APP can produce supplemental learning materials that complement presentations and lessons.

**Acceptance Criteria:**

**Given** handouts and reference materials are identified as target content types
**When** the discovery process completes
**Then** a requirements document exists covering:
  - handout types (study guide, cheat sheet, quick reference, glossary, procedure guide, worksheet)
  - design requirements (visual design standards, accessibility, print-readiness)
  - agent roles (Irene for content, Canva specialist for visual design guidance, research services for citations)
  - tool requirements (Canva for design, Gamma for visual elements, PDF generation)
  - relationship to primary content (companion to specific lesson, standalone reference)
  - output formats (PDF, Markdown, Canva design template, print-optimized)
  - workflow family definition
**And** the discovery document is reviewed before implementation stories are created

### Story 18.5: Content Type Discovery & Requirements Elicitation — Podcasts & Audio Content

As a product owner,
I want detailed requirements for podcast and audio-first content production,
So that the APP can produce audio learning experiences beyond slide narration.

**Acceptance Criteria:**

**Given** podcasts and audio content are identified as target content types
**When** the discovery process completes
**Then** a requirements document exists covering:
  - audio content types (lecture podcast, interview/dialogue, case discussion audio, audio summary/recap)
  - script structure (monologue, dialogue with multiple voices, interview format)
  - agent roles (Irene for script, ElevenLabs specialist for multi-voice production, Quinn-R for quality)
  - tool requirements (ElevenLabs dialogue API, Wondercraft for enhanced podcast features, Descript for editing)
  - production requirements (intro/outro, music beds, chapter markers, transcript generation)
  - output formats (MP3, enhanced podcast with chapters, transcript + VTT, RSS-ready)
  - workflow family definition
**And** the discovery document is reviewed before implementation stories are created

### Story 18.6: Content Type Discovery & Requirements Elicitation — Instructional Diagrams & Infographics

As a product owner,
I want detailed requirements for instructional diagram and infographic production,
So that the APP can produce visual learning aids that explain processes, relationships, and data.

**Acceptance Criteria:**

**Given** instructional diagrams and infographics are identified as target content types
**When** the discovery process completes
**Then** a requirements document exists covering:
  - visual types (process flow, concept map, comparison chart, timeline, data visualization, anatomical/technical diagram)
  - design requirements (brand alignment, accessibility, resolution for print and screen)
  - agent roles (Irene for content, Canva specialist for design guidance, Midjourney specialist for bespoke visuals)
  - tool requirements (Canva, Midjourney, Gamma for simple diagrams, manual tools for complex)
  - accuracy requirements (data visualization validation, domain expert review)
  - output formats (PNG, SVG, PDF, embeddable in slides/handouts)
  - workflow family definition
**And** the discovery document is reviewed before implementation stories are created

### Story 18.7: Workflow Family Implementation Framework

As a system architect,
I want a reusable framework for implementing new workflow families based on discovery documents,
So that each approved content type can be stood up efficiently without reinventing pipeline infrastructure.

**Acceptance Criteria:**

**Given** one or more discovery documents (Stories 18.1-18.6) are approved
**When** the implementation framework is created
**Then** a workflow-family template exists providing:
  - pipeline stage template (stage name, agent, input contract, output contract, HIL gate placement)
  - run-constants.yaml extension pattern for new workflow families
  - structural-walk manifest extension pattern for new workflow families
  - learning ledger initialization for new workflow families (integrates with Story 15.6)
  - pre-flight check extension pattern for new tool dependencies
  - prompt-pack template for operator guidance
**And** the framework is documented in `docs/workflow/workflow-family-implementation-guide.md`
**And** the framework is validated by implementing the first approved content type end-to-end
**And** subsequent content types can be stood up by following the framework without architectural changes