# Story 3.10: Tech Spec Wrangler Skill

Status: done

## Story

As a specialist agent,
I want a shared tech spec wrangler skill that finds, validates, and delivers current tool documentation, working examples, and how-to guides,
so that I always have authoritative, up-to-date API knowledge before production work and woodshed cycles.

## Acceptance Criteria

1. `skills/tech-spec-wrangler/SKILL.md` exists and defines a Ref-MCP-first doc-refresh workflow
2. The skill loads `doc-sources.yaml` from the requesting mastery skill reference set
3. The skill checks changelog/doc sources and produces a structured update report with cited URLs
4. The skill updates `last_refreshed` and `refresh_notes` in the target `doc-sources.yaml`
5. The skill can append discoveries to the requesting agent’s `patterns.md`
6. Unit tests cover doc-source loading, refresh-note updates, report generation, and memory logging
7. At least the active creation/composition tools have `doc-sources.yaml` coverage suitable for this skill (`gamma-api-mastery`, `elevenlabs-audio`, `compositor`)

## Tasks / Subtasks

- [x] Task 1: Create the shared tech-spec-wrangler skill (AC: #1, #2, #3, #4, #5)
  - [x] 1.1 Create `skills/tech-spec-wrangler/SKILL.md`
  - [x] 1.2 Create `skills/tech-spec-wrangler/references/report-format.md`
  - [x] 1.3 Create `skills/tech-spec-wrangler/scripts/doc_refresh.py`

- [x] Task 2: Add doc-source coverage for active creative/composition tools (AC: #2, #7)
  - [x] 2.1 Preserve and validate existing `skills/gamma-api-mastery/references/doc-sources.yaml`
  - [x] 2.2 Create `skills/elevenlabs-audio/references/doc-sources.yaml`
  - [x] 2.3 Create `skills/compositor/references/doc-sources.yaml`

- [x] Task 3: Add automated tests (AC: #6)
  - [x] 3.1 Create `skills/tech-spec-wrangler/scripts/tests/test_doc_refresh.py`

- [x] Task 4: Produce one proof report and wire status artifacts (AC: #3, #4, #5)
  - [x] 4.1 Generate a sample refresh report from one existing `doc-sources.yaml`
  - [x] 4.2 Update story/status/context artifacts to review state if validation passes

## Dev Notes

### Party Mode Consensus

- **Winston:** build this as reusable infrastructure that stabilizes every current specialist before expanding into more platform work.
- **Amelia:** focus first on Gamma, ElevenLabs, and Compositor, because those are the active asset-creation/composition surfaces.
- **Quinn:** the minimum credible implementation is file-driven and testable, with MCP use documented at the skill layer and deterministic update/report scripts underneath.

### Guardrails

- Ref MCP is the primary retrieval mechanism at the skill layer; the Python script should handle local file/report duties, not try to fake an MCP client.
- Keep the script reusable across tools by taking `doc-sources.yaml` and optional sidecar paths as inputs.
- Avoid overengineering research/discovery. The first goal is authoritative docs refresh and reproducible reporting.

## Dev Agent Record

### Debug Log References

- Story created after party consensus to reinforce active asset/composition agents before any more platform-specialist expansion
- Tech spec wrangler unit suite: `5 passed`
- Proof report generated: `skills/tech-spec-wrangler/refresh-report-elevenlabs.json`
- `elevenlabs-audio` doc-sources metadata updated with `last_refreshed` + `refresh_notes`
- ElevenLabs sidecar `patterns.md` appended with doc-refresh discovery note

### Completion Notes List

- Story initialized directly on `story3-4-elevenlabs-specialist`
- Built a shared, file-driven doc-refresh/report/update skill around existing Ref-MCP-first workflow assumptions
- Added doc-source coverage for active asset/composition surfaces: Gamma, ElevenLabs, and Compositor
- Proved the skill against the ElevenLabs doc-source set and logged the refresh result into the specialist sidecar

### File List

**Created:**
- `_bmad-output/implementation-artifacts/3-10-tech-spec-wrangler-skill.md`
- `skills/tech-spec-wrangler/SKILL.md`
- `skills/tech-spec-wrangler/references/report-format.md`
- `skills/tech-spec-wrangler/scripts/doc_refresh.py`
- `skills/tech-spec-wrangler/scripts/tests/test_doc_refresh.py`
- `skills/elevenlabs-audio/references/doc-sources.yaml`
- `skills/compositor/references/doc-sources.yaml`
- `skills/tech-spec-wrangler/refresh-report-elevenlabs.json`

**Modified:**
- `skills/bmad-agent-marcus/SKILL.md`
- `docs/agent-environment.md`
- `docs/dev-guide.md`
- `_bmad-output/implementation-artifacts\sprint-status.yaml`
- `_bmad-output/implementation-artifacts\bmm-workflow-status.yaml`
- `next-session-start-here.md`
- `docs/project-context.md`
- `_bmad/memory/elevenlabs-specialist-sidecar/patterns.md`

### Change Log

- 2026-03-27: Story file created and implementation started
- 2026-03-27: Story implemented, validated, and moved to review
