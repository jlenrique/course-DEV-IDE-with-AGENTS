# Sprint Change Proposal: APP Trial Remediation and Contract Hardening

Date: 2026-03-30
Project: course-DEV-IDE-with-AGENTS
Scope Classification: Moderate

## 1) Issue Summary

A successful ad-hoc trial run produced mixed-fidelity slides and exports for run C1-M1-PRES-ADHOC-20260330, including nuanced card ordering and file-path reconciliation.

Post-run audit identified contract-level gaps that can cause downstream reliability risk if left unmitigated:
- Missing formal outbound quality metadata in Gary result payload.
- Missing mandatory perception grounding artifacts for Irene Pass 2 input contract.
- Theme selection and theme->parameter mapping handshake not explicitly captured as a required pre-dispatch gate.

This proposal preserves proven success behavior while introducing enforceable controls.

## 2) Impact Analysis

Epic Impact:
- Existing APP epics 1, 2, 2A, 3, 4A, 4, 5, 6, G, and 10 remain complete/done.
- New Epic 11 is introduced for mitigation-only follow-on work.

Story Impact:
- Add stories 11.1 to 11.4 under Epic 11.
- No reopening of completed legacy stories.

Artifact Impact:
- Update control docs:
  - _bmad-output/implementation-artifacts/sprint-status.yaml
  - _bmad-output/implementation-artifacts/bmm-workflow-status.yaml
  - _bmad-output/planning-artifacts/epics.md
- Add this sprint change proposal as planning traceability.

Technical Impact:
- Validation and contract enforcement around run payload assembly and handoff gating.
- Additional checks and explicit stop-on-missing-required-fields behavior.

## 3) Recommended Approach

Recommended path: Direct adjustment via a new remediation epic with due-diligence-first sequencing.

Rationale:
- Protects demonstrated success path from regression.
- Converts observed gaps into traceable, finding-linked requirements.
- Avoids unnecessary re-planning of completed APP epics.

Risk Assessment:
- Primary risk is under-scoped due diligence; mitigated by mandatory Story 11.1 completion before coding stories.
- Secondary risk is operational drift between prompts and runtime checks; mitigated by contract-gated acceptance criteria in Stories 11.2-11.4.

## 4) Detailed Change Proposals

### Stories

Story 11.1: Trial Due Diligence and Findings Matrix
- Output: Evidence matrix with finding IDs, severity, expected vs actual, owner, and mitigation linkage.

Story 11.2: Gary Outbound Contract Completeness and Validation Gate
- Output: Required outbound fields (`gary_slide_output`, `quality_assessment`, `parameter_decisions`, `recommendations`, `flags`) enforced and auditable.

Story 11.3: Irene Pass 2 Perception Grounding Enforcement
- Output: Pass 2 hard gate requiring both `gary_slide_output` and `perception_artifacts`.

Story 11.4: Theme Selection and Parameter Mapping Handshake Enforcement
- Output: User-confirmed theme and mapped parameter set required before dispatch; mismatch stops run.

### Governance and Sequence

Execution order:
1. 11.1 (mandatory due diligence)
2. 11.2
3. 11.3
4. 11.4

No Epic 11 implementation story can be marked done without explicit reference to at least one 11.1 finding ID.

## 5) Implementation Handoff

Handoff recipients:
- Scrum Master: Create and sequence Epic 11 stories.
- Developer Agent / Quick Dev: Implement 11.2-11.4 after 11.1 approval.
- QA Engineer: Validate each story against finding-linked acceptance criteria.

Success criteria:
- All completed legacy epics remain marked done in control docs.
- Epic 11 due diligence artifact is approved before mitigation code changes.
- New gates block progression when required contract inputs are missing.
- Trial success baseline remains intact (mixed-fidelity generation and export path).
