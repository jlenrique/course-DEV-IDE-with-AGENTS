# How to add a dispatch edge (Marcus)

Audience: Developers adding or retrofitting a Marcus to specialist boundary to
use the PR-R dispatch contract.

When this guide applies:
- You are adding a new edge that sends work from Marcus to a specialist.
- You are retrofitting an existing edge to emit standard dispatch envelope and
  receipt payloads.

When this guide does not apply:
- You are changing specialist-internal logic.
- You are changing retrieval adapter behavior (use
  [how-to-add-a-retrieval-provider.md](how-to-add-a-retrieval-provider.md)).

## 1. Know the three contract surfaces

Every dispatch edge must align three surfaces:

1. Code contract: [marcus/dispatch/contract.py](../../marcus/dispatch/contract.py)
2. Registry lockstep: [skills/bmad-agent-marcus/references/dispatch-registry.yaml](../../skills/bmad-agent-marcus/references/dispatch-registry.yaml)
3. L1 checker: [scripts/validators/check_dispatch_registry_lockstep.py](../../scripts/validators/check_dispatch_registry_lockstep.py)

If you change one, update the others in the same story.

## 2. Add or reuse a dispatch kind

Preferred order:
- Reuse an existing `DispatchKind` when semantics match.
- Add a new enum value only if this is a genuinely new edge type.

When adding a new kind:
- Add enum member in `DispatchKind`.
- Add specialist mapping in `DISPATCH_KIND_TO_SPECIALIST`.
- Keep `_classify_dispatch_kind` fail-closed for unknown values.

Do not use open string dispatch kinds in boundary scripts.

## 3. Register the edge

Add one row under `dispatch_edges` in
[skills/bmad-agent-marcus/references/dispatch-registry.yaml](../../skills/bmad-agent-marcus/references/dispatch-registry.yaml):
- `dispatch_kind`
- `specialist_id`
- `entrypoint`
- `contract_module`
- short `notes`

Then run the lockstep validator:
- python -m scripts.validators.check_dispatch_registry_lockstep

Use module invocation. Running script paths directly can break imports.

## 4. Retrofit the boundary script additively

In the edge entrypoint script, follow this sequence:

1. Build envelope near start:
- `build_dispatch_envelope(...)`
- include `run_id`, `dispatch_kind`, edge-specific `input_packet`, and useful
  `context_refs`

2. Emit structured start log:
- `dispatch.start` with `dispatch_start_log_fields(...)`

3. On each terminal branch (success and each failure branch):
- build receipt with `build_dispatch_receipt(...)`
- attach nested `dispatch_contract` payload
- emit `dispatch.end` with `dispatch_end_log_fields(...)`

Additive retrofit rule:
- Keep existing output shape stable.
- Add `dispatch_contract` as a nested field.
- Do not remove legacy fields in the same story unless explicitly scoped.

## 5. Pin or refresh schema artifacts

If contract schema changed, update
[state/config/schemas/marcus-dispatch-envelope.schema.json](../../state/config/schemas/marcus-dispatch-envelope.schema.json)
from `dump_contract_schemas()` output.

If this story touched pipeline lockstep surfaces, ensure
[state/config/pipeline-manifest.yaml](../../state/config/pipeline-manifest.yaml)
includes the new paths.

## 6. Test requirements

Minimum test set per edge:
- Contract model validation on emitted envelope and receipt.
- Success and failure branch coverage for receipt emission.
- Unknown dispatch kind rejection stays fail-closed.

Recommended locations:
- Contract unit tests: [tests/marcus_dispatch/test_dispatch_contract.py](../../tests/marcus_dispatch/test_dispatch_contract.py)
- Registry lockstep tests: [tests/marcus_dispatch/test_dispatch_registry_lockstep.py](../../tests/marcus_dispatch/test_dispatch_registry_lockstep.py)
- Edge boundary tests beside the entrypoint script tests.

## 7. Validation commands

Run these before closing the story:

1. Focused dispatch tests
- python -m pytest tests/marcus_dispatch/test_dispatch_contract.py tests/marcus_dispatch/test_dispatch_registry_lockstep.py

2. Retrofitted edge tests
- python -m pytest <edge-test-files>

3. Lockstep validators
- python -m scripts.utilities.check_pipeline_manifest_lockstep
- python -m scripts.validators.check_dispatch_registry_lockstep

## 8. Worked examples in this repo

Current PR-R retrofit examples:
- Irene Pass 2 boundary:
  [skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py](../../skills/bmad-agent-marcus/scripts/prepare-irene-pass2-handoff.py)
- Kira motion boundary:
  [skills/kling-video/scripts/run_motion_generation.py](../../skills/kling-video/scripts/run_motion_generation.py)
- Texas retrieval boundary:
  [skills/bmad-agent-texas/scripts/run_wrangler.py](../../skills/bmad-agent-texas/scripts/run_wrangler.py)

These examples show additive `dispatch_contract` attachment while preserving
existing payload contracts.
