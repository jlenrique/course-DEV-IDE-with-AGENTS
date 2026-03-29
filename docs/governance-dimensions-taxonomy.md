# Governance Dimensions Taxonomy

Canonical vocabulary for `governance.decision_scope`.

Use these exact values in all context envelopes and schema examples.

## Owned Dimensions

- `orchestration`
- `instructional_design`
- `tool_execution_quality.slides`
- `tool_execution_quality.video`
- `tool_execution_quality.audio`
- `tool_execution_quality.composition`
- `source_fidelity`
- `quality_standards`
- `content_accuracy_flagging`
- `platform_deployment`

## Restricted Dimensions

Restricted dimensions must be selected from the same vocabulary above.

A specialist may only exercise judgments in `owned_dimensions`. Any requested judgment outside that set is out-of-scope and must be escalated.

## Authority-Chain Escalation Payload

When out-of-scope work is requested, return:

```yaml
scope_violation:
  detected: true
  reason: "outside_decision_scope"      # outside_decision_scope | outside_allowed_outputs
  requested_work: "Assess accessibility compliance for generated slides"
  route_to: "marcus"                    # must equal governance.authority_chain[0]
  details:
    current_scope: ["tool_execution_quality.slides"]
    restricted_scope: ["quality_standards"]
```

## Validation Rules

- Planned output keys must be a subset of `governance.allowed_outputs`.
- Planned judgments must be a subset of `governance.decision_scope.owned_dimensions`.
- `authority_chain` is an ordered non-empty list of escalation targets.
- `route_to` must always be `authority_chain[0]`.
