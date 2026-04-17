# Story 26-3: Dan BMB Sanctum Migration

**Epic:** 26 — BMB Sanctum Migration
**Tier:** Tier-2 (specialist — narrow-lane Creative Director)
**Status:** done
**Created:** 2026-04-17
**Predecessors:** 26-1 Marcus (done 2026-04-17), 26-2 Irene (done 2026-04-17)

## Story

As the platform maintainer, I want Dan (the persona occupying the `bmad-agent-cd` Creative Director lane) migrated to the BMB sanctum pattern, so that:
- The third pilot stress-tests scaffold v0.1 on a **narrow-lane specialist** (Dan has only 2 references, no scripts) — contrasting with Marcus (orchestrator, broad surface) and Irene (specialist, deep content).
- The pattern's **minimum-viable migration** shape is established for the 11+ remaining batch-candidate agents.

## Dependencies

- 26-1 Marcus + 26-2 Irene both closed BMAD-clean.
- Shared AC spine (Tiers A-F including B5 + B6 added during 26-2 remediation).
- Scaffold v0.1 frozen.

## Acceptance Criteria

Inherits shared spine — Tiers A, B (incl. B5, B6), C, D, F apply.

**Dan-specific (Tier-D26-3):**
- **D1** — Legacy 43-line SKILL.md expands to BMB-conformant ≤60 lines (specialist-tier shared A1 ceiling; adds Three Laws + Sacred Truth + On Activation branching + Session Close; preserves Lane Responsibility + Intake Contract + Guardrails). *Amended during review:* Required Output Contract merged into Intake Contract as a single "MUST follow X AND MUST pass Y" paragraph (HTML comment records the merge); this concession was needed to fit the specialist ≤60 ceiling while preserving all canonical BMB blocks.
- **D2** — 2 capability codes preserved with frontmatter retrofits: `DR` (directive rules) on `creative-directive-contract.md`, `PT` (profile targets) on `profile-targets.md`.
- **D3** — Dan's lane shorthand "CD" preserved in references and contracts. The persona name "Dan" is used in persona/communication style; "CD" denotes the lane throughout documentation.
- **D4** — A new `scripts/` directory is created just for `init-sanctum.py` forwarder (Dan had none before).
- **D5** — Legacy `dan-sidecar` deprecated in place.

## Implementation Plan

Streamlined from Marcus/Irene pattern (fewer moving parts):

1. Downstream-ref-map (done — above).
2. Worksheet template.
3. 3 BMB seed refs (first-breath, memory-guidance, capability-authoring) tailored to Dan's narrow lane.
4. 6 asset templates.
5. Retrofit frontmatter on 2 existing refs.
6. New SKILL.md.
7. `scripts/init-sanctum.py` forwarder (new `scripts/` dir).
8. Run scaffold.
9. Deprecate `dan-sidecar/index.md`.
10. Link-rewrite sweep (Step 10b verifier — expected zero hits).
11. Dan migration tests.
12. Worksheet closeout.
13. `bmad-code-review` (layered).
14. Remediate + close.

## Risks

| Risk | Mitigation |
|------|-----------|
| "Simplest-migration-so-far" complacency — might overlook something subtle | Run the same layered 3-reviewer code review; don't short-cut |
| Scaffold sees zero scripts to copy (Dan has no scripts dir pre-migration) | Verified in dry-run; scaffold handles empty scripts list gracefully |
| Dan's lane name "CD" also appears inside Irene's bundle (cluster-decision-criteria.md) | Codes are per-agent-scoped; no scaffold-level collision. Worth noting in worksheet Decision 1. |

## Validation Evidence

- `tests/migration/test_bmb_scaffold.py`: 34 passed (7 new Dan tests + 2 parametrized additions)
- Full pytest suite: 949 passed, 2 skipped, 3 failed. The 3 failures are in `tests/test_structural_walk.py` and stem from pre-existing uncommitted work on `state/config/structural-walk/motion.yaml` unrelated to Dan (verified by stashing Dan-only changes).
- Scaffold dry-run + real run both exit 0; sanctum rendered at `_bmad/memory/bmad-agent-cd/` with all 6 canonical files, sessions/ + capabilities/ + references/ + scripts/ subdirectories, and auto-generated CAPABILITIES.md enumerating DR + PT codes from frontmatter.
- Link-rewrite sweep: 0 broken references introduced.

## Review Record

Layered `bmad-code-review` conducted 2026-04-17. Findings summary:

| Layer | MUST-FIX | SHOULD-FIX | CONSIDER |
|-------|----------|------------|----------|
| Blind Hunter | 3 | 4 | 9 |
| Edge Case Hunter | 1 | 3 | 4 |
| Acceptance Auditor | 1 FAIL (F1 worksheet) + 3 PARTIAL | — | — |

**Remediation applied:**

*Per-Dan (fixed in this story):*
- Story D1 amended from ≤50 to ≤60 + documented Output Contract merge (this diff).
- `SKILL.md:37` strengthened Intake Contract to explicit "MUST pass validator" (EH-4).
- `first-breath.md` urgency/discovery ordering reversed — envelope-first is the normal case (Blind Hunter S3).
- Sidecar sibling files (`dan-sidecar/{patterns,chronology,access-boundaries}.md`) received DEPRECATED banners (EH-2).
- Migration worksheet filed at `_shared/migration-worksheet-dan.md` (F1).

*Scaffold fleet-wide (deferred to Story 26-4 — scaffold v0.2):*
- V2-1: Scaffold reads wrong config path (`_bmad/config.yaml` instead of `_bmad/core/config.yaml`) → `{user_name}` renders as "friend" in BOND.md.
- V2-2: Scaffold substitutes `{sanctum_path}` with absolute Windows path → INDEX.md ships author's local filesystem location.
- V2-3: Scaffold copies `references/*.md` verbatim; `{sanctum_path}` / `{project_root}` tokens survive as literal text in sanctum references.
- All 3 reproduce identically on already-merged Marcus (26-1) and Irene (26-2). Logged in `_shared/scaffold-v0.2-backlog.md`. Dan is not worse than predecessors; fleet-wide fix deserves a dedicated story rather than inline per-agent patching that would leave Dan inconsistent.

## Closure

**Closed:** 2026-04-17. 3rd pilot of Epic 26. Scaffold v0.1 contract validated on 3 consecutive agents (orchestrator + specialist-content + specialist-narrow); v0.2 triggers documented separately. Ready to unlock batch migration wave for remaining ~14 agents after Story 26-4 closes.
