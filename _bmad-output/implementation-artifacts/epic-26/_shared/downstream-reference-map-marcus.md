# Downstream Reference Map — Marcus (Pre-Work for Story 26-1)

**Built:** 2026-04-17
**Source commands:**
```bash
grep -rn "skills/bmad-agent-marcus/" docs/ scripts/ tests/ _bmad-output/ state/ maintenance/
grep -rn "marcus-sidecar" docs/ scripts/ tests/ _bmad-output/ state/
```

**Purpose:** Enumerate everything that references Marcus by path or section anchor, so Story 26-1 can verify nothing breaks.

---

## Summary

| Reference type | Count | Risk if Marcus migration breaks it |
|---|---|---|
| `skills/bmad-agent-marcus/scripts/*` | ~120 | HIGH — broken CLI invocations in docs + tests |
| `skills/bmad-agent-marcus/references/*` | ~40 | HIGH — broken doc links in user/admin/dev guides |
| `skills/bmad-agent-marcus/SKILL.md` | ~15 | MEDIUM — section-anchor references (no line-level anchors in use today; H2-only) |
| `_bmad/memory/marcus-sidecar/*` | ~90 | LOW — mostly structural-walk reports and session notes; not runtime-critical |
| `marcus-sidecar` (string reference) | ~2 | LOW — will update in E2 deprecation banner |

## Tier-B AC Coverage

**Tier-B (Path Preservation) in the shared AC already mandates:**
- B1 — scripts/ paths unchanged
- B2 — references/ paths unchanged
- B3 — tests/ paths unchanged

Which means ~160 of the ~165 HIGH/MEDIUM references self-resolve by not moving anything. The migration-specific concern is just SKILL.md-internal anchors.

## SKILL.md Section-Anchor References

Callers that reference Marcus's SKILL.md by content (not path):

| Caller | Anchor/content | Migration destination | Action |
|--------|----------------|------------------------|--------|
| `docs/dev-guide.md:566` | "Marcus's External Skills routing table in `SKILL.md`" | **new** `references/external-specialist-registry.md` | update doc link |
| `docs/lane-matrix.md:42` | checklist reference to `bmad-agent-marcus/SKILL.md` | SKILL.md still exists | no change needed (path still resolves) |
| `bmad-session-protocol-session-START.md:98` | "Master Orchestrator: Marcus (`skills/bmad-agent-marcus/SKILL.md`)" | SKILL.md still exists | no change needed |
| `maintenance/cross-harmonization-report-2026-04-15-pass2.md:59` | "CD routing confirmed at lines 29/31/37/65-72/224" | line numbers will shift after SKILL.md rewrite | **stale reference** — already stale as soon as any edit happens; not Marcus-migration-caused |
| `_bmad-output/implementation-artifacts/3-*-*.md` | delegation to Marcus (several stories) | Marcus delegates via CREED + references/specialist-registry.md | no change needed (conceptual, not path) |

## Reference-File Paths (must survive per AC B2)

Documented callers of Marcus's `references/*.md`:

| Caller | Target ref | Status |
|--------|------------|--------|
| `docs/ad-hoc-contract.md:9-10` | `mode-management.md`, `conversation-mgmt.md` | paths preserved ✓ |
| `docs/app-logging-evaluation.md:56,214` | `conversation-mgmt.md` | paths preserved ✓ |
| `docs/dev-guide.md:135` | `workflow-templates.yaml` | paths preserved ✓ |
| `docs/user-guide.md:281` | `conversation-mgmt.md` (Imagine handoff) | paths preserved ✓ |
| `docs/user-guide.md:304` | `mode-management.md` | paths preserved ✓ |
| `docs/workflow/production-session-start.md:75` | `specialist-registry.yaml` | paths preserved ✓ |
| `scripts/utilities/structural_walk.py:674` | `workflow-templates.yaml` | paths preserved ✓ |

## Script-Path Callers (must survive per AC B1)

Key script-path callers from the grep sweep (sample; full output in [raw grep log below](#raw-grep-output-excerpt)):

- `docs/admin-guide.md:506-507` — `build-pass2-inspection-pack.py`, `prepare-irene-pass2-handoff.py`
- `docs/admin-guide.md:564` — `validate-gary-dispatch-ready.py`
- `docs/structural-walk.md:119-129` — cluster_* scripts + interstitial_redispatch scripts
- `docs/workflow/cluster-workflow.md:40-43` — cluster_* scripts
- `docs/workflow/first-tracked-run-checklist.md:71,75` — pass2 scripts
- `docs/workflow/operator-script-v4.2-irene-ab-loop.md:196` — `evaluate_cluster_template_selection.py`
- `docs/user-guide.md:122-123` — pass2 scripts
- `pyproject.toml:43`, `.vscode/settings.json:8` — `scripts/tests` dir
- `skills/production-coordination/scripts/run_reporting.py` — platform allocation import path
- `skills/bmad-agent-audra/SKILL.md` — cross-agent reference (Audra knows of Marcus)
- `scripts/state_management/init_state.py` — references the sidecar path (`marcus-sidecar/` will be deprecated, not removed)
- `tests/test_structural_walk.py` — multiple Marcus script paths exercised

## Marcus Sidecar Path References (deprecation, not removal)

`_bmad/memory/marcus-sidecar/` appears in ~90 files, almost all in `reports/structural-walk/`, `reports/doc-drift-audit-*/`, and `reports/dev-coherence/`. These are **historical reports**, not active runtime consumers.

**Action for 26-1:**
- Add deprecation banner to `_bmad/memory/marcus-sidecar/index.md` pointing to `_bmad/memory/bmad-agent-marcus/`.
- Do **not** remove sidecar files in this story. Epic 27 cleanup.
- If any active runtime (not report) resolves `marcus-sidecar/`, it must continue to resolve. Grep shows `scripts/state_management/init_state.py` and `tests/test_state_management.py` — check these carefully in Step 10 link-rewrite sweep.

## Raw Grep Output Excerpt

Full listings suppressed for brevity; regenerate via the commands at the top of this file. Key first-page output:

```
bmad-session-protocol-session-START.md:98,236
docs/ad-hoc-contract.md:9,10
docs/admin-guide.md:107,506,507,564
docs/app-logging-evaluation.md:56,214
docs/dev-guide.md:121,135,566,593
docs/directory-responsibilities.md:41,42
docs/lane-matrix.md:42
docs/project-context.md:150,217
docs/structural-walk.md:119-129
docs/user-guide.md:122,123,281,304
docs/workflow/cluster-workflow.md:40-43
docs/workflow/first-tracked-run-checklist.md:71,75
docs/workflow/operator-script-v4.2-irene-ab-loop.md:196
docs/workflow/production-session-start.md:75
pyproject.toml:43
.vscode/settings.json:8
skills/bmad-agent-audra/SKILL.md
skills/bmad-agent-marcus/SKILL.md (self)
skills/bmad-agent-marcus/references/memory-system.md (self)
skills/bmad-agent-marcus/references/save-memory.md (self)
skills/bmad-agent-marcus/references/init.md (self)
skills/bmad-agent-marcus/scripts/platform_allocation.py (self)
skills/production-coordination/scripts/run_reporting.py
scripts/state_management/init_state.py
scripts/utilities/structural_walk.py:674
state/config/structural-walk/{standard,cluster,motion}.yaml
tests/test_state_management.py
tests/test_structural_walk.py
```

## Conclusions for Story 26-1

1. **Tier-B path-preservation AC covers ~95% of the risk surface**: don't move scripts/ or references/.
2. **The only section-anchor reference worth migrating explicitly** is `docs/dev-guide.md:566` (External Skills routing table) — update that single doc link when the new `references/external-specialist-registry.md` lands.
3. **Line-number references in maintenance reports** (`cross-harmonization-report-*`) are already stale and not Marcus-migration-caused. Out of scope.
4. **Marcus sidecar** (`_bmad/memory/marcus-sidecar/`) is referenced by historical reports only, plus two runtime callers (`init_state.py`, `test_state_management.py`) that must continue to resolve. Deprecate in-place, don't remove.
5. **No cross-agent SKILL.md references** need content updates (Audra references Marcus structurally, not by anchor).
