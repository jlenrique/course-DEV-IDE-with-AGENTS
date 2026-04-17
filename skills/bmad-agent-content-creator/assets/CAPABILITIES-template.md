# Capabilities

_(Note: This template is overwritten by the scaffold with an auto-generated listing derived from `references/*.md` frontmatter. Hand-authored Tools section below survives if the scaffold merges it; otherwise use it as a reference for what the Built-in section should cover.)_

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| IA | pedagogical-framework | Instructional analysis; umbrella for LO/BT/CL/CS | `./references/pedagogical-framework.md` |
| LO | learning-objective-decomposition | Per-asset objective tracing | `./references/learning-objective-decomposition.md` |
| BT | blooms-taxonomy-application | Cognitive-level → content-type matching | `./references/blooms-taxonomy-application.md` |
| CL | cognitive-load-management | Chunking, scaffolding, dual-coding | `./references/cognitive-load-management.md` |
| CS | content-sequencing | Presentation order, spiral curriculum | `./references/content-sequencing.md` |
| AA | template-assessment-brief | Assessment alignment, backward design | `./references/template-assessment-brief.md` |
| PQ | delegation-intent-verification | Behavioral-intent check on returned prose | `./references/delegation-intent-verification.md` |
| WD | delegation-protocol | Writer selection, brief composition, revision management | `./references/delegation-protocol.md` |
| MG | template-segment-manifest | Machine-readable production contract | `./references/template-segment-manifest.md` |
| CD | cluster-decision-criteria | Clustering evaluation | `./references/cluster-decision-criteria.md` |
| SB | spoken-bridging-language | Bridge cadence in learner-heard audio | `./references/spoken-bridging-language.md` |
| PC | perception-contract-enforcement | Pass 2 perception gate (script-backed) | `./references/perception-contract-enforcement.md` |
| VR | visual-reference-injection | Deictic visual references in narration (script-backed) | `./references/visual-reference-injection.md` |
| MP | motion-plan-hydration | Gate 2M hydration (script-backed) | `./references/motion-plan-hydration.md` |
| MC | motion-perception-confirmation | Video perception confirmation (script-backed) | `./references/motion-perception-confirmation.md` |
| MA | manual-animation-support | Manual-tool animation brief + validation (script-backed) | `./references/manual-animation-support.md` |
| SM | save-memory | Session-context persistence | `./references/save-memory.md` |
| IB | interstitial-brief-specification | Constrained briefs for Gamma cluster interstitials | `./references/interstitial-brief-specification.md` |
| NA | cluster-narrative-arc-schema | Narrative arc + master behavioral intent | `./references/cluster-narrative-arc-schema.md` |
| DC | cluster-density-controls | Run-level density, per-slide overrides, interstitial count | `./references/cluster-density-controls.md` |
| CP | cluster-planning | Umbrella capability (no single ref; coordinates CD+NA+DC+IB+CS) | multiple — see `./references/cluster-decision-criteria.md` |

## Learned

_Capabilities added by the operator over time. Prompts live in `capabilities/`._

| Code | Name | Description | Source | Added |
|------|------|-------------|--------|-------|

## How to Add a Capability

Tell me "I want you to be able to do X" and we'll create it together. Load `./references/capability-authoring.md` for the full framework.

## Tools

### Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/perception_contract.py` | Image + motion perception enforcement; PC, MC capabilities |
| `./scripts/visual_reference_injector.py` | Pass 2 visual reference injection; VR capability |
| `./scripts/manifest_visual_enrichment.py` | Gate 2M motion-plan hydration; MP capability |
| `./scripts/manual_animation_workflow.py` | Manual animation brief + validation; MA capability |

### User-Provided Tools

- **MCPs:** typically none invoked directly by Irene — she consumes outputs from Marcus's context envelope. Sensory bridges (image + video) are invoked indirectly via `perception_contract.py`.
- **APIs:** none (Irene does not call APIs directly).
- **State files:** `state/config/course_context.yaml`, `state/config/narration-script-parameters.yaml`, `state/config/fidelity-contracts/g4-narration-script.yaml` (read-only).
