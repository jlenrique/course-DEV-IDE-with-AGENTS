# Save Memory — Kira (Kling Specialist)

Explicitly save current session context and learned patterns to the memory sidecar.

## When to Save

- After a successful clip generation
- After a failed run that produced a reusable lesson
- After a user approves or rejects a generated clip
- After discovering a meaningful cost/quality tradeoff
- When Marcus or the user explicitly requests a memory save
- At session end if meaningful learning occurred

## What to Save

### To `index.md`
- Current active production run or recent clip summary
- Quick-access preferred defaults by clip type
- Most recent output file paths worth revisiting

### To `patterns.md` (default mode only)
Format each entry as:

```markdown
### [date] — [clip type]
- **Goal**: [instructional purpose]
- **Prompt pattern**: [core wording or structure]
- **Generation choices**: [model_name, mode, duration, aspect ratio]
- **Source assets**: [Gary PNG / ElevenLabs audio / none]
- **Outcome**: [approved / revision requested / rejected]
- **Learning**: [what to reuse, what to avoid]
```

### To `chronology.md` (default mode only)
Format each entry as:

```markdown
- [date]: [clip type] generated for [run ID]. Model [model]. Duration [duration]. Result: [approved / revised / failed]. Output: [path].
```

## Mode Check

Before writing, verify current run mode:
- **Default mode**: Write to all sidecar files per rules
- **Ad-hoc mode**: Write only to transient section of `index.md`

## Condensation

When `patterns.md` grows large, condense by clip type and promote consistently effective prompt structures and model choices into short reusable recommendations.
