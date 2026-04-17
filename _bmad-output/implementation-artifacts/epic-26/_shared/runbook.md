# Epic 26 Runbook — BMB Sanctum Migration

**Target reader:** Whoever is executing a per-agent migration (human or AI). This is the procedural complement to [acceptance-criteria.md](./acceptance-criteria.md).

**Template version:** v0.1 (2026-04-17).

---

## Pre-Work (required for Tier-A and Tier-1 agents; optional for Tier-3 batch)

### P1. Build the downstream-reference map
```bash
grep -rn "skills/bmad-agent-<agent>/" docs/ scripts/ tests/ _bmad-output/ state/ maintenance/ > epic-26/_shared/downstream-reference-map-<agent>.md.raw
```
Classify each reference:
- **Path-only** (e.g., `skills/bmad-agent-marcus/scripts/foo.py`) — must resolve post-migration; goes to path-preservation AC (Tier-B).
- **Section-anchor** (e.g., "see Marcus SKILL.md §Capabilities") — will break if chunk moves. Enumerate in the worksheet and update post-migration.
- **Doctrine quote** (rare) — another doc restates Marcus content. Flag for de-duplication.

### P2. Read the target's legacy SKILL.md end-to-end
Chunk it mentally by type (persona / doctrine / runbook / tables / examples). Open the worksheet and start the chunk inventory (AC C1).

### P3. Verify scaffold version
`head -10 scripts/bmb_agent_migration/init_sanctum.py` — ensure template version matches the worksheet's stamp target.

---

## Migration Procedure

### Step 1. Create the migration worksheet
Copy [migration-worksheet-TEMPLATE.md](./migration-worksheet-TEMPLATE.md) → `migration-worksheet-<agent>.md`. Fill header metadata.

### Step 2. Write the chunk inventory
For every non-frontmatter chunk in the legacy SKILL.md, record: **what it is** (persona / runbook / doctrine / table / reference) → **where it goes** (`sanctum/PERSONA.md`, `sanctum/CREED.md`, `references/<newfile>.md`, etc.) → **why**.

Rule: every chunk has exactly one destination. If two homes seem plausible, choose the one where the content's audience actually looks for it.

### Step 3. Create the seed references
In `skills/bmad-agent-<agent>/references/`, create (or copy from Texas and adapt):
- `first-breath.md` — conversational onboarding when no sanctum exists.
- `memory-guidance.md` — session close discipline (sessions/ + MEMORY curation).
- `capability-authoring.md` — how the owner can teach the agent a new capability.

### Step 4. Create the template assets
In `skills/bmad-agent-<agent>/assets/`, create six `*-template.md` files with `{var}` placeholders. Use Texas assets as reference; adapt persona/creed to the agent's identity.

### Step 5. Extract doctrine into reference files
For each chunk the worksheet routes to a new reference file (e.g., `references/storyboard-procedure.md`), create the file and move the content verbatim. Do **not** summarize — the migration preserves content, it does not rewrite it.

### Step 6. Rewrite SKILL.md
Create the new terse SKILL.md (≤ 80 lines) using Texas as the structural template. Adapt:
- Persona opener matching the agent's voice.
- Three Laws (customize for orchestrator vs specialist vs manual-tool).
- Mission one-liner.
- Sacred Truth (the canonical BMB rebirth block; wording can vary slightly but the meaning is fixed).
- On Activation: first-breath vs rebirth branches.
- Session Close pointing to memory-guidance.

### Step 7. Wire the per-agent init forwarder
Create `skills/bmad-agent-<agent>/scripts/init-sanctum.py` using the hardened version from the Marcus pilot at `skills/bmad-agent-marcus/scripts/init-sanctum.py` as the template. Includes a sanity check that the shared scaffold exists and emits a clear error on missing prerequisites. Do **not** use a minimal one-liner forwarder — the missing-scaffold diagnostic is load-bearing for the 16 downstream migrations.

### Step 8. Run the scaffold
```bash
.venv/Scripts/python skills/bmad-agent-<agent>/scripts/init-sanctum.py --dry-run
.venv/Scripts/python skills/bmad-agent-<agent>/scripts/init-sanctum.py
```
Inspect `_bmad/memory/bmad-agent-<agent>/` — six sanctum files + sessions/ + capabilities/ + references/ + scripts/.

### Step 9. Deprecate the legacy sidecar
In `_bmad/memory/<agent>-sidecar/index.md`, add at the top:
```markdown
> **DEPRECATED (Epic 26, <date>):** This sidecar is superseded by `_bmad/memory/bmad-agent-<agent>/`. Files remain for backward-compat until Epic 27 cleanup. New writes should target the new sanctum.
```

### Step 10. Link-rewrite sweep
For each section-anchor reference enumerated in P1, update to point at the new destination. Commit grep output to the worksheet.

### Step 10b. Verify sweep completeness (MANDATORY)
```bash
grep -rn "skills/bmad-agent-<agent>/SKILL.md#" docs/ scripts/ tests/ _bmad-output/ state/ maintenance/
grep -rn "Marcus's.*SKILL\.md\|<agent>.*SKILL\.md §" docs/ scripts/ tests/ _bmad-output/
```
Both should return zero matches (or explicitly-waived ones recorded in the worksheet). Human-driven sweeps lose references silently; this verifier is the safety net.

### Step 11. Tests
- `tests/migration/test_bmb_scaffold.py` — should already be green from the scaffold story. Add per-agent parametrize row if needed.
- Run full suite: `.venv/Scripts/python -m pytest tests -v`.
- Run contract validator: `.venv/Scripts/python scripts/validate_fidelity_contracts.py`.

### Step 12. Fill worksheet closing sections
- Review decisions made during extraction.
- Grep results (pre/post link-rewrite).
- Template version stamp.
- Any deviations from the spine AC + rationale.

### Step 13. Code review
Run `bmad-code-review` skill (layered — Blind Hunter, Edge Case Hunter, Acceptance Auditor). Address MUST-FIX + SHOULD-FIX. Record in the story's Review Record section.

### Step 14. Mark story done
Update `sprint-status.yaml` (`<key>: done`) and append the closure note to the story artifact.

---

## Rollback

If a migration breaks downstream callers:
1. **Keep** the new sanctum and new SKILL.md — don't discard the work.
2. **Restore** the legacy SKILL.md from git (`git show HEAD~1:skills/bmad-agent-<agent>/SKILL.md > /tmp/old.md`).
3. **Rename** new SKILL.md to `SKILL-new.md` temporarily.
4. **Commit** the dual state; file a follow-up story with the specific downstream breakage.
5. **Do not** leave the repo in a state where both SKILL.md files claim to be canonical.

## Invariants (Do Not Violate)

1. **Script paths are cemented.** Never rename or move `skills/<agent>/scripts/*.py` during migration.
2. **Reference paths are cemented.** Same rule for `skills/<agent>/references/*.md` (the new BMB seeds are additive).
3. **Content preserved, not rewritten.** Migration is structural. If you find yourself "improving" the prose, stop and do that in a follow-up story.
4. **One home per chunk.** No duplication between SKILL.md, sanctum, and references.
5. **Scaffold stays generic.** No agent-specific conditionals in `scripts/bmb_agent_migration/init_sanctum.py`. If an agent needs special behavior, express it via frontmatter or config, not code branches.
