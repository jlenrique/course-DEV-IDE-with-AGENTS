# Quality Report: bmad-agent-gamma

**Scanned:** 2026-03-27T00:08Z
**Skill Path:** skills/bmad-agent-gamma
**Report:** skills/reports/bmad-agent-gamma/quality-scan/2026-03-26_200831/quality-report.md
**Performed By** QualityReportBot-9001

## Executive Summary

- **Total Issues:** 11
- **Critical:** 0 | **High:** 2 | **Medium:** 3 | **Low:** 6
- **Overall Quality:** Good
- **Overall Cohesion:** mostly-cohesive
- **Craft Assessment:** Strong — no critical craft defects; SKILL.md is concise (~109 lines, ~2.5k tokens) with clean progressive disclosure via reference routing; persona voice is appropriate investment for a domain-expert agent.

Gary is a well-designed Gamma slide specialist whose persona, principles, quality rubric, and memory system form a coherent product surface. The two high-severity findings are both **repo-completeness gaps** — the execution stack (gamma-api-mastery skill, GammaEvaluator scripts) referenced throughout SKILL.md and references is absent from the current workspace, which fragments end-to-end user journeys despite strong documentation design. No logic or prompt-craft defects were found.

### Issues by Category

| Category | Critical | High | Medium | Low |
|----------|----------|------|--------|-----|
| Structure & Capabilities | 0 | 0 | 1 | 1 |
| Prompt Craft | 0 | 0 | 0 | 2 |
| Execution Efficiency | 0 | 0 | 1 | 1 |
| Path & Script Standards | 0 | 0 | 0 | 0 |
| Agent Cohesion | 0 | 2 | 1 | 2 |
| Creative | — | — | 7 | 4 |

---

## Agent Identity

- **Persona:** Gary — Slide Architect and Gamma API parameter specialist for medical education slides, delegated from Marcus, honest about embellishment and layout limits.
- **Primary Purpose:** Choose Gamma parameters, invoke API execution via gamma-api-mastery, assess slide quality, persist learnings, and support woodshed exemplar mastery.
- **Capabilities:** 8 (6 internal: PR, SG, QA, ES, CT, SM; 2 external: gamma-api-mastery, woodshed)

---

## Strengths

*What this agent does well — preserve these during optimization:*

**Persona & Identity Coherence**
- Identity is actionable and tightly aligned to capabilities — ties physician-audience constraints, Gamma parameter mastery, embellishment awareness, and specialist boundaries to the actual capability table and external skills. *(structure)*
- Persona, principles, and degradation handling align tightly with the Slide Architect role — reads as one coherent product surface rather than a grab bag of prompts. *(agent-cohesion)*

**Communication & Progressive Disclosure**
- Communication style includes concrete, persona-matched examples — parameter tuples, agent-to-agent tone, structured quality scores, and exemplar-grounded language match the delegation model without abstract filler. *(structure)*
- Capabilities table routes depth to references cleanly — SKILL.md stays compact with procedural activation and a matrix pointing to `references/*.md`, matching multi-capability progressive disclosure. *(prompt-craft, enhancement-opportunities)*
- Overview balances mission, domain, and delegation model without redundancy — seven lines covering what Gary does, physician/med-ed framing, Marcus delegation, and woodshed/debug paths. *(prompt-craft)*

**Principles & Decision Frameworks**
- Principles are domain-specific decision frameworks — enforce learning-objective traceability, physician-appropriate visuals, style-guide precedence, Gamma embellishment control, export discipline, and honest scoring. *(structure)*
- Quality rubric matches persona emphasis on honesty and pedagogy — dimensions (brand, fidelity, layout, accessibility, pedagogical alignment, completeness) and L-level weights mirror stated principles. *(agent-cohesion)*

**Activation & Memory Architecture**
- On Activation ordering is logical for config, memory, and modes — loads project config first, then memory sidecar (with init fallback), then branches headless/interactive/woodshed. *(structure)*
- Sidecar uses `index.md` as single memory entry point with selective loading — fallback to `references/init.md` avoids full sidecar when none exists. *(execution-efficiency)*
- Memory sidecar design reinforces learning principle without caching the style bible — default vs ad-hoc write rules, append discipline, and condensation guidance align with principles. *(agent-cohesion)*
- First-run path bridges missing sidecar to concrete next actions via init.md. *(agent-cohesion)*

**Failure Handling**
- Degradation handling is explicit and actionable across API, quality, circuit breaker, and missing context — concrete next steps (retry timing, stronger instructions, Canva fallback, structured failure-report) reduce dead-end frustration. *(enhancement-opportunities)*

**Efficiency Design**
- Capability table loads references only when a route is taken — reduces baseline token use and keeps context aligned to the active task. *(execution-efficiency)*
- Doc refresh and exemplar workflow mix procedure with clear Gary/evaluator split — appropriate intelligence placement. *(prompt-craft)*

---

## Truly Broken or Missing

*Issues that prevent the agent from working correctly:*

### HIGH-1: Documented execution stack for Gamma API is not present in this workspace
**Source:** agent-cohesion | **File:** `SKILL.md:88`

SKILL.md and memory boundaries require `skills/gamma-api-mastery` (and project `api_clients`) for all HTTP operations, but the repository only contains minimal gamma-api-mastery content (e.g., `doc-sources.yaml`) and no SKILL.md, `parameter-catalog.md`, or GammaClient artifacts were found. A user or orchestrator following On Activation and External Skills would hit dead ends for generate/poll/export/download and doc refresh targets.

**Fix:** Add the full gamma-api-mastery skill (SKILL.md, parameter catalog, operations scripts) and Gamma client code referenced in references, or add an explicit repo note in SKILL.md when this agent is distributed without the execution bundle.

### HIGH-2: Woodshed integration references evaluator scripts that are absent
**Source:** agent-cohesion | **File:** `references/exemplar-study.md:41`

Exemplar study names GammaEvaluator, `gamma_evaluator.py`, `gamma_operations.py`, and parameter-catalog refresh paths. Those files are not present in the workspace, so the ES capability and woodshed row in SKILL.md describe a workflow the current tree cannot run. This breaks end-to-end exemplar mastery until the stack exists or docs are scoped to optional.

**Fix:** Either implement the referenced scripts under `skills/gamma-api-mastery` and `skills/woodshed` integration, or revise `exemplar-study.md` and SKILL.md external table to state prerequisites and minimal stubs.

---

## Detailed Findings by Category

### 1. Structure & Capabilities

**Agent Metadata:**
- Sections found: Overview, Identity, Communication Style, Principles, Does Not Do, Degradation Handling, On Activation, Capabilities (Internal, External, Delegation Protocol)
- Capabilities: 8 (6 internal + 2 external)
- Memory sidecar: yes (`_bmad/memory/gamma-specialist-sidecar/index.md`)
- Headless mode: yes
- Structure assessment: Pre-pass reported zero structural issues; all expected sections present with strong identity, examples, and principles.

#### Medium

| # | Title | File | Detail |
|---|-------|------|--------|
| S-M1 | Description trigger clause omits quoted invocation phrases | `SKILL.md:3` | BMad guidelines recommend quoted specific phrases (e.g., `'talk to Gary'`) to reduce ambiguous activations. Current description uses paraphrased triggers without quotes, which is slightly weaker for conservative routing. |

**Action:** Revise the description trigger segment to include explicit quoted phrases, e.g., `Use when the user asks to 'talk to Gary', requests the 'Slide Architect', or needs 'Gamma slides'`.

#### Low

| # | Title | File | Detail |
|---|-------|------|--------|
| S-L1 | Opening summary segment is nine words (guideline 5–8) | `SKILL.md:3` | First sentence counts nine words; one word over the typical 5–8 word summary target. |

**Action:** Optionally tighten to eight words or fewer, e.g., "Gamma slide specialist; full API parameter mastery."

#### Note

- **Sidecar on disk may start with index.md only** (`SKILL.md:62`): `references/memory-system.md` documents `patterns.md`, `chronology.md`, and `access-boundaries.md` under the sidecar but only `index.md` exists on disk. Acceptable if save flows create the other files on first run; if onboarding expects them immediately, add bootstrap templates.

### 2. Prompt Craft

**Agent Assessment:**
- Agent type: domain-expert
- Overview quality: appropriate (7 lines, load-bearing for judgment, not redundant with Identity)
- Progressive disclosure: good (109 lines with capability matrix routing to references)
- Persona context: appropriate (examples are intentional persona investment)
- Notes: ~2.5k tokens estimated; Principles and Does Not Do add constraints without philosophical bloat. No inline data extraction needed.

#### Low

| # | Title | File | Detail |
|---|-------|------|--------|
| PC-L1 | No formal progression markers on SKILL.md | `SKILL.md:55` | Pre-pass reported `has_progression: false`. On Activation branches Headless/Interactive/Woodshed with distinct load steps, so behavior is not under-specified; gap is metadata/convention alignment if downstream tooling expects explicit progression blocks. |
| PC-L2 | Reference prompts assume SKILL.md persona and config context | `references/parameter-recommendation.md:8` | Zero root-level capability `.md` files (pre-pass `total_prompts: 0`). Reference files omit YAML config headers with `{communication_language}`; under heavy context compaction, an executing model might lack language variables unless SKILL.md remains loaded. Mild risk, not a broken self-reference pattern. |

**Action (PC-L1):** If BMAD pipelines require progression fields, add concise explicit gates without duplicating reference bodies.
**Action (PC-L2):** Optional — add a one-line session anchor to highest-traffic references, or introduce thin root stubs that repeat config header and link to references.

### 3. Execution Efficiency

#### Medium

| # | Title | File | Detail |
|---|-------|------|--------|
| EE-M1 | On Activation lists independent reads without parallel batching guidance | `SKILL.md:57` | Loads `_bmad/config.yaml`, optional `config.user.yaml`, `references/memory-system.md`, sidecar `index.md` or `init.md`, and `style_guide.yaml` as a linear list. These I/Os have no hard ordering; serial tool rounds add latency versus one batched parallel read pass. |

**Action:** Add an explicit line: when using file tools, issue parallel reads for config files, memory-system.md, sidecar index (or init), and style_guide.yaml in one round unless a parse result gates the next step.

#### Low

| # | Title | File | Detail |
|---|-------|------|--------|
| EE-L1 | First-interaction onboarding steps are fully sequential | `references/init.md:19` | Gamma connectivity check, style guide read, and report are listed sequentially. The style guide read does not depend on API success; partial parallelization may save a small fraction of first-run time. |

**Action:** Where the runtime allows, run connectivity preflight and `style_guide.yaml` read in parallel, then synthesize the greeting from both outcomes.

**Optimization Opportunities:**

| # | Title | File | Savings | Detail |
|---|-------|------|---------|--------|
| EE-OP1 | Doc refresh can batch parallel Ref MCP fetches | `references/exemplar-study.md:11` | Proportional to page count | Multiple independent URL reads typical; batching in one message reduces latency. |

**Action:** When multiple parameter docs need refresh, fetch all affected URLs in parallel in a single tool batch, then merge updates into `parameter-catalog.md`.

### 4. Path & Script Standards

**Script Inventory:** 0 scripts (no `scripts/` directory) | No tests to assess.

Path standards scan returned zero findings — all paths in skill files follow conventions. Clean pass.

### 5. Agent Cohesion

**Cohesion Analysis:**

| Dimension | Score | Notes |
|-----------|-------|-------|
| Persona Alignment | strong | Expertise, communication style, principles, QA rubric, and degradation handling consistently support a parameter-savvy, pedagogy-first specialist. |
| Capability Completeness | gaps-obvious | On paper the lifecycle (recommend, generate, assess, export, remember) is complete; in-repo artifacts for API and woodshed execution are the main holes. |
| Redundancy Level | some-overlap | Parameter merge order repeated across `parameter-recommendation.md` and `style-guide-integration.md`. |
| External Integration | intentional | gamma-api-mastery and woodshed are first-class; production-coordination appears only in SG write-back and should be surfaced the same way. |
| User Journey | fragmented | Documentation supports end-to-end flows; current workspace layout does not fully instantiate them. |

**Consolidation Opportunities:**

- **PR parameter merge / SG merge logic / CT usage merge** — parameter priority appears in `parameter-recommendation.md` and `style-guide-integration.md` with slightly different ordering labels. Define a single canonical merge-order subsection in one reference; have others link to it with one sentence each.

#### Medium

| # | Title | File | Detail |
|---|-------|------|--------|
| AC-M1 | Style guide write-back routes through an unlisted external skill | `references/style-guide-integration.md:41` | SG documents persistence via production-coordination and `manage_style_guide.py`, but SKILL.md External Skills only lists gamma-api-mastery and woodshed. Hidden dependency in the learning loop. |

**Action:** Add production-coordination (or the exact script path) to External Skills with status and context, or fold write-back steps into `save-memory.md` with explicit orchestration notes for Marcus.

#### Low

| # | Title | File | Detail |
|---|-------|------|--------|
| AC-L1 | Frontmatter trigger emphasizes direct user chat while body centers Marcus delegation | `SKILL.md:3` | Description invites talking to Gary for slides; Overview states Gary communicates primarily with Marcus in standard production. Tension is mostly resolved by interactive vs headless sections but can confuse routing expectations. |
| AC-L2 | Parameter merge order is repeated across multiple references | `references/parameter-recommendation.md:13` | Concepts align but duplication increases drift risk if one file is updated without the other. |

**Action (AC-L1):** Tweak description to mention orchestrated workflows and optional direct woodshed/debug mode.
**Action (AC-L2):** Define a single canonical merge-order subsection in one reference; have others link with one sentence.

**Creative Suggestions:**

- **Optional delegation checklist** (`SKILL.md:66`, source: agent-cohesion): Capabilities chain logically (CT/PR → gamma-api-mastery → QA → SM/SG) but are spread across files. A short 6–10 step numbered checklist in On Activation or Capabilities (envelope parse → style guide + CT → call API skill → export/download → QA block → memory/style write-back) linking to existing reference anchors would strengthen user-journey coherence without adding new capabilities.

- **Style guide YAML read deduplication** (`references/parameter-recommendation.md:7`, source: execution-efficiency): `parameter-recommendation.md` and `style-guide-integration.md` both instruct reading `style_guide.yaml` at invocation. Tasks that route through PR then SG (or vice versa) may repeat the same read. State in SKILL or cross-references: one read of `tool_parameters.gamma` per task satisfies both capabilities; subsequent steps reuse the loaded block.

### 6. Creative (Edge-Case & Experience Innovation)

**Agent Understanding:**
- **Purpose:** Act as Gary, a Gamma API slide specialist for medical education: merge style guide and envelopes, recommend parameters, invoke gamma-api-mastery, assess quality, persist learning to a memory sidecar, and support woodshed exemplar mastery.
- **Primary User:** Marcus orchestrator (primary production path); course authors and power users for direct woodshed, debugging, and exemplar study.
- **Key Assumptions:**
  - Marcus supplies a sufficiently complete context envelope when delegating
  - `style_guide.yaml` and `course_context.yaml` exist at expected paths when needed
  - Audience is physician-oriented unless envelope overrides; templates are medically framed
  - gamma-api-mastery and optionally woodshed and production-coordination tooling are available
  - English/default BMad language config unless config overrides

**Enhancement Findings:**

#### High-Opportunity

| # | Title | File | Detail |
|---|-------|------|--------|
| CR-H1 | Context envelope fields described in prose but not as a machine-checkable contract | `SKILL.md:97` | Marcus delegation lists production run ID, content type, objectives, constraints, style sections, and exemplar refs — but no canonical schema, required vs optional fields, or example envelope. Automators and Marcus implementations may diverge silently. |
| CR-H2 | Power users with a complete envelope still share the same activation narrative as explorers | `SKILL.md:14` | Experts who already have YAML parameters, a frozen style guide, and a content type want to skip greeting and mastery small talk. No crisp `expert_fast_path` trigger phrase or envelope flag to jump straight to invoke gamma-api-mastery + QA return. |

**Action (CR-H1):** Add `references/context-envelope-schema.md` (or a YAML example) with required keys, optional keys, and one full golden envelope for headless and orchestrator tests.
**Action (CR-H2):** Document `expert_fast_path` or equivalent: if envelope contains `parameters_ready: true` and full Gamma parameter block, skip interactive greet and woodshed prompts; execute merge order and return.

#### Medium-Opportunity

| # | Title | File | Detail |
|---|-------|------|--------|
| CR-M1 | First-timer meets 'woodshed' without plain-language onboarding | `SKILL.md:69` | Interactive activation assumes the user knows what woodshed means, what exemplar L-levels are, and why mastery order matters. |
| CR-M2 | Structured return to Marcus lacks a versioned output contract | `SKILL.md:104` | Outbound bullets name artifact path, scores, parameter decisions, and flags, but chained agents and CI cannot rely on a single parseable shape. |
| CR-M3 | Gamma API pre-flight failure leaves first-run underspecified | `references/init.md:21` | No prescribed user-visible fallback if credentials are missing, .env is denied, or the client errors. |
| CR-M4 | Write-back depends on production-coordination skill that may be absent | `references/style-guide-integration.md:43` | In a minimal checkout, Gary can read defaults but silently cannot persist learning, creating success amnesia. |
| CR-M5 | Doc refresh is mandatory before woodshed but has no soft gate or time-box | `references/exemplar-study.md:15` | No "use last refresh if less than N days" or skip option — can feel ceremonious for experts or stall creative flow. |
| CR-M6 | Quality assessment is single-lens self-scoring with no parallel review | `references/quality-assessment.md:6` | High-stakes slides might benefit from a second lens (skeptic on embellishment, accessibility spotter) before Marcus approves. |

#### Low-Opportunity

| # | Title | File | Detail |
|---|-------|------|--------|
| CR-L1 | Templates assume medical physician audience; non-clinical courses map through medical framing | `references/content-type-mapping.md:93` | When envelope.audience differs from template, tone/audience strings skew Gamma's text generation. |
| CR-L2 | Session end and 'meaningful learning' are subjective for when to save | `references/save-memory.md:11` | Risk of lost transient index context or over-writing ad-hoc sections without user confirmation. |
| CR-L3 | User who invoked Gary by mistake has no scripted wrong-agent recovery | `SKILL.md:46` | No single-line redirect to bmad-help or Marcus beyond staying in persona. |
| CR-L4 | Ad-hoc mode read-only sidecar is correct but invisible to the delegating user | `references/memory-system.md:26` | Marcus or the user may not realize experimental runs do not update patterns. |

**Top Insights:**

1. **Version the context envelope and Gary return payload** — Orchestration and CI reliability jump when Marcus and Gary agree on required keys and a single parseable return shape. *Action:* Add small schema docs plus one golden example for each direction; reference them from SKILL.md.

2. **Expert fast-path is the highest-leverage delight win** — Reduces perceived latency and token cost for repeat users who already mastered parameters. *Action:* Document envelope flag and behavior: skip greet, run merge + API + QA, return.

3. **Optional second-lens QA before handoff** — Protects publication quality when self-scores are borderline or embellishment is detected. *Action:* Gate a cheap adversarial rubric pass on threshold triggers rather than always-on cost.

---

## User Journeys

*How different user archetypes experience this agent:*

### First-Timer

Opens Gary, sees mastery counts and woodshed — may not know execution order or that Marcus normally delegates; may wander into references without a single happy path.

**Friction Points:**
- Jargon (woodshed, L-levels) without inline definitions
- Choosing between interactive vs headless description

**Bright Spots:**
- Clear Does Not Do and Principles
- init.md for first-run sidecar creation

### Expert

Has parameters and content ready; wants one-shot generation and terse return — may find greeting and exemplar status noise.

**Friction Points:**
- No documented expert fast-path flag
- Doc refresh before every woodshed cycle

**Bright Spots:**
- Parameter-precise communication style
- Merge order documented in SG and PR

### Confused

Invoked Gary for non-slide work; Gary stays in specialist persona.

**Friction Points:**
- No explicit handoff line to general help or PM agents

**Bright Spots:**
- Narrow scope reduces misleading answers if user corrects intent

### Edge-Case

Valid but odd input — new content type, contradictory style overrides, or preserve mode with very long input.

**Friction Points:**
- Closest-template heuristic may miss pedagogical intent
- Gamma embellishment despite constraints

**Bright Spots:**
- CT capability documents extension to patterns.md
- Embellishment detection in QA

### Hostile Environment

Missing files, API down, Ref MCP unavailable for doc refresh, or write-back script missing.

**Friction Points:**
- Init pre-flight under-specified
- Silent inability to persist style learning if script missing

**Bright Spots:**
- Degradation section covers 429 and quality failures
- Ad-hoc mode protects production memory

### Automator

CI or subagent passes envelope and expects deterministic artifact path and parseable status.

**Friction Points:**
- No versioned envelope/return schema
- Human gates implied for woodshed and approval write-back

**Bright Spots:**
- Headless delegation path described in On Activation
- YAML examples for parameters and quality_assessment

---

## Autonomous Readiness

- **Overall Potential:** partially-adaptable
- **HITL Interaction Points:** 9
- **Auto-Resolvable:** 4
- **Needs Input:** 5
- **Suggested Output Contract:** Parseable object (YAML or JSON) with keys: `schema_version`, `production_run_id`, `artifact_paths[]`, `quality_assessment` (dimensions + embellishment flags), `parameter_decisions`, `recommendations[]`, `memory_mode`, `errors[]`. Optional markdown summary for human inbox.
- **Required Inputs:**
  - `content_type` or equivalent pedagogical description
  - `learning_objectives` or explicit waiver flag from Marcus
  - source content or `inputText`
  - `production_run_id`
  - `style_guide` path readable or embedded overrides
- **Notes:** Production delegation from Marcus is largely automatable when the envelope is complete. Woodshed, doc refresh policy, user approval for style write-back, and ambiguous objectives remain fundamentally HITL. An explicit headless/expert flag would unlock most friction for pipelines without diluting interactive mastery flows.

---

## Script Opportunities

**Existing Scripts:** none (no `scripts/` directory)

| # | Sev | Title | File | Savings | Prepass | Reusable |
|---|-----|-------|------|---------|---------|----------|
| SO-H1 | high | Context envelope parsing and field extraction delegated to the LLM | `SKILL.md:67` | 200–600 tok/delegation | yes | yes (Marcus envelopes) |
| SO-H2 | high | Condensation trigger uses numeric thresholds the LLM must estimate by reading files | `references/save-memory.md:47` | 300–800 tok/check | yes | yes (append-only memory) |
| SO-H3 | high | Doc refresh pipeline: read YAML sources, compare dates, flag stale docs | `references/exemplar-study.md:9` | 500+ tok | yes | yes (doc-sources.yaml) |
| SO-M1 | medium | LLM loads and merges BMAD YAML config on every activation | `SKILL.md:57` | 120–250 tok/invocation | yes | yes (shared config merge) |
| SO-M2 | medium | Interactive greeting asks the LLM to compute exemplar mastery counts | `SKILL.md:70` | 80–200 tok/activation | yes | yes (woodshed catalog) |
| SO-M3 | medium | Woodshed activation: catalog load and circuit-breaker checks are rule-based | `SKILL.md:73` | 100–400 tok/session | yes | partial |
| SO-M4 | medium | First-run sidecar file and directory initialization described as LLM steps | `references/init.md:6` | 150–400 tok (one-shot) | no | yes (agent sidecar template) |
| SO-M5 | medium | Documented parameter merge order is a deterministic deep-merge over YAML sources | `references/style-guide-integration.md:21` | 200–500 tok/recommendation | yes | yes |
| SO-M6 | medium | Structured fields from exemplar brief.md listed for manual extraction | `references/exemplar-study.md:19` | 150–400 tok/exemplar | yes | partial |
| SO-M7 | medium | Markdown exemplar table duplicates authoritative _catalog.yaml | `references/exemplar-study.md:56` | 50–150 tok/edit | yes | yes |
| SO-M8 | medium | quality_assessment YAML structure could be validated after LLM fills scores | `references/quality-assessment.md:29` | 100–300 tok/return | no | yes |
| SO-L1 | low | Parameter recommendation YAML block is schema-validatable | `references/parameter-recommendation.md:48` | 50–120 tok/invocation | no | partial |
| SO-L2 | low | Sidecar expected file layout could be linted without LLM inspection | `references/memory-system.md:9` | 80–150 tok | yes | yes |

**Token Savings:** ~2.0k–4.5k tokens per full session (activation + delegation + woodshed + save-memory checks) | Highest value: context envelope parse/validate + doc refresh staleness pipeline + patterns.md condensation metrics | Prepass opportunities: 9 of 13 findings

---

## Quick Wins (High Impact, Low Effort)

| Issue | File | Effort | Impact |
|-------|------|--------|--------|
| Add quoted trigger phrases in description | `SKILL.md:3` | trivial | Improves routing precision for skill activation |
| Add production-coordination to External Skills table | `SKILL.md:88` | trivial | Closes hidden dependency; makes learning-loop discoverable |
| Tweak description to mention orchestrated workflows | `SKILL.md:3` | trivial | Aligns frontmatter with body's Marcus-delegation focus |
| Canonical merge-order subsection in one reference | `references/parameter-recommendation.md` | low | Eliminates drift risk between PR and SG merge docs |
| Add wrong-agent one-line redirect | `SKILL.md:46` | trivial | Prevents confused users from getting stuck in specialist persona |
| Exemplar mastery count script | `SKILL.md:70` | trivial | Saves 80–200 tokens/activation; deterministic, reusable |

---

## Optimization Opportunities

**Token Efficiency:**
The agent is already strong on selective loading — references are loaded only when a capability route is taken, and the memory sidecar uses an `index.md` entry point before deeper files. The main token wins come from scripting deterministic work currently done by the LLM: config YAML merging (~120–250 tok/invocation), envelope parsing (~200–600 tok/delegation), and patterns.md condensation threshold checks (~300–800 tok/check). Aggregate savings of 2.0k–4.5k tokens per full session are achievable with 4–5 small scripts.

**Performance:**
Cold-start latency can be reduced by explicitly batching parallel reads for config files, memory-system.md, sidecar index, and style_guide.yaml in a single tool round. Doc refresh pipeline benefits from parallel Ref MCP URL fetches when multiple parameter pages need scanning. First-run onboarding can partially parallelize connectivity preflight with style guide read.

**Maintainability:**
The parameter merge order is documented in two references with slightly different framing — consolidating to a single canonical source linked from both eliminates drift risk. Context envelope and return payload schemas should be formalized to prevent silent divergence between Marcus and Gary implementations. Adding production-coordination to the External Skills table makes all dependencies explicit and auditable.

---

## Recommendations

1. **Ship or stub the gamma-api-mastery execution stack** — The two high-severity gaps (missing GammaClient, evaluator scripts, parameter catalog) block every production and woodshed workflow. Either add the full skill or add explicit "prerequisites not yet available" guards in SKILL.md and references to prevent dead-end activation.

2. **Formalize context envelope and return payload schemas** — Add `references/context-envelope-schema.md` with required/optional keys and one golden example. Define a stable `gary_return` schema with version field. This is the single highest-leverage improvement for automation and orchestration reliability.

3. **Add production-coordination to External Skills and batch activation reads** — Two trivial changes: list the hidden external dependency so the learning loop is discoverable, and add one line to On Activation enabling parallel config/memory/style reads to cut cold-start latency.

4. **Document expert fast-path flag** — An envelope flag (`parameters_ready: true`) that skips greeting, exemplar status, and woodshed prompts is the highest-leverage delight win for repeat users and pipeline callers, reducing both perceived latency and token cost.

5. **Implement 3–4 highest-value prepass scripts** — Config merge, envelope validator, patterns.md condensation metrics, and catalog count scripts would save ~1.5k–3k tokens per session and are all reusable across other agents. Start with envelope validation (SO-H1) and condensation trigger (SO-H2) for immediate ROI.
