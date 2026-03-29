---
stepsCompleted: ["step-01-init", "step-02-discovery", "step-02b-vision", "step-02c-executive-summary", "step-03-success", "step-04-journeys", "step-05-domain", "step-06-innovation", "step-07-project-type", "step-08-scoping", "step-09-functional", "step-10-nonfunctional", "step-11-polish", "step-12-complete"]
inputDocuments: [
  "_bmad-output/brainstorming/brainstorming-session-20260325-150802.md",
  "docs/project-context.md",
  "docs/agent-environment.md",
  "docs/workflow/human-in-the-loop.md",
  "_bmad-output/strategic-decisions-collaborative-intelligence.md"
]
documentCounts: {
  briefCount: 0,
  researchCount: 0,
  brainstormingCount: 1,
  projectDocsCount: 3,
  strategicCount: 1
}
classification:
  projectType: "developer_platform"
  domain: "edtech"
  complexity: "high"
  projectContext: "brownfield"
  innovation: "persistent_collaborative_intelligence"
epicValidation:
  status: "refined_and_validated"
  keyEnhancements: ["coordination_infrastructure", "state_management", "cross_run_persistence"]
  newEpic: "workflow_coordination_state_infrastructure"
workflowType: 'prd'
---

# Product Requirements Document - course-DEV-IDE-with-AGENTS

**Author:** Juanl
**Date:** March 25, 2026

## Executive Summary

**course-DEV-IDE-with-AGENTS** creates a persistent collaborative intelligence infrastructure for systematically scaling creative expertise in online course content production. This system orchestrates specialized AI agents that communicate with each other, manipulate professional media tools through APIs and MCPs, and systematically capture creative decision-making patterns for iterative refinement and reuse.

The system serves as a "Party Mode on steroids" environment where a custom master orchestrator agent provides a conversational interface for all user interactions, coordinating specialist skills to transform course creation from manual multi-tool workflows into intelligent collaborative orchestration. Users interact exclusively through natural language conversation with the orchestrator, which manages all system complexity behind an intuitive dialogue interface. Agents maintain persistent context across production runs, ensuring brand consistency, instructional design alignment, and quality standards while enabling exponential productivity gains without creative quality loss.

Target users: Individual educators and instructional designers seeking to scale high-quality course production through systematic agent collaboration rather than automation replacement of human expertise.

### What Makes This Special

**Core Innovation:** Agent-to-agent communication combined with direct tool manipulation and systematic expertise crystallization creates the first intelligent creative collaboration platform with persistent memory and coordination capabilities.

**Breakthrough Insight:** While existing AI tools operate as individual assistants, this system enables agents to collaborate intelligently, review each other's work against captured creative standards, and systematically improve workflows through experience. Agents become repositories of creative decision-making that execute at scale while preserving and enhancing human expertise rather than replacing it.

**Differentiation:** Creates a coordinated agent ecosystem that maintains state across workflow runs, remembers creative decisions and their rationale, and iteratively refines creative processes. Users gain an evolving creative production team that gets smarter with each course module rather than static automation tools.

**Value Proposition:** Transform course creation from time-intensive manual coordination of multiple tools (Gamma, ElevenLabs, Vyond, Canvas, CourseArc) into intelligent collaborative workflows managed through natural conversation with a master orchestrator. Users gain a "general contractor" agent experience that scales creative expertise systematically while maintaining instructional design quality and brand consistency through conversational workflow direction.

## Project Classification

**Project Type:** Developer Platform - Specialized multi-agent orchestration toolkit for creative workflow automation  
**Domain:** Educational Technology (EdTech) - Course content production and deployment systems  
**Complexity:** High - Combines educational compliance requirements (FERPA, accessibility), multi-platform integration challenges, and novel multi-agent coordination architecture  
**Project Context:** Brownfield - Substantial architectural foundation and strategic planning completed through comprehensive brainstorming and BMad Party Mode validation

## Success Criteria

### User Success

**Quality-Speed Scaling Achievement**: Maintain all quality standards while achieving 50% faster production speed across course module creation. Quality takes priority over speed - reliability is more important than blinding speed, with acceptable speed variations across complexity gradients.

**Reduced Cognitive Load**: Eliminate workflow management stress through systematic agent coordination. Success indicated by ability to focus on creative/instructional decisions rather than tool handoffs, reduced mental juggling of multiple platforms, and confidence to step away during production runs without anxiety.

**Systematic Expertise Capture**: Evidence that agents systematically apply captured creative decisions rather than generic automation. Measured through consistency with previous creative choices, automatic application of brand guidelines and pedagogical approaches, and visible improvement of resources through multi-agent production cycles.

### Business Success

**3-Month Near-Term Success**: Successfully complete 2-3 varied complexity modules with quality maintained and measurable stress reduction in workflow management. Demonstrate reliable agent coordination without workflow failures.

**12-Month Transformational Success**: System intelligence that enables taking on more ambitious course projects, quality improvements beyond manual processes, and optimization suggestions that enhance creative capabilities.

**MVP Validation Milestone**: Complete 1 full presentation module through multi-agent production cycle (baseline→enhancement→visual→audio→quality control→assembly) with 50% time reduction, maintained quality standards, and evident expertise capture.

### Technical Success

**API Reliability**: 100% pre-session API connectivity verification with graceful degradation during production failures. Clear human escalation triggers for tool connectivity issues.

**Agent Coordination Effectiveness**: Autonomous workflow management with strategic quality/design decision points properly routed to human oversight. Agents handle execution coordination while human focuses on creative direction.

**System Recovery**: Acceptable workflow interruption frequency (monthly or less) with rapid recovery from tool API failures or agent coordination issues.

### Measurable Outcomes

**Quality Standards Maintained**: Instructional design quality (learning objectives, Bloom's taxonomy), brand consistency (visual, voice, tone), content accuracy and compliance (FERPA, accessibility, citations).

**Production Cycle Evidence**: Single resources demonstrate systematic enhancement through multi-agent coordination - baseline slides→text optimization→B-roll generation→voiceover integration→quality validation→final assembly.

**Validation Success**: After first complete module production, confidence that "collaborative intelligence approach fundamentally works and should be scaled."

## Product Scope

### MVP - Minimum Viable Product (Foundation-First Approach)

**Epic Sequence (Revised for Iterative Development):**

**Epic 1: Repository Environment & Agent Infrastructure** (FOUNDATIONAL)
- Cursor plugin setup with `.cursor-plugin/plugin.json` manifest and auto-discovery configuration
- Agent directory structure: `agents/`, `skills/`, `rules/`, `commands/`, `hooks/`
- Python infrastructure: `.venv`, `requirements.txt`, `.env` for API keys (following canvas_api_tools patterns)
- SQLite + YAML state management infrastructure with BMad memory sidecar directories
- MCP integration via `.mcp.json` bundled in plugin
- **Core API/MCP Integration**: Built and tested API clients for Gamma, ElevenLabs, and Canvas with verified connectivity, retry logic, and error handling - available for all subsequent agent and skill development
- **Pre-Flight Check Infrastructure**: Hook-based MCP/API connectivity verification and tool documentation scanning
- **Testing Framework**: Agent coordination validation and skill execution testing infrastructure

**Epic 2: Master Agent Architecture & Development**
- Create master orchestrator agent via `bmad-agent-builder` six-phase discovery process
- Agent .md file with persona, conversational capabilities, and routing table to specialist agents
- Memory sidecar for persistent orchestrator learning (production patterns, user preferences)
- Cursor IDE chat integration as primary conversational interface
- **Conversational Workflow Management**: Natural language run initiation, human checkpoints, work product review
- **Run Mode Management**: Binary ad-hoc/default mode switch with natural language control; ad-hoc routes assets to scratch/staging with state tracking suppressed; QA always runs; future evolution to per-level modality matrix
- **Parameter Intelligence Coordination**: Style guide integration with conversational elicitation
- **Pre-Flight Check Orchestration**: User-invokable system validation through conversation
- **Agent Coordination Protocols**: Capability matching and delegation to specialty agents
- **Source Wrangling Coordination**: Orchestrator awareness of external reference sources (Notion, Box Drive) for production context enrichment

**Epic 3: Core Tool Specialist Agents & Mastery Skills** 
- Create specialty agents via `bmad-agent-builder`: Gamma specialist, ElevenLabs specialist, Canvas specialist
- Each agent as .md file with tool mastery persona and parameter intelligence
- Mastery skills (SKILL.md + references/) that orchestrate the already-working API clients from Epic 1
- Complete parameter catalogs with context-specific optimization patterns
- Tool capability parameter preferences stored in style guide YAML format
- Content creator and quality reviewer agents for instructional design and validation
- **Source Wrangler**: Dedicated agent or skill for pulling reference materials from Notion (via API) and Box Drive (local filesystem), with feedback-writing capability to Notion; design decision (agent vs. skill) to be resolved during story creation

**Epic 4: Workflow Coordination & State Infrastructure**
- Cross-run state persistence using BMad memory sidecars + SQLite coordination database
- Production run lifecycle management with YAML run context entities
- Quality gate coordination through agent peer review skill invocation
- **Production intelligence and comprehensive run reporting** via reporting skills with Python analytics scripts
- **Workflow optimization insights** captured in agent memory sidecars
- **Learning loop closure**: Agent sidecar pattern updates for systematic expertise crystallization

**Production Validation**: **Complete Course 1, Module 1 recreation** through multi-agent production cycle using existing content as baseline. This real-world module provides concrete complexity requirements including Welcome video production, knowledge checks, discussion boards, multimedia integration (Freakonomics podcast, YouTube videos), and grading rubrics.

**MVP Success Criteria**: Successfully reproduce Course 1, Module 1 with 50% time improvement, maintained quality standards, and evident systematic expertise capture through agent coordination rather than manual tool management.

**Human-AI Collaboration Framework**: Clear decision points for human creative oversight with autonomous agent coordination for operational workflow management, validated against actual C1M1 production requirements.

### Growth Features (Post-MVP)

**Epic 5: Unified Content Production Engine** 
- Create additional specialty agents via `bmad-agent-builder`: Vyond, Midjourney, CapCut specialists
- Multi-modal assembly coordination skills with cross-tool handoff workflows
- Style orchestration skill with brand consistency enforcement using style guide YAML

**Epic 6: LMS Platform Integration & Delivery**
- Create CourseArc specialist agent via `bmad-agent-builder` with LTI 1.3 compliance knowledge
- Enhanced Canvas specialist agent with grading passback and analytics capabilities
- Platform deployment skills with content format translation and SCORM packaging scripts

**Epic 7: Multi-Platform Intelligence Matrix**
- Platform allocation agent with four-platform decision intelligence (Canvas/CourseArc/Playbook/Qualtrics)
- Context-aware routing skills with platform-specific optimization references
- Handoff choreography patterns captured in coordination skills and agent memory

**Epic 8: Tool Review & Optimization Intelligence**
- Tool review agent with adaptive environment scanning and documentation monitoring skills
- Policy crystallization captured in agent memory sidecars and style guide YAML evolution
- Cost-benefit optimization recommendations through production intelligence reporting

### Vision (Future)

**Epic 9: Living Architecture Documentation System**
- Documentation agent with self-improving capability using BMad memory sidecar patterns
- Systematic knowledge crystallization through agent memory pattern analysis and consolidation
- Agent capability enhancement based on operational outcome analysis captured in chronology.md

**Epic 10: Strategic Production Orchestration** 
- Enhanced master orchestrator with predictive optimization skills based on accumulated production memory
- Complex dependency management through evolved coordination protocols and agent communication patterns
- Performance monitoring skills with systematic workflow improvement recommendations

**Vision Completion: Full Collaborative Intelligence Infrastructure**
- Complete "Party Mode on steroids" environment with persistent agent ecosystem using BMad memory sidecars
- Systematic creative expertise scaling through agent memory patterns across unlimited production scenarios  
- Platform-agnostic intelligence with comprehensive tool capability registry maintained by tool review agent

## User Journeys

### Primary User Journey - Juanl as Course Creator & System Orchestrator

**Opening Scene: From Syllabus to System**

Meet Juanl: Sitting with course outline, syllabus, and detailed notes mapping course modules to weekly lessons. All content must serve specific course-level and module-level learning objectives - no creative work can be arbitrary.

Current Emotional State: Excited about high-level instructional design and creative possibilities, but dreading the repetitive chores and trial-and-error frustration with constantly changing media authoring tools that have evolved since last use.

The Pain: Manual coordination of multiple tools, keeping track of "everything," remembering which features changed in which applications, and ensuring all content serves learning objectives.

**Rising Action: Agent Ecosystem Collaboration**

System Handoff: Agents take responsibility for staying current with tool capabilities and interface changes, routing work through production stages systematically, managing "everything" (version control, handoffs, quality gates), and applying course/module learning objectives to all content decisions.

Workflow Transformation: Juanl converses with master orchestrator like a trusted general contractor, focusing on creative direction and instructional strategy while the orchestrator manages all operational coordination and tool mastery behind the conversational interface.

**Climax: The Critical Success Moment**

Scene Production: A course design note describing a specific presentation scene gets transformed through multi-agent coordination:

1. Base slide creation (Content agent)
2. Text layer optimization (Copy agent) 
3. Photo-realistic or animated narrator integration (Visual agent)
4. Natural-sounding voiceover synthesis (Audio agent)
5. Perfect instructional graphics (Design agent)
6. B-roll enhancing transitions (Assembly agent)
7. Final export-ready package from Descript/CapCut (Coordination agent)

The Moment: Juanl reviews a complete, professional presentation sequence that matches the instructional vision perfectly - created through agent collaboration while he focused on strategic design decisions.

**Resolution: New Reality**

Transformed Capability: Course creation becomes systematic creative collaboration rather than manual tool juggling.

Multiple Content Types Mastered: Each content type (polls/surveys, quizzes with answer-level feedback, presentations, videos) has its own optimized step-by-step workflow managed by the agent ecosystem.

Continuous Improvement: Agents evolve policies and exemplars based on production experience and tool capability changes, keeping the system current without manual maintenance.

### Secondary User Journeys

**Agent Ecosystem "Users"**

Master Orchestrator Agent Journey: Receives course design requirements, coordinates specialist agents based on content type, manages quality gates and learning objective alignment, reports status and escalates strategic decisions to Juanl.

Specialist Agent Journey: Receives work from orchestrator with context from previous stages, applies learned policies and exemplars to specific tasks, performs peer review with other agents, contributes to system learning through performance feedback.

**System Roles Journey**

Juanl as System Administrator: API connectivity pre-checks before production runs, tool capability updates and integration maintenance, agent behavior refinement based on production outcomes.

Juanl as Quality Reviewer: Strategic design decision points during workflow, final approval before content publication, creative standard refinement for agent learning.

### Journey Requirements Summary

These journeys reveal needs for multi-content-type workflow orchestration (presentations, quizzes, polls, videos), learning objective alignment validation across all content, tool capability intelligence with automatic updates, multi-stage quality review (agent peer review + human strategic review), systematic policy and exemplar evolution based on experience, and production coordination with clear escalation paths for human decisions.

## Domain-Specific Requirements

### Compliance & Regulatory

**Educational Privacy**: FERPA compliance maintained through human review gates before any content reaches live classroom environments. No automated student data handling through agent workflows.

**Accessibility Standards**: WCAG 2.1 AA compliance enforced through agent quality control protocols and systematic accessibility verification across all generated content types.

**Content Standards**: Institutional content policies managed through human oversight rather than agent enforcement, with final approval required before classroom deployment.

### Technical Constraints

**API Reliability & Recovery**: Exponential fallback and retry mechanisms for all tool integrations (Canvas, Gamma, ElevenLabs, Vyond, etc.). Failed operations logged with timeout handling, while non-dependent production processes continue to completion.

**Agent Coordination Security**: Secure API key management across multiple tool integrations with audit trails for agent decision-making and content modifications. Version control for both content artifacts and agent coordination states.

**Multi-Platform Integration**: Canvas API rate limiting coordination among agents, CourseArc LTI 1.3 compliance for content delivery, and systematic handling of platform-specific deployment requirements.

### Integration Requirements

**Tool Ecosystem Coordination**: Seamless integration management across Gamma, ElevenLabs, Vyond, Canvas, CourseArc, Midjourney, CapCut, Descript with intelligent fallback when individual tools fail.

**Workflow State Persistence**: Maintain production run state across tool failures and system interruptions, enabling resumption without losing work or coordination context.

### Risk Mitigations

**Content Accuracy Liability**: Human review checkpoint before classroom deployment ensures educational content accuracy and institutional responsibility for agent-created materials.

**Brand Consistency Assurance**: Systematic enforcement of institutional standards through captured style guides and quality control agents, with human override for brand-critical decisions.

**Production Continuity**: Graceful degradation patterns that allow partial workflow completion when individual tool APIs fail, minimizing impact on overall production timelines.

## Innovation & Novel Patterns

### Detected Innovation Areas

**Core Innovation: Systematic Creative Expertise Crystallization**

This system pioneers the first **persistent collaborative intelligence infrastructure** that systematically captures, crystallizes, and scales human creative expertise through multi-agent coordination across production runs. Unlike automation (replacement) or copilots (assistance), this creates **collaborative creative intelligence** where agents become repositories of creative decision-making that execute at scale while preserving and enhancing human expertise.

**Novel Architecture Patterns:**
- **Agent-to-Agent Creative Collaboration**: Peer review protocols where agents evaluate each other's outputs against crystallized creative standards
- **Persistent Creative Memory**: Cross-run context that remembers creative decisions, their rationale, and effectiveness patterns
- **Systematic Expertise Evolution**: Agent learning mechanisms that refine creative decision-making based on production outcomes and tool capability changes

### Market Context & Competitive Landscape

**Category Creation**: No existing systems combine multi-agent orchestration with systematic creative expertise capture for content production workflows. Current AI tools operate as individual assistants rather than collaborative ecosystems with persistent creative intelligence.

**BMAD Builder Connection**: This system may pioneer concepts being explored in the BMAD Builder module direction - creating collaborative intelligence frameworks that scale human expertise rather than replacing it.

**Differentiation**: While creative automation tools exist (individual AI assistants for writing, design, video), no system orchestrates collaborative agent intelligence that learns and applies human creative expertise systematically across complex multi-tool workflows.

### Validation Approach

**Primary Validation: Course 1, Module 1 Recreation**
- Demonstrate agents applying systematic creative decisions rather than generic automation
- Evidence of quality improvements through multi-agent coordination and peer review
- Proof that agents remember and apply creative patterns from previous production runs

**Systematic Expertise Evidence:**
- Agents making tool choices consistent with captured creative reasoning
- Quality control agents applying learned standards automatically
- Production workflow improvements based on crystallized experience patterns

**Story Design/Development Will Address:**
- Specific mechanics of expertise crystallization capture
- Context and judgment preservation across agent learning cycles  
- Measurement frameworks distinguishing "crystallized expertise" from "automation"
- Adaptation mechanisms for applying successful patterns to new scenarios

### Risk Mitigation

**Innovation Fallback Strategy**: If systematic expertise crystallization proves more complex than anticipated, system still provides significant value as "intelligent automation" with sophisticated multi-agent coordination and tool integration.

**Quality Assurance**: Human review checkpoints prevent crystallization of ineffective patterns, with explicit override capabilities for creative decisions requiring contextual judgment.

**Adaptive Learning Controls**: System designed to evolve expertise patterns based on production outcomes while maintaining core creative quality standards through human oversight.

**Story Design/Development Will Address:**
- Mechanisms preventing crystallization of outdated or ineffective approaches
- Validation frameworks for measuring systematic expertise application effectiveness
- Evolution controls for maintaining creative standards while enabling intelligent adaptation

## Developer Platform Specific Requirements

### Project-Type Overview

**Multi-Agent Orchestration Platform**: Agents implemented as .md files following BMad patterns, packaged as a Cursor IDE plugin with native agent/skill auto-discovery. Python infrastructure provides supporting code for API clients, state management, and tool manipulation. Built using `bmad-agent-builder` six-phase conversational discovery process for agent creation.

### Technical Implementation Architecture

**Agent Implementation Model:**
- **Agents as .md files**: Custom agents defined in `agents/` directory with YAML frontmatter (name + description), following BMad SKILL.md standard with persona, activation, and capability routing
- **Skills as SKILL.md**: Tool-specific capabilities in `skills/{tool}/SKILL.md` directories with progressive disclosure via `references/` subfolder
- **Python infrastructure**: Supporting scripts in `scripts/` for API clients, state management, file operations, and deterministic operations requiring code execution
- **Cursor Plugin Packaging**: `.cursor-plugin/plugin.json` manifest with auto-discovery of agents, skills, rules, and MCP servers

**Agent Creation Methodology:**
- **BMad Agent Builder** (`bmad-agent-builder`): Six-phase conversational discovery process (Intent → Capabilities → Requirements → Draft → Build → Summary) for creating each custom agent
- **Quality Optimization**: Builder's quality scan system for structural validation and prompt craft optimization
- **Agent Memory System**: BMad sidecar pattern (`_bmad/memory/{skillName}-sidecar/`) for persistent agent learning with index.md, patterns.md, chronology.md, and access-boundaries.md

**Cursor IDE Integration:**
- **Plugin Structure**: Native Cursor plugin with agents/, skills/, rules/, commands/, hooks/ directories
- **Hooks System**: Cursor event hooks for production coordination (sessionStart → pre-flight, afterFileEdit → quality validation, sessionEnd → run reporting)
- **MCP Integration**: `.mcp.json` bundled in plugin for tool server definitions
- **Rules System**: `.cursor/rules/*.mdc` files for persistent agent behavior guidance

### Core Entity Model (Critical Architecture Component)

**Run-Defining Entities** (Beginning of Production Process):
- **Course Context Entity**: YAML file with overall course definition, learning objectives, brand guidelines, platform requirements
- **Module Context Entity**: YAML file with module-specific objectives, timeline, content types, assessment strategies  
- **Asset Specification Entity**: YAML file with individual content piece requirements, format specifications, quality criteria

**Runtime Coordination Entities** (Used/Updated During Production):
- **Production Run State**: SQLite database tracking workflow progress, agent assignments, quality gate status, coordination checkpoints
- **Agent Memory Sidecars**: BMad sidecar directories for each active agent with learned patterns and session context
- **Resource Version Tracking**: Git-versioned asset evolution history with creative decision audit trail

**Run Completion Entities** (Final Version-Controlled Updates):
- **Asset Release Manifest**: YAML file with final artifact specifications, deployment targets, quality certification
- **Process Learning Capture**: Agent sidecar pattern updates with workflow effectiveness patterns and optimization insights
- **Course/Module Memory Update**: Persistent sidecar context for future production runs and creative pattern crystallization

### Agent Communication Architecture

**Inter-Agent Coordination**: Agents invoke each other through orchestrator coordination using BMad skill routing patterns. Master orchestrator maintains conversation state and delegates to specialty agents via capability matching.

**Skills as Integration Bridge**: Skills provide the interface between agent reasoning (.md intelligence) and code execution (Python scripts for API calls, file operations, state management). Skills follow BMad progressive disclosure pattern with references/ for complex capabilities.

**State Persistence**: Hybrid YAML configuration (human-readable, git-versioned) + SQLite runtime coordination (ACID transactions) + BMad memory sidecars (agent learning persistence).

### Documentation & Examples Strategy

**Agent Behavior Configuration**: BMad Builder-generated agent .md files with persona, capabilities, and routing tables serving as self-documenting agent specifications.

**Workflow Template Repository**: Production process patterns for different content types (presentations, assessments, videos) defined as skills with step-by-step coordination workflows.

**Tool Integration Guides**: Skill-based documentation with parameter mastery references, context optimization patterns, and troubleshooting guidance.

## Project Scoping & Phased Development

### MVP Strategy & Philosophy

**MVP Approach:** Foundation-First Validation MVP - Establish robust infrastructure for agent coordination evolution while proving basic collaborative intelligence with simplified automation and systematic expertise capture through skills-based tool optimization.

**Strategic MVP Philosophy:** Automated foundation with human augmentation where complex automation isn't ready, skills-based tool expertise stewardship with basic agent coordination, and strong evolutionary architecture that can grow into full peer review protocols.

**Resource Requirements:** Single developer with Python/AI agent expertise, access to tool ecosystem (Gamma, ElevenLabs, Canvas), Cursor IDE optimization environment.

### MVP Feature Set (Phase 1 - Epics 1-4)

**Core User Journeys Supported:**
- Complete Course 1, Module 1 production run with agent coordination
- Basic tool integration with skills-based prompt optimization (Gamma expertise, ElevenLabs mastery)
- Human review checkpoints with automated quality components at each production stage
- Agent handoff protocols (simplified but functional) with workflow state persistence

**Must-Have Capabilities:**
- **Epic 1**: Repository environment with agent development infrastructure and MCP integration framework
- **Epic 2**: Master orchestrator with basic coordination protocols and simplified agent registry
- **Epic 3**: Core tool integrations (Gamma, ElevenLabs, Canvas) with skills-based tool expertise stewardship
- **Epic 4**: Workflow state persistence, production run management, and cross-run context memory
- **Quality Control**: Automated review components at every stage plus human oversight for complex creative decisions
- **Skills Framework**: Tool-specific expertise crystallization in modular, evolvable skills architecture

### Post-MVP Features

**Phase 2 (Growth - Epics 5-8):**
- Advanced agent peer review protocols (evolution from simplified coordination)
- Full quality control automation (reducing manual components)
- Multi-platform intelligence matrix with sophisticated tool selection reasoning
- Enhanced skills ecosystem with community-driven tool expertise and optimization patterns

**Phase 3 (Expansion - Epics 9-10):**
- Living architecture documentation with self-improving systems and automatic pattern extraction
- Strategic production orchestration with predictive optimization and resource allocation intelligence
- Complete collaborative intelligence infrastructure with platform-agnostic tool capability registry

### Risk Mitigation Strategy

**Technical Risks:** Simplified agent coordination might not scale to full collaborative intelligence
**Mitigation:** Strong architectural foundation designed for evolution, skills-based modularity enables incremental sophistication

**Quality Risks:** Hybrid manual/automated quality control might not maintain creative standards
**Mitigation:** Automated components at every stage provide consistency baseline, human oversight ensures quality gates

**Innovation Risks:** Systematic expertise capture might not emerge from simplified MVP architecture
**Mitigation:** Skills framework serves as expertise crystallization foundation, demonstrable through tool optimization effectiveness

## Functional Requirements

### Agent Orchestration & Coordination
- FR1: Master orchestrator can coordinate multiple specialist agents through production workflows
- FR2: Agents can communicate with each other through event-driven messaging protocols  
- FR3: Agents can register their capabilities and availability in the coordination registry
- FR4: Master orchestrator can assign tasks to agents based on capability matching
- FR5: Agents can report task completion and status updates to the coordination system
- FR6: System can manage agent dependencies and handoff protocols between production stages

### Production Workflow Management  
- FR7: Users can initiate production runs for course modules with context specification
- FR8: System can maintain production run state across tool failures and interruptions
- FR9: System can track workflow progress through multiple coordinated stages
- FR10: Users can review and approve work at designated human checkpoint gates
- FR11: System can manage cross-run context and memory for course consistency
- FR12: Users can access production run history and audit trails
- FR33: Users can export completed content to target platforms (Canvas, CourseArc, Panopto) with platform-specific formatting
- FR34: System can manage learning objectives alignment across all content production decisions  
- FR35: Users can configure run presets (explore, draft, production, regulated) with parameter overrides

### Tool Integration & API Management
- FR13: System can integrate with external tools through MCP, direct API connections, and local filesystem access
- FR14: System can verify API connectivity before production runs begin
- FR15: Agents can manipulate tools (Gamma, ElevenLabs, Canvas, Notion) through standardized interfaces
- FR16: System can handle tool API failures with retry mechanisms and graceful degradation
- FR17: System can manage API keys and authentication across multiple tool integrations

### Skills & Expertise Management
- FR18: System can store and evolve skills for tool-specific expertise (Gamma prompts, ElevenLabs optimization)
- FR19: Agents can access and apply skills for specialized tool interactions  
- FR20: System can capture and crystallize creative decision patterns through skills evolution
- FR21: Users can review and refine skills based on production outcomes
- FR22: System can version control skills and track effectiveness improvements
- FR42: System can analyze and recommend tool optimization strategies based on production outcome patterns
- FR43: System can detect and suggest workflow improvements through systematic experience analysis
- FR44: Users can access systematic expertise insights and creative pattern recommendations

### Quality Control & Review
- FR23: Agents can perform automated quality review at each production stage
- FR24: System can enforce quality standards through configurable validation rules
- FR25: Agents can conduct peer review of other agents' outputs against creative standards
- FR26: Users can override quality decisions when creative judgment is required
- FR27: System can maintain quality audit trails for production accountability
- FR48: System can provide comprehensive audit trails for compliance and quality assurance reporting
- FR49: Users can configure accessibility standards enforcement across all content production workflows

### Content & Asset Management
- FR28: System can manage course, module, and asset context entities throughout production
- FR29: System can track asset evolution history and creative decision rationale
- FR30: Users can define and update brand guidelines, style standards, and creative policies  
- FR31: System can ensure content accessibility and compliance with educational standards
- FR32: System can generate release manifests for final content deployment
- FR45: Agents can maintain creative consistency across multiple content types within the same course module
- FR46: System can provide creative decision rationale tracking for learning objective alignment  
- FR47: Users can access creative pattern libraries built from successful production runs

### System Infrastructure & Development
- FR36: System can manage the core entity model (Course Context, Module Context, Asset Specification entities) with version control
- FR37: System can provide real-time coordination state visibility for debugging and monitoring agent interactions
- FR38: System can backup and restore production run states for disaster recovery
- FR39: Developers can set up the development environment with automated dependency and API verification
- FR40: System can provide development mode with enhanced logging and debugging capabilities for agent coordination
- FR41: Users can validate system configuration before initiating production runs

### Production Intelligence & Reporting
- FR50: System can generate comprehensive production run reports including purpose achievement, stage effectiveness, and optimization recommendations
- FR51: Users can access comparative analysis between production runs to track workflow improvement patterns  
- FR52: System can automatically identify workflow bottlenecks and suggest optimization strategies based on run performance data

### Conversational Orchestrator Interface
- FR53: Users can initiate production runs through natural language conversation with master orchestrator
- FR54: Master orchestrator can request user input, confirmation, and direction through conversational prompts
- FR55: Users can provide information, address problems, and confirm actions through direct conversation with orchestrator
- FR56: Master orchestrator can present work products for user review and incorporate feedback through conversational interaction  
- FR57: Users can monitor and direct production run progress through continuous dialogue with orchestrator
- FR58: System can provide conversational interface for all user interactions with master orchestrator
- FR59: Master orchestrator can manage conversation flow including requests, confirmations, and reviews
- FR60: Users can access all system capabilities through natural language conversation with orchestrator

### Parameter Intelligence & Tool Mastery
- FR61: Specialty agents can master complete tool API/MCP parameter sets including all control options and value ranges
- FR62: Orchestrator can elicit tool parameters through conversational education when not previously established
- FR63: System can store parameter decisions in human-readable style guide format organized by course/project context
- FR64: Specialty agents can determine optimal parameters through runtime elicitation, style guide defaults, and prior run patterns
- FR65: Users can provide exemplar-based parameter guidance that agents apply to similar contexts with intelligent inference

### Pre-Flight Check & Tool Validation
- FR66: Users can invoke pre-flight system validation through conversational request to master orchestrator
- FR67: System can verify MCP connectivity, API authentication, and tool availability before production runs
- FR68: System can scan current tool documentation to detect API changes, new capabilities, or status modifications
- FR69: Pre-flight check can identify potential issues and provide resolution guidance before production workflow initiation
- FR70: System can update tool capability knowledge and parameter catalogs based on documentation intelligence scanning

### Source Wrangling & External Reference Integration
- FR71: System shall integrate with Notion API to read course development notes by database or page reference
- FR72: System shall support writing feedback (readiness assessments, design recommendations) back to Notion pages
- FR73: System shall read source materials from a configured local Box Drive path
- FR74: System shall provide a source wrangling capability that pulls reference materials from configured external sources (Notion, Box Drive, future sources) into the production context

### Run Mode Management
- FR75: Master Orchestrator shall support a binary ad-hoc/default mode switch, settable and reportable via natural language conversation
- FR76: In ad-hoc mode, all state-tracking writes (SQLite, YAML config, memory sidecars) shall be suppressed or redirected to scratch state
- FR77: In ad-hoc mode, all produced assets shall route to a designated scratch/staging area separate from production paths
- FR78: Quality assurance actions shall execute regardless of the current run mode
- FR79: Mode switch shall persist within a session until explicitly changed by the user
- FR80: System shall support future evolution to a per-level (course/module/lesson/asset) modality matrix with additional modes (write-only, read-only)

### Agent Governance & Authority (Added 2026-03-28)
- FR81: System shall maintain an explicit run baton for every active production run, containing run_id, orchestrator identity, current gate, invocation_mode, allowed delegate graph, escalation target, and blocking authority
- FR82: During an active production run, every specialist agent shall check the run baton before performing user-facing actions — if the user invokes a specialist directly during a Marcus-led run, the default behavior shall redirect to Marcus unless the user explicitly enters standalone consult mode
- FR83: Every delegated context envelope shall carry invocation_mode (delegated/standalone), current_gate, authority_chain, decision_scope, and allowed_outputs — specialists shall not expand beyond the specified scope
- FR84: System shall maintain a single authoritative lane matrix defining which agent owns which judgment dimension — orchestration, instructional design, tool execution, perception, fidelity verification, and quality assessment shall each have exactly one owner
- FR85: Specialist agents shall not report authoritative judgment on dimensions outside their lane — tool specialists report execution quality only (layout integrity, parameter confidence, embellishment risk), not content fidelity or pedagogical alignment
- FR86: The lane matrix shall be maintained as a central document and briefly restated in each specialist's SKILL.md to ensure local awareness matches global authority
- FR87: Every agent revision shall pass a mandatory quality scan (structure, prompt craft, cohesion, execution efficiency, script opportunities) before acceptance — agent QA is a release gate, not optional
- FR88: Sensory bridge perception results shall be computed once per artifact per production run and cached — both the Fidelity Assessor and Quality Reviewer shall consume the same canonical perception output, never performing independent interpretation passes
- FR89: System shall provide observability hooks for gate pass rates, fidelity scores (O/I/A counts), quality trends, and agent performance metrics to support production intelligence reporting
- FR90: Lane boundary violations detected during production runs shall be logged as governance findings and surfaced in run reports for systematic remediation
- FR91: System shall enforce ad-hoc run mode as a ledger and learning boundary — observability and cache records shall carry `run_mode` (`default` | `ad-hoc`) so sandbox runs are excluded from course/module building progress metrics; coordination databases, production run completion, quality-gate persistence, and durable sidecar learning (`patterns.md`, `chronology.md`) shall not treat ad-hoc runs as institutional production progress unless explicitly redesigned and documented

## Non-Functional Requirements

### Performance

**Agent Coordination Response Times:**
- Agent-to-agent communication handoffs complete within 5 seconds under normal conditions
- Tool API calls (Gamma, ElevenLabs, Canvas) timeout after 30 seconds before triggering retry mechanisms
- Production run status updates provided to user within 10 seconds of stage completion
- Quality review checkpoints present results within 15 seconds for human decision-making

**Production Run Performance:**
- Complete Course 1, Module 1 recreation completes within 45 minutes for standard complexity content
- Individual production stages (slide creation, voiceover generation, etc.) complete within 10 minutes per asset
- System startup and environment verification complete within 2 minutes

### Integration

**API Reliability Standards:**
- Tool API failure rate maintained below 5% during production runs
- Exponential backoff retry mechanism: 3 attempts with 2s, 4s, 8s delays before escalation to human intervention
- API connectivity verification achieves 100% success rate during pre-production checks
- Critical integrations (Gamma, ElevenLabs, Canvas) maintain 95% availability during standard business hours

**Integration Resilience:**
- System continues production workflow when non-critical tool integrations fail temporarily
- API rate limiting compliance prevents service disruptions across all integrated platforms
- Integration failures logged with sufficient detail for troubleshooting and optimization

### Security

**API Key & Credential Management:**
- All API keys stored in encrypted .env files with restricted file system permissions
- API keys never logged in plain text or included in audit trails
- Tool authentication tokens refreshed automatically before expiration
- System access logs maintain 30-day retention for security audit purposes

**Content & Data Protection:**
- Production run data encrypted at rest using AES-256 encryption
- Agent coordination state information protected from unauthorized access
- Temporary files created during production runs automatically cleaned up after completion

### Accessibility

**Content Output Standards:**
- All generated content meets WCAG 2.1 AA compliance requirements automatically
- Visual assets include descriptive alt-text generated and validated by quality review agents
- Color contrast ratios maintain 4.5:1 minimum for normal text, 3:1 for large text
- Generated audio content includes synchronized captions and transcripts

**Accessibility Validation:**
- Automated accessibility scanning integrated into quality review workflows
- Manual accessibility verification checkpoints for complex multimedia content
- Accessibility compliance reporting available for institutional audit requirements

### Reliability

**System Availability:**
- Development environment maintains 99% availability during planned working hours
- Production run failure rate below 5% due to system issues (excluding external API failures)
- Agent coordination system recovers automatically from individual agent failures within 30 seconds
- Backup and recovery capabilities restore production run state within 5 minutes of system restart

**Error Handling:**
- Graceful degradation when individual tools become unavailable during production runs
- Clear error messages provided to user with actionable recovery suggestions
- Agent coordination failures escalated to human oversight with sufficient context for resolution