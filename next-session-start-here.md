# Next Session Start Here

> Scope note: this file tracks APP project development state only.
> For production content operations, use docs/workflow/production-session-launcher.md.

## Current Dev State (as of 2026-04-03)

- Active branch: **master** (clean, synced with origin)
- Working tree: clean — all prior branches merged
- Latest completed work: workflow template registry infrastructure (2026-04-02) + happy-path simulation v2 (2026-04-03)
- All BMAD epics: **done** (11 epics, 47 stories, all complete)

## No Immediate Development Actions Required

The APP project is complete. Master is production-ready.

To start a **production content run** (not APP development), use:
- docs/workflow/production-session-launcher.md
- Tell Marcus: "Let's build a narrated lesson for [course/module/lesson]"
- Marcus will call `generate-production-plan.py narrated-lesson` and scaffold the 23-stage plan

## For New APP Development Work

Create a new feature branch:

```bash
git checkout master && git pull origin master
git checkout -b dev/[feature-name]
```

Reference: `_bmad-output/implementation-artifacts/sprint-status.yaml` for all epic/story history.

## Key Infrastructure Added 2026-04-02 → 2026-04-03

- `skills/bmad-agent-marcus/references/workflow-templates.yaml` — YAML registry with 12 workflow templates
- `narrated-lesson` (23 stages) + `narrated-slides` (19 stages) as first-class template IDs with aliases
- `generate-production-plan.py` — now registry-backed (reads YAML, not embedded dict)
- `tests/Happy Path Simulation Display Screens 2026-04-03.md` — v2 simulation validating all 23 stages with party-mode team review

## Worktree Hygiene

- git worktree list checked during wrapup.
- Registered worktrees: only the primary worktree at C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS.
- No temporary worktree cleanup required this session.

## Quality Gate Snapshot (2026-04-02)

- git diff --check: pass
- APP task: Session Readiness + Preflight (JSON): overall_status=pass
- Targeted validator regression tests:
  - skills/bmad-agent-marcus/scripts/tests/test-validate-gary-dispatch-ready.py
  - skills/bmad-agent-marcus/scripts/tests/test-validate-irene-pass2-handoff.py
  - Result: 31 passed

## Hot-Start Paths

- course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/pass2-envelope.json
- course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/perception-artifacts.json
- course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/segment-manifest.yaml
- course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/DESCRIPT-ASSEMBLY-GUIDE.md
- course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/storyboard/storyboard.json
- _bmad-output/implementation-artifacts/sprint-status.yaml
- _bmad-output/implementation-artifacts/bmm-workflow-status.yaml

## Gotchas

- runTests tool may not discover these Marcus script tests by file path; direct pytest invocation is reliable.
- PowerShell chaining uses semicolons, not &&.
