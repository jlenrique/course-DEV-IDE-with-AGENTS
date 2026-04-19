# Fidelity Walk

`Fidelity Walk` is now a legacy name for the canonical
[Structural Walk](structural-walk.md).

Use this page only as a compatibility note if older docs, prompts, or
operator habits still reference `python -m scripts.utilities.fidelity_walk`.

## Canonical Procedure

Use:

```powershell
.\.venv\Scripts\python.exe -m scripts.utilities.structural_walk --workflow standard
.\.venv\Scripts\python.exe -m scripts.utilities.structural_walk --workflow motion
```

The canonical documentation lives in [docs/structural-walk.md](structural-walk.md).

## Legacy Alias

This compatibility command still works:

```powershell
.\.venv\Scripts\python.exe -m scripts.utilities.fidelity_walk
```

Behavior:

- routes to the canonical structural walk
- defaults to the `standard` workflow
- writes reports under `reports/structural-walk/standard/`
- prints the canonical command so operators can migrate cleanly

## Why The Rename Happened

The old name implied a full happy-path simulation. The implemented tool is
better described as a workflow-specific structural sanity check:

- gate asset integrity
- contract and config parsing
- executable import sanity
- workflow-document integrity markers
- optional command probes
