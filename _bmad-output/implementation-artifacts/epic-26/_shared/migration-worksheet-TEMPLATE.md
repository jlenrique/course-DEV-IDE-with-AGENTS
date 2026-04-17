# BMB Migration Worksheet — {AGENT_NAME}

**Template version:** v0.1
**Migration date:** {YYYY-MM-DD}
**Migrator:** {name/id}
**Story:** 26-{N}-{agent}-bmb-sanctum-migration.md
**Legacy SKILL.md line count:** {N}
**New SKILL.md line count:** {N}

---

## Pre-Migration Inventory

### Legacy SKILL.md Chunks

One row per top-level section in the legacy SKILL.md. Destination must be singular.

| Chunk (H2 heading) | Lines | Type | Destination | Notes |
|-------------------|-------|------|-------------|-------|
| e.g. `## Overview` | 8-24 | persona | `sanctum/PERSONA.md` (partial) + new `SKILL.md` opener | keep 3 lines in SKILL.md; rest to PERSONA |
| e.g. `## Principles` | 53-64 | doctrine | `sanctum/CREED.md` | verbatim move |
| e.g. `## Capabilities` | 108-205 | runbook + tables | `references/capability-registry.md` (new) | table preserved; link from SKILL.md |
| ... | | | | |

### Legacy Sidecar

| File | Lines | Disposition |
|------|-------|-------------|
| `_bmad/memory/{agent}-sidecar/index.md` | {N} | deprecation banner added |
| `_bmad/memory/{agent}-sidecar/access-boundaries.md` | {N} | content merged to CREED §Dominion |
| `_bmad/memory/{agent}-sidecar/patterns.md` | {N} | empty stub → no merge needed |
| `_bmad/memory/{agent}-sidecar/chronology.md` | {N} | empty stub → no merge needed |

### Downstream Reference Map Summary

| Reference type | Count | Affected files |
|---------------|-------|----------------|
| Path-only (scripts/, references/) | {N} | — (preserved by Tier-B AC) |
| Section-anchor | {N} | {list, or link to grep output} |
| Doctrine quote | {N} | {list, or "none"} |

**Link-rewrite sweep pre-count:** {N}
**Link-rewrite sweep post-count (newly-broken):** 0 (target)

---

## During-Migration Decisions

Document non-obvious routing decisions for future migrators.

- **Decision 1:** {description} — **Chose:** {option} — **Why:** {rationale}
- **Decision 2:** ...

---

## Post-Migration Verification

### Scaffold Dry Run
```
$ .venv/Scripts/python skills/bmad-agent-{agent}/scripts/init-sanctum.py --dry-run
{paste output excerpt}
```

### Scaffold Real Run
```
$ .venv/Scripts/python skills/bmad-agent-{agent}/scripts/init-sanctum.py
{paste output excerpt}
```

### Sanctum Tree
```
$ ls _bmad/memory/bmad-agent-{agent}/
{paste listing}
```

### Test Results
- `tests/migration/test_bmb_scaffold.py`: {N} passed
- Full suite: {N} passed, {N} skipped, {N} failed
- Contract validator: {N} errors

### Negative Test
- Scenario: sanctum directory absent
- Observed behavior: {describe — should route to first-breath.md, not fall back to embedded doctrine}

---

## Review Record

Filled by `bmad-code-review`. See: Story review section.

| Layer | MUST-FIX | SHOULD-FIX | CONSIDER |
|-------|----------|------------|----------|
| Blind Hunter | 0 | 0 | 0 |
| Edge Case Hunter | 0 | 0 | 0 |
| Acceptance Auditor | 0 | 0 | 0 |

**Status:** {BMAD clean / remediated / waived with rationale}

---

## Lessons Learned

Any gotchas or non-obvious things that would speed up the next migration. Keep to bullets, one screen max.

- ...
