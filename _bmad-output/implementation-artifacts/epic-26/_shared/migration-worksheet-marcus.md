# BMB Migration Worksheet — Marcus

**Template version:** v0.1
**Migration date:** 2026-04-17
**Migrator:** Claude (Opus 4.7, session dev/trial-run-c1m1-tejal-20260417 — branch name is stale after scope pivot)
**Story:** [26-1-marcus-bmb-sanctum-migration.md](../26-1-marcus-bmb-sanctum-migration.md)
**Legacy SKILL.md line count:** 249 (pre-migration)
**New SKILL.md line count:** 73 (post-remediation; initial rewrite was 84, trimmed after code-review flagged AC A1 violation)

---

## Pre-Migration Inventory

### Legacy SKILL.md Chunks

| Chunk (H2 heading) | Lines | Type | Destination | Notes |
|-------------------|-------|------|-------------|-------|
| `## Overview` | 8-24 | persona / identity | new `SKILL.md` (compressed) + `assets/PERSONA-template.md` | core identity stays visible; detail in PERSONA |
| `## Lane Responsibility` | 27-32 | doctrine | `assets/CREED-template.md` § Boundaries + new SKILL.md § Lane Boundaries (one-line) | CREED holds the detail |
| `## Identity` | 33-37 | persona | `assets/PERSONA-template.md` § Identity + Vibe | verbatim |
| `## Communication Style` | 39-50 | persona | `assets/PERSONA-template.md` § Communication Style | verbatim |
| `## Principles` | 52-64 | doctrine | `assets/CREED-template.md` § Core Principles | 10 principles preserved verbatim |
| `## Creative Director Routing` | 66-73 | runbook | new `SKILL.md` § Creative Director Routing | kept in SKILL.md (lightweight router, operator-relevant) |
| `## Does Not Do` | 75-77 | doctrine | `assets/CREED-template.md` § Boundaries + new SKILL.md § Lane Boundaries | consolidated |
| `## On Activation` | 79-107 | activation protocol | new `SKILL.md` § On Activation + § Session Start Handshake | restructured into BMB first-breath / rebirth pattern; handshake detail remains |
| `## Capabilities` (Internal) | 108-120 | capability registry | new `SKILL.md` § Capabilities (Router) | router table only; procedures in refs |
| `### Gary slide storyboard` | 122-189 | runbook (large) | `references/storyboard-procedure.md` (NEW, verbatim) | AC E6 — full preservation |
| `## Cluster Workflow Knowledge` | 191-205 | knowledge / doctrine | `references/cluster-workflow-knowledge.md` (NEW, verbatim) | |
| `### External Skills` | 207-219 | delegation table | `references/external-specialist-registry.md` (NEW) | AC E3 preserved |
| `### External Specialist Agents` | 220-246 | delegation table | `references/external-specialist-registry.md` (NEW) | AC E3 preserved |
| `**Descript manual-tool handoff:**` | 247-248 | runbook | `references/external-specialist-registry.md` § Descript Manual-Tool Handoff | verbatim |
| `When delegating...` (context envelope) | 250 | doctrine | `references/external-specialist-registry.md` § Context Envelope | truncated in legacy — completed from conversation-mgmt.md |

### Legacy Sidecar

| File | Lines | Disposition |
|------|-------|-------------|
| `_bmad/memory/marcus-sidecar/index.md` | 15 | **deprecation banner added** pointing to `bmad-agent-marcus/` sanctum |
| `_bmad/memory/marcus-sidecar/access-boundaries.md` | 19 | content merged to `assets/CREED-template.md` § Dominion |
| `_bmad/memory/marcus-sidecar/patterns.md` | 3 | empty stub ("No durable patterns recorded yet") — no merge |
| `_bmad/memory/marcus-sidecar/chronology.md` | 3 | empty stub — no merge |

### Downstream Reference Map Summary

| Reference type | Count | Affected files |
|---------------|-------|----------------|
| Path-only (scripts/, references/) | ~160 | Tier-B AC covers all (paths preserved) |
| Section-anchor | 1 | `docs/dev-guide.md:566` (External Skills routing table) — **updated to point at new external-specialist-registry.md** |
| Doctrine quote | 0 | n/a |
| Legacy sidecar path (`marcus-sidecar`) | ~92 | deprecated with banner; not removed; Epic 27 cleanup |

**Link-rewrite sweep pre-count:** 1 section-anchor
**Link-rewrite sweep post-count (newly-broken):** 0

---

## During-Migration Decisions

- **Decision 1 — Keep `specialist-registry.yaml` and `workflow-templates.yaml` in skill bundle, not sanctum.** These are infrastructure configs consumed by scripts at runtime, not agent memory. Scaffold globs `*.md` for references, which naturally excludes YAMLs. Confirmed correct — scripts resolve from skill bundle path, not sanctum. YAMLs stay put.
- **Decision 2 — New `external-specialist-registry.md` preserves the tables verbatim but cross-links to `specialist-registry.yaml` (canonical paths) and `conversation-mgmt.md` (envelope schema).** Avoids duplicating path data while keeping the delegation context-envelope narrative in a discoverable place.
- **Decision 3 — Principles live in CREED, not a separate `principles.md`.** The CREED-template already has the 10 Marcus principles embedded. A standalone `references/principles.md` would duplicate. Paige's "one home per chunk" rule.
- **Decision 4 — SKILL.md target size is 78 lines, over Texas's 35 but under the AC ceiling of 120.** Orchestrator router surface (capability table with 7 codes + CD routing paragraph) justifies the extra length. Specialists can aim lower in their future migrations.
- **Decision 5 — Legacy sidecar path (`_bmad/memory/marcus-sidecar/`) deprecated, not removed.** Two runtime callers still resolve it (`scripts/state_management/init_state.py`, `tests/test_state_management.py`). Epic 27 cleanup will prune.
- **Decision 6 — Existing references get BMB frontmatter retrofitted (name/code/description).** Required for auto-discovery into CAPABILITIES.md. Conservative additions — no existing content altered.
- **Decision 7 — Old sidecar files (`access-boundaries.md`, `patterns.md`, `chronology.md`) stay in-place alongside the deprecation banner.** Removing would break the 92 historical-report references even after deprecation. Epic 27 handles.

---

## Post-Migration Verification

### Scaffold Dry Run
```
$ .venv/Scripts/python skills/bmad-agent-marcus/scripts/init-sanctum.py --dry-run
BMB Sanctum Scaffold v0.1 — DRY RUN
Skill: bmad-agent-marcus
Target sanctum: _bmad/memory/bmad-agent-marcus
Would render 6 templates from assets/:
  INDEX-template.md -> INDEX.md (+ 5 more)
Would copy 15 reference files.
Would copy 23 scripts.
Would discover 7 capabilities via frontmatter: CM, PR, HC, MM, SP, SM, SB
```

### Scaffold Real Run
```
$ .venv/Scripts/python skills/bmad-agent-marcus/scripts/init-sanctum.py
BMB Sanctum Scaffold v0.1 — COMPLETE
Sanctum written to: _bmad/memory/bmad-agent-marcus
```

### Sanctum Tree
```
$ ls _bmad/memory/bmad-agent-marcus/
BOND.md  CAPABILITIES.md  CREED.md  INDEX.md  MEMORY.md  PERSONA.md
capabilities/  references/  scripts/  sessions/
```

All six sanctum files present; sessions/, capabilities/, references/, scripts/ subdirectories created.
CAPABILITIES.md correctly auto-discovered all 7 capability codes (CM, PR, HC, MM, SP, SM, SB).

### Test Results
- `tests/migration/test_bmb_scaffold.py`: **13 passed, 0 skipped, 0 failed**
- Full pytest suite (all testpaths): **932 passed, 2 skipped, 0 failed** (baseline was 919; new total includes +13 migration tests = 932 exact)
- Contract validator: **0 errors** (9 files, 79 criteria)
- Structural walks: _(not re-run this session; baseline 3/3 READY preserved)_

### Fixes Applied to Pre-Existing Tests

Three contract tests were reading specialist names directly from Marcus's legacy SKILL.md. Updated to read from the new `external-specialist-registry.md`:
- `tests/test_canva_specialist_contract.py::test_marcus_lists_canva_specialist_as_active`
- `tests/test_coursearc_specialist_contract.py::test_marcus_lists_coursearc_as_active`
- `tests/test_manual_tool_specialist_contracts.py::test_marcus_registry_lists_story_5_1_specialists`

These edits are **part of** the Marcus migration (AC E3 moved the table); no semantic change — tests still validate Marcus registers the specialists, just at the new canonical location.

### Negative Test
- Scenario: Marcus's sanctum absent (simulated via test checking that SKILL.md references first-breath.md and does NOT retain embedded doctrine).
- Observed: Test `test_negative_case_missing_sanctum_routes_to_first_breath` passes. New SKILL.md explicitly names `first-breath.md` and the activation branch. Embedded doctrine (Principles, Communication Style, Capability procedures) is absent from SKILL.md; only the terse BMB blocks remain.

---

## Review Record

_(filled after `bmad-code-review` runs — see story artifact Review Record section)_

---

## Lessons Learned

- **Scaffold `*.md`-only glob is intentional and correct.** YAMLs are skill-infrastructure, not agent memory. Future migrations should NOT add YAMLs to the scaffold copy set.
- **Auto-capability discovery via frontmatter requires retrofitting the existing refs.** Add `name:` + `code:` + `description:` frontmatter to capability references before scaffolding. Future migrations: build this into the runbook step 5 (doctrine extraction) explicitly.
- **Contract tests that read legacy SKILL.md section names will break.** Enumerate them with grep before scaffolding; fix them as part of the migration, not as follow-up. For Marcus, 3 tests needed the `external-specialist-registry.md` redirect.
- **Forwarder script is 18 lines and should stay that short.** If it grows, the agent-specific logic belongs in `.bmb-scaffold-config.yaml`, not the forwarder.
- **73-line SKILL.md for Marcus (orchestrator) sets the practical floor for the ≤80 ceiling.** AC A1 now tiers: orchestrator ≤80, specialist ≤60. Review flagged the initial 84-line draft.
- **Sanctum sessions/ and capabilities/ need `.gitkeep`** so git tracks empty dirs. Scaffold handles this automatically.
- **Downstream reference map is the highest-leverage pre-work.** Spent 5 minutes, saved us from breaking 3 tests silently. Build it for every Tier-1 agent.
