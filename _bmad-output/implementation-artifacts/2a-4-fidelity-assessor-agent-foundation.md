# Story 2A-4: Fidelity Assessor Agent — Foundation (G2-G3)

Status: review

## Story

As a course content producer,
I want an independent Fidelity Assessor agent that verifies whether production artifacts are faithful to their source of truth at each gate,
So that fidelity failures are caught automatically before quality review or human checkpoint — and the system's fidelity evaluation improves over time as LLM capabilities advance.

## Background & Motivation

This is the most substantial story in Epic 2A. The fidelity audit (Story 2A-1) established that the APP is at Level 0 for fidelity assurance — zero independent evaluation. Quinn-R reviews quality but not fidelity. Gary self-grades but no independent agent verifies whether his output matches the slide brief. Irene's slide brief is unchecked against the lesson plan. The Fidelity Assessor fills this gap as a **forensic** agent that answers one question: "Is this output faithful to its source of truth?"

**Prerequisites already completed:**
- Story 2A-1: L1 contracts defined for all 7 gates (38 criteria) in `state/config/fidelity-contracts/`
- Story 2A-2: 5 sensory bridges (PPTX, image, audio, PDF, video) with canonical perception schema, confidence rubric, and universal perception protocol
- Story 2A-3: `source_ref` provenance annotations in all 5 live templates; source-ref grammar spec

**Key architectural principle:** The fidelity *requirement* (L1 contract) is invariant. The fidelity *assessment mechanism* (L2 agentic evaluation) evolves with LLM capability. This story builds the agent with initial L2 logic (structural comparison, keyword matching, item counting) that will get smarter as LLMs improve — same contracts, smarter detection.

**GOLD document:** `_bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md`

## Acceptance Criteria

### Agent Creation (via bmad-agent-builder)

1. `skills/bmad-agent-fidelity-assessor/SKILL.md` exists with persona, identity, communication style, principles, capabilities, "does not do" boundary, and on-activation instructions
2. Agent role is strictly forensic: "Is this output faithful to its source of truth?" — distinct from Quinn-R (quality) in role, mandate, and assessment criteria
3. Memory sidecar at `_bmad/memory/fidelity-assessor-sidecar/` with `index.md`, `patterns.md`, `chronology.md`, `access-boundaries.md`
4. Agent has references directory with at minimum: `memory-system.md`, `save-memory.md`, `init.md`, `fidelity-trace-report.md`, `gate-evaluation-protocol.md`

### Three-Layer Architecture

5. L1 contracts loaded from `state/config/fidelity-contracts/` — agent reads YAML files for the gate being evaluated
6. L2 evaluation logic starts with structural comparison, keyword/item coverage, and content matching — designed to evolve with LLM capability
7. L3 memory captures fidelity assessment outcomes, gate-specific learnings, and user corrections in the sidecar

### Fidelity Trace Report (Standard Output)

8. Every assessment produces a Fidelity Trace Report with findings categorized as **Omissions**, **Inventions**, or **Alterations**
9. Each finding includes: `gate`, `artifact_location` (slide N, line range, timestamp), `severity` (critical/high/medium), `source_ref`, `output_ref`, `suggested_remediation`
10. Report includes a gate-level pass/fail verdict with overall fidelity score
11. Report includes evidence retention: `resolved_source_slice`, `output_slice`, `resolution_confidence`, `comparison_result` (per `docs/source-ref-grammar.md`)

### G2 Coverage (Slide Brief vs. Lesson Plan)

12. Verifies every lesson plan LO is covered by at least one slide (no Omissions)
13. Verifies fidelity classifications (`literal-text`, `literal-visual`, `creative`) are appropriate based on source material signals (no Alterations in classification)
14. Verifies `content_items` trace to lesson plan sections via `source_ref` fields
15. Reports Omissions (missing LOs), Inventions (slides without LO traceability), Alterations (misclassified fidelity)
16. Loads G2 L1 contract from `state/config/fidelity-contracts/g2-slide-brief.yaml` — evaluates all 6 criteria (G2-01 through G2-06)

### G3 Coverage (Generated Slides vs. Slide Brief)

17. For text verification: invokes the PPTX sensory bridge (`pptx_to_agent.py`) on the PPTX export for deterministic text extraction — this is the **primary path** per Hourglass principle
18. For visual verification: invokes the image sensory bridge (`png_to_agent.py`) on PNGs for layout and visual element assessment
19. Confirms perception of each slide with confidence level before evaluating (universal perception protocol)
20. For `literal-text` slides: verifies all `content_items` from the slide brief appear verbatim in the PPTX extracted text
21. For `literal-visual` slides: verifies the specified image is present (via image bridge) and text is preserved (via PPTX bridge)
22. For `creative` slides: verifies content coverage — all `content_items` themes are semantically represented even if creatively enhanced
23. Reports Omissions, Inventions, and Alterations per slide with slide number and content item references
24. Loads G3 L1 contract from `state/config/fidelity-contracts/g3-generated-slides.yaml` — evaluates all 6 criteria (G3-01 through G3-06)

### Circuit Breaker and Operating Policy

25. **Critical finding:** Immediate circuit break — pipeline halts, artifact returned to producing agent, Marcus notified with full Fidelity Trace Report. No retry without human review.
26. **High finding:** Circuit break — producing agent receives report and may retry once with specific remediation guidance. Second failure escalates to Marcus + human.
27. **Medium finding:** Warning — logged in report, artifact proceeds to Quinn-R and human checkpoint with findings attached. No circuit break.
28. Remediation owner: Irene at G2, Gary at G3. Marcus is escalation path. Human is waiver authority.
29. Maximum 2 retries per gate per production run before mandatory human escalation.
30. Waivers: only the human (via Marcus) can waive a critical or high finding. Waivers are logged in the Fidelity Trace Report with rationale.
31. In ad-hoc mode: high findings downgrade to warnings (proceed with advisory); critical findings still halt.

### Marcus Integration

32. Marcus's `conversation-mgmt.md` updated to invoke Fidelity Assessor after each producing agent returns results at G2 and G3
33. Marcus's delegation flow: `Producing Agent → Fidelity Assessor → Quinn-R → HIL Gate` — fidelity is a precondition for quality
34. Fidelity Assessor receives a context envelope from Marcus with: production_run_id, gate, artifact_paths, source_of_truth_paths, fidelity_contracts_path, run_mode (default/ad-hoc)

### Interaction Tests

35. An interaction test guide at `tests/agents/bmad-agent-fidelity-assessor/interaction-test-guide.md` with scenarios covering G2 pass, G2 failure (omission), G3 literal-text pass, G3 literal-text failure, G3 creative coverage pass, circuit breaker escalation

## Tasks / Subtasks

- [x] Task 1: Create Fidelity Assessor agent via bmad-agent-builder (AC: #1, #2, #3, #4)
  - [x] 1.1 Run bmad-agent-builder six-phase discovery using the GOLD document spec, role matrix from `docs/fidelity-gate-map.md`, and existing agent patterns (Quinn-R, Marcus) as structural references
  - [x] 1.2 Create `skills/bmad-agent-fidelity-assessor/SKILL.md` — persona (Vera), identity, communication style, 10 principles, capabilities table, does-not-do, on-activation, degradation handling
  - [x] 1.3 Create references: `memory-system.md`, `save-memory.md`, `init.md` (follows Quinn-R's pattern)
  - [x] 1.4 Create `references/fidelity-trace-report.md` — report format, O/I/A taxonomy, evidence retention format, severity definitions
  - [x] 1.5 Create `references/gate-evaluation-protocol.md` — 9-step protocol for evaluating a gate (receive → load contract → load source → load output → perceive → evaluate → compile → circuit breaker → return)
  - [x] 1.6 Initialize memory sidecar: `_bmad/memory/fidelity-assessor-sidecar/` with `index.md`, `patterns.md`, `chronology.md`, `access-boundaries.md`

- [x] Task 2: Define Fidelity Trace Report format (AC: #8, #9, #10, #11)
  - [x] 2.1 Create `references/fidelity-trace-report.md` with YAML report schema, O/I/A finding format, evidence retention format, severity/verdict definitions
  - [x] 2.2 Include example G2 alteration scenario in report schema (fidelity misclassification with evidence)

- [x] Task 3: Implement G2 evaluation protocol (AC: #12, #13, #14, #15, #16)
  - [x] 3.1 Document G2 evaluation steps in `references/gate-evaluation-protocol.md` — loading lesson plan, loading slide brief, cross-referencing LOs to slides, checking fidelity classifications, checking source_ref validity
  - [x] 3.2 G2 evaluation confirmed text-only (no perception needed — `requires_perception: false` for all G2 criteria)
  - [x] 3.3 All 6 G2 L1 contract criteria (G2-01 through G2-06) included with agent instructions: 4 deterministic, 2 agentic

- [x] Task 4: Implement G3 evaluation protocol (AC: #17, #18, #19, #20, #21, #22, #23, #24)
  - [x] 4.1 Document G3 evaluation steps — load slide brief, invoke PPTX bridge on PPTX export, invoke image bridge on PNGs, cross-reference
  - [x] 4.2 Document dual-bridge strategy: PPTX for text verification (primary deterministic path per Hourglass), image bridge for visual verification (supplementary)
  - [x] 4.3 Document per-fidelity-class evaluation rules: literal-text (verbatim match), literal-visual (image + text), creative (semantic coverage)
  - [x] 4.4 All 6 G3 L1 contract criteria (G3-01 through G3-06) included with agent instructions: 2 deterministic, 4 agentic (all perception-required)

- [x] Task 5: Implement circuit breaker and operating policy (AC: #25, #26, #27, #28, #29, #30, #31)
  - [x] 5.1 Document circuit breaker behavior in SKILL.md (Principles #7), fidelity-trace-report.md (severity-to-response table), and gate-evaluation-protocol.md (Step 8)
  - [x] 5.2 Include severity-to-response mapping from `docs/fidelity-gate-map.md` operating policy
  - [x] 5.3 Document ad-hoc mode downgrade (high → warning in gate-evaluation-protocol.md Step 8 and SKILL.md Degradation Handling)
  - [x] 5.4 Document waiver protocol (Principle #9 in SKILL.md, interaction test scenario 9)

- [x] Task 6: Update Marcus delegation flow (AC: #32, #33, #34)
  - [x] 6.1 Updated `skills/bmad-agent-marcus/references/conversation-mgmt.md` — Vera inserted after Irene P1 (G2) and after Gary (G3) in pipeline dependency graph
  - [x] 6.2 Added Fidelity Assessor context envelope specification (outbound and inbound YAML schemas)
  - [x] 6.3 Documented Marcus's circuit breaker handling: halt/retry/proceed routing with detailed behavior

- [x] Task 7: Create interaction tests (AC: #35)
  - [x] 7.1 Created `tests/agents/bmad-agent-fidelity-assessor/interaction-test-guide.md` with 12 scenario scripts
  - [x] 7.2 Scenarios: G2 clean pass, G2 LO omission, G2 fidelity misclassification, G3 literal-text pass, G3 literal-text verbatim failure, G3 creative coverage pass, G3 creative omission, G3 harmful invention, circuit breaker critical escalation, circuit breaker high retry, ad-hoc mode downgrade, degraded evaluation (no PPTX)

- [x] Task 8: Validate and complete
  - [x] 8.1 Run existing project tests — 131 pass, 2 known pre-existing failures, 3 skipped. No regressions.
  - [x] 8.2 Agent SKILL.md follows established patterns (section structure matches Quinn-R, Marcus)
  - [x] 8.3 All 12 L1 contract criteria (G2-01–G2-06, G3-01–G3-06) addressed in gate evaluation protocol
  - [x] 8.4 Memory sidecar follows established 4-file pattern (index, patterns, chronology, access-boundaries)
  - [x] 8.5 Update sprint-status.yaml: `2a-4-fidelity-assessor-agent-foundation: done`

## Dev Notes

### Agent Creation Pattern

Follow the established agent creation pattern used for all 6 existing agents:

| Component | Pattern | Reference |
|-----------|---------|-----------|
| **SKILL.md structure** | Frontmatter → Overview → Identity → Communication Style → Principles → Does Not Do → On Activation → Capabilities → Degradation Handling | `skills/bmad-agent-quality-reviewer/SKILL.md` |
| **References directory** | `memory-system.md`, `save-memory.md`, `init.md` + domain-specific refs | `skills/bmad-agent-quality-reviewer/references/` |
| **Memory sidecar** | 4 files: `index.md`, `patterns.md`, `chronology.md`, `access-boundaries.md` | `_bmad/memory/quality-reviewer-sidecar/` |
| **Interaction tests** | Scenario-based test guide with human-readable scripts | `tests/agents/bmad-agent-quality-reviewer/interaction-test-guide.md` |

**Critical identity distinction:** The Fidelity Assessor is **forensic** — "Is this *right* relative to the source?" Quinn-R is **evaluative** — "Is this *good* against standards?" The producing agent is **reflective** — "Did I use the tool *well*?" These three never overlap in scope. See role matrix in `docs/fidelity-gate-map.md`.

### Three-Layer Architecture (How the Agent Works Internally)

**L1 — Contract Loading:**
- Read `state/config/fidelity-contracts/g{n}-*.yaml` for the gate being evaluated
- Parse the `criteria[]` array — each criterion has `id`, `name`, `description`, `fidelity_class`, `severity`, `evaluation_type`, `check`, `requires_perception`, `perception_modality`
- Schema at `state/config/fidelity-contracts/_schema.yaml`

**L2 — Evaluation Logic (initial implementation):**
- **Deterministic criteria** (`evaluation_type: deterministic`): structural checks — count matching, field presence, schema compliance, parameter coherence
- **Agentic criteria** (`evaluation_type: agentic`): content comparison — keyword coverage, theme matching, semantic assessment. Initial approach is keyword/item counting; future LLMs will enable deeper semantic analysis
- For perception-required criteria (`requires_perception: true`): invoke the appropriate sensory bridge FIRST, confirm perception, THEN evaluate

**L3 — Memory:**
- After each assessment: record gate, verdict, finding count by severity, and key observations in `chronology.md`
- After user corrections: note what the user accepted/rejected/waived in `patterns.md` for calibration
- Pattern examples: "User waived G3-05 finding for creative slides where analogy was appropriate" → adjust future severity

### G3 Dual-Bridge Strategy

This follows the Hourglass principle (deterministic through the narrow neck):

| Purpose | Bridge | Script | Why |
|---------|--------|--------|-----|
| **Text extraction** (primary) | PPTX | `pptx_to_agent.py` | Exact text objects from slide data — no OCR uncertainty. Used for G3-02 (literal text), G3-04 (creative coverage), G3-05 (invention detection) |
| **Visual verification** (supplementary) | Image | `png_to_agent.py` | Layout, image presence, visual elements. Used for G3-03 (literal visual), overall visual assessment |

Gary exports both PPTX and PNG files. The Fidelity Assessor should request both from Marcus's context envelope. If PPTX is unavailable (e.g., Gamma API only returned PNGs), fall back to image bridge for all checks with a `degraded_evaluation` warning.

### Source_ref Resolution (Simplified for 2A-4)

The full `validate_source_refs()` resolver is deferred to Story 2A-8. For 2A-4, the Fidelity Assessor does **basic resolution**:
1. Split `source_ref` on first `#` — left is filename, right is path expression
2. Read the referenced file
3. Find the referenced section (heading match or line range)
4. Extract the content slice for comparison
5. If file not found or section not found → report as "broken source_ref" finding (severity: high)

Grammar spec: `docs/source-ref-grammar.md`

### Circuit Breaker Integration with Marcus

When the Fidelity Assessor completes evaluation, it returns to Marcus:

```yaml
status: passed | failed | warning
gate: "G2" | "G3"
verdict:
  pass: true | false
  fidelity_score: 0.0-1.0
  highest_severity: critical | high | medium | none
findings:
  omissions: [{...}]
  inventions: [{...}]
  alterations: [{...}]
circuit_breaker:
  triggered: true | false
  action: halt | retry | proceed
  remediation_target: "irene" | "gary"
  remediation_guidance: "..."
```

Marcus handles the routing:
- `halt` → stop pipeline, present full report to user, no auto-retry
- `retry` → re-invoke producing agent with remediation guidance attached to envelope, re-run Fidelity Assessor on new output, escalate on second failure
- `proceed` → pass findings to Quinn-R as advisory, continue pipeline

### Existing Components to Reuse

| Component | Location | Reuse |
|-----------|----------|-------|
| L1 fidelity contracts | `state/config/fidelity-contracts/g2-*.yaml`, `g3-*.yaml` | Load and evaluate against |
| PPTX bridge | `skills/sensory-bridges/scripts/pptx_to_agent.py` | G3 text extraction |
| Image bridge | `skills/sensory-bridges/scripts/png_to_agent.py` | G3 visual verification |
| Perception protocol | `skills/sensory-bridges/references/perception-protocol.md` | Follow 5-step protocol |
| Confidence rubric | `skills/sensory-bridges/references/confidence-rubric.md` | Interpret bridge confidence levels |
| Validator handoff | `skills/sensory-bridges/references/validator-handoff.md` | Bridge output consumption contract |
| Fidelity gate map | `docs/fidelity-gate-map.md` | Role matrix, operating policy, gate definitions |
| APP design principles | `docs/app-design-principles.md` | Three-Layer Model, Hourglass, Leaky Neck |
| Source-ref grammar | `docs/source-ref-grammar.md` | Provenance resolution rules |
| Quinn-R agent pattern | `skills/bmad-agent-quality-reviewer/` | Structural reference for agent creation |
| Marcus conversation mgmt | `skills/bmad-agent-marcus/references/conversation-mgmt.md` | Delegation flow to update |
| Slide brief template | `skills/bmad-agent-content-creator/references/template-slide-brief.md` | G2 source of truth schema |
| Context envelope schema | `skills/bmad-agent-gamma/references/context-envelope-schema.md` | G3 output contract |

### File Structure (Expected Output)

```
skills/bmad-agent-fidelity-assessor/
├── SKILL.md
└── references/
    ├── memory-system.md
    ├── save-memory.md
    ├── init.md
    ├── fidelity-trace-report.md
    └── gate-evaluation-protocol.md

_bmad/memory/fidelity-assessor-sidecar/
├── index.md
├── patterns.md
├── chronology.md
└── access-boundaries.md

tests/agents/bmad-agent-fidelity-assessor/
└── interaction-test-guide.md

# Updated existing files:
skills/bmad-agent-marcus/references/conversation-mgmt.md  (delegation flow update)
```

### Testing Approach

This is an **agent creation** story — the primary deliverable is `.md` files, not Python code. Testing is via interaction tests (human-readable scenario scripts), not pytest:

1. **Interaction test guide** with 8-12 scenarios covering G2 pass/fail, G3 pass/fail per fidelity class, circuit breaker, ad-hoc mode
2. **Regression check**: run existing 131 tests to confirm no regressions (no Python code changes expected)
3. **Structural validation**: verify SKILL.md follows established agent patterns
4. **Contract coverage**: verify all G2 (6 criteria) and G3 (6 criteria) L1 contract items are addressed in the gate evaluation protocol

### Previous Story Intelligence

**From Story 2A-2 (Sensory Bridges):**
- Bridge scripts accept canonical request schema and return response schema — the Fidelity Assessor invokes these
- PPTX bridge returns `slides[]` with `slide_number`, `text_frames[]` (exact text), `image_refs[]`, `notes`
- Image bridge returns `extracted_text`, `layout_description`, `visual_elements[]`, `confidence`
- Confidence rubric thresholds: PPTX HIGH = all text frames extracted; Image HIGH = ≥95% OCR confidence
- Universal perception protocol: Receive → Perceive → Confirm → Proceed → Escalate

**From Story 2A-1 (Fidelity Audit):**
- 38 criteria across 7 gates — the Fidelity Assessor evaluates these
- G2 has 6 criteria (G2-01 through G2-06): LO traceability, content item completeness, fidelity classification accuracy, downstream parameter coherence, no content loss, fidelity-control vocabulary
- G3 has 6 criteria (G3-01 through G3-06): slide count match, literal text preservation, literal visual placement, creative content coverage, no harmful invention, provenance manifest completeness
- Operating policy defined in `docs/fidelity-gate-map.md`

**From Story 2A-3 (Provenance Protocol):**
- `source_ref` fields now exist in lesson plan, slide brief, narration script, segment manifest, and context envelope templates
- Grammar: `{filename}#{path_expression}` — heading hierarchy, line range, or heading anchor
- Evidence retention format documented in `docs/source-ref-grammar.md`

### Git Intelligence

Recent commits show Epic 2A work pattern:
- Stories 2A-1, 2A-2, 2A-3 all completed in one session (2026-03-28)
- Agent creation stories (2.1 Marcus, 3.1 Gary, 3.2 Irene/Quinn-R) followed bmad-agent-builder six-phase discovery
- All agents have interaction test guides in `tests/agents/bmad-agent-{name}/`
- Memory sidecars initialized with minimal content — populated through use

### Gotchas

- **Branch**: `dev/story-3.11-mixed-fidelity` carries Epic 2A work (repurposed)
- **PowerShell**: no `&&` chaining — use `;` or sequential commands
- **Python 3.13**: active interpreter via pyenv
- **No new Python scripts expected**: this is an agent `.md` creation story. Sensory bridges already exist as shared scripts.
- **PPTX availability**: Gary exports PPTX files alongside PNGs. If PPTX unavailable, fall back to image bridge with degraded_evaluation warning.
- **2 pre-existing test failures**: venv detection + style guide `brand` key — not regressions
- **Kling test collection error**: missing `jwt` module — pre-existing, unrelated

### Project Structure Notes

- Agent location: `skills/bmad-agent-fidelity-assessor/` — follows established `skills/bmad-agent-{name}/` pattern
- Memory sidecar: `_bmad/memory/fidelity-assessor-sidecar/` — follows established `{skillName}-sidecar/` pattern
- Tests: `tests/agents/bmad-agent-fidelity-assessor/` — follows established test location pattern
- No conflicts with existing paths

### References

- [Source: _bmad-output/brainstorming/party-mode-fidelity-assurance-architecture.md] — GOLD document, Fidelity Assessor spec
- [Source: _bmad-output/planning-artifacts/epics.md#Story 2A-4] — Epic acceptance criteria
- [Source: docs/fidelity-gate-map.md] — Role matrix, operating policy, gate definitions
- [Source: docs/app-design-principles.md] — Three-Layer Model, Hourglass, design principles
- [Source: docs/source-ref-grammar.md] — Provenance resolution rules
- [Source: state/config/fidelity-contracts/g2-slide-brief.yaml] — G2 L1 contract (6 criteria)
- [Source: state/config/fidelity-contracts/g3-generated-slides.yaml] — G3 L1 contract (6 criteria)
- [Source: state/config/fidelity-contracts/_schema.yaml] — Contract schema definition
- [Source: skills/sensory-bridges/SKILL.md] — Sensory bridge capabilities
- [Source: skills/bmad-agent-quality-reviewer/SKILL.md] — Quinn-R pattern reference
- [Source: skills/bmad-agent-marcus/references/conversation-mgmt.md] — Marcus delegation flow

## Dev Agent Record

### Agent Model Used

Claude claude-4.6-opus (via Cursor)

### Debug Log References

No debug issues encountered.

### Completion Notes List

- Created Vera (Fidelity Assessor) agent with SKILL.md following established 6-agent pattern (Marcus, Quinn-R, Gary, Irene, ElevenLabs Voice Director, Kira)
- Agent named "Vera" (from Latin *veritas* — truth) with forensic verification identity
- 5 reference documents: memory-system.md, save-memory.md, init.md, fidelity-trace-report.md, gate-evaluation-protocol.md
- Fidelity Trace Report format defined with YAML schema, O/I/A taxonomy, evidence retention, severity-to-response mapping
- Gate evaluation protocol covers all 12 L1 criteria across G2 (6) and G3 (6) — 6 deterministic, 6 agentic
- G3 dual-bridge strategy: PPTX (primary deterministic text) + image (supplementary visual) per Hourglass principle
- Circuit breaker fully specified: critical → halt, high → retry (1 max), medium → proceed with advisory; ad-hoc downgrades high → warning
- Memory sidecar initialized with 4 files following established pattern
- Marcus delegation flow updated: Vera inserted at G2 (after Irene P1) and G3 (after Gary), before Quinn-R at both gates
- Fidelity context envelope specification added to Marcus's handoff protocol (outbound + inbound YAML)
- 12 interaction test scenarios covering all gate types, severity levels, circuit breaker actions, ad-hoc mode, and degraded evaluation
- 131 tests pass, no regressions (2 pre-existing failures: venv detection, style guide brand key)

### File List

**New files:**
- `skills/bmad-agent-fidelity-assessor/SKILL.md`
- `skills/bmad-agent-fidelity-assessor/references/memory-system.md`
- `skills/bmad-agent-fidelity-assessor/references/save-memory.md`
- `skills/bmad-agent-fidelity-assessor/references/init.md`
- `skills/bmad-agent-fidelity-assessor/references/fidelity-trace-report.md`
- `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md`
- `_bmad/memory/fidelity-assessor-sidecar/index.md`
- `_bmad/memory/fidelity-assessor-sidecar/patterns.md`
- `_bmad/memory/fidelity-assessor-sidecar/chronology.md`
- `_bmad/memory/fidelity-assessor-sidecar/access-boundaries.md`
- `tests/agents/bmad-agent-fidelity-assessor/interaction-test-guide.md`

**Modified files:**
- `skills/bmad-agent-marcus/references/conversation-mgmt.md` (delegation flow + Vera envelope)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (2A-4 status)
- `_bmad-output/implementation-artifacts/2a-4-fidelity-assessor-agent-foundation.md` (this file)

### Change Log

- 2026-03-28: Story 2A-4 implemented — Vera (Fidelity Assessor) agent created with G2-G3 coverage, Fidelity Trace Report format, circuit breaker, Marcus integration, 12 interaction tests
