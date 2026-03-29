# Next Session Start Here

## Immediate Next Action

**Run live-profile test triage before starting new feature work.**

Default suite is stable and now excludes live integrations by default. Next session should resolve remaining `--run-live` instability (starting with Kling live paths), then continue Epic 3 deferred queue work.

---

## Current Status

| Epic | Status | Stories |
|------|--------|---------|
| Epic 1 | DONE | 11/11 |
| Epic 2 | DONE | 6/6 |
| **Epic 2A** | **DONE** | **9/9** — Vera (G0-G5), sensory bridges, perception protocol, source_ref resolver, drift tracking, fidelity-control vocabulary, maturity audit |
| **Epic 3** | **8/11 done** | 3.1-3.5, 3.9, 3.10, 3.11 done. 3.6-3.8 deferred. |
| **Epic 4A** | **DONE** | 4A-1 through 4A-6 complete |
| **Epic 4** | **DONE** | 4.1 through 4.5 complete |

**Roadmap rebaselined 2026-03-28; amended 2026-03-29:** 9 epics, **41 stories** (+4A-6). Epics 7+8+9 collapsed into Epic G. Epic 5 trimmed. Epic 6.2 merged into 3.6. PRD: **FR81–FR91** (FR91 ad-hoc ledger boundary). Architecture updated with governance section.

---

## Shutdown Quality Gate Snapshot (2026-03-29)

- Default tests: `155 passed, 23 deselected, 5 warnings`.
- Live tests: still pending targeted triage with `--run-live`.
- Lint: `ruff` reports a large baseline backlog (`1407` issues), not a same-session regression.
- Whitespace check: failed on trailing whitespace in this file and should be rechecked after edits.

---

## Key Deliverables This Session

- **Epic 2A complete** (Stories 2A-4 through 2A-9)
- **Story 3.11** (mixed-fidelity Gamma generation) — `execute_generation()` production entry point, `merge_parameters()` vocabulary enforcement, `generate_deck_mixed_fidelity()` two-call orchestrator, URL validation wired
- **Full roadmap rebaseline** — PRD (10 new FRs), architecture (governance section), epics restructured
- **Three Party Mode consultations** — mixed-fidelity compatibility, video pipeline, downstream epic audit
- **Two external code reviews** with all findings resolved
- **Story 4A-1 implemented** — runtime run baton contract (`manage_baton.py`), specialist redirect protocol, close-on-complete/cancel lifecycle, 52 production-coordination tests passing
- **Story 4A-2 done** — party-mode + independent-review closure fixes applied: Gary execution-only QA reference, Irene duplicate/label cleanup, fidelity role-matrix wording precision, platform-owner rule + lane-coverage checklist
- **Story 4A-3 done** — governance block contract added across Marcus + specialist envelope docs, canonical decision-scope taxonomy added, dedicated Vera envelope schema added, mandatory adversarial + party review closure completed with consensus fixes
- **Story 4A-4 done** — agent QA release gate documented and enforced in create-story/dev-story workflows; archival utility + tests added; proof scan archived; adversarial findings remediated and party-mode consensus closure passed
- **Story 4A-5 done** — run-scoped sensory cache + observability hooks with run_mode tagging and governance findings summary support
- **Story 4A-6 done** — hard ad-hoc persistence boundary enforcement, transient ad-hoc run/observability paths, and normative contract doc (`docs/ad-hoc-contract.md`)
- **Epic 4 stories 4.1-4.5 done** — lifecycle enhancements, quality gate coordinator, entity alignment manager, production intelligence reporting, and deployment coordinator with focused validation
- **Session shutdown protocol executed** — quality gates run, stale generated runtime folders removed, startup/handoff docs refreshed for next operator

---

## Branch

**Repository baseline branch:** `master`
**Next working branch:** `dev/epic-4a-agent-governance`

**Startup commands:**
- `git checkout master`
- `git pull origin master`
- `git checkout dev/epic-4a-agent-governance` *(or `git checkout -b dev/epic-4a-agent-governance master` if not yet created locally)*

**Closeout exception recorded:** merge-to-master was not executed in this shutdown pass due outstanding lint baseline backlog and pending live-profile triage.

---

## Key File Paths for Epic 4A

| File | Role |
|---|---|
| `_bmad-output/planning-artifacts/epics.md` | Epic 4A story ACs (search "Epic 4A") |
| `_bmad-output/planning-artifacts/architecture.md` | Governance architecture section |
| `_bmad-output/planning-artifacts/prd.md` | FR81-FR91 (governance FRs; FR91 ad-hoc ledger boundary) |
| `docs/lane-matrix.md` | Authoritative lane ownership map introduced in Story 4A-2 |
| `docs/fidelity-gate-map.md` | Fidelity gate role matrix and compatibility baseline for lane matrix |
| `_bmad-output/implementation-artifacts/runtime-refactor-timing-plan.md` | Refactor timing/placement decisions (what to do now vs end of 4A vs Epic 4+) |
| `_bmad-output/implementation-artifacts/4a-6-ad-hoc-ledger-enforcement.md` | Story 4A-6 pointer (ad-hoc ledger enforcement, FR91) |
| `docs/app-design-principles.md` | Three-Layer Model, Hourglass |
| `skills/bmad-agent-marcus/references/conversation-mgmt.md` | Current delegation flow to update with baton |

## Session Lesson (Carry Forward)

**Before marking any story done, verify the execution path end-to-end.** This session had repeated findings of "helpers without callers" — functions that were tested in isolation but not wired into production call paths. The fix each time was to create orchestrator functions, CLI entry points, or non-test callers. **The check**: for every new Python function, confirm at least one non-test call site exists. For every new agent protocol step, confirm the referenced script has a CLI entry point.

## Gotchas

- PowerShell: no `&&` chaining
- Python 3.13 via pyenv
- Default local validation should run without live integrations: `python -m pytest tests -v`
- Live integrations require explicit opt-in: `python -m pytest tests -v --run-live`
- Runtime-generated folders can pollute working tree if not ignored/cleaned (`state/config/runs`, `state/runtime/ad-hoc-observability`, `state/runtime/perception-cache`)
