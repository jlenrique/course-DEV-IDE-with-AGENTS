# Quality Report: bmad-agent-quality-reviewer

**Scanned:** 2026-03-27T03:38:09+00:00
**Skill Path:** skills/bmad-agent-quality-reviewer
**Report:** skills/reports/bmad-agent-quality-reviewer/quality-scan/2026-03-26_233759/quality-report.md
**Performed By** QualityReportBot-9001

## Executive Summary

- **Total Issues:** 12
- **Critical:** 0 | **High:** 0 | **Medium:** 1 | **Low:** 11
- **Overall Quality:** Good
- **Overall Cohesion:** mostly-cohesive
- **Craft Assessment:** Strong prompt craft for a single-SKILL agent with clear Overview, identity, and outcome-focused principles; progressive disclosure to references is appropriate. Main gaps are config consistency and mildly suggestive memory loading phrasing.

Quinn-R is a meticulous QA guardian for educational and medical-ed production artifacts, operating as the final automated gate before human review with structured five-dimension rubrics and optional calibration memory. The agent's architecture is sound — complete required sections, verified capability routes, headless delegation, and sidecar memory — with no critical or high-severity defects. The most significant finding is the absence of structured JSON output alongside Markdown reports, which limits reliable chaining in pipelines and CI despite strong input-side orchestration from Marcus.

### Issues by Category

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Structure & Capabilities | 0 | 0 | 0 | 0 |
| Prompt Craft | 0 | 0 | 0 | 3 |
| Execution Efficiency | 0 | 0 | 0 | 1 |
| Path & Script Standards | 0 | 0 | 0 | 0 |
| Agent Cohesion | 0 | 0 | 0 | 4 |
| Script Opportunities | 0 | 0 | 1 | 3 |
| Creative | — | 2 high-opp | 9 med-opp | 5 low-opp |

---

## Agent Identity

- **Persona:** Quinn-R, meticulous QA specialist for educational/medical artifacts, final gate before human review, structured severity and calibration with Marcus.
- **Primary Purpose:** Systematic multi-dimension quality validation of production artifacts with structured reports and optional persistence via quality-control and sidecar memory.
- **Capabilities:** 6 internal + 3 external

---

## Strengths

*What this agent does well — preserve these during optimization:*

**Structural Integrity**
- **Complete required sections with clean pre-pass** — All eight required H2 sections are present, frontmatter is valid, no template artifacts remain, and the deterministic pre-pass reported zero issues. This means the agent structure is production-ready without remediation. *(structure)*
- **Headless delegation path documented end-to-end** — On Activation defines inputs (artifact paths, run ID, specialist, content type, mode), required reads (style bible, course_context, tool_policies), quality-control automation via review-protocol, judgment review, feedback-format output, logging behavior, and return to Marcus. This enables reliable autonomous operation. *(structure)*
- **Sidecar memory specifies boundaries, modes, and save triggers** — memory-system.md documents index/access-boundaries/patterns/chronology roles, read/write/deny zones, ad-hoc vs default write rules, explicit save triggers, and coordination with save-memory.md. *(structure)*

**Identity & Communication**
- **Description uses two-part summary plus conservative quoted triggers** — Concrete capability summary plus Use-when clause with quoted phrases supports reliable activation and distinguishes this agent from generic QA skills. *(structure)*
- **Identity is actionable and aligned with declared dimensions** — Persona frames expertise, independence from content creation, constructive feedback, and calibration with human reviewer, matching the five review dimensions and delegation model. *(structure)*
- **Communication style includes concrete, persona-appropriate examples** — Severity semantics, location granularity, actionable suggestion shape, report organization, score summaries, and calibration transparency are all specified. *(structure)*
- **Principles are domain-specific decision frameworks** — Tied to accessibility, brand, alignment, actionability, pattern reporting, calibration, medical flagging vs adjudication, mode behavior, independence, and tone — avoiding generic platitudes. *(structure)*

**Execution Efficiency**
- **Explicit parallel batch for independent cold-load reads** — On Activation batches config files, memory-system.md, sidecar index, style bible, course_context.yaml, and tool_policies.yaml in one round with no hard ordering dependencies, reducing tool round-trips. *(execution-efficiency)*
- **Selective sidecar loading for patterns and chronology** — index.md loads on activation; patterns.md and chronology.md are load-when-needed, saving tokens on typical runs. *(execution-efficiency)*

**Cohesion & Architecture**
- **Persona and pipeline role align tightly** — Quinn-R separates judgment from delegated automation (quality-control), threads medical-education context, calibration, and independence consistently through Identity, Principles, and activation flows. *(agent-cohesion)*
- **Five quality dimensions are operationalized end-to-end** — Review protocol, feedback-format dimension table, and SKILL overview all enumerate the same five dimensions with matching severity semantics and escalation rules. *(agent-cohesion)*
- **Degradation and partial-review behavior is explicit** — Style bible, scripts, course context, and incomplete artifacts each have a defined fallback or SKIP pattern. *(agent-cohesion)*
- **Zero scripts in agent directory is architecturally correct** — Deterministic checks are owned by the companion quality-control skill per SKILL.md delegation model; duplicating them here would contradict the separation of concerns. *(script-opportunities)*

**Prompt Craft**
- **Overview clearly frames mission, modes, and delegation** — Seven-line Overview covers the Quality Guardian role, five review dimensions, delegation to quality-control, dual default vs ad-hoc behavior, and human calibration. *(prompt-craft)*
- **Capabilities table uses imperative Load routes to references** — Not optional "see if needed" language; direct Load instructions support self-containment and context survival. *(prompt-craft)*

---

## Detailed Findings by Category

### 1. Structure & Capabilities

**Agent Metadata:**
- Sections found: Overview, Identity, Communication Style, Principles, Does Not Do, Degradation Handling, On Activation, Capabilities
- Capabilities: 9 (6 internal, 3 external)
- Memory sidecar: Yes (memory/quality-reviewer-sidecar/index.md)
- Headless mode: Yes
- Structure assessment: Deterministic pre-pass is clean. Strong structural integrity with verified capability routes and full headless plus sidecar memory documentation.

No issues found. All structure findings were strengths or notes.

### 2. Prompt Craft

**Agent Assessment:**
- Agent type: workflow-facilitator
- Overview quality: appropriate
- Progressive disclosure: good
- Persona context: appropriate
- 114 lines, ~3k tokens: well within guidelines. Heavy procedural and persona content is load-bearing for a QA gate agent. Procedure depth lives in references/review-protocol.md and feedback-format.md appropriately.

**Low:**

| # | Title | File | Detail | Action |
|---|-------|------|--------|--------|
| 1 | Human reviewer name hardcoded while config uses `user_name` | SKILL.md:18, SKILL.md:29, SKILL.md:38, references/memory-system.md:34 | On Activation resolves `{user_name}` from config, but Identity, Communication Style, Principles, and memory-system reference use the concrete name "Juan". This breaks portability across projects. Not persona waste — the intent is calibration examples — but implementation should stay consistent with variables. *(prompt-craft, prompt-craft)* | Replace with `{user_name}` (null-safe phrasing) or neutral wording such as "the human reviewer" wherever reviewer-specific examples appear. |
| 2 | Suggestive loading for patterns.md and chronology.md | references/memory-system.md:32 | Sections use "Load when needed" rather than mandatory triggers. Under context compaction or rushed execution, the agent may skip pattern and history files when calibration or recurring-issue reporting depends on them. | Replace with explicit when-to-load rules (e.g., load patterns.md before emitting pattern_alerts; load chronology.md when reporting calibration_notes). |
| 3 | No explicit progression or continuation conditions | SKILL.md:71 | Headless vs interactive paths are described, but no stated gates for multi-phase reviews. For typical single-shot Marcus handoffs this is acceptable; risk grows for long or interrupted reviews. | If multi-phase reviews are common, add explicit continuation conditions; otherwise document that single-pass completion is intentional. |

### 3. Execution Efficiency

**Low:**

| # | Title | File | Detail | Action |
|---|-------|------|--------|--------|
| 1 | Sidecar entry point names index only; access-boundaries load implicit | SKILL.md:67 | references/memory-system.md requires access-boundaries.md on activation alongside index.md. SKILL.md only mandates the sidecar index. If index omits a pointer, the model may skip the security file or reread memory-system.md for boundaries. | In On Activation, add access-boundaries.md to the parallel batch when the sidecar exists. |

**Optimization Opportunities:**

| # | Title | Severity | File | Detail | Action |
|---|-------|----------|------|--------|--------|
| 1 | Automated checks listed as sequential bullets | medium-opportunity | references/review-protocol.md:19 | Step 1 invokes accessibility_checker.py then brand_validator.py as separate bullets with no guidance to run concurrently. Parallel execution cuts wall-clock time roughly in half. | Add explicit guidance to invoke both scripts in parallel when inputs are ready, then merge results. |
| 2 | Multi-artifact cross-checks without parallel fan-out | low-opportunity | references/review-protocol.md:69 | For large sets of independent artifact pairs, a parent coordinator could delegate each pair to a subagent with a fixed JSON return shape to cap context growth. | For N+ paired artifacts, optionally document parallel subagent tasks per pair. |

### 4. Path & Script Standards

**Script Inventory:** 0 scripts | No scripts/ directory found — architecturally correct per delegation model to quality-control.

**Path Standards:** Clean pass — no path standard violations found across 6 files scanned.

No issues found.

### 5. Agent Cohesion

**Cohesion Analysis:**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Persona Alignment | strong | Expertise matches protocol and feedback formats; tone and reporting rules match the QA guardian role. |
| Capability Completeness | mostly-complete | Core review, reporting, memory, and external automation hooks present; minor table and prerequisite clarity gaps. |
| Redundancy Level | some-overlap | QA, CC, BV, LA all load the same review-protocol.md file. |
| External Integration | intentional | quality-control scripts and SQLite logging documented with context; redirect to bmad-help consistent with Marcus orchestration. |
| User Journey | mostly-complete | Headless and interactive paths, partial review, and escalation to human form a coherent journey; standalone use needs companion assets. |

**Consolidation Opportunities:**

| Capabilities | Suggested Consolidation |
|-------------|------------------------|
| QA, CC, BV, LA | Treat as one "Run review protocol" capability with dimension tags, or state clearly that all four codes load the same file for different mental models. |

**Low:**

| # | Title | File | Detail | Action |
|---|-------|------|--------|--------|
| 1 | Instructional soundness lacks a discrete capability row | SKILL.md:81 | SKILL.md lists QA, CC, BV, LA, FG, and SM while instructional soundness is a full dimension in review-protocol and feedback-format. Implementers scanning only the capability table might assume that dimension is out of scope. | Add an IS row pointing to review-protocol.md, or annotate QA as covering all five dimensions explicitly. |
| 2 | Four capability codes route to the same review protocol file | SKILL.md:83 | QA, CC, BV, and LA all load ./references/review-protocol.md. Distinct codes suggest four separate procedures but progressive disclosure is one protocol with steps. | Document that these codes are aliases or phases of one workflow, or merge into a single capability. |
| 3 | CC label 'Compliance checking' easy to misread as umbrella compliance | SKILL.md:84 | In the protocol, brand and accessibility are separate dimensions; CC suggests broad compliance. New readers may confuse scope. | Rename CC to something scope-specific (e.g., Accessibility & WCAG compliance) or add a one-line gloss. |
| 4 | quality-control skill required but not declared as install prerequisite | SKILL.md:90 | Activation and protocol assume scripts under quality-control. In a repo without it, headless runs hit degradation paths unless another skill supplies those assets. | Add a Prerequisites or Companion skills subsection listing quality-control and key paths. |

**Creative Suggestions:**

| # | Title | Source | Detail | Action |
|---|-------|--------|--------|--------|
| 1 | Quote 'quality gate validation' in description trigger clause | structure | Sibling trigger phrases use single quotes; 'quality gate validation' appears unquoted. Matching would tighten activation consistency. | Wrap in single quotes alongside other trigger phrases. |
| 2 | Extend Save Memory with bullet triggers cross-linked to memory-system | agent-cohesion | save-memory.md summarizes checkpoints while memory-system.md carries access boundaries, triggers, and mode rules. A single consolidated checklist could reduce missed updates. | Extend save-memory.md with bullet triggers cross-linked to memory-system sections. |

### 6. Creative (Edge-Case & Experience Innovation)

**Agent Understanding:**
- **Purpose:** Systematic quality validation (brand, accessibility, learning alignment, instructional soundness, content accuracy flags) for educational production artifacts, as gatekeeper to human review, with optional calibration memory.
- **Primary User:** Marcus (orchestrator) delegating at checkpoints; human reviewers calibrating severity; specialists consuming structured feedback.
- **Key Assumptions:**
  - quality-control skill scripts and paths (style bible, course_context, tool_policies) exist or degrade gracefully
  - Marcus supplies structured delegation payloads for headless runs
  - Medical accuracy is always escalated, never adjudicated by the agent
  - SQLite and sidecar exist for default-mode persistence

**Enhancement Findings:**

**High-Opportunity:**

| # | Title | File | Detail | Action |
|---|-------|------|--------|--------|
| 1 | Primary report is Markdown-first; headless chains want structured data | references/feedback-format.md:7 | Pipelines invoking Quinn-R programmatically must scrape Markdown or re-ask the model to emit JSON, which is fragile and duplicates the structured fields already implied (verdict, dimension_scores, findings). | Define an optional parallel JSON block or companion schema for the same report so quality_logger and downstream tools consume one shape. |
| 2 | No parallel review lenses before final report | references/review-protocol.md:19 | A single Quinn-R pass blends five dimensions. High-stakes publication could benefit from a brief structured second pass (skeptic on medical flags, pedagogy-only lens on soundness). | Optional step: after draft report, run a short adversarial checklist per dimension when review_depth=thorough. |

**Medium-Opportunity:**

| # | Title | File | Detail | Action |
|---|-------|------|--------|--------|
| 1 | Interactive greeting assumes pipeline stats the user may not have | SKILL.md:74 | First-timer or someone outside the Marcus pipeline has no meaningful cycle counts, creating an awkward dead-end. | Add a branch: if sidecar/SQLite history is missing or empty, use a compact onboarding line and offer clear choices. |
| 2 | Headless path is Marcus-only; direct automators lack a declared contract | SKILL.md:71 | No documented JSON/XML schema or example request body for non-Marcus callers (CI, another skill). | Add a minimal machine-readable request/response example in SKILL.md or references. |
| 3 | Multi-artifact review depends on optional cross_artifact_refs | references/review-protocol.md:69 | A caller could omit cross_artifact_refs and get siloed per-file reviews without the skill surfacing that pairing checks were skipped. | Default to running cross-artifact checks unless explicitly disabled; note when pairing was inferred vs explicit. |
| 4 | Ad-hoc mode executes fully but calibration learning path is unclear | references/memory-system.md:53 | Users doing quick audits may expect calibration to stick. Skill doesn't spell out that calibration saves require default mode and Save Memory. | Add one sentence: ad-hoc reviews are ephemeral unless user switches to default mode and runs SM. |
| 5 | Calibration loop assumes Marcus relays human feedback reliably | references/review-protocol.md:84 | If the human reviews without Marcus relay, Quinn-R's patterns.md and chronology drift from reality. | Document a fallback: direct human calibration commands that Quinn-R can record without Marcus. |
| 6 | Mid-session scope change and pause are not described | SKILL.md:50 | No guidance on preserving partial state or cleanly restarting when users want to stop after automated checks, add an artifact, or change review_depth. | Add capability note: how to resume, cancel, or append artifacts to the same run ID. |
| 7 | No dual-output: human report vs LLM distillate for downstream agents | references/feedback-format.md:38 | Downstream fix agents must ingest long Markdown findings. A token-efficient distillate would speed chained workflows. | Offer optional dual-output: full report plus compact findings JSON or bullet distillate. |

**Low-Opportunity:**

| # | Title | File | Detail | Action |
|---|-------|------|--------|--------|
| 1 | Partial review and FAIL verdict ambiguity for consumers | SKILL.md:56 | Orchestrators may not know whether to block the pipeline or continue with degraded confidence. | Add a machine-oriented field: blocking vs non-blocking partial review, or a numeric readiness score. |
| 2 | Mis-invocation redirect names agents but not concrete next prompts | SKILL.md:46 | Redirect text points to Irene, Marcus, and bmad-help without example user phrases per route. | Append example prompts for each redirect target. |
| 3 | Fixed score deduction table may not fit all content types | references/feedback-format.md:85 | Linear deduction model treats all critical findings equally; small quizzes vs full modules might warrant weighting. | Allow optional content_type multipliers from tool_policies.yaml. |
| 4 | Expert path could skip narrative when payload is complete | SKILL.md:12 | Experts supplying all required fields still go through the same activation narrative as exploratory users. | Document a compact activation phrase that skips greeting and jumps to review-protocol execution. |
| 5 | Environment check lists dependencies but not remediation order | references/init.md:17 | When several dependencies are missing, user gets partial review but no suggested fix order. | Add a prioritized recovery list: which missing dependency blocks which dimensions. |

**Top Insights:**

1. **Add structured IO alongside Markdown reports** — The agent is orchestration-friendly at the input boundary for Marcus but output remains prose-first, which limits reliable chaining in agents and CI. *Action:* Publish a minimal JSON report shape next to feedback-format.md and optionally emit it in headless runs.

2. **Infer or default cross-artifact checks** — Pairing consistency is high value for medical courseware; optional cross_artifact_refs risks silent weakening of that value. *Action:* Default on pairing heuristics when multiple paths are co-submitted unless opted out.

3. **First-message and ad-hoc clarity** — Greeting and persistence rules are the main UX cliffs for humans; the rubric itself is strong. *Action:* Branch greeting on empty history; one-line ad-hoc vs default persistence reminder on activation.

---

## User Journeys

*How different user archetypes experience this agent:*

### First-Timer

Invokes Quinn-R directly; reads strong principles and degradation handling but may freeze on the interactive greeting that expects prior cycle metrics.

**Friction Points:**
- Greeting placeholders without history
- Many parallel loads on activation without a single checklist UI

**Bright Spots:**
- Clear Does Not Do and redirect
- init.md environment checklist
- Dimension-organized feedback format

### Expert

Wants fastest path to a verdict and fix list; appreciates severity discipline but may find Markdown-only output and fixed scoring rigid for automation.

**Friction Points:**
- No documented JSON IO for direct API-style use
- Score formula not tunable per artifact type in-skill

**Bright Spots:**
- Headless Marcus path with explicit required fields
- review_depth optional parameter
- Location-specific feedback norms

### Confused User

Mistook Quinn-R for content author; gets a short redirect.

**Friction Points:**
- Redirect could use example phrases for next step

**Bright Spots:**
- Explicit boundary: no content modification

### Edge-Case User

Submits partial slides, contradictory objectives, or multiple artifacts without explicit pairing hints.

**Friction Points:**
- Optional cross_artifact_refs may silently reduce pairing rigor
- PARTIAL REVIEW vs FAIL semantics for orchestrators

**Bright Spots:**
- Incomplete artifact handling in Degradation Handling
- Multi-artifact section in review-protocol

### Hostile Environment

Style bible missing, scripts fail, or course_context absent.

**Friction Points:**
- Judgment-only fallback lowers confidence but thresholds may still expect automation
- Init remediation order not prioritized

**Bright Spots:**
- Explicit SKIPPED dimension reporting
- Fresh style bible read (no stale cache)

### Automator

CI or another agent invokes after Marcus or tries to mimic Marcus payload.

**Friction Points:**
- Canonical output is Markdown-oriented
- No published minimal schema example in repo for non-Marcus callers

**Bright Spots:**
- Structured outbound field list in SKILL.md
- Logging toggle via run mode

---

## Autonomous Readiness

- **Overall Potential:** easily-adaptable
- **HITL Interaction Points:** 4
- **Auto-Resolvable:** 5
- **Needs Input:** 3
- **Suggested Output Contract:** Return status (pass|pass_with_notes|fail|partial_review), verdict confidence, dimension_scores object, findings[] with severity/dimension/location/description/fix_suggestion, medical_accuracy_flags[], logging_status; optional parallel JSON file path if dual-output added.
- **Required Inputs:** production_run_id, artifact_paths, content_type, producing_specialist, run_mode (default | ad-hoc)
- **Notes:** Headless delegation from Marcus is already specified; biggest gap is machine-readable report parity and documented request schema for non-Marcus automators. Interactive value remains for calibration and exploratory audits.

---

## Script Opportunities

**Existing Scripts:** None in agent directory (architecturally correct — deterministic checks are owned by companion quality-control skill).

| # | Severity | Title | File | Detail | Action |
|---|----------|-------|------|--------|--------|
| 1 | medium | Dimension scores and overall verdict are deterministic functions of finding severities | references/feedback-format.md:85 | Token savings: 100-300 per report. Complexity: trivial. Language: Python. Reusable: yes. The model re-derives subtraction rules and thresholds from prose each run. | Add a small post-processor (under quality-control or shared tooling) that accepts structured findings + thresholds and emits dimension_scores, pass/fail, and overall verdict JSON. |
| 2 | low | First-run environment path checks are pure filesystem verification | references/init.md:17 | Token savings: <100 per onboarding. Complexity: trivial. Could be prepass. | Optional verify_paths script that checks all dependencies and emits a JSON readiness block. |
| 3 | low | Multi-artifact pairing and lesson-plan references are partially pattern-checkable | references/review-protocol.md:73 | Token savings: 150-400 on multi-file reviews. Complexity: moderate. Could be prepass. | Pre-pass script to extract declared artifact IDs, LP references, and cross-artifact pointers. |
| 4 | low | Access-boundary checks are allowlist/denylist logic | references/memory-system.md:28 | Complexity: moderate (must stay in sync with documented zones). | Consider a shared path-guard utility that validates paths against documented read/write/deny zones. |

**Token Savings:** ~350-800 estimated total | Highest value: verdict/score computation post-processor | Prepass opportunities: 2

---

## Quick Wins (High Impact, Low Effort)

| Issue | File | Effort | Impact |
|-------|------|--------|--------|
| Replace hardcoded "Juan" with `{user_name}` or "the human reviewer" | SKILL.md:18,29,38 + memory-system.md:34 | Low | Fixes portability across projects |
| Quote 'quality gate validation' in description triggers | SKILL.md:3 | Trivial | Consistency with sibling trigger phrases |
| Add access-boundaries.md to On Activation parallel batch | SKILL.md:67 | Low | Prevents skipped security file on activation |
| Add IS capability row or annotate QA as covering all 5 dimensions | SKILL.md:81 | Low | Eliminates implementer confusion about instructional soundness |
| Add one-line ad-hoc vs default persistence reminder | SKILL.md:71 | Trivial | Prevents user surprise when calibration doesn't persist |
| Declare quality-control as companion prerequisite | SKILL.md:90 | Low | Clarifies dependencies for standalone installs |

---

## Optimization Opportunities

**Token Efficiency:**
The agent's token footprint is already well-managed at ~3k tokens for SKILL.md with procedure depth deferred to references. The primary token waste is the model recomputing deterministic score/verdict arithmetic from prose on every report — a trivial post-processor script (est. 100-300 tokens/report saved) would eliminate this. Selective sidecar loading and batched cold reads are already implemented strengths.

**Performance:**
Wall-clock time for reviews could be reduced by adding explicit guidance to run accessibility_checker.py and brand_validator.py in parallel rather than sequentially. For multi-artifact reviews at scale, optional parallel subagent fan-out per artifact pair would cap context growth. Both are low-effort documentation changes.

**Maintainability:**
Three changes would improve long-term maintainability: (1) replacing hardcoded reviewer name with config variables across 4 locations, (2) consolidating or clarifying the four capability codes (QA/CC/BV/LA) that route to the same protocol file, and (3) adding a companion skills prerequisite section so future maintainers know which external assets are expected.

---

## Recommendations

1. **Define structured JSON output alongside Markdown reports** — This is the highest-value enhancement. Add an optional JSON report schema (verdict, dimension_scores, findings array) so downstream agents and CI pipelines can consume Quinn-R output without scraping prose. *(high-opportunity, affects automator and expert journeys)*

2. **Replace hardcoded reviewer name with `{user_name}` or neutral phrasing** — Affects 4+ locations across SKILL.md and memory-system.md. Trivial effort, eliminates a portability defect that breaks the agent's config-driven design. *(low severity, high breadth, low effort)*

3. **Clarify the capability table: add instructional soundness, scope CC, and document alias pattern** — The four codes routing to one file and the missing IS dimension create implementer confusion. Either merge QA/CC/BV/LA into one documented workflow entry or annotate them as aliases. *(4 low-severity cohesion findings, moderate breadth)*

4. **Branch greeting on empty history and add ad-hoc persistence reminder** — The interactive greeting assumes prior cycle stats that first-timers lack, and ad-hoc mode's ephemeral nature is not surfaced to users. Two small text additions fix the main UX friction points. *(medium-opportunity, low effort)*

5. **Add a verdict/score post-processor script to quality-control** — The only medium-severity issue: deterministic arithmetic (deduction rules, thresholds, pass/fail) is re-derived from prose on every report. A trivial Python script would save 100-300 tokens per report and reduce computation error risk. *(medium severity, trivial effort)*
