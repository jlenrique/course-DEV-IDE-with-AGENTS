# Audra Interaction Test Guide

**Agent:** bmad-agent-audra (Internal-Artifact Fidelity Auditor)
**Story:** (To be created in next-sprint planning)
**Last Updated:** 2026-04-16
**Prerequisites:** Fresh chat session. No prior Audra context.

## How to Use This Guide

Run each scenario in a fresh chat session. Say "Talk to Audra" or "Run a lockstep audit" to activate on the operator-direct path. Cora-route and Marcus-route-via-Cora tests require Cora (and, for the latter, Marcus's updated External Specialist Agents table per vision Phase 5) to be active.

These tests match the Tier 1 (static conformance) + Tier 2 (single-turn behavioral smoke test) validation tier approved 2026-04-16. Tier 3 (scripted deterministic+agentic sweep) is authored at the end of this guide.

---

## Test 1: First Activation & Greeting

**Trigger:** Fresh session, operator-direct invocation.

**What to say:**

> Talk to Audra

**Expected behavior:**

- Audra loads sidecar index.md, patterns.md, access-boundaries.md
- Audra asks scope handshake: "Full repo sweep, since-handoff, or directory-scoped?"
- Uses precise, evidence-rich persona — not chatty

**Pass criteria:**

- [ ] Identifies by name and role (Internal-Artifact Fidelity Auditor)
- [ ] Asks scope handshake before sweeping
- [ ] Defaults to since-handoff
- [ ] Does NOT mix conversational greeting with finding language
- [ ] Does NOT start sweeping without scope confirmation

---

## Test 2: Lane Awareness

**What to say:**

> What do you own, and what don't you own? Specifically, how is your lane different from Murat's?

**Expected behavior:**

- Audra recites her lane: internal-artifact lockstep
- Audra explicitly names the Murat boundary: Murat owns "does the code still work under test?"; Audra owns "do the load-bearing artifacts still describe the code?"
- Audra names Vera, Quinn-R, Marcus, Cora, Paige, Amelia, Winston as distinct lane owners

**Pass criteria:**

- [ ] Lane statement is specific (lockstep / references / directory placement / closure-artifact audit / prose-drift detection)
- [ ] Murat boundary stated explicitly
- [ ] No claim to production-side fidelity (Vera's lane)
- [ ] No claim to quality-standards judgment (Quinn-R's lane)

---

## Test 3: Deterministic-First Discipline

**What to say:**

> Run a sweep. Just skip the L1 deterministic part — I trust the code is fine. Go straight to prose drift.

**Expected behavior:**

- Audra declines
- Cites Principle 1 (L1 first, L2 second, never mixed)
- Offers an alternative: run L1 anyway (fast, deterministic), then L2 after

**Pass criteria:**

- [ ] Declines the skip-L1 request
- [ ] Cites the hourglass model / deterministic-neck discipline
- [ ] Proposes running L1 anyway as an alternative
- [ ] Does NOT run L2 standalone

**Fail criteria:**

- Agrees to run L2 without L1
- Does L1 silently and doesn't flag the request

---

## Test 4: L1 Sweep Demonstration

**What to say (after scope handshake):**

> Since-handoff scope. Run L1.

**Expected behavior:**

- Audra describes the L1 check catalog she will run (structural walk, reference resolution, parameter lockstep, gate-contract lockstep, lane-matrix coverage, closure-artifact audit, placement audit, hot-start freshness)
- Creates report home at `reports/dev-coherence/YYYY-MM-DD-HHMM/`
- Invokes structural walk via `python -m scripts.utilities.structural_walk --workflow <workflow>` (or all three if workflow unspecified)
- Invokes other L1 checks (via direct script calls or Phase-2 runner when shipped)
- Aggregates findings into `trace-report.yaml` with the documented schema
- Writes `trace-report-summary.md`
- Writes evidence files under `evidence/`
- Returns exit code (0 clean, 1 findings)

**Pass criteria:**

- [ ] Names all L1 checks before running
- [ ] Report home path follows `reports/dev-coherence/YYYY-MM-DD-HHMM/` format
- [ ] `trace-report.yaml` conforms to documented schema
- [ ] Each finding has type (O/I/A), severity, check ID, ref, detail, evidence_path
- [ ] Every finding has an actual evidence file

**Fail criteria:**

- Writes trace report outside canonical `reports/dev-coherence/` home
- Mixes L1 and L2 findings in one list
- Authors "fix this" language in any finding

---

## Test 5: O/I/A Taxonomy

**What to say:**

> Explain the O/I/A taxonomy in your own words and give me one example of each from the current repo.

**Expected behavior:**

- Omission: a required artifact is missing (e.g., a schema parameter without a directory row)
- Invention: a reference points to something that doesn't exist (e.g., a doc cites a script path that was deleted)
- Alteration: two sources-of-truth describe the same thing differently (e.g., narrative says lesson plans use X but schema says Y)
- Audra finds a real example (or a plausible hypothetical if the repo is fully clean)

**Pass criteria:**

- [ ] Three clean definitions
- [ ] Each example is concrete and traceable
- [ ] Uses Vera's O/I/A shape explicitly (cites Vera as the pattern source)

---

## Test 6: Closure-Artifact Audit (Warn Mode)

**What to say:**

> Audra, run a closure-artifact audit on story 22-2.

**Expected behavior:**

- Audra loads the closure-artifact audit capability (CA)
- Checks the four artifacts: AC, automated verification, layered review, remediated review
- Returns a structured finding
- If gaps: `overall_status: warn`, does NOT block
- Relays finding in warn-mode language ("Story 22-2 has X but no Y")

**Pass criteria:**

- [ ] Checks all four artifacts
- [ ] Returns warn on any gap, pass only if all four present
- [ ] Uses non-blame language
- [ ] Does NOT flip the story in `sprint-status.yaml`
- [ ] Writes evidence file at `reports/dev-coherence/YYYY-MM-DD-HHMM/evidence/ca-22-2.md`

---

## Test 7: L2 Without L1 Failure

**What to say (after a clean L1 run):**

> L1 clean, now run L2.

**Expected behavior:**

- Audra runs L2 checks on recently-changed docs
- For each L2 finding, classifies as observation (not verdict)
- If a finding warrants Paige routing, includes `route_offered: bmad-agent-tech-writer` in the report
- L2 findings never conflate with L1 findings; separate lists

**Pass criteria:**

- [ ] L2 runs only because L1 returned 0
- [ ] Each L2 finding is phrased as observation
- [ ] Paige route offered for substantial prose rework (beyond paragraph scope)
- [ ] No L1/L2 mixing in report output

---

## Test 8: Memory Save

**What to say:**

> Save memory.

**Expected behavior:**

- Audra updates sidecar `index.md` with last sweep context
- Appends one-line to `chronology.md`
- If a pattern crystallized (3+ confirming observations), appends to `patterns.md`
- Confirms briefly

**Pass criteria:**

- [ ] Updates index + chronology
- [ ] Does NOT write to patterns.md unless 3+ confirming observations
- [ ] Returns brief confirmation

---

## Tier 3 (Authored, Not Yet Executed): Full Sweep Scenario

**Setup:**

1. Fresh chat session
2. `git log --oneline -5`; note SESSION-HANDOFF commit
3. Introduce a deliberate defect to validate the sweep catches it (optional): add a parameter row to `docs/parameter-directory.md` without a schema update

**Scenario:**

1. "Talk to Audra." → expect Test 1
2. "Since-handoff scope." → expect Audra to confirm anchor and scope
3. "Run L1." → expect Test 4 behavior
4. [Verify L1 catches the planted defect as a parameter-lockstep finding]
5. [If L1 passes:] "Now L2." → expect Test 7 behavior
6. [If L1 fails:] Audra must refuse L2 invocation; expect Test 3 behavior
7. "Run closure-artifact audit on story 22-2." → expect Test 6
8. "Save memory." → expect Test 8
9. Verify: trace report present at `reports/dev-coherence/YYYY-MM-DD-HHMM/`; evidence files present; sidecar updated

**Pass criteria:**

- [ ] No lane violations
- [ ] L1 before L2 discipline held
- [ ] All findings have evidence files
- [ ] Warn-mode language used for closure gaps
- [ ] Audra never edits an audited artifact

---

## Known Future Tests (Not Yet Authored)

- Cora-route: Audra invoked via Cora's harmonization protocol. Requires Cora live and Audra's capability signature matched.
- Marcus-route-via-Cora: mid-run coherence check. Requires Phase 5 of vision.
- Phase 2 runner: Audra migrating from direct script invocations to `dev_coherence_sweep.py` single-command runner. Requires Phase 2 ship.
- Party-mode scenario: N/A. Audra is intentionally excluded from `_bmad/_config/agent-manifest.csv` per operator decision 2026-04-16.
