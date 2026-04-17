# Capabilities

_(Note: This template is overwritten by the scaffold with an auto-generated listing derived from `references/*.md` frontmatter. It serves as a fallback only if the scaffold's frontmatter scan finds nothing.)_

## Built-in

| Code | Name | Description | Source |
|------|------|-------------|--------|
| CM | conversation-mgmt | Conversation management, intent parsing, production planning, workflow orchestration | `./references/conversation-mgmt.md` |
| PR | progress-reporting | Progress reporting, status summaries, and error handling | `./references/progress-reporting.md` |
| HC | checkpoint-coord | Human checkpoint coordination and review-gate transitions | `./references/checkpoint-coord.md` |
| MM | mode-management | Execution mode management (tracked/default vs ad-hoc) | `./references/mode-management.md` |
| SP | source-prompting | Proactive source-material prompting (Notion / Box Drive) | `./references/source-prompting.md` |
| SM | save-memory | Immediate session-context persistence to the sanctum | `./references/save-memory.md` |
| SB | storyboard-procedure | Gary slide storyboard review surface (pre- and post-Irene) | `./references/storyboard-procedure.md` |

## Learned

_Capabilities added by the owner over time. Prompts live in `capabilities/`._

| Code | Name | Description | Source | Added |
|------|------|-------------|--------|-------|

## How to Add a Capability

Tell me "I want you to be able to do X" and we'll create it together.
I'll write the prompt, save it to `capabilities/`, and register it here.
Next session, I'll know how.
Load `./references/capability-authoring.md` for the full creation framework.

## Tools

### Scripts (migrated into the sanctum via scaffold)

| Script | Purpose |
|--------|---------|
| `./scripts/generate-storyboard.py` | Build Gary slide storyboard HTML + JSON |
| `./scripts/write-authorized-storyboard.py` | Persist operator-approved storyboard with fail-closed overwrite protection |
| `./scripts/cluster_dispatch_sequencing.py` | Ordered cluster dispatch planning |
| `./scripts/cluster_coherence_validation.py` | Intra-cluster coherence checks |
| `./scripts/cluster_template_selector.py` | Content-aware cluster template selection |
| `./scripts/platform_allocation.py` | Platform recommendation intelligence |
| `./scripts/read-mode-state.py` | Read execution mode state |
| `./scripts/build-pass2-inspection-pack.py` | Reviewer-facing slide/motion inspection |
| `./scripts/prepare-irene-pass2-handoff.py` | Refresh Pass 2 envelope, archive stale rerun outputs |
| `./scripts/validate-gary-dispatch-ready.py` | Gate-2 readiness validator |

_(Full enumeration is auto-discovered from `scripts/`. See `./references/external-specialist-registry.md` for delegation surface.)_

### User-Provided Tools

- **MCPs:** Gamma (slides), Canvas LMS (deployment), Notion (source wrangling), Ref (doc research), Playwright (browser automation)
- **APIs:** Gamma, ElevenLabs, Canvas, Qualtrics, Kling, Descript, Botpress, Wondercraft
- **Local FS:** Box Drive via `BOX_DRIVE_PATH`
