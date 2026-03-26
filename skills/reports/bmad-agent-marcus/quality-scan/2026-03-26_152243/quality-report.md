# Quality Report: bmad-agent-marcus

**Scanned:** 2026-03-26T15:22:43
**Skill Path:** skills/bmad-agent-marcus
**Report:** skills/reports/bmad-agent-marcus/quality-scan/2026-03-26_152243/quality-report.md
**Performed By** QualityReportBot-9001

## Executive Summary

- **Total Issues:** 25
- **Critical:** 0 | **High:** 2 | **Medium:** 11 | **Low:** 12
- **Overall Quality:** Good
- **Overall Cohesion:** Cohesive
- **Craft Assessment:** Well-crafted workflow-facilitator — strong persona voice, exemplary intelligence placement, good progressive disclosure

Marcus is a veteran executive producer orchestrator for health sciences and medical education content with exceptional persona-capability alignment and deeply embedded domain expertise. The architecture demonstrates strong progressive disclosure across 8 self-contained reference files, a sophisticated memory sidecar system, and exemplary separation of deterministic operations (scripts) from judgment operations (prompts). The most significant operational gaps are that external skill and specialist agent dependencies are referenced but unvalidated, and the mode state verification script always returns hardcoded defaults rather than actual state.

### Issues by Category

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Structure & Capabilities | 0 | 0 | 3 | 3 |
| Prompt Craft | 0 | 0 | 1 | 4 |
| Execution Efficiency | 0 | 0 | 2 | 2 |
| Path & Script Standards | 0 | 2 | 2 | 0 |
| Agent Cohesion | 0 | 0 | 3 | 3 |
| Creative (opportunity levels) | — | — | 6 | 24 |

---

## Agent Identity

- **Persona:** Veteran executive producer for health sciences and medical education content — a calm, experienced orchestrator who coordinates multi-agent production workflows, manages human checkpoints, and ensures educational artifacts meet professional and accreditation standards.
- **Primary Purpose:** Single conversational point of contact for medical education course content production, bridging user intent to specialist execution through structured workflows, quality gates, and persistent learning.
- **Capabilities:** 19

---

## Strengths

*What this agent does well — preserve these during optimization:*

**Persona & Identity Design**
- **Exemplary persona-capability alignment.** Marcus's identity as a veteran executive producer maps precisely to what he does: orchestrate, delegate, manage checkpoints, report progress, and enforce quality. The persona doesn't promise abilities the capability set can't deliver, and the "Does Not Do" section explicitly excludes code, tests, git, and API work — drawing a clean orchestrator boundary. *(agent-cohesion)*
- **Deep medical education domain embedding.** Marcus speaks the language of medical education: Bloom's taxonomy, backward design, clinical case integration, assessment-objective tracing, LCME/ACGME accreditation awareness. This domain knowledge is woven into Identity, Communication Style, Principles, and checkpoint quality criteria — not bolted on. A faculty user would immediately feel Marcus understands their world. *(agent-cohesion)*
- **Communication Style section is high-quality persona craft.** Eight detailed bullet points with concrete example utterances precisely calibrate Marcus's voice: lead-with-context, options-with-recommendations, natural progress reporting, appropriate urgency, domain-native vocabulary, unambiguous mode confirmations. Each bullet includes a worked example. This is load-bearing persona voice that directly instructs the LLM on output style. *(prompt-craft)*

**Architecture & Design Patterns**
- **Context envelope pattern for specialist delegation.** The specialist handoff protocol defines a consistent context envelope (outbound: run ID, content type, scope, learning objectives, constraints, style bible sections, exemplar refs; inbound: artifact path, quality self-assessment, parameter decisions, status). This provides a clean, repeatable interface contract for all specialist agents, making the delegation pattern scalable. *(agent-cohesion)*
- **Mode management with hard enforcement boundaries.** The default/ad-hoc mode system gives faculty a safe experimentation sandbox without polluting production state while maintaining QA in both modes. Enforcement rules are explicit: no state writes in ad-hoc, no production routing, no pattern learning. Mode switch confirmations are unambiguous. *(agent-cohesion)*
- **Sophisticated memory system with mode-aware write discipline.** The sidecar architecture (index.md, access-boundaries.md, patterns.md, chronology.md) is well-structured. Mode-aware write rules prevent ad-hoc experimentation from corrupting learned patterns. The principle that style bible content is never cached in memory prevents stale reference drift. *(agent-cohesion)*
- **Asset-lesson pairing invariant is a strong quality guardrail.** The non-negotiable rule that every educational artifact must be paired with instructional context prevents orphaned assets. This reflects real medical education accreditation requirements where traceability is essential. *(agent-cohesion)*

**Prompt Engineering Quality**
- **Exemplary intelligence placement between scripts and prompts.** Deterministic operations (production plan generation, state reading) are correctly placed in scripts. Judgment operations (intent parsing, quality gate decisions, specialist routing, user interaction) remain in prompts. Textbook correct placement for a workflow-facilitator agent. *(prompt-craft)*
- **Strong self-containment across all reference files.** All 8 reference files have their own Purpose section, sufficient domain context, and can function independently if SKILL.md drops from context. No reference file requires SKILL.md presence to make sense. This is the correct pattern for progressive disclosure. *(prompt-craft)*

**User Experience Bright Spots** *(from user journey analysis)*
- Warm greeting with name and clear next-step offer creates a personal first impression
- Source prompting ("want me to pull your Notion notes?") is immediately useful for first-timers
- Memory-based session continuity means Marcus picks up where experts left off
- Never guesses — asks clarifying questions instead of assuming, which protects confused users
- Error handling protocol is well-designed: inform, suggest alternatives, adjust plan, never fail silently
- Quality gates provide natural teaching moments about content standards
- Architecture cleanly supports future headless mode (agent/specialist/API layers separated)

---

## Truly Broken or Missing

*Issues that prevent the agent from working correctly:*

**HIGH-1** | `scripts/generate-production-plan.py` + `scripts/read-mode-state.py` | **uv not found on PATH — cannot run ruff for Python linting**
*(scripts scanner — affects both Python scripts)*

Both Python scripts cannot be linted because `uv` is not available on the system PATH. This prevents automated code quality checks via ruff.

**Action:** Install uv: https://docs.astral.sh/uv/getting-started/installation/

---

## Detailed Findings by Category

### 1. Structure & Capabilities

**Agent Metadata:**
- Sections found: Overview, Identity, Communication Style, Principles, Does Not Do, On Activation, Capabilities, Internal Capabilities, External Skills, External Specialist Agents
- Capabilities: 19
- Memory sidecar: Yes (`memory/bmad-agent-marcus-sidecar/index.md`)
- Headless mode: No
- Structure assessment: Well-structured agent with comprehensive memory system, strong domain-specific identity, and excellent communication style examples. Primary gaps are operational: external skill/agent dependencies are unvalidated, and access boundary loading is implicit rather than explicit.

#### Medium

**S-M1** | `SKILL.md:50` | **Access boundaries not explicitly loaded in On Activation sequence**
*(category: consistency)*

memory-system.md declares access-boundaries.md with "Load on activation" and states "On every activation, load these boundaries first. Before any file operation, verify the path is within allowed boundaries." However, the On Activation sequence in SKILL.md (lines 52-66) loads config → memory index → state → greet without explicitly mentioning access-boundaries.md. This creates a gap: if index.md doesn't explicitly point to access-boundaries.md, the boundaries may not be loaded on first run where init.md creates the file but the activation flow branches to init.md instead of the normal memory load path.

**Action:** Add an explicit step in On Activation to load access-boundaries.md from the memory sidecar (or from memory-system.md inline definition) before any state reads or file operations. Place it immediately after loading index.md.

**S-M2** | `SKILL.md:81` | **External Skills reference 5 unvalidated target skills**
*(category: capability-completeness)*

The External Skills table references pre-flight-check, production-coordination, run-reporting, parameter-intelligence, and source-wrangling. These are core to Marcus's production workflow (connectivity checks, state management, reporting, style elicitation, source material retrieval). If these skills do not exist, Marcus cannot execute multi-agent production workflows as designed. No validation that these targets are built or stubbed.

**Action:** Build or stub these 5 skills, or add explicit "Status: planned" annotations to the External Skills table so Marcus can gracefully degrade when they are unavailable.

**S-M3** | `SKILL.md:91` | **External Specialist Agents reference 6 active + 2 future unvalidated agents**
*(category: capability-completeness)*

The External Specialist Agents table references gamma-specialist, elevenlabs-specialist, canvas-specialist, content-creator, quality-reviewer, and assembly-coordinator as active dependencies, plus qualtrics-specialist and canva-specialist as future. The 6 active agents are listed without availability status.

**Action:** Validate that the 6 active specialist agents exist and are callable. Add a "Status" column to the table (active/planned/future) so Marcus can route around unavailable specialists during production planning.

#### Low

**S-L1** | `SKILL.md:16` | **Identity section mixes persona definition with domain knowledge enumeration**
*(category: identity)*

The identity opens with a strong one-sentence persona but then extends into a domain knowledge inventory (Bloom's taxonomy, LCME, ACGME, etc.) and a role relationship statement. The blending makes the persona less immediately graspable.

**Action:** Consider separating into a focused one-sentence persona followed by a "Domain Expertise" subsection. Low priority — current form is functional and effective.

**S-L2** | `SKILL.md:0` | **No bmad-skill-manifest.yaml present**
*(category: structure)*

Other BMAD agents in the workspace include a bmad-skill-manifest.yaml for metadata and discoverability. bmad-agent-marcus does not have one, creating inconsistency with the agent cohort.

**Action:** Add a bmad-skill-manifest.yaml if it is part of the standard BMAD agent structure. If intentionally omitted, document why.

**S-L3** | `SKILL.md:33` | **High principle count (10) may increase token pressure in long sessions**
*(category: principles)*

All 10 principles are domain-specific and high quality. However, principles 3/4/5 all address quality/rigor from different angles and could potentially be consolidated. Similarly, principles 9/10 both address reference consultation. At 10 principles, the section consumes meaningful token budget on every activation.

**Action:** Consider consolidating to 7-8 principles by merging related quality/rigor principles and reference consultation principles. Low priority — current principles are all actionable and domain-specific.

### 2. Prompt Craft

**Agent Assessment:**
- Agent type: workflow-facilitator
- Overview quality: appropriate
- Progressive disclosure: good
- Persona context: appropriate
- SKILL.md is 105 lines / ~2395 tokens — lean but functional for a complex orchestrator. Progressive disclosure to 8 reference files and 2 scripts is well-executed. Persona voice is rich and load-bearing. Overview establishes who/what/how/why but could benefit from 1-2 additional sentences covering the mode system and memory architecture.

**Prompt Health:** 1/8 with config header | 0/8 with progression conditions | 8/8 self-contained

#### Medium

**P-M1** | `SKILL.md:10` | **Overview slightly lean for orchestrator complexity**
*(category: under-contextualization)*

Overview is ~3 sentences plus a reference-library note and Args line (~7 content lines). For a complex persona-driven orchestrator managing two run modes, a memory sidecar system, multi-specialist delegation, style-bible/exemplar integration, and source-material prompting, the overview could benefit from 1-2 additional sentences explicitly surfacing the mode system and memory concepts. Currently the LLM must read to On Activation (line 50) before encountering mode/memory, which delays scope comprehension.

**Action:** Add 1-2 sentences to the overview mentioning the default/ad-hoc mode boundary and the sidecar memory system. Target ~10 overview sentences to match the agent's complexity tier.

#### Low

**P-L1** | `SKILL.md:12` | **Style-bible/exemplar re-read-from-disk instruction repeated 5 times**
*(category: token-waste)*

The "always re-read from disk, never cache" instruction appears in: SKILL.md overview (line 12-13), Principle 10 (line 44), Does Not Do (line 48), memory-system.md (line 7), and checkpoint-coord.md (line 26). Five occurrences across the agent surface. The three occurrences within SKILL.md itself are redundant since they always load together.

**Action:** Consolidate to one strong statement in Overview or Principles within SKILL.md. Keep the repetition in memory-system.md and checkpoint-coord.md for self-containment.

**P-L2** | `references/save-memory.md:1` | **YAML frontmatter present only in save-memory.md**
*(category: structural-inconsistency)*

save-memory.md has YAML frontmatter (name, description, menu-code) while all other reference files use plain markdown with a Purpose section. Suggests different source or template.

**Action:** Either add consistent frontmatter to all reference files or remove frontmatter from save-memory.md and rely on the Capabilities table in SKILL.md for the menu-code mapping.

**P-L3** | `references/conversation-mgmt.md:39` | **Hardcoded path for course context YAML**
*(category: brittleness)*

Line 39 references `state/config/course_context.yaml` as a literal path. The generate-production-plan.py script resolves this path dynamically, but the prompt text embeds it as a fixed string. If the project structure changes, the prompt text drifts from the script's resolution logic.

**Action:** Reference the path using a config variable or note that the script handles resolution.

**P-L4** | `references/memory-system.md:22` | **Access boundaries embedded in memory-system.md rather than standalone**
*(category: progressive-disclosure)*

The access-boundaries section (lines 22-57) is a critical security construct — deny zones, mode-aware write permissions, boundary verification on every file operation. It's embedded as a subsection of memory-system.md rather than being a standalone reference. Given that access-boundaries.md is also a sidecar file created at init, having the specification embedded creates a layering question: is memory-system.md the source of truth, or is the generated access-boundaries.md?

**Action:** Consider extracting access boundaries into a standalone reference (access-boundaries-spec.md) that serves as the canonical specification. Low priority since current structure is functional.

### 3. Execution Efficiency

#### Medium

**E-M1** | `SKILL.md:59` | **Eager full-directory loading of style-bible and exemplars on every activation**
*(category: resource-loading)*

On Activation reads the entire resources/style-bible/ and resources/exemplars/ directories fresh on every activation, even when the user intent is a non-production task (status check, mode switch, memory save). These directories can grow large. The conversation-mgmt.md reference (line 68) already specifies passing "relevant style bible sections (matched to specialist domain)" to specialists — showing that selective access is the intended downstream usage.

**Action:** Defer style-bible and exemplar loading to the CM capability when production planning begins, or to HC when quality criteria are needed. Add a note in On Activation: "Style bible and exemplars are read fresh when production planning or quality review requires them — not on activation."

**E-M2** | `references/conversation-mgmt.md:72` | **Specialist return format specified as narrative prose instead of structured schema**
*(category: delegation-format)*

The Specialist Handoff Protocol describes the expected inbound return from specialists as prose bullets. For an orchestrator that processes many specialist returns to route workflows, a structured format specification would reduce parsing ambiguity and enable consistent downstream processing.

**Action:** Define an explicit structured return contract. Example: `{ artifact_path: string, quality_assessment: {passed: bool, notes: string[]}, parameter_decisions: object[], status: enum(completed|blocked|failed), issues: string[] }`.

#### Low

**E-L1** | `SKILL.md:52` | **Sequential activation reads where four independent operations could be batched**
*(category: parallelization)*

The On Activation sequence lists these as implicitly sequential: (1) load config, (2) load sidecar memory index.md, (3) load memory-system.md reference, (4) run read-mode-state.py. Steps 1, 3, and 4 are fully independent of each other and of step 2 (which has a conditional branch to init.md).

**Action:** Restructure into two groups: a parallel batch (config files, memory-system.md reference, mode state script) and a sequential follow-up (sidecar index.md → conditional init.md).

**E-L2** | `references/checkpoint-coord.md:26` | **Quality criteria re-reads entire style-bible per review gate without section targeting**
*(category: resource-loading)*

Checkpoint coordination states quality criteria sources are "both re-read fresh for each review gate" referring to the full style-bible directory. Each review gate loads the entire style bible rather than sections relevant to the artifact under review.

**Action:** Scope reads to sections relevant to the artifact type and specialist domain. The outbound context envelope already identifies "relevant style bible sections" — apply the same selectivity for checkpoint evaluation.

### 4. Path & Script Standards

**Script Inventory:** 2 scripts (Python: 2) | Missing tests: none detected

#### High

**PS-H1** | `scripts/generate-production-plan.py` + `scripts/read-mode-state.py` | **uv not found on PATH — cannot run ruff for Python linting**
*(category: lint-setup — see Truly Broken section)*

#### Medium

**PS-M1** | `scripts/generate-production-plan.py:1` | **No json.dumps found — output may not be structured JSON**
*(category: agentic-design)*

**Action:** Use json.dumps for structured output parseable by workflows.

**PS-M2** | `scripts/read-mode-state.py:1` | **No json.dumps found — output may not be structured JSON**
*(category: agentic-design)*

**Action:** Use json.dumps for structured output parseable by workflows.

### 5. Agent Cohesion

**Cohesion Analysis:**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Persona Alignment | strong | Marcus's identity maps precisely to the capability set. Every internal capability maps to what an orchestrator should do. The "Does Not Do" section reinforces the boundary. Medical education domain knowledge is embedded throughout, not bolted on. |
| Capability Completeness | mostly-complete | Core production workflow is well-covered. Main gaps at lifecycle boundaries: how a run formally closes, how past production feeds into future production. Missing: run closure/finalization, curriculum-level planning, content search/reuse, revision workflows. |
| Redundancy Level | clean | CM could be split rather than consolidated — it bundles four concerns (conversation mgmt, intent parsing, production planning, specialist orchestration) that might benefit from being two capabilities. |
| External Integration | intentional | 13 external references. Clean separation between workflow tools (5 external skills) and content producers (6 active + 2 future specialist agents). Context envelope provides consistent interface contract. |
| User Journey | mostly-complete | Faculty can accomplish meaningful end-to-end content production. Gaps at lifecycle edges: finalizing completed runs, revising old content, leveraging past production. These don't create dead-ends but rather soft edges. |

#### Medium

**C-M1** | `references/conversation-mgmt.md` | **CM capability is overloaded — four distinct concerns in one reference**
*(category: gap)*

CM bundles conversation management, intent parsing, production planning, workflow orchestration, AND specialist handoff protocol into a single reference file. These are at least three distinct operational concerns. The reference is the longest and most complex, creating a single point of failure.

**Action:** Consider splitting CM into at least two capabilities: "IP" (Intent Parsing & Conversation Management) and "PP" (Production Planning & Specialist Orchestration). This would improve selective loading and reduce blast radius.

**C-M2** | `scripts/read-mode-state.py` | **Mode state script doesn't actually track run mode (default vs ad-hoc)**
*(category: misalignment)*

read-mode-state.py returns a hardcoded `'mode': 'default'` and never queries the database for actual mode state. mode-management.md says to "invoke ./scripts/read-mode-state.py to verify" after a mode switch, but the script cannot verify anything. The actual mode appears to be tracked only in the memory sidecar's index.md.

*(Cross-ref: also identified by enhancement-opportunities scanner as low-opportunity finding)*

**Action:** Either (a) add a mode column to the SQLite coordination.db and have the script read it, (b) have the script read the mode from the memory sidecar index.md, or (c) update mode-management.md to remove the script verification reference.

**C-M3** | `SKILL.md` | **No explicit production run closure or finalization lifecycle stage**
*(category: gap)*

The production workflow covers intake → plan → delegate → review → approve, but there's no explicit "close run" or "finalize and deliver" capability. What happens after the last checkpoint approval? No orchestrator-level finalization step archives the run, confirms delivery, or triggers chronology/pattern updates.

**Action:** Add a lightweight "RF" (Run Finalization) capability or extend CM to include a close-out protocol: confirm all assets delivered, update chronology, trigger pattern extraction, archive run state, present summary to user.

#### Low

**C-L1** | `references/conversation-mgmt.md` | **No curriculum-level or batch production planning**
*(category: gap)*

Marcus can plan production for individual content items but there's no capability for planning at the module or semester level. A faculty user preparing an entire module would need coordinated multi-item production plans with dependency ordering across lessons.

**Action:** Consider adding a "curriculum planning" mode or extending production planning to handle multi-item requests with inter-item dependency awareness.

**C-L2** | `SKILL.md` | **No content search or reuse capability**
*(category: gap)*

No explicit capability for searching previously produced assets for reuse or adaptation. The memory sidecar tracks production history (chronology.md) but there's no search or retrieval interface for past artifacts.

**Action:** Consider adding a content discovery capability that can search course-content/ for existing assets by content type, module, topic, or learning objective.

**C-L3** | `references/checkpoint-coord.md` | **No revision workflow for previously-approved content**
*(category: gap)*

Checkpoint coordination handles the approve/revise/reject cycle during initial production but there's no documented workflow for revising content that was previously approved and delivered. The current model assumes production runs produce new content.

**Action:** Document a revision workflow: how to initiate a revision of existing approved content, how to version it, and how revision context is passed to specialists.

**Creative Suggestions:**

**CS-1** | `SKILL.md` | **Separate future specialist agents from current ones in the table**

The External Specialist Agents table mixes currently available agents with future/planned ones using inline "Future:" labels. This could confuse the LLM during activation — it might attempt to delegate to a nonexistent specialist.

**Action:** Split the table into "Available Specialist Agents" and "Planned Specialist Agents" or add an explicit "Status" column.

**CS-2** | `references/source-prompting.md` | **Source prompting could integrate with content-creator for automatic context enrichment**

Currently, source prompting offers to pull materials before production, and the retrieved materials are manually incorporated. When content-creator is invoked, Marcus could automatically attach previously-pulled source materials for the target lesson without requiring user confirmation each time.

**Action:** Consider a "smart source attachment" behavior: if materials were already pulled for a lesson during a prior session, automatically include them in the specialist context envelope with a brief mention.

**CS-3** | `SKILL.md` | **No multi-user collaboration or handoff capability**

Marcus assumes a single user. In real medical education departments, multiple faculty may collaborate on a course. There's no concept of delegating review checkpoints to a different faculty member or sharing production state.

**Action:** For a future version, consider a lightweight collaboration model: named reviewers at checkpoint gates, production run ownership, and the ability to share run status.

### 6. Creative (Edge-Case & Experience Innovation)

**Agent Understanding:**
- **Purpose:** Single conversational point of contact for health sciences / medical education course content production. Coordinates multi-agent workflows, delegates to specialist agents, manages human checkpoint gates, enforces quality standards, and learns from production runs — all while hiding system complexity behind conversational ease.
- **Primary User:** Medical education faculty member who is the domain expert and creative director. They understand medical education deeply but shouldn't need to understand production orchestration, specialist agents, or state management.
- **Key Assumptions:**
  - User has or will create a style bible and exemplar library before meaningful production begins
  - User is fluent in medical education vocabulary (Bloom's taxonomy, backward design, LCME/ACGME, etc.)
  - Production requests map neatly to one of 8 predefined content types
  - Production follows a linear forward-only workflow through sequential stages
  - One course context is active at a time — no multi-course parallel work
  - The user is available for checkpoint gates within a reasonable timeframe
  - Specialist agents are available and responsive when invoked
  - Source materials (Notion, Box Drive) are organized enough to retrieve programmatically
  - Context window is sufficient for the full production lifecycle of a single content artifact
  - The user always wants to produce something (vs. review, plan, or explore)

**Enhancement Findings:**

#### High Opportunity

**EH-1** | `references/init.md` | **First-run onboarding asks 5 questions before delivering any value**

Init discovery asks for user name, course context, style bible, exemplar library, and tool availability before Marcus can do anything. A first-timer who just wants to try Marcus hits an interrogation wall. They likely have none of this infrastructure yet.

**Action:** Add a "quick start" path: detect empty infrastructure and offer a zero-config demo flow. "I see this is your first time. Want me to walk you through a sample production run so you can see how I work, or would you prefer to set up your course structure first?"

**EH-2** | `SKILL.md` | **No mechanism to promote ad-hoc output to production**

Ad-hoc mode routes everything to course-content/staging/ad-hoc/. If a user experiments in ad-hoc mode, produces something they love, and says "actually, let's use this for real" — there is no documented path to promote the asset. The user is told to switch modes and reproduce the work.

**Action:** Add a "promote to production" capability: when the user approves an ad-hoc artifact, Marcus copies it to the production staging path, creates the state records retroactively, and runs it through the standard review gate.

**EH-3** | `references/conversation-mgmt.md` | **Content type vocabulary is closed — unrecognized types hit a dead end**

The content type vocabulary (lecture slides, case study, assessment, discussion prompt, video script, voiceover, infographic, interactive module) is exhaustive-by-design. But medical education produces many other artifact types: patient encounter simulations, OSCE checklists, clinical skills rubrics, podcast episodes, journal clubs, team-based learning activities.

**Action:** Add a "custom content type" fallback: when the request doesn't match known vocabulary, Marcus says "I don't have a standard workflow for [X] yet, but let's design one together." Then save the custom workflow to patterns.md for future reuse.

**EH-4** | `references/conversation-mgmt.md` | **Assumes user always wants to produce — no support for review, planning, or exploration modes**

Marcus's intent parsing focuses entirely on "what content type do you want to produce." But users often come wanting: "show me what we have for Module 3," "help me plan the semester content calendar," "compare the two assessment approaches we discussed."

**Action:** Expand intent parsing to recognize non-production intents: portfolio review, planning, analysis, status, and restructuring. Map each to appropriate capabilities.

**EH-5** | `references/conversation-mgmt.md` | **Missing capture-don't-interrupt pattern for tangential user mentions**

During production conversations, users frequently mention tangential needs: "oh, I also need to update the syllabus." Marcus has no mechanism to capture these asides without derailing the current workflow.

**Action:** Add a "noted" capture mechanism: Marcus acknowledges, captures in index.md as a pending item, and surfaces it at the next natural break point.

**EH-6** | `SKILL.md` | **Architecture supports headless batch production but no pathway exists**

Marcus's architecture cleanly separates judgment (agent layer) from execution (specialist agents) from connectivity (API clients). This three-layer separation means headless production is architecturally feasible. The current 6+ human gates per workflow would be reduced to a final batch review.

**Action:** Design a headless input contract: `{ course_context, content_type, module_scope, quality_thresholds, auto_approve_rules, style_bible_path, exemplar_path }`. Tier checkpoint gates: auto-approve if quality score exceeds threshold, queue for human review otherwise. Start with simple content types.

#### Medium Opportunity

**EM-1** | `references/checkpoint-coord.md` | **No streamlined path for expert users who trust the workflow**

After 50 production runs, the expert still gets the full production plan, all checkpoint gates, and explicit approval at every stage. No "trust mode" or "expedited review."

**Action:** Add a "confidence level" concept: for well-established workflows with high pattern confidence, offer to collapse intermediate gates while keeping the final review gate mandatory.

**EM-2** | `references/conversation-mgmt.md` | **No batch operations for multi-lesson production runs**

Marcus processes requests one at a time. "Build slides for all 6 lessons in Module 3" requires 6 sequential production plans.

**Action:** Add batch production planning: consolidated plan showing all runs, shared parameters, and per-lesson customizations. Present as a single approval with per-item override capability.

**EM-3** | `references/conversation-mgmt.md` | **No "repeat last run" shortcut for similar production requests**

After building lecture slides for M3L1, building the same for M3L2 should be trivial — same content type, same specialist sequence, same style parameters, different lesson. But there's no explicit "repeat with different scope" pattern.

**Action:** Add template detection: when the current request closely matches a recent production run, offer to pre-fill the production plan from the template.

**EM-4** | `references/progress-reporting.md` | **No session summary or portfolio view on exit**

When a production session ends, there's no wrap-up. No "here's everything we accomplished today," no portfolio view, no course-level progress dashboard. The value Marcus delivers over time is invisible.

**Action:** Add natural session wrap-up when the user signals they're done. Also add a "show me the portfolio" capability for on-demand course-level progress.

**EM-5** | `SKILL.md` | **Pattern learning is invisible to the user — missed delight opportunity**

Marcus learns patterns in patterns.md but never shows the user what he's learned. The user doesn't experience "oh, Marcus remembered that I always want more clinical images." Invisible value that can't be corrected.

**Action:** Periodically surface learned patterns. Add a "show me what you've learned" capability so the user can review and correct patterns.

**EM-6** | `references/memory-system.md` | **Memory system assumes single-course scope — no multi-course support**

The memory sidecar stores production context without explicit course scoping. A faculty member who teaches multiple courses would have pattern confusion. Memory entries don't tag which course they belong to.

**Action:** Add course-level scoping to memory entries. When Marcus loads patterns, filter by the active course context.

**EM-7** | `references/conversation-mgmt.md` | **No partial restart — production plan is forward-only**

If the user approves stage 3 (slides) but then realizes the outline (stage 1) was wrong, there's no "go back to stage 1" protocol. Medical education content creation is highly iterative.

**Action:** Add stage rollback to production coordination: acknowledge downstream impact, roll back the plan state, and re-sequence.

**EM-8** | `SKILL.md` | **Assumes style bible and exemplar library exist and are well-formed**

Marcus's production planning, specialist handoffs, and quality gates all reference the style bible and exemplar library. Init.md acknowledges they might not exist, but the downstream workflow doesn't degrade gracefully.

**Action:** Define explicit "no style bible" and "no exemplar" degraded states. Make style bible context optional in the specialist context envelope.

**EM-9** | `references/conversation-mgmt.md` | **Missing pedagogical intent elicitation before production**

Source prompting asks logistics questions ("do you have Notion notes?"). Missing is the deeper question: "What learning experience do you envision for students?" This pedagogical intent shapes every downstream decision but is never explicitly elicited.

**Action:** Add an "intent elicitation" step before production planning: "Before we build, tell me about the learning experience you're designing."

**EM-10** | `references/checkpoint-coord.md` | **Quality review uses single lens — no parallel review perspectives**

The quality-reviewer validates against the style bible as a single rubric. Medical education content has multiple quality dimensions: accessibility, clinical accuracy, pedagogical alignment, assessment validity, brand consistency.

**Action:** Consider parallel review lenses within the quality-reviewer specialist. Present results as a multi-dimensional quality scorecard.

**EM-11** | `references/mode-management.md` | **Missing "planning mode" — third mode for semester-level content strategy**

Marcus has default (production) and ad-hoc (experimental). Missing is a "planning" mode for content strategy across an entire module or semester without producing anything.

**Action:** Add a lightweight "planning" mode or extend conversation management to recognize planning-intent conversations. Output a content strategy document that serves as the production roadmap.

**EM-12** | `references/progress-reporting.md` | **Proactive cross-reference detection between production runs**

Marcus treats each production run independently. Medical education content is deeply interconnected: a pharmacology concept in Module 2 may be prerequisite to a clinical case in Module 4.

**Action:** Add cross-reference awareness to production planning: scan existing content for related concepts and surface connections proactively.

**EM-13** | `references/conversation-mgmt.md` | **Clarifying questions assume the user can answer them**

When requests are ambiguous, Marcus asks clarifying questions. But a new or confused user might not know module names, lesson identifiers, or content types. No fallback for "I don't know — show me what's available."

**Action:** Add "discovery" fallbacks: use course_context.yaml to present navigable options instead of requiring the user to know identifiers.

**EM-14** | `SKILL.md` | **Context window exhaustion risk for long production sessions**

A complex production run with multiple specialist interactions, review gates, and revisions could fill the context window. Marcus re-reads style bible, exemplars, memory sidecar, and state on every activation. No explicit strategy for context management within a long session.

**Action:** Add context window awareness: define a "condensation protocol" for long sessions where Marcus summarizes completed stages into compact state records and releases the detailed context.

**EM-15** | `references/conversation-mgmt.md` | **Shared/reused assets conflict with the asset-lesson pairing invariant**

The invariant says every artifact is paired with instructional context. But medical education commonly reuses assets across modules. The invariant doesn't account for one-to-many pairing.

**Action:** Clarify the invariant to support one-to-many pairing: an asset must have at least one instructional context, and when reused, each usage must have its own documented pairing.

#### Low Opportunity

**EL-1** | `scripts/read-mode-state.py` | **read-mode-state.py doesn't actually read or set the run mode**

The script reads production run state from SQLite but returns mode as hardcoded "default." No mechanism to persist or retrieve the current run mode.

*(Cross-ref: also identified by agent-cohesion scanner as C-M2)*

**Action:** Add a mode column to the production_runs table or a separate mode_state table/file.

**EL-2** | `SKILL.md` | **No "what can you do?" onboarding capability**

Marcus has 6 internal capabilities, 5 external skills, and 8 specialist agents. But there's no guided capability tour for new users.

**Action:** Add a natural "what I can do" response pattern presenting capabilities as production scenarios rather than capability tables.

**EL-3** | `references/source-prompting.md` | **Assumes Notion and Box Drive content is well-organized and retrievable**

Source prompting offers to pull content but assumes sources are organized in a way Marcus can navigate. Faculty Notion pages are often chaotic.

**Action:** Add a "source quality assessment" to the source-wrangling interaction: report when pulled content is sparse, disorganized, or unclear.

**EL-4** | `references/progress-reporting.md` | **No celebration or reinforcement when milestones are reached**

When a module is complete or the first production run finishes, Marcus reports it as routine status. No milestone recognition.

**Action:** Add milestone awareness: "That's Module 2 complete — all 5 lessons have slide decks, assessments, and voiceovers. That's a big milestone."

**EL-5** | `SKILL.md` | **Cross-specialist coordination value is invisible to the user**

Marcus builds context envelopes and passes them to every specialist. This is Marcus's core value add. But the user never sees this happening.

**Action:** Occasionally make coordination visible: "I'm passing the learning objectives and your feedback to Gamma for the slide redesign — they'll have full context."

**EL-6** | `references/mode-management.md` | **Mode names are system-centric, not user-centric**

"Default mode" and "ad-hoc mode" are implementation-level names. A faculty member thinks in terms of "working on my course" vs "trying something out."

**Action:** Consider user-facing mode names: "Production mode" vs "Sandbox mode."

**EL-7** | `references/checkpoint-coord.md` | **No dual-output option at review gates**

At checkpoint gates, Marcus presents the artifact for user review. No "generate a shareable summary" output alongside the review presentation.

**Action:** Add optional dual-output: produce a condensed description (content, objectives, quality assessment) in a shareable format.

**EL-8** | `SKILL.md` | **No handling for mid-production user absence (days/weeks gap)**

Marcus's memory system captures state, but there's no explicit handling for staleness. If a user returns after 3 weeks, are pending review gates still valid?

**Action:** Add staleness detection to activation: if the last session activity was more than N days ago, proactively check for changes.

**EL-9** | `references/memory-system.md` | **No "expertise evolution" visibility — Marcus gets smarter but user doesn't see it**

patterns.md accumulates valuable learned preferences over time. But this evolution is invisible. After 20 sessions, Marcus doesn't summarize what it's learned.

**Action:** Add periodic "what I've learned" summaries at natural milestones and offer pattern review/correction.

**Top Insights:**

1. **The first 5 minutes determine adoption — and they're the worst 5 minutes.** Marcus's init.md asks 5 setup questions before delivering any value. A first-timer with no infrastructure gets an interrogation about things they don't have. The memory system means session 2+ will be great — but many users won't reach session 2 if session 1 feels like filling out forms.
   - **Action:** Add a "quick start" path: detect empty infrastructure and offer a guided demo production run using sample content. Setup becomes "now that you've seen what I can do, let's set up your course properly."

2. **Ad-hoc mode is a hotel with no checkout — great experiments can't move to production.** The ad-hoc/default mode boundary is well-enforced but one-way. This creates a perverse incentive to always use default mode, defeating the purpose of having a safe sandbox.
   - **Action:** Add a "promote" operation: copy to production staging, create state records retroactively, run the standard review gate.

3. **Marcus orchestrates production but doesn't help plan production — the strategic gap.** Every interaction assumes the user knows what they want to produce. Faculty often need help BEFORE production: "I have 40 hours of content to produce this semester — where do I start?"
   - **Action:** Add a "content strategy" capability or planning mode: map out production priorities, identify reuse opportunities, estimate effort, create a production roadmap.

4. **The expert user is being slowed down by the guardrails designed for everyone else.** After 50 production runs, the expert doesn't need the full production planning ceremony or intermediate checkpoint gates for well-established workflows. The same quality rigor that protects a new user becomes friction for an expert.
   - **Action:** Add confidence-based ceremony reduction: collapse redundant ceremony when confidence is high. Keep quality gates running internally but only surface the final approval gate.

5. **Marcus learns in silence — the user never sees the intelligence accumulating.** patterns.md accumulates valuable learned preferences. But the user never sees this happening. They can't correct wrong patterns AND don't feel the value of long-term use.
   - **Action:** Surface learned patterns periodically. Add "show me what you've learned" as a capability so users can review and correct the pattern library.

---

## User Journeys

*How different user archetypes experience this agent:*

### First-Timer

A new faculty member who heard about Marcus and wants to try it out. They have lecture notes in Notion but haven't set up any infrastructure (no style bible, no exemplars, no course context YAML). They want to produce a slide deck for their upcoming lecture.

**Friction Points:**
- Init asks 5 questions before any value — feels like filling out a form to use a tool
- Terms like "style bible," "exemplar library," and "asset-lesson pairing invariant" are opaque
- No demo or guided tour — Marcus assumes the user knows what an orchestrator does
- If infrastructure doesn't exist, Marcus can note it but can't actually produce much
- Mode names (default/ad-hoc) mean nothing to a first-timer

**Bright Spots:**
- Warm greeting with name and clear next-step offer — feels personal
- Source prompting ("want me to pull your Notion notes?") is immediately useful
- Clear communication style — professional without being intimidating
- Memory system means the SECOND session is much better than the first

---

### Expert

A faculty member who has run 50+ production runs, knows their course inside out, and wants to rapidly produce content for a new module. They have established patterns and strong preferences.

**Friction Points:**
- Full production planning ceremony every time — no "fast track" for known workflows
- No batch operations — "build slides for all lessons in Module 3" requires 6 individual runs
- No "repeat last run" shortcut for similar content
- Intermediate checkpoint gates feel like busywork for trusted patterns
- Pattern learning is invisible — expert doesn't know Marcus has learned their preferences

**Bright Spots:**
- Memory-based session continuity — Marcus picks up where they left off
- Style bible and exemplar consultation ensures consistency across the course
- Natural progress reporting matches expert's expectation of a professional collaborator
- Options with recommendations saves decision fatigue

---

### Confused User

A faculty member who is new to instructional design, unfamiliar with production workflows, and not sure what they need. They know they want "better online content" but can't articulate specific content types or pedagogical objectives.

**Friction Points:**
- Medical education vocabulary barrier (Bloom's, backward design, assessment tracing)
- Clarifying questions assume the user can answer them — no "show me what's available" fallback
- Content type vocabulary requires the user to know what artifact type they want
- No guided discovery path — "tell me about your teaching goals and I'll suggest what to build"
- Mode distinction adds unnecessary cognitive load

**Bright Spots:**
- Marcus never guesses — asks clarifying questions instead of assuming
- Conversational style is approachable and non-technical
- Recommendations come with rationale, which is educational
- Quality gates provide natural teaching moments about content standards

---

### Edge-Case User

A faculty member who teaches across 3 courses, wants to reuse assets between modules, has unusual content needs (patient simulations, OSCE checklists), and sometimes works in bursts with multi-week gaps between sessions.

**Friction Points:**
- Single course context — switching between courses isn't explicitly supported
- Asset-lesson pairing invariant doesn't support one-to-many reuse
- Content types they need (simulations, OSCE) aren't in the vocabulary
- Multi-week gaps may produce stale state with no freshness detection
- Partial production restarts not supported — can't go back to stage 2 after approving stage 4

**Bright Spots:**
- Memory persistence means they can resume after gaps
- Ad-hoc mode supports experimentation without commitment
- Specialist routing is flexible enough to add new specialist types
- Quality gates catch issues regardless of how unusual the content is

---

### Hostile Environment

A session where Gamma is down, Notion API is timing out, the style bible was recently reformatted and has formatting issues, and the SQLite database has a corrupted record from a crashed session.

**Friction Points:**
- Cascading failures — if 3+ specialists are unavailable, Marcus has nothing to delegate to
- No "offline mode" — Marcus without specialist agents is just a conversation partner
- read-mode-state.py hardcodes mode as "default" — doesn't handle corrupt or missing mode state
- Style bible malformation could produce subtle downstream errors
- No self-healing — Marcus detects problems but can't fix infrastructure

**Bright Spots:**
- Error handling protocol is well-designed: inform, suggest alternatives, adjust plan, never fail silently
- Pre-flight check capability can detect issues proactively
- Graceful degradation messaging is clear and actionable
- QA runs in all modes — quality never silently degrades

---

### Automator

A curriculum coordinator who wants to batch-produce content across an entire semester — 8 modules, 40 lessons, standardized slide decks and assessments for all of them. They want to set parameters once and let Marcus handle it.

**Friction Points:**
- Interactive-only for v1 — no headless batch production
- No programmatic trigger or CI integration
- No production run templates — every run goes through intent parsing
- No "when X changes, do Y" automation triggers
- Each production run requires manual checkpoint approvals

**Bright Spots:**
- Architecture cleanly supports future headless mode (agent/specialist/API layers separated)
- Pattern learning could feed template generation
- Scripts are already structured for programmatic use
- Style bible and exemplar consistency means standardized output quality

---

## Autonomous Readiness

- **Overall Potential:** HIGH — Marcus's architecture (agent judgment layer separated from specialist execution layer separated from API connectivity layer) is textbook-ready for headless operation. The specialist context envelope is already a machine-readable handoff contract. The main barriers are human checkpoint gates (6+ per workflow) and ambiguity resolution in intent parsing.
- **HITL Interaction Points:** 8
- **Auto-Resolvable:** 5
- **Needs Input:** 3
- **Suggested Output Contract:** `{ artifacts: [{ path, content_type, module, lesson, quality_score, specialist_decisions }], quality_report: { per_artifact_scores, style_bible_compliance, bloom_alignment, accessibility_check }, decision_log: [{ stage, decision, rationale, auto_or_human }], production_summary: { total_artifacts, approved, needs_review, failed } }`
- **Required Inputs:**
  - course_context.yaml — full course/module/lesson hierarchy with learning objectives
  - content_type — which artifact type to produce (or "all" for full module build)
  - module_scope — which module(s) and lesson(s) to target
  - style_bible_path — path to resources/style-bible/
  - exemplar_path — path to resources/exemplars/
  - quality_thresholds — `{ auto_approve_above: 0.9, flag_for_review_below: 0.7 }`
  - parameter_overrides — optional per-specialist parameter preferences from patterns.md
- **Notes:** Start with simple content types for headless (discussion prompts, where quality judgment is less subjective). Tier checkpoint gates: auto-approve if quality score > threshold, queue for human review otherwise. The 3 non-automatable HITL points are: (1) pedagogical intent not captured in learning objectives, (2) clinical accuracy judgment requiring domain expertise, and (3) final approval for publication. The brainstorming doc explicitly marks this as "Interactive mode only for v1" — headless is the obvious v2 headline feature.

---

## Script Opportunities

**Existing Scripts:** read-mode-state.py, generate-production-plan.py

Both existing scripts follow good patterns: argparse CLI, JSON output, graceful fallbacks, stderr diagnostics. New scripts should follow the same conventions.

#### High Priority

**SO-H1** | `SKILL.md:52` | **Activation data aggregator — gather all startup context into one JSON payload**
*(preprocessing — estimated savings: 900 tokens — complexity: moderate — prepass: yes)*

On every activation Marcus reads config YAML, checks sidecar memory existence, reads index.md, scans style-bible/ and exemplars/ directories, and invokes read-mode-state.py. Each of these is pure file I/O and YAML/markdown parsing. A single "preflight-activation.py" script could return a unified JSON blob.

**Action:** Create "preflight-activation.py" that reads config.yaml + config.user.yaml, checks sidecar dir, lists style-bible/ and exemplars/ contents, calls read-mode-state internally, and returns unified JSON.

**SO-H2** | `references/init.md:11` | **First-run environment discovery — check required directories and files exist**
*(structure — estimated savings: 500 tokens — complexity: trivial — prepass: yes)*

On first run, Marcus manually checks existence of state/config/course_context.yaml, resources/style-bible/, resources/exemplars/, and the sidecar directory. This is pure filesystem existence checking — completely deterministic.

**Action:** Add a "--check-environment" flag to preflight-activation.py (or standalone "check-environment.py") that returns JSON: `{path: exists_bool}` for every required path.

**SO-H3** | `references/init.md:20` | **Memory sidecar scaffolding — create initial directory and template files**
*(transformation — estimated savings: 700 tokens — complexity: trivial)*

On first run, Marcus creates four files (index.md, access-boundaries.md, patterns.md, chronology.md) in the sidecar directory from fixed templates. The LLM currently generates these from scratch each time.

**Action:** Create "init-sidecar.py" that creates the sidecar directory and populates template files. Accepts --project-root and --agent-name.

**SO-H4** | `references/memory-system.md:22` | **Access boundary path validation — check file operations against allow/deny rules**
*(validation — estimated savings: 300 per check, 1500+ per session — complexity: moderate)*

Marcus verifies every file operation path against read/write/deny zone rules. The rules are static path-prefix matching — pure deterministic work.

**Action:** Create "check-access.py" that encodes the allow/deny rules. Input: path, operation (read/write), mode (default/ad-hoc). Output: `{allowed: bool, rule: string, zone: string}`.

#### Medium Priority

**SO-M1** | `references/memory-system.md:76` | **Mode-aware write permission lookup**
*(validation — estimated savings: 150 per check — complexity: trivial)*

The mode-aware write rules table is a pure lookup the LLM performs by re-reading the table each time.

**Action:** Fold into "check-access.py" — sidecar file write rules become additional entries in the permission table.

**SO-M2** | `SKILL.md:52` | **Config variable resolution — parse YAML configs and extract settings**
*(extraction — estimated savings: 350 — complexity: trivial — prepass: yes)*

Marcus reads config.yaml and config.user.yaml, extracts three variables, and applies defaults. Pure YAML key extraction.

**Action:** Include as part of "preflight-activation.py" config section.

**SO-M3** | `references/conversation-mgmt.md:39` | **Course hierarchy resolver — extract module/lesson/objective tree from YAML**
*(preprocessing — estimated savings: 400 — complexity: trivial — prepass: yes)*

When the user references a module/lesson, Marcus reads course_context.yaml and resolves the hierarchy path.

**Action:** Add "--resolve MODULE [LESSON]" mode to generate-production-plan.py (or create "resolve-course-context.py").

**SO-M4** | `references/conversation-mgmt.md:78` | **Asset-lesson pairing validator — verify every artifact has instructional context**
*(validation — estimated savings: 400 — complexity: moderate)*

Before marking any production step complete, Marcus verifies: asset has parent lesson, learning objectives documented, assessment alignment explicit. The structural checks are deterministic.

**Action:** Create "validate-asset-pairing.py" that takes asset path and lesson ID, checks structural requirements.

**SO-M5** | `references/conversation-mgmt.md:61` | **Context envelope assembler — pre-populate specialist handoff data**
*(preprocessing — estimated savings: 400 — complexity: moderate — prepass: yes)*

When delegating to specialists, Marcus constructs a context envelope with mostly deterministic lookups from state DB + course context + file inventory.

**Action:** Create "assemble-context-envelope.py" taking run_id, content_type, module_id, lesson_id. Returns partial envelope JSON. LLM fills in qualitative fields.

#### Low Priority

**SO-L1** | `references/checkpoint-coord.md:33` | **Checkpoint outcome record validator**
*(postprocessing — estimated savings: 200 — complexity: trivial)*

After checkpoint decisions, the record structure is fixed. A post-processing script could validate all required fields.

**Action:** Create "validate-checkpoint-record.py" that validates: all required fields present, decision in valid enum, types correct.

**SO-L2** | `references/mode-management.md:28` | **Mode switch state updater — write new mode to state**
*(transformation — estimated savings: 150 — complexity: trivial)*

Complementary to read-mode-state.py, a "set-mode-state.py" could handle mode writes: update SQLite, clear ad-hoc session section, return confirmation.

**Action:** Create "set-mode-state.py" taking target mode (default/ad-hoc). Pairs with read-mode-state.py.

**Token Savings:** ~4,550 estimated tokens/session | Highest value: preflight-activation.py (900 tokens) | Prepass opportunities: 6

---

## Quick Wins (High Impact, Low Effort)

| Issue | File | Effort | Impact |
|-------|------|--------|--------|
| Install uv for Python linting (PS-H1) | Environment | Trivial | Enables ruff linting for both scripts |
| Expand overview with mode/memory mention (P-M1) | SKILL.md | Trivial (add 1-2 sentences) | Improved LLM scope comprehension |
| Add Status column to specialist agents table (S-M3) | SKILL.md | Trivial (add column) | Prevents premature delegation attempts |
| Separate future vs current specialist agents (CS-1) | SKILL.md | Trivial (split table) | Eliminates LLM confusion at activation |
| Consolidate re-read-from-disk instructions (P-L1) | SKILL.md | Low (remove 2 of 3 within SKILL.md) | Minor token savings per activation |
| Add explicit access-boundaries step in On Activation (S-M1) | SKILL.md | Low (add 1 step) | Closes security gap in activation |
| Remove/harmonize save-memory.md frontmatter (P-L2) | save-memory.md | Trivial | Structural consistency |

---

## Optimization Opportunities

**Token Efficiency:**
The primary token optimization is deferring eager resource loading. Style-bible and exemplar directories are loaded on every activation (~variable token cost depending on directory size) even when the session never touches production. Deferring to capability-time loading (E-M1) would eliminate this waste for non-production sessions. Additionally, the re-read-from-disk instruction is stated 5 times across the agent surface — consolidating within SKILL.md saves ~50 tokens per activation (P-L1). The 10 principles (S-L3) could be consolidated to 7-8 for minor per-activation savings. The script-opportunities analysis identifies ~4,550 tokens/session of deterministic work that could be offloaded to scripts, with the preflight-activation aggregator (900 tokens) being the highest single-target savings.

**Performance:**
Sequential activation reads (E-L1) could be parallelized into two groups, reducing activation latency. The proposed preflight-activation.py script (SO-H1) would collapse 4+ file reads and one script invocation into a single call, dramatically reducing activation time. Style-bible loading at review gates (E-L2) could be scoped to relevant sections, reducing both latency and context consumption during checkpoint coordination.

**Maintainability:**
The CM capability (C-M1) bundles four concerns into one reference file — splitting it would improve selective loading and reduce blast radius. Missing bmad-skill-manifest.yaml (S-L2) creates inconsistency with the BMAD agent cohort. The structural inconsistency of YAML frontmatter in save-memory.md only (P-L2) should be harmonized. The 5 unvalidated external skills and 6 unvalidated specialist agents (S-M2, S-M3) are the biggest maintainability risk — adding status annotations would enable graceful degradation and make the dependency graph explicit.

---

## Recommendations

1. **Fix mode state tracking.** The read-mode-state.py script always returns "default" regardless of actual mode, creating a disconnect between documented behavior and implementation. Either add mode persistence to the database or update mode-management.md to reflect that mode is tracked in memory only. This is the single most impactful fix for operational correctness. *(C-M2, EL-1)*

2. **Validate and annotate external dependencies.** Add a "Status" column (active/planned/future) to both the External Skills and External Specialist Agents tables. Validate that the 6 active specialist agents and 5 external skills exist and are callable. This prevents silent failures during production planning and enables graceful degradation. *(S-M2, S-M3, CS-1)*

3. **Defer eager resource loading to capability-time.** Move style-bible and exemplar directory loading from On Activation to the CM/HC capabilities when production planning or quality review actually needs them. This eliminates wasted tokens and latency for non-production sessions while maintaining the "always re-read fresh" principle. *(E-M1, E-L2)*

4. **Create preflight-activation.py.** Collapse config loading, environment checking, sidecar status, and mode state into a single script returning unified JSON. This is the highest-ROI script opportunity: ~900 tokens/activation of pure deterministic work moved out of the LLM. *(SO-H1, SO-H2, SO-M2, E-L1)*

5. **Add explicit access-boundaries loading to On Activation.** The security-critical access boundaries are specified with "Load on activation" in memory-system.md but aren't explicitly mentioned in SKILL.md's activation sequence. Adding one step closes this gap with trivial effort. *(S-M1)*
