# First-Run Setup for Audra

Welcome. Setting up Audra's internal-artifact auditor workspace.

## Memory Location

Creating `{project-root}/_bmad/memory/audra-sidecar/`.

## Initial Discovery

1. **Operator name** — Confirm from `_bmad/config.user.yaml`.
2. **Structural walk availability** — Confirm `python -m scripts.utilities.structural_walk --workflow standard` runs without error and returns an exit code. This is Audra's foundational L1 check.
3. **Lockstep pair presence** — Confirm `docs/parameter-directory.md` and `state/config/parameter-registry-schema.yaml` both exist.
4. **Sprint-status presence** — Confirm `_bmad-output/implementation-artifacts/sprint-status.yaml` exists.
5. **Report-home location** — Confirm `{project-root}/reports/dev-coherence/` is writable or can be created.
6. **Phase awareness** — Per `dev-support-agents-vision.md`, note which vision phases are live:
   - Phase 2 (single-command `dev_coherence_sweep.py` runner): planned, likely not shipped at init. Audra runs structural walk + per-check invocations directly until shipped.
   - Phase 3 (auxiliary check scripts): planned, likely not shipped at init. Same note.
   - Phase 6 (pre-closure hook in warn mode): live once Cora is wired to call Audra on story-done intent.

## Initial Structure

Create four sidecar files per memory-system.md:

- `index.md` — seeded with operator preferences and current invocation context (if any)
- `patterns.md` — empty header
- `chronology.md` — first entry: `YYYY-MM-DD HH:MM — Audra initialized.`
- `access-boundaries.md` — copied from sidecar template

Confirm: "Sidecar initialized. Ready to sweep."
