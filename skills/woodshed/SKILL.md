---
name: woodshed
description: "Exemplar-driven agent skill development and regression testing. Agents study exemplar artifacts, reproduce them programmatically via API/MCP, and prove mastery through structured comparison."
---

# Woodshed — Exemplar Mastery Skill

## Purpose

Enable any specialist agent to **study** exemplar artifacts, **reproduce** them programmatically through the tool's API or MCP, and **prove mastery** through structured comparison against the original. Supports progressive skill development and regression testing to ensure mastery is never lost.

## When to Use

- During specialist agent development (Story 3.x) to validate the agent can actually produce quality output
- When Juan adds new exemplars to an agent's library and says "go to the woodshed"
- Before production runs as a confidence check (regression mode)
- When refining agent skills after quality feedback

## Workflow

Read `resources/exemplars/_shared/woodshed-workflow.md` for the complete study → reproduce → compare → refine → register workflow.

## Key Paths

| Path | Purpose |
|------|---------|
| `resources/exemplars/{tool}/` | Exemplar library per tool |
| `resources/exemplars/{tool}/_catalog.yaml` | Registry of exemplars with mastery status |
| `resources/exemplars/{tool}/{id}/brief.md` | Annotation: what it is, why it's good, what to learn |
| `resources/exemplars/{tool}/{id}/source/` | The actual exemplar artifact(s) |
| `resources/exemplars/{tool}/{id}/reproduction-spec.yaml` | API parameters for reproduction |
| `resources/exemplars/{tool}/{id}/reproductions/` | Timestamped reproduction attempts + comparisons |
| `resources/exemplars/{tool}/{id}/failure-report.yaml` | Structured failure report (if circuit breaker tripped) |
| `resources/exemplars/_shared/comparison-rubric-template.md` | Scoring rubric for comparisons |
| `resources/exemplars/_shared/woodshed-workflow.md` | Complete workflow protocol (includes run logging, reflection, and give-up protocol) |

## Per-Attempt Artifacts (Always Retained)

Every reproduction attempt — pass or fail — produces a full record:

```
reproductions/{timestamp}/
├── run-log.yaml       # exact API call, prompt, MCP interaction, response, comparison conclusion
├── output/            # the actual artifact(s) the agent produced (always kept)
├── comparison.yaml    # rubric scores + agent's conclusion
└── reflection.md      # (failures only) root cause analysis + predicted improvement
```

## References

- `references/comparison-rubric.md` — how to score reproductions
- `references/reproduction-spec-schema.md` — schema for reproduction spec files
- `resources/exemplars/_shared/doc-refresh-protocol.md` — how agents refresh tool docs before woodshed cycles

## Documentation Refresh

Every woodshed cycle begins with a **mandatory doc refresh**. Each mastery skill maintains a `references/doc-sources.yaml` listing authoritative URLs, LLM-optimized endpoints, and changelog locations for its tool. Before studying any exemplar, the agent:

1. Checks the tool's changelog for changes since `last_refreshed`
2. Scans for new/changed parameters via Ref MCP (`ref_search_documentation`, `ref_read_url`)
3. Updates the baseline `parameter-catalog.md` if changes are found
4. Logs discoveries to its memory sidecar

This ensures agents never attempt reproduction with stale API knowledge. See `resources/exemplars/_shared/doc-refresh-protocol.md` for the full protocol.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/woodshed_base.py` | **Common base classes**: `BaseEvaluator` (abstract), catalog/circuit-breaker/pass-fail utilities |
| `scripts/study_exemplar.py` | Parse exemplar brief + source, generate reproduction spec draft |
| `scripts/reproduce_exemplar.py` | Execute reproduction via API client, save output + run log |
| `scripts/compare_reproduction.py` | Score reproduction against source using rubric |
| `scripts/run_regression.py` | Reproduce all mastered exemplars, flag regressions |

## DRY Architecture

The woodshed owns the **process**. Each mastery skill owns the **evaluation intelligence**.

- `woodshed_base.py` defines `BaseEvaluator` — abstract methods that every specialist agent's mastery skill must implement: `analyze_exemplar()`, `derive_reproduction_spec()`, `execute_reproduction()`, `compare_reproduction()`
- Example: `skills/gamma-api-mastery/scripts/gamma_evaluator.py` extends `BaseEvaluator` with Gamma-specific slide analysis, API parameter derivation, and visual comparison logic
- The woodshed runner calls the evaluator — it never needs to know whether it's comparing slides, audio, or LMS deployments

## Evaluator Design Requirements (Mandatory for All Specialist Agents)

These requirements were established during Gary (Gamma specialist) development and apply to every evaluator built for Stories 3.2-3.8. They exist because a rubber-stamp evaluator that checks process compliance ("did a file download?") instead of actual output quality is worse than no evaluator — it gives false confidence.

### 1. Guide the tool's intelligence — never suppress it

Every creative tool has a core strength. The evaluator's `derive_reproduction_spec()` must craft instructions that GUIDE the tool toward the desired outcome, not suppress its capabilities. Rich instructions describing the desired result outperform restrictive constraints that strip the tool's design intelligence.

| Tool | Guide (correct) | Suppress (wrong) |
|------|-----------------|-------------------|
| Gamma | "Two-column comparison with medical icons" | "No images, no additions" |
| ElevenLabs | "Warm professional tone, emphasis on clinical terms" | "Read exactly as written, no inflection" |
| Canva | "JCPH brand kit, data visualization style" | "Plain text only, no templates" |
| Kling | "Subtle data animation, reveal sequentially" | "Static frame, no transitions" |
| Qualtrics | "Branch on Q3 response, skip logic for experienced" | "Simple list of questions" |

### 2. Extract and compare actual output — not just process metadata

The evaluator's `compare_reproduction()` must perform **medium-specific output extraction** and compare against the source content. Checking "did a file download?" is not comparison.

| Tool | Output | Extraction Method |
|------|--------|-------------------|
| Gamma | PNG/PDF slides | PDF text extraction (pymupdf), file size as visual richness signal |
| ElevenLabs | MP3 audio | Duration vs expected read time, speech-to-text for pronunciation |
| Canva | PNG/SVG graphics | Color extraction for brand compliance, text OCR |
| Kling | MP4 video | Frame extraction, duration, scene detection |
| Qualtrics | JSON survey | Question count, logic path validation, response type coverage |

### 3. Score based on content coverage — not exact text match

Compare source KEY WORDS and PHRASES against the reproduction. The tool may enhance, restructure, or add contextual sub-descriptions — this is usually beneficial, not a failure. Only flag additions that change meaning, add wrong content, or violate the professional aesthetic.

### 4. Use a cheap quality signal appropriate to the medium

Every medium has an instant-check proxy for quality that costs nothing to compute:

| Tool | Cheap Signal | What It Tells You |
|------|-------------|-------------------|
| Gamma | File size (bytes) | 8KB = bare text (bad), 50KB+ = visually rich (good) |
| ElevenLabs | Audio duration vs script word count | Too short = words skipped; too long = pacing issues |
| Canva | Image dimensions + file size | Tiny/compressed = low quality export |
| Kling | Video duration vs narration length | Mismatch = sync problems |
| Qualtrics | Question count vs learning objectives | Too few = coverage gaps |

### 5. Remember that woodshed is training — production QA is different

Woodshed compares reproduction against a source exemplar to prove tool control. Production QA compares output against the context envelope (what Marcus asked for) — style compliance, learning objective alignment, content completeness, accessibility. Same rubric dimensions, different reference point. Never confuse the two workflows.

### 6. Capture know-how in the memory sidecar from real production feedback

The agent's `patterns.md` grows through the user's checkpoint reviews in production, not through woodshed scores. The most valuable patterns emerge from seeing what each tool does with different instruction styles — and the user saying "this is excellent" or "fix the density."

## Reflection Between Cycles

When a reproduction fails, the agent **must** reflect before retrying:
1. Diagnose root cause of sub-par performance
2. Predict how performance might be improved
3. Document the plan in `reflection.md`
4. Update `reproduction-spec.yaml` with corrections
5. Only then retry

This prevents mindless retrying and forces deliberate, documented improvement.

## Circuit Breaker (Give-Up Protocol)

Agents cannot attempt reproduction indefinitely:
- **3 attempts max per session** — prevents runaway token burn
- **7 attempts max total** across all sessions for one exemplar
- **2 consecutive no-improvement** attempts → stop immediately

When limits are reached, the agent produces a structured `failure-report.yaml` with capability gap analysis and recommended resolution paths. The exemplar's catalog status moves to `blocked`, signaling that human intervention is needed.

See `resources/exemplars/_shared/woodshed-workflow.md` for the complete failure report schema and circuit breaker rules.

## Integration with Specialist Agents

Any specialist agent can invoke the woodshed skill. The agent provides:
1. The `tool` name (gamma, elevenlabs, canvas, etc.)
2. The exemplar ID to study (or "all" for regression)

The woodshed skill handles the rest — it knows where exemplars live, how to compare, how to enforce reflection between attempts, and when to give up.

## Progressive Mastery Model

```
L1-L2 exemplars  → Prove basic API/MCP competence (single artifacts, simple layouts)
L3-L4 exemplars  → Prove parameter intelligence + context awareness (complex layouts, assessment, narrative)
L5+ exemplars    → Prove multi-artifact orchestration (full slide decks, narrative control, density management)
```

New exemplars can be added at any time. The agent studies them independently. Previously mastered exemplars are regression-tested to ensure the agent never loses capability.

## Two Modes: Faithful → Creative

Each exemplar supports two sequential mastery modes:

1. **Faithful**: Reproduce the exemplar as exactly as possible. Proves the agent has full control of tool parameters. `creative_status: locked` until this passes.
2. **Creative**: Reproduce the exemplar's intent with freedom to enhance. Proves creative judgment. The agent may propose changes to difficulty levels or the scale itself.

A musician must play the sheet music before they improvise.

## Export and Download

All reproductions MUST download production-quality artifacts (PDF, PPTX, MP3, etc.). Screenshots are supplementary only. Export URLs are time-limited — download immediately when generation completes. Downloaded artifacts are stored in `reproductions/{timestamp}/output/` for comparison, assembly, and downstream workflow use.
