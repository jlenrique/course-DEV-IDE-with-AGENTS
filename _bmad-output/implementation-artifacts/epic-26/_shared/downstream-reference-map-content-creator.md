# Downstream Reference Map — Irene / bmad-agent-content-creator (Pre-Work for Story 26-2)

**Built:** 2026-04-17
**Source commands:**
```bash
grep -rn "skills/bmad-agent-content-creator/" docs/ scripts/ tests/ _bmad-output/ state/ maintenance/
grep -rn "irene-sidecar\|_bmad/memory/irene" docs/ scripts/ tests/ _bmad-output/ state/
```

**Purpose:** Enumerate everything that references Irene by path or section anchor, so Story 26-2 can verify nothing breaks.

---

## Summary

| Reference type | Count | Risk if migration breaks it |
|---|---|---|
| `skills/bmad-agent-content-creator/scripts/*` | ~60 | HIGH — Pass 2 perception_contract, visual_reference_injector, manifest_visual_enrichment, manual_animation_workflow |
| `skills/bmad-agent-content-creator/references/*` | ~75 | HIGH — artifact templates (lesson-plan, slide-brief, narration-script, segment-manifest, dialogue-script, assessment-brief, first-person-explainer), cluster docs, delegation-protocol, pedagogy framework, runtime-variability framework |
| `skills/bmad-agent-content-creator/SKILL.md` | ~10 | MEDIUM — mostly "Present" checks in structural-walk reports; one lane-matrix section checklist |
| `_bmad/memory/irene-sidecar/*` | ~7 | LOW — stub files; deprecate, don't remove |
| `irene-sidecar` (string ref) | ~5 | LOW — will update via deprecation banner |

## Tier-B AC Coverage

**Tier-B (Path Preservation)** mandates:
- B1 — scripts/ paths unchanged → covers ~60 script refs
- B2 — references/ paths unchanged → covers ~75 reference refs
- B3 — tests/ paths unchanged → covers `skills/bmad-agent-content-creator/scripts/tests/`

So ~135 of the ~145 HIGH/MEDIUM references self-resolve by not moving anything. New BMB seed refs + stub capability refs are additive.

## SKILL.md Section-Anchor References

Callers referencing Irene's SKILL.md by content (not path):

| Caller | Anchor/content | Migration destination | Action |
|--------|----------------|------------------------|--------|
| `docs/lane-matrix.md:43` | checklist reference to `bmad-agent-content-creator/SKILL.md` | new SKILL.md preserves `## Lane Responsibility` section (AC A1 canonical name) | no change needed (path + section resolves) |
| `maintenance/cross-harmonization-report-2026-04-15.md:33` | "Irene SKILL.md doesn't reference `narration_profile_controls` input" | historical finding, already remediated; reference is to SKILL.md Pass 2 content | **stale reference** — not Marcus-migration-caused (audit report from prior date) |
| `reports/structural-walk/cluster/*.md` | "Skill | skills/bmad-agent-content-creator/SKILL.md | Present" | SKILL.md still exists at path | no change needed (path still resolves) |
| `reports/dev-coherence/2026-04-16-2350/evidence/L1-5-lane-matrix-coverage.md` | checklist entry | SKILL.md exists + has Lane Responsibility section | no change needed |

**Conclusion**: zero blocking section-anchor rewrites needed. Irene migration is cleaner than Marcus (no `dev-guide.md:566`-style anchor pointing into SKILL.md content).

## Reference-File Path Callers (must survive per AC B2)

Sample of documented callers of Irene's `references/*`:

| Caller | Target ref | Status |
|--------|------------|--------|
| `skills/bmad-agent-marcus/references/external-specialist-registry.md` | `template-segment-manifest.md` | path preserved ✓ |
| `skills/compositor/references/*` | `template-segment-manifest.md` | path preserved ✓ |
| `docs/workflow/cluster-workflow.md` | `cluster-decision-criteria.md`, `cluster-density-controls.md`, etc. | paths preserved ✓ |
| `scripts/validate_fidelity_contracts.py` | `template-narration-script.md`, `template-segment-manifest.md` | paths preserved ✓ |
| Multiple `_bmad-output/implementation-artifacts/*` | cluster docs, delegation-protocol.md, pedagogical-framework.md | paths preserved ✓ |

## Script-Path Callers (must survive per AC B1)

Irene's scripts are called across the pipeline:

- `scripts/perception_contract.py` → `enforce_perception_contract()`, `enforce_motion_perception_contract()` — invoked from Pass 2 tests, structural walks, workflow docs
- `scripts/visual_reference_injector.py` → `inject_visual_references()`, `inject_all_slides()` — Pass 2 narration
- `scripts/manifest_visual_enrichment.py` → `apply_motion_plan_to_segments()` — Gate 2M hydration
- `scripts/manual_animation_workflow.py` — manual animation guidance

All paths preserved under AC B1.

## Irene Sidecar Path References (deprecation, not removal)

`_bmad/memory/irene-sidecar/` appears in ~7 files — structural-walk / dev-coherence reports. No active runtime consumers besides Irene herself via her SKILL.md activation block.

**Action for 26-2:**
- Add deprecation banner to `_bmad/memory/irene-sidecar/index.md` pointing to `_bmad/memory/bmad-agent-content-creator/`.
- Do **not** remove sidecar files. Epic 27 cleanup.
- No runtime callers identified (Irene's own Pass 2 scripts don't touch her sidecar directly).

## Raw Grep Output Summary

Full listings suppressed for brevity; regenerate via the commands at the top of this file. Key patterns:

```
docs/lane-matrix.md:43
docs/workflow/cluster-workflow.md (multiple)
docs/workflow/operator-script-v4.2-irene-ab-loop.md (multiple)
scripts/validate_fidelity_contracts.py
_bmad-output/planning-artifacts/architecture.md (multiple)
_bmad-output/implementation-artifacts/{19,20,22,23}-*-*.md (story artifacts)
_bmad-output/implementation-artifacts/sprint-status.yaml
skills/bmad-agent-marcus/references/external-specialist-registry.md (newly created for Marcus migration)
skills/compositor/ (multiple)
state/config/fidelity-contracts/g4-narration-script.yaml (template-narration-script ref)
```

## Conclusions for Story 26-2

1. **Tier-B path-preservation AC covers ~93% of the risk surface** — don't move scripts/ or references/.
2. **Zero blocking section-anchor rewrites** (simpler than Marcus, who had 1).
3. **Structural-walk reports and maintenance reports** reference SKILL.md by path — will still resolve post-migration.
4. **Irene sidecar deprecation** is clean: no runtime callers, 7 historical-report references.
5. **NEW concerns for Irene (not present in Marcus)**:
   - 20 capability codes vs Marcus's 7 — 5 route to scripts not refs, 4 share `pedagogical-framework.md`, 1 umbrella (CP) routes to 5 files. Requires stub refs for 10 of them to satisfy scaffold's frontmatter-discovery + unique-code guard.
   - 7 artifact-template files (`template-*.md`) — these are Irene's production output templates, NOT BMB sanctum templates. They stay in place; BMB assets templates are separate.
6. **No Marcus-migration-style contract-test breakage anticipated** (no tests grep Irene SKILL.md for specific specialist names).
