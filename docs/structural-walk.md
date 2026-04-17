# Structural Walk

The Structural Walk is the canonical sanity check for the repo's
primary narrated production workflows:

- `standard` - narrated deck video export without motion
- `motion` - motion-enabled narrated workflow with Gate 2M and Motion Gate
- `cluster` - cluster + interstitial narrated workflow with G1.5 and G2.5 gates

It is intentionally narrower than a full end-to-end simulation. The
default run is deterministic and local, but it uses real checks where
the dependency is meant to be runnable or parseable:

- fidelity contract validation
- YAML and JSON parsing
- Python import sanity for executable scripts
- redirect placeholder verification
- workflow-document integrity checks
- optional command probes for CLI/API readiness

Generated reports are operational artifacts and now live under
`reports/structural-walk/`, not `tests/`.

Workflow parity data is now declared in machine-readable manifests under:

- `state/config/structural-walk/standard.yaml`
- `state/config/structural-walk/motion.yaml`
- `state/config/structural-walk/cluster.yaml`

Those manifests define the workflow-specific cross-cutting checks and
document-integrity checkpoints that the canonical tool evaluates.

## When To Run

- before the first live run of a new workflow variant
- after changes to contracts, prompt packs, orchestration, or key scripts
- as a branch-close or pre-release sanity check
- when a human checkpoint suggests structural drift in the pipeline

## Canonical Commands

Standard workflow:

```powershell
python -m scripts.utilities.structural_walk --workflow standard
```

Motion workflow:

```powershell
python -m scripts.utilities.structural_walk --workflow motion
```

Cluster workflow:

```powershell
python -m scripts.utilities.structural_walk --workflow cluster
```

Optional explicit output path:

```powershell
python -m scripts.utilities.structural_walk --workflow motion --output reports/structural-walk/motion/custom-report.md
```

Optional live probes:

```powershell
python -m scripts.utilities.structural_walk --workflow standard --live-probe contracts-cli
python -m scripts.utilities.structural_walk --workflow motion --live-probe heartbeat
```

Read-only dry-run planning preview:

```powershell
python -m scripts.utilities.structural_walk --workflow standard --dry-run
python -m scripts.utilities.structural_walk --workflow motion --dry-run
python -m scripts.utilities.structural_walk --workflow cluster --dry-run
```

Exit code rules:

- `0` means `READY`
- `1` means remediation is required

## Output Locations

Default report paths:

- `reports/structural-walk/standard/structural-walk-standard-YYYYMMDD-HHMMSS.md`
- `reports/structural-walk/motion/structural-walk-motion-YYYYMMDD-HHMMSS.md`
- `reports/structural-walk/cluster/structural-walk-cluster-YYYYMMDD-HHMMSS.md`

Historical fidelity-walk artifacts from earlier sessions are retained under:

- `reports/structural-walk/standard/history/`

## What It Checks

For standard, motion, and cluster workflows:

- G0-G6 gate asset integrity
- cross-cutting orchestrator and validator assets
- literal-visual contract/operator checkpoints
- prompt-pack document integrity markers
- creative directive contract presence (`skills/bmad-agent-cd/references/creative-directive-contract.md`)
- experience-profiles configuration (`state/config/experience-profiles.yaml`)
- parameter-registry schema (`state/config/parameter-registry-schema.yaml`)

For motion workflow only:

- motion-planning and Kling execution assets
- motion manifest hydration and motion perception wiring
- Gate 2M / Motion Gate / winner-deck binding markers

For cluster workflow:

- G1.5 Cluster Plan gate contract (`state/config/fidelity-contracts/g1.5-cluster-plan.yaml`)
- cluster dispatch sequencing (`skills/bmad-agent-marcus/scripts/cluster_dispatch_sequencing.py`)
- cluster coherence validation (`skills/bmad-agent-marcus/scripts/cluster_coherence_validation.py`)
- cluster prompt engineering (`skills/bmad-agent-marcus/scripts/cluster_prompt_engineering.py`)
- cluster template library (`skills/bmad-agent-marcus/scripts/cluster_template_library.py`)
- cluster template planner (`skills/bmad-agent-marcus/scripts/cluster_template_planner.py`)
- cluster template selector (`skills/bmad-agent-marcus/scripts/cluster_template_selector.py`)
- cluster prompt engineering config (`state/config/prompting.yaml`)
- dispatch policy config (`state/config/dispatch.yaml`)
- validation rules config (`state/config/validation.yaml`)
- interstitial redispatch protocol (`skills/bmad-agent-marcus/scripts/interstitial_redispatch_protocol.py`)
- interstitial redispatch CLI (`skills/bmad-agent-marcus/scripts/run-interstitial-redispatch.py`)
- G4-16–19 cluster-specific criteria in the G4 contract

## Manifest Contract

The workflow manifests are declarative parity registries, not runtime
orchestration plans. In tranche two they serve one purpose:

- declare the workflow-specific structural checks in a machine-readable form

They do not, by themselves:

- run production workflows
- add network-bound behavior
- replace gate/contract vocabulary
- remove the legacy fidelity-walk alias

## Dry-Run Planning Preview

The current dry-run slice is deliberately narrow:

- supports standard, motion, and cluster workflow previews
- local and deterministic
- read-only apart from the generated report
- no network, no live probes, no downstream asset generation
- `--dry-run` cannot be combined with `--live-probe`
- standard preview includes the broader local contract/document summary steps already approved
- motion and cluster previews currently add manifest resolution plus Marcus-derived workflow sequence parity
- all supported workflows can also verify manifest-declared Marcus stage-to-document checkpoint parity

It adds two report sections:

- `Dry Run Plan`
- `Dry Run Results`

This mode is a planning preview, not a workflow execution.

Accepted dry-run step kinds in the current manifest contract:

| Kind | Meaning |
| --- | --- |
| `manifest` | Resolve the selected workflow manifest, confirm the dry-run shape, and confirm Marcus planning assets used by the preview are declared in that workflow manifest |
| `sequence` | Resolve Marcus's workflow template locally and preview the resulting stage sequence |
| `sequence_docs` | Validate manifest-declared document checkpoints against Marcus's resolved stage order for that workflow |
| `contracts` | Summarize local contract-validation readiness for the workflow |
| `aggregate` | Summarize cross-cutting structural checks for the workflow |
| `documents` | Summarize workflow-document parity checks for the workflow |

## Legacy Alias

The legacy command still works:

```powershell
python -m scripts.utilities.fidelity_walk
```

It is now a compatibility alias that routes to the canonical structural
walk for the `standard` workflow and prints the canonical command.
