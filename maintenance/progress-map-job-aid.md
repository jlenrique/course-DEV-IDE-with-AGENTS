# Progress Map — Job Aid

**What:** A "You Are Here" orientation report showing completed work, active job site, upcoming milestones, backlog horizon, and current risks — all derived from existing sprint artifacts.

**When to use:** Start of session, mid-session reorientation, or anytime you need a quick read on where development stands relative to the full plan.

---

## How to Run

### Option A: VS Code Task Palette

1. Press `Ctrl+Shift+P`
2. Type **Tasks: Run Task**
3. Select **APP: Progress Map**

For JSON output, select **APP: Progress Map (JSON)** instead.

### Option B: Terminal

```powershell
.\.venv\Scripts\python.exe -m scripts.utilities.progress_map
```

Add `--json` for machine-readable JSON:

```powershell
.\.venv\Scripts\python.exe -m scripts.utilities.progress_map --json
```

### Option C: Ask the Agent

Say: "run the progress map" or "show me the you-are-here report."

---

## What the Report Shows

| Section | Content |
|---------|---------|
| **Overall** | Progress bar, story/epic counts, completion percentage |
| **Completed** | All finished epics (compact list) |
| **★ You Are Here** | Active epics with per-epic progress bars, in-progress and ready-for-dev stories |
| **Next Up** | Immediate action items from `next-session-start-here.md` |
| **Horizon** | Backlog and deferred epics |
| **⚠ Risks** | Unresolved issues from session handoff |

---

## Data Sources (no extra maintenance required)

The report reads artifacts you already maintain at session boundaries:

- `_bmad-output/implementation-artifacts/sprint-status.yaml` — epic/story status matrix
- `SESSION-HANDOFF.md` — "What Is Next" + "Unresolved Issues" sections
- `next-session-start-here.md` — "Immediate Next Action" + "Key Risks" sections

---

## Script Location

`scripts/utilities/progress_map.py`
