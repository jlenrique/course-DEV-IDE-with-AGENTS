# Capabilities

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| SI | Source Interview | Gather source knowledge from the HIL operator through Marcus | `./references/source-interview.md` |
| EV | Extract & Validate | Extract content and immediately validate quality — never pass thin material | `./references/extract-and-validate.md` |
| FR | Fallback Resolution | Resolve failed extractions through alternative pathways or asset substitution | `./references/fallback-resolution.md` |

## Learned

_Capabilities added by the owner over time. Prompts live in `capabilities/`._

| Code | Name | Description | Source | Added |
|------|------|-------------|--------|-------|

## How to Add a Capability

Tell me "I want you to be able to do X" and we'll create it together.
I'll write the prompt, save it to `capabilities/`, and register it here.
Next session, I'll know how. Load `./references/capability-authoring.md` for the full creation framework.

## Tools

Prefer crafting your own tools over depending on external ones. A script you wrote and saved is more reliable than an external API.

### Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/extraction_validator.py` | Proportionality checks, quality tier classification, structural fidelity assessment |
| `./scripts/cross_validator.py` | Compare extraction against reference assets (section matching, key term coverage) |

### User-Provided Tools

_MCP servers, APIs, or services the owner has made available. Document them here._
