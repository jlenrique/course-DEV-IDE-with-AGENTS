# L2 Agentic Sweep

Runs only when L1 has returned exit code 0. Scope: recently-changed docs in the session anchor's git-diff window (since-handoff default) or a specified directory.

Every L2 finding is an **observation**, not a verdict. Operator or Cora or Paige judges whether the observation warrants action.

## Check Catalog

### L2-1: Prose Drift

For each changed doc in the window, read the doc's narrative. For each load-bearing claim in the narrative (a claim about what the code does, what a contract means, what a lane owns):

- Sample the corresponding code or contract to spot-check whether the narrative still matches
- If the narrative and the sampled reality disagree, flag drift

Flag as L2 finding, type: `alteration`, severity by drift magnitude:

- Low: cosmetic (terminology that has aged, a renamed script path mentioned but the old name still works)
- Medium: narrative describes a workflow variant that is still supported but no longer default
- High: narrative describes a capability that no longer exists

Substantial drift (more than paragraph scope) → include `route_offered: bmad-agent-tech-writer` in the trace report.

### L2-2: Intent-of-Change

For each story that landed since the anchor, look at the git diff. If the diff includes a schema, contract, or parameter-registry touch but does not include a corresponding doc update:

- Read the commit message and story file to infer intent
- Decide whether the gap is real (doc update missed) or internal (pure schema move with no public-facing meaning change)

Flag as L2 finding, type: `omission`, severity:

- Low: purely internal schema move, no doc update needed
- Medium: ambiguous — doc update might be warranted
- High: schema change is publicly meaningful; doc update is missing

This is a classic agentic-judgment check. Do not mechanize; the intent inference depends on reading prose and code together.

### L2-3: Doc-to-Code Narrative Alignment

For high-leverage docs (Marcus SKILL.md, lane-matrix.md, fidelity-gate-map.md, parameter-directory.md, structural-walk.md, directory-responsibilities.md):

- Scan for claims about specific capabilities, scripts, or flows
- Spot-check against the current state of those capabilities

Flag misalignment as L2 finding, type: `alteration`, severity by load-bearing-ness. Lane-matrix misalignment is always High.

### L2-4: Parameter-Directory Pruning Candidates

Read `docs/parameter-directory.md`. For each parameter row:

- Check whether any validator or consumer references the parameter (grep across `scripts/`, `skills/`, `_bmad/`, config files)
- If no reference, flag as pruning candidate

Flag as L2 finding, type: `omission` (in reverse — parameter present but not used), severity: `low`. The operator decides whether to prune or whether the unused parameter has a known reason.

### L2-5: Lane-Matrix Gap Sensing

Read `docs/lane-matrix.md`. For any skill directory under `skills/bmad-agent-*/` **not** listed in the Coverage Checklist:

- Decide whether the skill genuinely owns a lane that the matrix is missing

Flag as L2 finding, type: `omission`, severity: `medium`. Route-offered: `bmad-agent-architect` (Winston) for lane-matrix hourglass-integrity review.

## Findings Format

Every L2 finding includes:

- `type`: omission | invention | alteration
- `severity`: low | med | high
- `check`: the L2 check ID
- `ref`: the doc path
- `detail`: one-line observation
- `evidence_path`: path under `evidence/` in the report home with the diff or excerpt
- `route_offered`: optional — target_agent + reason + affected_refs if the finding warrants routing beyond the operator

## Discipline Reminder

L2 findings are observations for the operator to judge. Audra does not author "fix this" language. Audra writes "here is what I observed; here is what that means; do you want to route this to Paige or handle inline?"
