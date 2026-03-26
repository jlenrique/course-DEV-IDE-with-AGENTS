# Woodshed Workflow

The "woodshed" is a musician's term for the practice room — where you go to hone your craft through deliberate, repeated practice. In this system, an agent goes to the woodshed to study exemplar artifacts and prove it can reproduce them programmatically.

## Three Modes

### 1. Learn New Exemplar (Faithful Reproduction)

Use when a new exemplar is added to an agent's `resources/exemplars/{tool}/` library. The goal is **exact reproduction** — proving the agent has full control of the tool's parameters and can make it produce precisely what is specified. This is about fluency, not creativity.

```
DOC REFRESH (mandatory before first attempt; see doc-refresh-protocol.md)
  0. Load doc-sources.yaml from the mastery skill's references/
  1. Check tool changelog for changes since last_refreshed date
  2. If changes found: scan affected doc pages via Ref MCP, update parameter-catalog.md
  3. Update last_refreshed timestamp and log discoveries to memory sidecar

STUDY
  1. Read brief.md — understand context, quality markers, what makes it good
  2. Examine source/ artifacts — analyze structure, parameters, creative choices
  3. Consult parameter-catalog.md and current API docs to identify optimal parameters
  4. Draft reproduction-spec.yaml — the agent's plan for programmatic recreation

REPRODUCE
  4. Execute reproduction via API/MCP using the spec
  5. Request EXPORTABLE output (e.g., Gamma: `exportAs: "pdf"` or `"pptx"`; ElevenLabs: audio file)
  6. Download the exported artifact to reproductions/{timestamp}/output/ (always retained — pass or fail)
  7. Save detailed run log to reproductions/{timestamp}/run-log.yaml (see Run Logging below)

  NOTE: Screenshots are for quick visual checks only. Production artifacts must be
  downloaded in their native format (PDF, PPTX, MP3, etc.) for comparison, assembly,
  and downstream workflow use. The export URL is time-limited (~7 days for Gamma)
  so download immediately after generation completes.

COMPARE
  7. Score reproduction against source using comparison-rubric-template.md
  8. Save comparison to reproductions/{timestamp}/comparison.yaml
  9. Determine pass/fail against rubric thresholds

REFLECT (if failed)
  10. Analyze comparison gaps — what specifically was wrong
  11. Diagnose root cause of sub-par performance
  12. Predict how performance might be improved (document in reflection.md)
  13. Update reproduction-spec.yaml with corrections
  14. Return to REPRODUCE step (subject to Circuit Breaker limits)

REGISTER
  15. If passed → update _catalog.yaml: status → mastered, record mastered_at date
  16. Save learned patterns to agent's memory sidecar (patterns.md)
  17. If circuit breaker tripped → log structured failure report (see Give-Up Protocol)
```

### 2. Creative Enhancement

Use AFTER an exemplar has been mastered in faithful mode. The agent reproduces the exemplar's *intent* but has creative freedom to enhance — better layout, stronger visual hierarchy, improved density or flow. The goal is proving **creative judgment**, not just tool control.

```
STUDY (same as faithful — brief, source, style guide)

REPRODUCE (creative freedom)
  1. Execute reproduction with agent's own creative choices
  2. May use different layout, imagery, density — but must preserve original intent and content
  3. Save output + run-log.yaml with creative rationale documented

COMPARE (shifted rubric)
  4. Structural fidelity weight drops to Medium (creative departures are expected)
  5. Creative quality weight rises to High (this is what's being tested)
  6. Content completeness stays Medium (core content must be preserved)
  7. A new dimension — "creative rationale" — requires the agent to explain WHY it made each departure

REGISTER
  8. If passed → update _catalog.yaml: creative_status → enhanced
  9. Save creative patterns to memory sidecar
```

**Sequencing rule**: An exemplar must be mastered in faithful mode (status: `mastered`) before creative mode is unlocked. You must prove you can play the sheet music before you improvise.

**Level/scale feedback**: In creative mode, the agent may propose changes to an exemplar's difficulty level or the scale itself. For example: "I think L2 should be L1 because the layout is simpler than the parallel comparison." This is encouraged as a sign of developing judgment.

### 3. Regression Run

Use to verify the agent hasn't lost mastery of previously mastered exemplars. Run before attempting new exemplars, or on demand.

```
For each exemplar with status: mastered in _catalog.yaml:
  1. Load reproduction-spec.yaml
  2. Execute reproduction via API/MCP
  3. Save output to reproductions/{timestamp}/output/ (always retained)
  4. Save run log to reproductions/{timestamp}/run-log.yaml
  5. Compare output against source/ using rubric
  6. If pass → confirm mastery holds
  7. If fail → flag regression, add to remediation queue
  8. Agent does NOT attempt new exemplars until regressions are resolved
```

---

## Run Logging

Every reproduction attempt generates a detailed run log at `reproductions/{timestamp}/run-log.yaml`. This log captures everything needed to understand, debug, and improve the attempt.

### Run Log Schema

```yaml
exemplar_id: "001-simple-lecture-deck"
tool: gamma
agent: bmad-agent-gamma
timestamp: "2026-03-28T14:30:00"
attempt_number: 1              # increments across sessions for this exemplar

# What was being reproduced
source_exemplar:
  brief_path: "resources/exemplars/gamma/001-simple-lecture-deck/brief.md"
  source_artifacts: ["source/original-deck.pdf"]
  reproduction_spec_path: "reproduction-spec.yaml"

# Exact API/MCP interaction
api_interaction:
  method: "generate_content"   # API method or MCP tool name
  client: "gamma_client.py"    # which client module was used
  endpoint: "https://api.gamma.app/..."  # actual endpoint hit
  request_payload:             # exact parameters sent
    topic: "Economic Reality of Higher Education"
    num_slides: 10
    theme: "professional-dark"
    style: "lecture"
    additional_instructions: "..."
  prompt_text: |               # if a prompt/instruction was composed, capture it verbatim
    Full prompt text sent to the API...
  mcp_tool_used: null          # or the MCP tool name if MCP was used instead of direct API
  mcp_arguments: null          # exact MCP tool arguments if applicable
  response_status: 200         # HTTP status or MCP result status
  response_summary: "..."      # brief summary of what came back
  latency_ms: 3400             # how long the API call took
  tokens_used: null            # if token usage is reported by the API

# What was produced
output:
  artifacts_saved:             # every file saved in output/
    - "output/api_response.json"
    - "output/presentation_url.txt"
  output_type: "presentation"
  output_format: "url"

# Comparison results (filled after COMPARE step)
comparison:
  rubric_used: "comparison-rubric-template.md"
  scores:
    structural_fidelity: { score: 4, notes: "..." }
    parameter_accuracy: { score: 5, notes: "..." }
    content_completeness: { score: 3, notes: "..." }
    context_alignment: { score: 4, notes: "..." }
    creative_quality: { score: 3, notes: "..." }
  overall_result: "pass"       # pass | conditional_pass | fail
  conclusion: |                # agent's plain-language summary of what the comparison revealed
    The reproduction successfully matched the exemplar's structure and
    parameters. Minor content gaps in the data visualization section...

# Resource usage
resources:
  session_attempt_number: 1    # which attempt this is within the current session
  cumulative_attempts: 1       # total attempts across all sessions for this exemplar
  estimated_token_cost: null   # if trackable
```

### Retention Policy

**All reproduction outputs are retained** — both passing and failing attempts. The `reproductions/` directory is append-only. Each timestamped attempt directory contains:

```
reproductions/{timestamp}/
├── run-log.yaml           # detailed log (schema above)
├── output/                # the actual artifact(s) produced
│   ├── api_response.json  # raw API response
│   └── {artifacts}        # any files/URLs produced
├── comparison.yaml        # rubric scores + conclusion
└── reflection.md          # (failures only) root cause analysis + improvement plan
```

This history enables:
- Comparing attempts side-by-side to see what changed
- Reviewing the exact API calls that produced good vs. bad results
- Understanding whether the agent's reflection led to actual improvement
- Post-mortem analysis when the circuit breaker trips

---

## Reflection Protocol (Between Cycles)

When a reproduction attempt fails the rubric, the agent **must reflect before retrying**. The reflection is saved at `reproductions/{timestamp}/reflection.md`.

### Reflection Template

```markdown
# Reflection: {exemplar_id} — Attempt {N}

## What Failed
[Which rubric dimensions scored below threshold and why]

## Root Cause Analysis
[Agent's diagnosis of WHY the reproduction was sub-par.
 Was it wrong parameters? Missing content? Wrong structure? API limitation?]

## Predicted Improvement
[What specifically will the agent change in the next attempt.
 Which parameters will be adjusted? What content will be added?
 What structural change will be made?]

## Spec Changes
[Exact diff of what changed in reproduction-spec.yaml for the next attempt]

## Confidence Level
[Agent's self-assessed confidence that the next attempt will pass: low/medium/high]
```

The reflection is **mandatory** — the agent cannot retry without documenting what it learned and what it plans to change. This prevents mindless retrying and forces deliberate improvement.

---

## Give-Up Protocol (Circuit Breaker)

An agent cannot attempt reproduction indefinitely. The circuit breaker prevents runaway token consumption and forces structured failure reporting.

### Circuit Breaker Limits

| Limit | Default | Description |
|-------|---------|-------------|
| **max_attempts_per_session** | 3 | Maximum reproduction attempts in a single woodshed session |
| **max_total_attempts** | 7 | Maximum cumulative attempts across all sessions for one exemplar |
| **max_consecutive_no_improvement** | 2 | If rubric scores don't improve for N consecutive attempts, stop |

When any limit is reached, the agent **must stop** and produce a failure report.

### Failure Report

Saved at `resources/exemplars/{tool}/{exemplar_id}/failure-report.yaml`:

```yaml
exemplar_id: "002-module-intro-with-visuals"
tool: gamma
agent: bmad-agent-gamma
failure_date: "2026-04-02"
total_attempts: 7
sessions_spent: 3

# Summary for the human
summary: |
  The Gamma agent was unable to reproduce this exemplar to the required
  standard after 7 attempts across 3 sessions.

# Best attempt achieved
best_attempt:
  timestamp: "2026-04-01_160000"
  scores:
    structural_fidelity: 4
    parameter_accuracy: 3
    content_completeness: 2
    context_alignment: 4
    creative_quality: 2
  gap_summary: "Content completeness and creative quality consistently below threshold"

# What the agent tried
approaches_attempted:
  - attempt: 1
    change: "Initial reproduction from brief analysis"
    result: "Structure correct but content incomplete"
  - attempt: 2
    change: "Added detailed content instructions to prompt"
    result: "Content improved but still missing data visualization section"
  # ... all attempts documented

# Agent's diagnosis of the capability gap
capability_gap_analysis: |
  The Gamma API's content generation does not support embedding specific
  data visualizations from external datasets. The exemplar contains
  custom charts that cannot be reproduced through prompt instructions alone.
  This may require a multi-step workflow: generate base slides, then
  programmatically inject chart images.

# Recommended resolution paths
recommended_actions:
  - "Simplify the exemplar to remove custom data visualizations"
  - "Add a chart generation step before Gamma slide creation"
  - "Provide chart images as additional context to the Gamma API"
  - "Accept this as a manual step in the production workflow"

# Catalog update
catalog_status: "blocked"    # new status: agent cannot master this without help
```

The `_catalog.yaml` entry for this exemplar gets updated to `status: blocked`, which signals to the human that intervention is needed. The agent will not re-attempt blocked exemplars unless the human explicitly resets the status.

### Catalog Status Lifecycle (Updated)

```
untested → attempted → mastered
                |          |
                |          | (regression detected)
                |          ↓
                |      attempted (remediation)
                |
                ↓ (circuit breaker tripped)
             blocked → untested (human resets after addressing gap)
```

---

## Catalog Status Definitions

- **untested**: Exemplar exists in library but agent has not attempted it
- **attempted**: Agent has tried reproduction but not yet passed the rubric
- **mastered**: Agent has produced a passing reproduction; subject to regression checks
- **blocked**: Agent exhausted all attempts and cannot master this exemplar without human intervention; a failure-report.yaml exists documenting the capability gap

## Invocation

The woodshed workflow can be invoked:
- **By the agent itself** during development (study phase of a new story)
- **By the user** saying "go to the woodshed" or "hone your skills on the new exemplars"
- **As a regression check** before any production run that uses the agent's tool

## Difficulty Levels (L-System)

Exemplars use an **L-level** system with dot extensions for within-level granularity:

| Level | Scope | Description |
|-------|-------|-------------|
| **L1** | Single artifact | Basic tool usage, minimal parameters, straightforward structure |
| **L2** | Single artifact | Moderate complexity, specific layout or formatting requirements |
| **L3** | Single artifact | Multiple internal sections, structural precision matters |
| **L4** | Single artifact | Complex layout, assessment/interactive elements, or narrative progression |
| **L5** | Artifact sets | Multi-artifact workflows (e.g., full slide decks, multi-page modules) |

**Dot extensions** (L4.1, L4.2, L5.3) distinguish difficulty within a level when multiple exemplars share the same level.

**Progression rule**: Master L1-L4 (single artifacts) before attempting L5 (artifact sets). Within a level, start with the lowest dot extension.

## DRY Architecture: Common Process + Agent-Specific Evaluation

The woodshed system uses a **base/evaluator pattern** to stay DRY:

- **Common (all agents share)**: `skills/woodshed/scripts/woodshed_base.py`
  - `WoodshedRunner` — orchestrates study → reproduce → compare → reflect → register
  - `BaseEvaluator` — abstract base class for agent-specific evaluation
  - Catalog management, circuit breaker, pass/fail rules, attempt directory creation

- **Agent-specific (each mastery skill provides)**: e.g., `skills/gamma-api-mastery/scripts/gamma_evaluator.py`
  - `analyze_exemplar()` — what makes THIS type of artifact good (slide layout, audio pacing, etc.)
  - `derive_reproduction_spec()` — what API parameters reproduce it
  - `execute_reproduction()` — the actual API/MCP call
  - `compare_reproduction()` — tool-specific comparison logic (structural, content, creative)
  - `get_custom_rubric_weights()` — how to weight rubric dimensions for this tool/level

This separation ensures the workflow engine is written once, while each agent brings its own domain expertise to evaluation.

## Adding New Exemplars

1. Create a numbered directory in `resources/exemplars/{tool}/` (e.g., `002-module-intro-with-visuals/`)
2. Write `brief.md` — what it is, why it's good, what the agent should learn
3. Place source artifact(s) in `source/`
4. Add entry to `_catalog.yaml` with `status: untested`
5. Tell the agent to go to the woodshed

The agent handles the rest: studying the brief, deriving the reproduction spec, attempting reproduction, comparing, reflecting on failures, and registering mastery (or reporting failure if the circuit breaker trips).
