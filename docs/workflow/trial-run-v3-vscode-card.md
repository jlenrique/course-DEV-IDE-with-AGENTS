# Trial Run v3 VS Code Card — Retired

**Status: Deprecated as of v4 (2026-04-03).**

This card was created during the ad-hoc trial era to provide a VS Code-safe session opener that avoided degrading Cursor MCP setup. It has been retired because:

1. **The production session launcher** (`docs/workflow/production-session-launcher.md`) now provides the canonical Marcus activation prompt for all IDEs, including VS Code.
2. **Preflight checks** are covered by production-session-start.md Gate 4 and the operator card.
3. **VS Code tasks** remain available in `.vscode/tasks.json` and are referenced from the operator card.
4. **MCP handling** is now stable across both IDEs; the non-breaking guardrails from this card are no longer needed.

## Where to go instead

- **Session launcher:** `docs/workflow/production-session-launcher.md`
- **Prompt pack:** `docs/workflow/production-prompt-pack-v4.1.md`
- **Operator card:** `docs/workflow/production-operator-card-v4.md`
- **VS Code tasks:** `.vscode/tasks.json` (APP: Session Readiness + Preflight)

## Historical content

The original v3 VS Code card content is preserved in git history at commit `b4cff8d` (pre-v4 era) for traceability.
