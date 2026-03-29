# Context Envelope Schema

Defines the delegation contract between Marcus (sender) and Vera (receiver) for fidelity-gate evaluation.

## Inbound Envelope (Marcus -> Vera)

```yaml
schema_version: "1.0"
gate: "G3"                              # G0 | G1 | G2 | G3 | G4 | G5 | G6
production_run_id: "C1-M1-P2S1-VID-001"
artifact_paths:
  pptx: "course-content/staging/.../deck.pptx"
  pngs:
    - "course-content/staging/.../card-01.png"
source_of_truth_paths:
  slide_brief: "course-content/staging/.../slide-brief.md"
fidelity_contracts_path: "state/config/fidelity-contracts/"
run_mode: "default"
governance:
  invocation_mode: "delegated"          # delegated | standalone
  current_gate: "G3"
  authority_chain: ["marcus", "quality-reviewer"]
  decision_scope:
    owned_dimensions:
      - "source_fidelity"
    restricted_dimensions:
      - "quality_standards"
      - "instructional_design"
      - "tool_execution_quality.slides"
      - "tool_execution_quality.video"
      - "tool_execution_quality.audio"
  allowed_outputs:
    - "fidelity_trace_report"
    - "fidelity_findings"
    - "circuit_breaker"
```

## Governance Enforcement

Before evaluation, Vera validates:

- planned outputs are in `governance.allowed_outputs`
- planned judgments are in `governance.decision_scope.owned_dimensions`

If an out-of-scope request is detected, Vera returns a scope violation payload to `governance.authority_chain[0]` and does not perform the out-of-scope judgment.

## Outbound Return (Vera -> Marcus)

```yaml
schema_version: "1.0"
production_run_id: "C1-M1-P2S1-VID-001"
gate: "G3"
status: "passed"                         # passed | warning | failed
verdict:
  pass: true
  fidelity_score: 0.95
  highest_severity: "none"               # critical | high | medium | none
findings:
  omissions: []
  inventions: []
  alterations: []
circuit_breaker:
  triggered: false
  action: "proceed"                      # halt | retry | proceed
  remediation_target: null
  remediation_guidance: null
scope_violation: null                      # object when out-of-scope work is requested
```

## Scope Violation Shape

```yaml
scope_violation:
  detected: true
  reason: "outside_decision_scope"       # outside_decision_scope | outside_allowed_outputs
  requested_work: "Score accessibility and brand compliance"
  route_to: "marcus"                     # governance.authority_chain[0]
  details:
    current_scope: ["source_fidelity"]
    restricted_scope: ["quality_standards"]
```
