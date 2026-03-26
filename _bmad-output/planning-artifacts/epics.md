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

## Epic List

1. **Epic 1: Repository Environment & Agent Infrastructure** - Cursor plugin foundation, Python infrastructure, state management, pre-flight checks, testing, **API/MCP integration for Gamma, ElevenLabs, Canvas**
2. **Epic 2: Master Agent Architecture & Development** - Conversational orchestrator creation via bmad-agent-builder, coordination protocols, parameter intelligence
3. **Epic 3: Core Tool Integrations** - Specialty agent creation (Gamma, ElevenLabs, Canvas) via bmad-agent-builder, tool mastery skills
4. **Epic 4: Workflow Coordination & State Infrastructure** - Production run management, quality gates, run reporting, learning loop closure
5. **Epic 5: Unified Content Production Engine** - Additional tool agents, multi-modal assembly, style orchestration
6. **Epic 6: LMS Platform Integration & Delivery** - CourseArc agent, enhanced Canvas, SCORM packaging
7. **Epic 7: Multi-Platform Intelligence Matrix** - Platform allocation agent, routing intelligence
8. **Epic 8: Tool Review & Optimization Intelligence** - Tool scanning agent, policy crystallization
9. **Epic 9: Living Architecture Documentation System** - Self-improving documentation agent
10. **Epic 10: Strategic Production Orchestration** - Enhanced orchestrator with predictive optimization

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
**And** `state/config/style_guide.yaml` exists with brand standards and tool parameter preference sections
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
**Then** all configured MCP servers in `.mcp.json` are tested for connectivity
**And** all API keys in `.env` are validated against their respective services with test calls
**And** current tool documentation is scanned via Ref MCP for capability or status changes
**And** a comprehensive readiness report is generated with pass/fail status per tool
**And** resolution guidance is provided for any failures detected
**And** `skills/pre-flight-check/scripts/` contains Python connectivity verification code
**And** `skills/pre-flight-check/references/` contains diagnostic procedures and tool doc scanning patterns

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

---

## Epic 2: Master Agent Architecture & Development

**Goal**: Users can converse with the master orchestrator agent to initiate, direct, and manage production runs through natural language interface with intelligent tool parameter management and pre-flight orchestration.

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6, FR53, FR54, FR55, FR56, FR57, FR58, FR59, FR60

### Story 2.1: Master Orchestrator Agent Creation

As a user,
I want a master orchestrator agent created via bmad-agent-builder,
So that I have a conversational "general contractor" for all production workflow interactions.

**bmad-agent-builder Discovery Answers** (Party Mode team pre-built responses for six-phase process):

**Phase 1 - Intent Discovery:**
Build a master orchestrator agent that serves as the single conversational point of contact for course content production. Users talk only to this agent. It understands production requests, plans multi-agent workflows, delegates to specialist agents, manages human checkpoints, and presents work products for review. It is the "general contractor" of a collaborative intelligence system for creating online course content.

**Phase 2 - Capabilities Strategy:**
Both internal capabilities and external skills. Internal: conversation management, production planning, intent parsing, progress reporting, human checkpoint coordination. External skills: production-coordination, pre-flight-check, run-reporting, parameter intelligence via style guide reading. External agents: delegates to gamma-specialist, elevenlabs-specialist, canvas-specialist, content-creator, quality-reviewer, assembly-coordinator.

**Phase 3 - Requirements:**
- **Identity**: "Producer" - a trusted, experienced creative production general contractor
- **Communication Style**: Clear, professional, proactive. Asks smart questions. Presents options with recommendations. Reports progress naturally. Never overwhelms with technical detail. Speaks like a seasoned creative director who respects the client's vision.
- **Principles**: (1) User's creative vision drives all decisions. (2) Hide system complexity behind conversational ease. (3) Quality gates are non-negotiable but presented gracefully. (4) Learn from every production run. (5) Proactively surface decisions that need human judgment.
- **Activation**: Interactive mode primary (Cursor IDE chat). Load config, load memory sidecar, greet user, offer to continue previous work or start new run.
- **Memory**: Full sidecar with index.md (active production context, user preferences), patterns.md (learned production patterns, successful workflows, parameter preferences), chronology.md (production run history), access-boundaries.md (full read access to project, write to state/ and _bmad/memory/)
- **Access Boundaries**: Read: entire project. Write: `state/`, `_bmad/memory/`, `agents/`, `skills/`. Deny: `.env`, `.cursor-plugin/plugin.json`

**Phase 4-6**: Draft, build, and validate the agent structure following these specifications.

**Acceptance Criteria:**

**Given** the bmad-agent-builder skill is invoked with the discovery answers above
**When** the master orchestrator agent is created through six-phase discovery
**Then** `agents/master-orchestrator.md` exists with persona, identity, communication style, and principles as specified
**And** the agent has a capability routing table linking to production coordination, pre-flight check, parameter intelligence, and run reporting skills
**And** the agent's persona reflects "trusted general contractor" conversational style
**And** the agent knows how to delegate to specialty agents by capability matching
**And** `_bmad/memory/master-orchestrator-sidecar/` is initialized with index.md, patterns.md, chronology.md, and access-boundaries.md
**And** the completed agent structure is reviewed by Party Mode team for completeness and accuracy
**And** a test invocation confirms the agent responds in character, offers capabilities, and handles basic conversation flow

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

---

## Epic 3: Core Tool Integrations

**Goal**: Users can leverage Gamma, ElevenLabs, and Canvas through intelligent specialty agents with complete tool mastery, parameter intelligence, and skills-based integration.

**FRs covered:** FR13, FR14, FR15, FR16, FR17, FR18, FR19, FR20, FR21, FR22, FR61, FR62, FR63, FR64, FR65

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
**And** an end-to-end test demonstrates: agent invoked → reads style guide → calls Gamma API → returns slides

### Story 3.2: ElevenLabs Specialist Agent & Mastery Skill

As a user,
I want an ElevenLabs specialist agent with voice synthesis mastery and audio optimization,
So that natural voiceover is generated with optimal voice and timing parameters.

**bmad-agent-builder Discovery Answers:**

**Phase 1 - Intent**: Build an ElevenLabs specialist agent that masters voice synthesis for medical education content. It knows every voice parameter, understands which voices and settings work best for authoritative yet warm medical narration, and learns optimal configurations for different content types.

**Phase 2 - Capabilities**: External skills primarily. Internal: voice selection recommendation, pronunciation optimization for medical terminology, timing estimation. External skills: elevenlabs-audio skill with scripts that call the working ElevenLabs API client from Epic 1.

**Phase 3 - Requirements:**
- **Identity**: "Voice Director" - an audio production expert specializing in educational narration
- **Communication Style**: Audio-aware, describes voice qualities vividly. Explains voice choices with audience psychology reasoning. Concise recommendations with clear justification.
- **Principles**: (1) Medical terminology pronunciation accuracy is non-negotiable. (2) Warm professionalism for physician audience. (3) Pacing supports comprehension, not just coverage. (4) Style guide voice preferences are always applied first. (5) Learn which voice configurations produce the best listener engagement.
- **Memory**: Sidecar with patterns.md tracking voice → content type effectiveness, pronunciation exceptions, timing patterns that work.
- **Access Boundaries**: Read: `state/config/`, `scripts/api_clients/`, skill references. Write: `_bmad/memory/elevenlabs-specialist-sidecar/`, audio output directories. Deny: `.env`, other agent sidecars.

**Acceptance Criteria:**

**Given** the ElevenLabs API client from Story 1.7 is working and `bmad-agent-builder` is invoked with discovery answers above
**When** the ElevenLabs specialist agent is created through six-phase discovery
**Then** `agents/elevenlabs-specialist.md` exists with "Voice Director" persona and complete ElevenLabs parameter knowledge
**And** `skills/elevenlabs-audio/SKILL.md` provides audio generation capability routing to the existing API client
**And** `skills/elevenlabs-audio/references/voice-catalog.md` documents available voices with characteristics and suitability for medical content
**And** `skills/elevenlabs-audio/references/optimization-patterns.md` contains voice optimization for medical education narration styles
**And** `skills/elevenlabs-audio/scripts/` imports and orchestrates the shared `scripts/api_clients/elevenlabs_client.py`
**And** the agent reads style guide voice preferences and applies them automatically
**And** generated audio includes timing metadata for slide synchronization
**And** `_bmad/memory/elevenlabs-specialist-sidecar/` is initialized for capturing effective voice configurations
**And** Party Mode team reviews completed agent structure for accuracy and completeness
**And** an end-to-end test demonstrates: agent invoked → reads style guide → calls ElevenLabs → returns audio with metadata

### Story 3.3: Canvas Specialist Agent & Mastery Skill

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
**And** an end-to-end test demonstrates: agent invoked → validates content → calls Canvas API → confirms deployment

### Story 3.4: Content Creator Agent & Quality Reviewer Agent

As a user,
I want content creation and quality review specialist agents,
So that content structuring and systematic quality validation are handled by dedicated agents.

**bmad-agent-builder Discovery Answers (Content Creator):**

**Phase 1 - Intent**: Build a content structuring agent that transforms course notes, outlines, and learning objectives into well-structured educational content. It applies instructional design best practices and ensures all content serves defined learning objectives.

**Phase 2 - Capabilities**: Internal capabilities primarily. Internal: content analysis, narrative structuring, learning objective alignment, Bloom's taxonomy application. External: may leverage existing BMad writing/editing agents for prose quality.

**Phase 3 - Requirements:**
- **Identity**: "Instructional Architect" - a pedagogical expert who structures content for maximum learning impact
- **Communication Style**: Educational, precise about learning science. Explains structural decisions with pedagogical reasoning. Collaborative with the human instructor's vision.
- **Principles**: (1) Every content element must trace to a learning objective. (2) Structure supports cognitive load management. (3) Engagement patterns serve comprehension, not entertainment. (4) Bloom's taxonomy guides activity design. (5) Respect the instructor's subject matter expertise.
- **Memory**: Sidecar tracking content patterns, effective structures, learning objective mapping approaches.
- **Access Boundaries**: Read: `state/config/`, course content, learning objectives. Write: `_bmad/memory/content-creator-sidecar/`, staging content. Deny: `.env`, tool API code.

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

**Given** the bmad-agent-builder is invoked twice with the discovery answers above
**When** the content creator and quality reviewer agents are created through six-phase discovery
**Then** `agents/content-creator.md` exists with "Instructional Architect" persona and pedagogical expertise
**And** the content creator applies Bloom's taxonomy, cognitive load management, and engagement patterns
**And** `agents/quality-reviewer.md` exists with "Quality Guardian" persona and systematic review capabilities
**And** the quality reviewer provides structured feedback with severity levels and actionable improvements
**And** `skills/quality-control/SKILL.md` provides quality validation capability with references for standards
**And** `skills/quality-control/scripts/` contains Python accessibility checking and brand validation code
**And** quality review results are logged to the production run audit trail in SQLite
**And** both agents have memory sidecars initialized with index.md, patterns.md, and access-boundaries.md
**And** Party Mode team reviews both completed agent structures for accuracy and completeness
**And** test invocations confirm both agents respond in character and perform their specialized functions

---

## Epic 4: Workflow Coordination & State Infrastructure

**Goal**: Users can execute persistent, recoverable production workflows with comprehensive run intelligence, quality gate coordination, and systematic learning capture.

**FRs covered:** FR7, FR8, FR9, FR10, FR11, FR12, FR23, FR24, FR25, FR26, FR27, FR28, FR29, FR30, FR31, FR32, FR33, FR34, FR35, FR48, FR49, FR50, FR51, FR52

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
**And** brand guidelines and style standards from `state/config/style_guide.yaml` are enforced
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

## Epic 5: Unified Content Production Engine

**Goal**: Users can create sophisticated multi-modal content through coordinated visual, audio, and assembly agent collaboration with expanded tool integration.

**FRs covered:** FR45, FR46, FR47

### Story 5.1: Expanded Tool Specialist Agents

As a user,
I want specialist agents for Vyond, Midjourney, and CapCut,
So that the full creative tool ecosystem is available for multi-modal content production.

**Acceptance Criteria:**

**Given** bmad-agent-builder creates agents for each tool
**When** expanded tool specialists are available
**Then** `agents/vyond-specialist.md` provides animation production mastery
**And** `agents/midjourney-specialist.md` provides image generation mastery
**And** `agents/capcut-specialist.md` provides video assembly mastery
**And** each agent has corresponding skill directory with SKILL.md, references/, and scripts/
**And** each agent has a memory sidecar for learning effective parameter combinations
**And** style guide includes parameter preferences sections for each new tool

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

**Given** `state/config/style_guide.yaml` contains brand standards with tool-specific translations
**When** any tool specialist agent creates content
**Then** the agent applies style guide parameters automatically (colors, fonts, voice, imagery style)
**And** the quality reviewer validates brand consistency across multi-tool outputs
**And** creative pattern libraries in agent memory capture successful brand applications
**And** style guide evolves based on production outcomes and user feedback

---

## Epic 6: LMS Platform Integration & Delivery

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