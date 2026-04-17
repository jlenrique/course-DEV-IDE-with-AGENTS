## BMAD Adversarial Code Review Checklist: Story 20a-4

### Acceptance Auditor
- [x] All acceptance criteria covered in artifacts
- [x] Add schema example for out-of-bounds `cluster_interstitial_count` errors
- [x] Track deferred implementation work for Epic 20b (logic, validation, prompt integration)

### Blind Hunter
- [x] Provide explicit schema, example YAML/UI, and precedence rules for operator input (run-constant vs per-slide)
- [x] Document override hierarchy and logic for contradictory operator instructions
- [x] Document how operator instructions are surfaced and audited in downstream gates/validators
- [x] Publicly document all defaults and ambiguous-case outcomes with clear examples

### Edge Case Hunter
- [x] Warn if `CLUSTER_DENSITY` is omitted (default to `none`), avoiding silent failures
- [x] Always surface an explicit, user-facing error for invalid `cluster_interstitial_count`
- [x] Log and clarify effective density when per-slide overrides exceed run-constant
- [x] Require confirmation or disambiguation if per-slide override descriptor matches multiple/no slides
- [x] Require/log reasons if operator repeatedly overrides scoring criteria
- [x] Add explicit compatibility/migration notes for legacy (pre-cluster) runs/artifacts
- [x] Ensure tight documentation-to-implementation sync for override syntax and behaviors
- [x] Enforce cap/hard max for excessive cluster/interstitials; warn clearly
- [x] Validate interactions between density controls and other run-constants (e.g., `DOUBLE_DISPATCH`)
- [x] If per-slide and run-constant contradict, log the authoritative source and outcome

Review closed 2026-04-11 during 20A readiness reconciliation.
