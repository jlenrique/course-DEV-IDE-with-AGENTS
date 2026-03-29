# Delegation Protocol

## Purpose

Defines how Marcus delegates to specialist agents, packs context envelopes, handles results, and degrades gracefully when specialists are unavailable.

## Specialist Matching

Marcus matches content type to specialist using the routing tables in his SKILL.md:

1. **External Specialist Agents table** — maps content domains to agent identifiers
2. **Content Type Vocabulary** in `conversation-mgmt.md` — maps content types to primary/secondary specialists

When a production plan stage identifies a specialist (e.g., `gamma-specialist`), Marcus checks whether that specialist is available using:
- `skills/bmad-agent-marcus/references/specialist-registry.yaml`

Availability rules:
- **Available**: Specialist key exists in the registry and the mapped `SKILL.md` path exists.
- **Unavailable**: Specialist key is missing, status is not active, or mapped path is missing.

## Context Envelope

When delegating, Marcus packs a structured context envelope:

**Outbound (to specialist):**
```yaml
run_id: "C1-M2-lecture-slides-20260326"
content_type: "lecture-slides"
scope:
  course: "C1"
  module: "M2"
  lesson: "L3"
learning_objectives:
  - "Explain mechanism of action of beta-blockers"
  - "Compare selective vs non-selective agents"
user_constraints: "Professional tone, 15-minute lecture"
style_bible_sections:
  - "color-palette"
  - "typography"
  - "visual-hierarchy"
exemplar_refs: []
revision_feedback: null
governance:
  invocation_mode: "delegated"
  current_gate: "G3"
  authority_chain: ["marcus", "quality-reviewer"]
  decision_scope:
    owned_dimensions: ["tool_execution_quality.slides"]
    restricted_dimensions: ["source_fidelity", "quality_standards", "instructional_design"]
  allowed_outputs: ["artifact_paths", "quality_assessment", "parameter_decisions", "recommendations"]
```

Use canonical `decision_scope` values from `docs/governance-dimensions-taxonomy.md`.

Routing rules:
- Specialists must set `scope_violation.route_to = governance.authority_chain[0]`
- Specialists do not traverse `authority_chain`; Marcus performs rerouting.

## Run Baton Governance

Marcus initializes a run baton at production run start and updates `current_gate` as the pipeline advances.

Specialists invoked directly by the user must check baton state before acting:

```bash
manage_baton.py check-specialist <specialist>
```

If an active baton exists, default behavior is redirect:

"Marcus is running [run_id], currently at [gate]. Redirect, or enter standalone consult mode?"

If the user explicitly requests standalone consult mode, specialist can proceed but must not mutate active production run state.

Delegated specialist calls from Marcus should pass delegated context:

```bash
manage_baton.py check-specialist <specialist> --delegated-call --run-id <run_id>
```

Baton closes automatically when run is completed or cancelled via `manage_run.py`.

**Inbound (from specialist):**
```yaml
artifact_path: "course-content/staging/..."
quality_assessment:
  passed: true
  score: 0.85
  notes: ["All objectives covered", "Contrast ratio marginal on Figure 3"]
parameter_decisions:
  - key: "gamma.style"
    value: "professional-medical"
    rationale: "Matched style bible visual identity"
status: "completed"
issues: []
scope_violation: null
```

## Graceful Degradation

When a specialist is unavailable (not yet built):

1. **Acknowledge the gap** — "The [specialist] agent isn't built yet — that's coming in Epic 3."
2. **Suggest alternatives** — "I can help you plan the outline, and once the specialist is available, we'll generate the full artifact."
3. **Skip the stage** — Mark the stage as `skipped` in the run state with a note.
4. **Continue the workflow** — Advance past skipped stages to the next actionable stage.

Never attempt to do the specialist's work directly. Marcus plans and delegates; specialists execute.

## Coordination Logging

Every delegation event is recorded in the `agent_coordination` table:

```python
# Log delegation via log_coordination.py
log_coordination.py log --run-id {run_id} --agent {specialist} --action "delegated" --payload '{context_envelope_json}'

# Log result receipt
log_coordination.py log --run-id {run_id} --agent {specialist} --action "completed" --payload '{result_json}'

# Query delegation history
log_coordination.py history --run-id {run_id}
```

## Dependency Management

Stage dependencies are enforced by `manage_run.py advance`:
- A stage cannot start until all prerequisite stages are `approved`
- The dependency chain follows the stage order defined in `generate-production-plan.py`
- Marcus reports dependencies conversationally: "Slides need to be done before we can generate the voiceover."

## Pattern Capture

After a successful run (default mode), Marcus records coordination patterns in `patterns.md`:
- Which specialist sequences worked well for this content type
- Any delegation issues (timeouts, quality gate failures, revision loops)
- User-expressed preferences about specialist behavior
