# Save Memory — Gary (Gamma Specialist)

Explicitly save current session context and learned patterns to the memory sidecar.

## When to Save

- After a successful production run (parameters, quality scores, user approval status)
- After exemplar mastery milestone (faithful or creative mode pass)
- After doc refresh discovers API changes
- When the user or Marcus explicitly requests a memory save
- At session end if meaningful learning occurred

## What to Save

### To `index.md` (active context)
- Current mastery status summary (which exemplars mastered, in-progress, blocked)
- Most recently effective parameter combinations (quick-access)
- Active production run context (if delegated from Marcus)
- Last doc refresh date

### To `patterns.md` (append-only, default mode only)
Format each entry as:

```markdown
### [date] — [content type / exemplar ID]
- **Parameters**: [key parameters used]
- **Quality score**: [overall and dimension breakdown]
- **Outcome**: [approved / revision requested / rejected]
- **Learning**: [what worked, what didn't, what to try differently]
```

### To `chronology.md` (append-only, default mode only)
Format each entry as:

```markdown
- [date]: [action] — [brief outcome]. Run ID: [id]. Quality: [score].
```

## Mode Check

Before writing, verify current run mode:
- **Default mode**: Write to all sidecar files per rules
- **Ad-hoc mode**: Write only to transient section of `index.md` — do NOT append to `patterns.md` or `chronology.md`

## Condensation

When `patterns.md` exceeds ~200 entries or ~5000 words, condense:
1. Group similar patterns by content type
2. Promote consistently effective combinations to authoritative recommendations
3. Archive contradicted or superseded patterns
4. Commit the condensed version
