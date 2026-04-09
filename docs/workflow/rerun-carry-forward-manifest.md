# Re-Run Carry-Forward Manifest

When re-running a production run with identical source material, copy these files from the prior bundle to the new bundle **before** executing the prompt pack. Files are grouped by the earliest prompt that requires them.

## Minimum carry-forward set

### Required before Prompt 1 (Activation + Preflight)
- `run-constants.yaml` — **create new** (do not copy; new run ID and updated parameters)
- `metadata.json` — **create new** with updated run ID, `prior_run_id` field, carried provenance

### Required before Prompt 2A (Operator Directives)
- `operator-directives.md` — copy, update `run_id` header

### Required before Prompt 3 (Ingestion Validation)
- `extracted.md` — copy as-is (identical source material)
- `raw/` — copy entire directory (perception artifacts)
- `ingestion-evidence.md` — copy as-is

### Required before Prompt 4 (Quality Gate)
- `ingestion-quality-gate-receipt.md` — copy, update `run_id` and `bundle_path`
- `irene-packet.md` — copy, update `run_id` and `bundle_path`

### Created empty (prompt pack populates during run)
- `storyboard/`
- `gamma-export/`
- `motion/`
- `recovery/`
- `assembly-bundle/`

## Run ID stamping

After copying, update the `run_id` and `bundle_path` references in:
- `operator-directives.md`
- `ingestion-quality-gate-receipt.md`
- `irene-packet.md`

Add `carried_from: <prior_run_id>` to any carried file's header for provenance.

## Files NOT carried (regenerated during run)
- `gary-slide-content.json`
- `gary-fidelity-slides.json`
- `gary-diagram-cards.json`
- `gary-theme-resolution.json`
- `gary-outbound-envelope.yaml`
- `gary-dispatch-result.json`
- `irene-pass1.md`
- `narration-script.md`
- `segment-manifest.yaml`
- `authorized-storyboard.json`
- `motion-designations.json`
- `motion_plan.yaml`
- `pass2-envelope.json`
- `voice-selection.json`
- All `storyboard/`, `gamma-export/`, `assembly-bundle/` contents

## Future improvement
A `init_rerun_bundle.py --from <prior-bundle> --run-id <new-id>` script would automate this entire process including run ID stamping.
