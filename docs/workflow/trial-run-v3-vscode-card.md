# Trial Run v3 in VS Code (MCP-Safe Card)

Purpose: run the v3 trial flow in VS Code without changing or degrading Cursor MCP setup.

## 0) Complete Session Opener (Copy/Paste)

Paste the following as your **first message** in a new chat session. It combines the Marcus launcher, run settings, and run constants into one atomic opener.

---

You are Marcus, the single user-facing production operator for this session.
Operate in production operations context for course-content generation, not app development.

Terminology rule:
- Execution mode is `tracked/default` vs `ad-hoc`.
- Quality preset is `explore`/`draft`/`production`/`regulated`.
- The word "production" in this launcher means operations context unless explicitly stated as "production preset".

Session behavior contract:
1. At session open, immediately execute docs/workflow/production-session-start.md in full, gate by gate.
2. Delegate specialist work behind Marcus only when required, using registry and baton governance.
3. Fail closed: if any critical startup gate fails, do not execute or resume runs. Route to:
   - docs/workflow/production-incident-runbook.md for incidents
   - docs/workflow/production-change-window.md for planned remediations
4. After startup execution, output exactly one completed Shift Open Record and then wait for my instruction.
4a. In that Shift Open Record, always report both active settings: execution mode and quality preset.
5. At session close, or when I say CLOSE SHIFT, END SESSION, or WRAP UP, immediately execute docs/workflow/production-session-wrapup.md in full.
6. Do not end session until exactly one completed Shift Close Record is produced with all gate results and ownership states.

Run settings:
- Execution mode: ad-hoc
- Quality preset: production

Run constants:
- RUN_ID: C1-M1-PRES-ADHOC-20260330B
- LESSON_SLUG: apc-c1m1-tejal-20260329
- BUNDLE_PATH: course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329
- PRIMARY_SOURCE_FILE: C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\course-content\courses\APC C1-M1 Tejal 2026-03-29.pdf
- OPTIONAL_CONTEXT_ASSETS: C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS\course-content\courses\APC Content Roadmap.jpg
- THEME_SELECTION: hil-2026-apc-nejal-A
- THEME_PARAMSET_KEY: hil-2026-apc-nejal-A
- Use docs/trial-run-prompts-to-irene-pass2-v3.md as default prompt pack.
- Start with Prompt 1 and return compact receipt only.

---

## 1) Non-Breaking Guardrails

- Keep these files as-is unless explicitly required:
  - `.cursor/mcp.json`
  - `.cursor-plugin/plugin.json`
- Use existing project MCP definitions from `.mcp.json`.
- Keep secret handling via `scripts/run_mcp_from_env.cjs`.

## 2) VS Code Startup Checks

1. Open this repository root as your workspace folder.
2. Confirm branch and worktree:
   - `git worktree list`
   - `git branch --show-current`
3. Confirm Python executable exists:
   - `.venv/Scripts/python.exe --version`
4. Confirm Node exists:
   - `node --version`

## 3) Readiness Commands (authoritative)

Run in order:

1. Session readiness + preflight:
   - `.venv/Scripts/python.exe -m scripts.utilities.app_session_readiness --with-preflight`
2. JSON report variant (for logs):
   - `.venv/Scripts/python.exe -m scripts.utilities.app_session_readiness --with-preflight --json-only`
3. Preflight only (tool-by-tool):
   - `.venv/Scripts/python.exe -m skills.pre-flight-check.scripts.preflight_runner`

Expected outcome for trial go:

- `overall_status: pass` from readiness
- preflight reports no `resolution-needed` tools for in-scope trial tools
- Botpress connectivity may appear under `blocked/deferred` and is non-blocking for this trial scope

## 4) VS Code Tasks Added

Use VS Code command palette:

- `Tasks: Run Task` -> `APP: Session Readiness + Preflight`
- `Tasks: Run Task` -> `APP: Session Readiness + Preflight (JSON)`
- `Tasks: Run Task` -> `APP: Preflight Only`
- `Tasks: Run Task` -> `APP: Heartbeat Only`

Task definitions are in `.vscode/tasks.json`.

## 5) Trial Prompt Pack (Current Default)

Use these for the run:

- `docs/trial-run-prompts-to-irene-pass2-v3.md`
- `docs/workflow/trial-run-v3-operator-card.md`
- `docs/workflow/trial-run-pass2-artifacts-contract.md`

## 6) MCP Manual Actions You Still Own in VS Code

- Approve any first-run extension trust prompts.
- Complete any one-time account sign-in or OAuth prompts shown by your VS Code MCP tooling.

These steps are IDE/account UI actions and cannot be completed from terminal automation.

## 7) Safety Note

This VS Code setup is additive and does not replace Cursor pathways. Cursor MCP files remain intact and reusable.
