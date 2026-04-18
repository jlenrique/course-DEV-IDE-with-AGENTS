# Agent instructions

**Sprint governance:** Multi-story BMAD work in this repo follows the same BMAD sprint run charter everywhere it applies:

| Environment | Mechanism |
| --- | --- |
| **Cursor** | [`.cursor/rules/bmad-sprint-governance.mdc`](.cursor/rules/bmad-sprint-governance.mdc) (`alwaysApply`) |
| **VS Code — GitHub Copilot Chat** | [`.github/copilot-instructions.md`](.github/copilot-instructions.md) (always-on workspace instructions) |
| **Claude Code CLI** | [`CLAUDE.md`](CLAUDE.md) |

Optional explicit load (skills): **`bmad-sprint-run-charter`**. In VS Code you can also use **Chat: Open Chat Customizations** (Command Palette) to confirm which instruction files are active.

**VS Code notes:** Custom instructions apply to chat (not inline completions as you type). File-scoped rules can live under `.github/instructions/` as `*.instructions.md` with `applyTo` in frontmatter; see [Use custom instructions in VS Code](https://code.visualstudio.com/docs/copilot/customization/custom-instructions).
