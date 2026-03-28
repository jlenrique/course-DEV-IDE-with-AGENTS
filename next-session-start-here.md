# Next Session Start Here

## Immediate Next Action

**Begin Epic 4A: Agent Governance, Quality Optimization & APP Observability**

Story 4A-1 (Run Baton & Authority Contract) is the first story. See `_bmad-output/planning-artifacts/epics.md` for full AC.

---

## Current Status

| Epic | Status | Stories |
|------|--------|---------|
| Epic 1 | DONE | 11/11 |
| Epic 2 | DONE | 6/6 |
| **Epic 2A** | **DONE** | **9/9** — Vera (G0-G5), sensory bridges, perception protocol, source_ref resolver, drift tracking, fidelity-control vocabulary, maturity audit |
| **Epic 3** | **8/11 done** | 3.1-3.5, 3.9, 3.10, 3.11 done. 3.6-3.8 deferred. |
| **Epic 4A** | **NEXT** | 5 stories: run baton, lane matrix, envelope governance, agent QA gate, perception caching + observability |

**Roadmap rebaselined 2026-03-28:** 9 epics, 40 stories. Epics 7+8+9 collapsed into Epic G. Epic 5 trimmed. Epic 6.2 merged into 3.6. PRD updated with FR81-FR90 (governance). Architecture updated with governance section.

---

## Key Deliverables This Session

- **Epic 2A complete** (Stories 2A-4 through 2A-9)
- **Story 3.11** (mixed-fidelity Gamma generation) — `execute_generation()` production entry point, `merge_parameters()` vocabulary enforcement, `generate_deck_mixed_fidelity()` two-call orchestrator, URL validation wired
- **Full roadmap rebaseline** — PRD (10 new FRs), architecture (governance section), epics restructured
- **Three Party Mode consultations** — mixed-fidelity compatibility, video pipeline, downstream epic audit
- **Two external code reviews** with all findings resolved

---

## Branch

**`dev/story-3.11-mixed-fidelity`** (carries all Epic 2A + 3.11 work)

---

## Key File Paths for Epic 4A

| File | Role |
|---|---|
| `_bmad-output/planning-artifacts/epics.md` | Epic 4A story ACs (search "Epic 4A") |
| `_bmad-output/planning-artifacts/architecture.md` | Governance architecture section |
| `_bmad-output/planning-artifacts/prd.md` | FR81-FR90 (governance FRs) |
| `docs/fidelity-gate-map.md` | Role matrix (to be extended to lane matrix) |
| `docs/app-design-principles.md` | Three-Layer Model, Hourglass |
| `skills/bmad-agent-marcus/references/conversation-mgmt.md` | Current delegation flow to update with baton |

## Session Lesson (Carry Forward)

**Before marking any story done, verify the execution path end-to-end.** This session had repeated findings of "helpers without callers" — functions that were tested in isolation but not wired into production call paths. The fix each time was to create orchestrator functions, CLI entry points, or non-test callers. **The check**: for every new Python function, confirm at least one non-test call site exists. For every new agent protocol step, confirm the referenced script has a CLI entry point.

## Gotchas

- Branch name mismatch: `dev/story-3.11-mixed-fidelity` carries governance work too
- PowerShell: no `&&` chaining
- Python 3.13 via pyenv
- 2 pre-existing test failures (venv detection, style guide brand key)
- Kling test collection error (missing jwt module)
