# Trial Run v3 in VS Code (MCP-Safe Card)

Purpose: run the v3 trial flow in VS Code without changing or degrading Cursor MCP setup.

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
