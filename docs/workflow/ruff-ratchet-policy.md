# Ruff Ratchet Policy

## Purpose

Allow feature delivery to continue while preventing new lint debt from entering the codebase.

## Policy

1. Treat the current Ruff backlog as a temporary baseline.
2. New or modified Python files in a change set must not introduce Ruff violations.
3. Pull requests must not increase the repository-level Ruff count above the recorded baseline.
4. Temporary ignores are allowed only when all conditions are met:
   - justified in review notes,
   - scoped to the narrowest rule/file,
   - assigned an owner,
   - assigned an expiry target (story, date, or milestone).

## Baseline

- Initial recorded baseline at adoption: **1407** issues.
- If the total count goes down, the new lower value becomes the baseline.
- The baseline must never move upward.

## Local Workflow

### 1) Check changed Python files only

```powershell
$changed = git diff --name-only -- '*.py'
if ($changed) {
  .venv\Scripts\python -m ruff check $changed
}
```

### 2) Check full-project count against baseline

```powershell
$full = .venv\Scripts\python -m ruff check . --output-format text | Out-String
$count = ($full | Select-String -Pattern '^.+:.+:.+:.+$').Count
"Current Ruff findings: $count"
```

If the full count is greater than the recorded baseline, do not merge.

## CI Recommendation

Run two lint gates:

1. Changed-file gate: fail on any Ruff violation in changed `.py` files.
2. Baseline gate: fail when full-project findings exceed the tracked baseline.

This gives immediate regression protection while allowing incremental cleanup over time.
