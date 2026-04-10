# Story 4A-3: Envelope Governance Extensions

Status: done

## Story

As a specialist agent,
I want every context envelope to carry explicit governance fields so I know my scope and authority,
So that I never exceed my delegated responsibilities or produce outputs outside my allowed scope.

## Acceptance Criteria

1. Given Marcus delegates work to any specialist, when the context envelope is constructed, then it includes a `governance` block with: `invocation_mode` (delegated/standalone), `current_gate`, `authority_chain`, `decision_scope`, and `allowed_outputs`.
2. The governance block is documented in Marcus's `conversation-mgmt.md` envelope specification.
3. Given a specialist receives an envelope with governance fields, when the specialist processes the request, then the specialist validates that planned outputs are within `allowed_outputs`.
4. Given a specialist receives an envelope with governance fields, when the specialist processes the request, then the specialist validates that judgments stay within `decision_scope`.
5. Any work outside scope is flagged and returned to the `authority_chain` for routing.
6. All existing context envelope schemas (Gary, Irene, Kira, ElevenLabs, Vera, Quinn-R) are updated to include the governance block.

## Tasks / Subtasks

- [x] Task 1: Update Marcus envelope specification (AC: #1, #2)
  - [x] 1.1 Add `governance` block to generic outbound envelope spec in `skills/bmad-agent-marcus/references/conversation-mgmt.md`
  - [x] 1.2 Add `governance` block to fidelity-specific Vera envelope examples in `conversation-mgmt.md`

- [x] Task 2: Update specialist envelope schemas and contracts (AC: #1, #3, #4, #5, #6)
  - [x] 2.1 Add governance block to Gary schema (`skills/bmad-agent-gamma/references/context-envelope-schema.md`)
  - [x] 2.2 Add governance block to Kira schema (`skills/bmad-agent-kling/references/context-envelope-schema.md`)
  - [x] 2.3 Add governance block to ElevenLabs schema (`skills/bmad-agent-elevenlabs/references/context-envelope-schema.md`)
  - [x] 2.4 Add governance block to Vera envelope references (`skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md`)
  - [x] 2.5 Add governance block to Irene inbound envelope contract in `skills/bmad-agent-content-creator/SKILL.md`
  - [x] 2.6 Add governance block to Quinn-R inbound envelope contract in `skills/bmad-agent-quality-reviewer/SKILL.md`

- [x] Task 3: Add specialist validation guidance for `decision_scope` and `allowed_outputs` (AC: #3, #4, #5)
  - [x] 3.1 Document required validation behavior in each specialist schema/contract
  - [x] 3.2 Document out-of-scope escalation payload format routed to `authority_chain`

- [x] Task 4: Validation and review gate
  - [x] 4.1 Run targeted checks for governance keys in all required files
  - [x] 4.2 Run adversarial review for Story 4A-3 and triage findings
  - [x] 4.3 Run party-mode consensus review for Story 4A-3 and apply consensus fixes
  - [x] 4.4 Re-validate checks after fixes

- [x] Task 5: Story/status updates
  - [x] 5.1 Update this story file (tasks, completion notes, file list, change log)
  - [x] 5.2 Update sprint/workflow artifacts when story reaches done

## Dev Notes

### Design Direction

This story extends envelope contracts and specialist processing guidance; implementation is primarily schema/contract documentation updates to enforce governance boundaries.

### Expected File Changes

- `_bmad-output/implementation-artifacts/4a-3-envelope-governance-extensions.md` (new)
- `skills/bmad-agent-marcus/references/conversation-mgmt.md` (modify)
- `skills/bmad-agent-gamma/references/context-envelope-schema.md` (modify)
- `skills/bmad-agent-kling/references/context-envelope-schema.md` (modify)
- `skills/bmad-agent-elevenlabs/references/context-envelope-schema.md` (modify)
- `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` (modify)
- `skills/bmad-agent-content-creator/SKILL.md` (modify)
- `skills/bmad-agent-quality-reviewer/SKILL.md` (modify)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (modify)
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml` (modify)
- `next-session-start-here.md` (modify)

## Dev Agent Record

### Agent Model Used
GPT-5.3-Codex

### Debug Log References
- 2026-03-28: Story initialized and implementation started.
- 2026-03-29: Adversarial review run on 4A-3 (NO-GO) identified three blockers: missing governance in Compositor example and two non-canonical taxonomy usages.
- 2026-03-29: Party-mode consensus review run on 4A-3; minimal remediation set accepted.
- 2026-03-29: Consensus fixes applied; adversarial and party re-reviews returned GO.

### Completion Notes List
- Added governance contract fields to Marcus envelope references and specialist schema/contracts for Gary, Kira, ElevenLabs, Vera, Irene, and Quinn-R.
- Added canonical governance taxonomy reference at `docs/governance-dimensions-taxonomy.md` and enforced usage in schema language.
- Added explicit scope-violation contract shape and authority-chain routing rule (`route_to = authority_chain[0]`) across envelope references.
- Added dedicated Vera context-envelope schema at `skills/bmad-agent-fidelity-assessor/references/context-envelope-schema.md`.
- Updated production coordination delegation protocol reference to include governance block and out-of-scope routing semantics.
- Applied consensus blocker fixes: added missing governance block in Marcus -> Compositor envelope example; replaced non-canonical decision scope values in Marcus/Irene examples; replaced non-canonical `tool_execution_quality` umbrella value in Vera gate protocol example.
- Validation: targeted key-presence checks passed across all required 4A-3 files.
- Mandatory review gate: adversarial review + party consensus review completed; consensus fixes applied; adversarial re-review GO; party re-review GO.

### File List
**Created:**
- `_bmad-output/implementation-artifacts/4a-3-envelope-governance-extensions.md`
- `docs/governance-dimensions-taxonomy.md`
- `skills/bmad-agent-fidelity-assessor/references/context-envelope-schema.md`

**Modified:**
- `skills/bmad-agent-marcus/references/conversation-mgmt.md`
- `skills/bmad-agent-gamma/references/context-envelope-schema.md`
- `skills/bmad-agent-kling/references/context-envelope-schema.md`
- `skills/bmad-agent-elevenlabs/references/context-envelope-schema.md`
- `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md`
- `skills/bmad-agent-content-creator/SKILL.md`
- `skills/bmad-agent-quality-reviewer/SKILL.md`
- `skills/production-coordination/references/delegation-protocol.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_bmad-output/implementation-artifacts/bmm-workflow-status.yaml`
- `next-session-start-here.md`

### Change Log
- 2026-03-28: Story initialized and implementation started.
- 2026-03-29: Story implemented, governance contracts aligned, mandatory adversarial + party review gates completed with consensus remediation, and moved to done.
