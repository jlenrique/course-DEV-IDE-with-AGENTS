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

Paste the following prompt to Marcus:

```
Run a Fidelity Walk.

Step through the full happy-path orchestration from source intake to Descript package
aggregation, one gate at a time (G0 → G6). At each step, identify every script, skill,
resource, and fidelity contract that would be invoked and confirm whether each is present,
valid, and consistent with its declared inputs/outputs. Surface any gaps, mismatches, or
remediation needs. Produce a sequenced report — one section per gate — with a final
summary verdict.

Save the report as a timestamped Markdown file:
  tests/fidelity-walk-YYYYMMDD-HHMMSS.md
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

---

## Output Location

All Fidelity Walk reports are saved to `tests/` with the naming convention:

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
