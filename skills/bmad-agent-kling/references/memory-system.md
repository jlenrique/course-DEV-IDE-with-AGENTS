# Memory System — Kira (Kling Specialist)

## Core Principle

Kira's memory captures prompt effectiveness, model tradeoffs, and production outcomes — the expertise that makes each successive educational clip more usable, cheaper, and easier to approve. Memory is mode-aware: default mode learns, ad-hoc mode does not.

## File Structure

Sidecar location: `{project-root}/_bmad/memory/kira-sidecar/`

| File | Purpose | Write Rules |
|------|---------|-------------|
| `index.md` | Active context, recent clips, quick-access preferences by video type | Default: full. Ad-hoc: transient section only |
| `access-boundaries.md` | Read/write/deny zones | Set at build time, read-only at runtime |
| `patterns.md` | Learned prompt patterns, model/mode/duration effectiveness, source asset pairings | Default mode only (append) |
| `chronology.md` | Video generation history, approvals, revision outcomes, useful credit observations | Default mode only (append) |

## Write Discipline

### Default Mode
- **`index.md`**: Update active clip context, recent successful outputs, preferred defaults by clip type
- **`patterns.md`**: Append after successful or instructive runs — what prompt worked, what model was used, whether the result was approved, and what to reuse or avoid next time
- **`chronology.md`**: Append after each generation cycle — run ID, clip type, parameters, output path, review result, and notable cost observations
- **`access-boundaries.md`**: Read-only at runtime

### Ad-Hoc Mode
- **`index.md`**: Transient ad-hoc session section only
- All other sidecar files: **read-only**

### Never Cache
Style bible content and course content are always re-read from disk. Memory stores pattern outcomes and production lessons, not reference-document contents.

## Memory Maintenance

`patterns.md` is append-only and should periodically be condensed into authoritative recommendations by clip type:
1. B-roll
2. Concept animation
3. Image-to-video transition
4. Lip-sync overlay
5. Bridge / transition clip

## Access Boundaries

### Read (both modes)
- `state/config/course_context.yaml`
- `state/config/style_guide.yaml`
- `resources/style-bible/`
- `course-content/staging/`
- `course-content/courses/`
- `skills/kling-video/`
- project-level Kling API client (read-only for understanding available methods)
- `{project-root}/_bmad/memory/kira-sidecar/`
- Source assets from Gary, Irene, ElevenLabs, and Marcus delegation

### Write (default mode)
- `{project-root}/_bmad/memory/kira-sidecar/`
- `course-content/staging/`

### Write (ad-hoc mode)
- `{project-root}/_bmad/memory/kira-sidecar/index.md` — transient section only
- `course-content/staging/ad-hoc/`

### Deny (both modes)
- `.env`
- Other agents' memory sidecars
- `resources/style-bible/` — never write
- `tests/`
- Runtime mutation of API client code from the agent layer
