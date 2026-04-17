# Capabilities

_(This template is overwritten by the scaffold with an auto-generated listing derived from `references/*.md` frontmatter. The hand-authored tables below are a fallback if auto-discovery finds nothing.)_

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| DR | creative-directive-contract | Directive schema + validation rules (sum-to-1.0, valid mode keys, 11-key narration controls) | `./references/creative-directive-contract.md` |
| PT | profile-targets | Initial numeric anchors for `slide_mode_proportions` per experience profile | `./references/profile-targets.md` |

## Learned

_Capabilities added by the operator over time. Prompts live in `capabilities/`._

| Code | Name | Description | Source | Added |
|------|------|-------------|--------|-------|

## How to Add a Capability

Tell me "I want you to be able to do X" and we'll create it together. Load `./references/capability-authoring.md` for the full framework.

## Tools

### Scripts

Dan has no agent-local scripts. Contract validation is performed by the shared utility:

- `scripts/utilities/creative_directive_validator.py` — runs after every directive emission; enforces schema v1.0 and numeric constraints.

### User-Provided Tools

- **State configs (read-only):** `state/config/experience-profiles.yaml`, `state/config/narration-script-parameters.yaml`
- **APIs:** none (Dan does not call APIs)
- **MCPs:** none invoked directly
