# Downstream Reference Map — Dan / bmad-agent-cd (Pre-Work for Story 26-3)

**Built:** 2026-04-17
**Source commands:**
```bash
grep -rn "skills/bmad-agent-cd/" docs/ scripts/ tests/ _bmad-output/ state/ maintenance/
grep -rn "dan-sidecar\|_bmad/memory/dan-sidecar" docs/ scripts/ tests/ _bmad-output/ state/
```

## Summary

| Reference type | Count | Risk if migration breaks it |
|---|---|---|
| `skills/bmad-agent-cd/*` paths | ~41 | MEDIUM — delegation contract refs, parameter-registry paths, story artifacts |
| `skills/bmad-agent-cd/SKILL.md` (section-style) | ~2 | LOW — lane-matrix checklist entries, not anchor-sensitive |
| `skills/bmad-agent-cd/references/creative-directive-contract.md` | ~8 | HIGH if moved — validator + resolver + multiple stories reference this path |
| `skills/bmad-agent-cd/references/profile-targets.md` | ~2 | LOW |
| `dan-sidecar` path references | 3 | LOW — deprecate in place |

## Tier-B AC Coverage

Tier-B (Path Preservation) mandates:
- B1 — scripts/ paths unchanged → Dan has no scripts today; adding a forwarder is additive, not a move
- B2 — references/ paths unchanged → preserves the 2 existing refs
- B5 — no legacy sidecar path in migrated bundle → verified clean (Dan has no `init.md` / `memory-system.md` orphan — simpler than Marcus/Irene)

## Section-Anchor References

| Caller | Anchor | Action |
|--------|--------|--------|
| `docs/lane-matrix.md` checklist | `bmad-agent-cd/SKILL.md` as a required Lane-Responsibility holder | no change — new SKILL.md preserves `## Lane Responsibility` |
| Story 20c-10 etc. | "Creative Directive Contract (20c-10)" anchor in `creative-directive-contract.md` | path preserved ✓ |

**No section-anchor rewrites required.** Simpler migration than either Marcus or Irene on this dimension.

## Script-Path Callers

Dan has no scripts today. The migration **adds** `skills/bmad-agent-cd/scripts/init-sanctum.py` (thin forwarder). No pre-existing script paths to preserve.

## Dan-Sidecar References (deprecate in-place)

3 references, all in structural-walk or dev-coherence historical reports. No active runtime callers.

## Conclusions for Story 26-3

1. **Simplest migration in the pilot wave.** 41 downstream refs, 0 section-anchor rewrites, 0 script-path preservation concerns (no scripts exist).
2. **Simpler capability surface** — only 2 references; assigning 2 codes (DR, PT) covers it.
3. **Sidecar deprecation is trivial** — 3 historical references only.
4. **No orphan `init.md` / `memory-system.md`** on Dan — he's post-Marcus-era. AC B5 passes by default.
5. **SKILL.md is already 43 lines** — well under the ≤60 specialist ceiling. Migration is mostly adding BMB canonical blocks (Three Laws, Sacred Truth, On Activation branching, Session Close) rather than aggressive trimming.
