# Run Mode Management

## Purpose

Marcus operates in two modes with a hard enforcement boundary between them. The mode switch is a gate on infrastructure routing — Marcus himself behaves identically in both modes. Only the state management and output routing change.

## Modes

### Default Mode
Full production with complete state tracking and memory learning.

- **State writes:** All enabled (SQLite production runs, coordination, quality gates)
- **Memory writes:** All sidecar files writable (index.md, patterns.md, chronology.md)
- **Output routing:** `course-content/staging/` for drafts, `course-content/courses/` after review gate approval
- **Learning:** Patterns captured, chronology updated, user preferences saved

### Ad-Hoc Mode
Experimental sandbox with assets routed to scratch/staging and state tracking suppressed.

- **State writes:** Suppressed (no SQLite updates, no config changes)
- **Memory writes:** Only transient ad-hoc session section in `index.md` — no patterns, chronology, or preference updates
- **Output routing:** `course-content/staging/ad-hoc/` scratch area only
- **Learning:** Disabled — experimental runs do not train Marcus's patterns
- **QA:** Still active — quality gates are non-negotiable in any mode

## Mode Switching

When the user requests a mode switch, Marcus:

1. Confirms the switch with an unambiguous statement covering all affected systems
2. Invokes `manage_mode.py set {mode}` to persist the mode switch (writes to `state/runtime/mode_state.json`)
3. Invokes `./scripts/read-mode-state.py` to verify the mode was persisted correctly
4. Adjusts all routing and write permissions immediately

**Default → Ad-hoc:** "Switching to ad-hoc mode. Assets route to staging scratch. State tracking paused. QA still active."

**Ad-hoc → Default:** "Switching to default mode. Full state tracking resumed. Assets route to production staging. Clearing ad-hoc session context."

On switch back to default, clear the transient ad-hoc session section in `index.md`.

## Enforcement

The mode boundary is a hard enforcement line:
- Never leak state writes in ad-hoc mode
- Never route ad-hoc output to production paths
- Never update patterns or chronology from ad-hoc runs
- Never suppress QA in either mode

## Mode Reporting

When reporting status, always include current mode. The user should never be uncertain about which mode is active.
