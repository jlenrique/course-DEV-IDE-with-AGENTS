# Fidelity Walk

A **Fidelity Walk** is a faithful simulation of the full happy-path production run, orchestrated by Marcus. It steps through every gate (G0 → G6) and confirms that every script, skill, resource, and fidelity contract invoked along the way is present, internally consistent, and correctly wired to its declared inputs and outputs. The walk does not produce real media artifacts — it produces a sequenced validation report that either confirms readiness or surfaces remediation needs before a live run.

Documented redirects are valid. If a placeholder path explicitly declares itself superseded and points to the active canonical path, record it as a redirect rather than a remediation item.

---

## When to Run

- Before the first live production run of a new course unit
- After any significant change to skills, scripts, fidelity contracts, or agent wiring
- As a release-gate check when closing a branch (post-sprint, pre-merge)
- Whenever a HIL checkpoint flags a structural concern worth tracing upstream

---

## Invoking the Fidelity Walk

Canonical invocation is the scripted generator:

```powershell
python -m scripts.utilities.fidelity_walk
```

Optional explicit output path:

```powershell
python -m scripts.utilities.fidelity_walk --output tests/fidelity-walk-YYYYMMDD-HHMMSS.md
```

Operator rule:
- Do not hand-compose or ad hoc generate Fidelity Walk reports.
- Treat the scripted output as the source of truth for canonical gate asset names and anti-drift checks.
- Exit code `0` means `READY`; exit code `1` means remediation is required.

If Marcus is driving the session conversationally, use a prompt that delegates to the scripted generator rather than freehand report writing:

```
Run a Fidelity Walk.

Invoke `python -m scripts.utilities.fidelity_walk` from the repo root.
Return the generated report path, overall verdict, critical finding count,
and any remediation items. Do not substitute guessed gate asset names.
```

---

## Report Structure (expected output)

Marcus should produce one section per gate following this pattern:

```markdown
## Gate Gn — <Artifact Name>

**Producing Agent:** <agent>  
**Source of Truth:** <input>  
**Fidelity Contract:** <path to g{n}-*.yaml>

### Invoked Assets
| Type     | Path                          | Status        |
|----------|-------------------------------|---------------|
| Skill    | skills/bmad-agent-{x}/        | ✅ Present     |
| Script   | scripts/{x}.py                | ✅ Present     |
| Contract | state/config/fidelity-contracts/g{n}-*.yaml | ✅ Valid |

### Findings
- _None_ / <list gaps, mismatches, or remediation items>
```

Final section must be:

```markdown
## Summary Verdict

**Overall status:** READY | NEEDS REMEDIATION  
**Critical findings:** <count>  
**Remediation items:** <bulleted list or "None">
```

The scripted report also includes a cross-cutting checks section for orchestration,
sidecars, redirect placeholders, and the contract validator.

Required anti-drift checks in the walk report:
- Verify Prompt 6B checkpoint exists and blocks Prompt 7 when required literal-visual cards are not operator-ready.
- Verify literal-visual dispatch payload rule is enforced: image-only on-slide, URL-only content rows, and explanatory prose deferred to narration.
- Verify Storyboard A checkpoint is required after Gary dispatch and before Gate 2 approval.
- Verify Storyboard B checkpoint is required after Irene Pass 2 and before downstream audio/script finalization.

---

## Output Location

By default the generator saves Fidelity Walk reports to `tests/` with the naming convention:

```
fidelity-walk-YYYYMMDD-HHMMSS.md
```

This follows the precedent set by prior simulation artifacts in `tests/`:
- `simulated-run-happy-path-20260402-224500.md`
- `Happy Path Simulation Display Screens 2026-04-03.md`

---

## Related Documents

- [docs/fidelity-gate-map.md](fidelity-gate-map.md) — authoritative gate definitions, role matrix, and assessment ordering
- [docs/lane-matrix.md](lane-matrix.md) — cross-agent ownership and lane responsibilities
- [state/config/fidelity-contracts/](../state/config/fidelity-contracts/) — L1 fidelity contracts per gate
- [docs/project-context.md](project-context.md) — system architecture and operational model
