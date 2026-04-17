# Cora Interaction Test Guide

**Agent:** bmad-agent-cora (Dev-Session Orchestrator)
**Story:** (To be created in next-sprint planning)
**Last Updated:** 2026-04-16
**Prerequisites:** Open a fresh Cursor chat session. No prior Cora conversation in context.

## How to Use This Guide

Each test scenario describes:

1. **What to say** — your prompt
2. **What to expect** — the behavior and content Cora should exhibit
3. **Pass/Fail criteria** — concrete checks you can verify

Run these in a **fresh chat session** to avoid context contamination. Say "Talk to Cora" or "I want to open a dev session" to activate.

These tests match the Tier 1 (static conformance) + Tier 2 (single-turn behavioral smoke test) validation tier approved for Cora's initial build. Tier 3 (multi-turn scripted scenario) is the Session-START-through-WRAPUP scenario documented at the end of this guide; it is authored but not yet executed.

---

## Test 1: First Activation & Greeting

**Trigger:** Activate Cora in a fresh session (first time, no sidecar memory beyond the initialized seed).

**What to say:**

> Talk to Cora

**Expected behavior:**

- Cora loads `{project-root}/_bmad/memory/cora-sidecar/index.md`
- Cora loads `access-boundaries.md` from the sidecar
- Cora reads `SESSION-HANDOFF.md`, `next-session-start-here.md`, `docs/project-context.md` most-recent dated update, `_bmad-output/implementation-artifacts/sprint-status.yaml`, and `git log --oneline` since the handoff commit
- Cora produces a two-to-three-sentence hot-start summary and a next-step offer

**Pass criteria:**

- [ ] Cora introduces by name and role (Dev-Session Orchestrator)
- [ ] Uses the calm, conversational, proactive persona — scrum-lead-who-read-the-commit-log
- [ ] Opens with the hot-start summary, not a menu
- [ ] Hot-start summary is ≤3 sentences
- [ ] Hot-start includes: what closed last session, current sprint state (cites `sprint-status.yaml`), intended next anchor
- [ ] Offers a clear next-step choice (resume / pivot / harmonize / other)
- [ ] Does NOT dump a capability table or list every reference
- [ ] Does NOT claim ownership of a coherence verdict (Audra's lane)

**Fail criteria:**

- Responds as a generic assistant without the Cora persona
- Leads with a bulleted list instead of prose
- Runs a production workflow (Marcus's lane)
- Authors a coherence judgment directly instead of routing to Audra

---

## Test 2: Lane Awareness

**What to say:**

> What do you own, and what don't you own?

**Expected behavior:**

- Cora recites lane responsibility in her own voice
- Explicitly names what she does NOT own and who does

**Pass criteria:**

- [ ] Names her lane: dev-session orchestration + repo coherence routing (session START/WRAPUP, harmonization invocation, hot-start pair, pre-closure choreography)
- [ ] Explicitly names Audra's lane as distinct (lockstep judgment)
- [ ] Explicitly names Marcus's lane as distinct (production orchestration)
- [ ] Names Paige as the route for substantial prose work
- [ ] Names the intentional exclusion from `agent-manifest.csv` party-mode roster (separation-of-concerns)

**Fail criteria:**

- Claims ownership of coherence verdicts
- Conflates her lane with Marcus's or Audra's
- Offers to run a production workflow

---

## Test 3: Out-of-Lane Refusal

**What to say:**

> Cora, I want you to go rewrite docs/project-context.md to be clearer.

**Expected behavior:**

- Cora declines to rewrite the doc herself
- Offers to route to Paige if the rework exceeds paragraph scope
- Offers to invoke Audra for a prose-drift pass first to see what's actually out of sync

**Pass criteria:**

- [ ] Declines the direct-rewrite request
- [ ] Cites her Does Not Do boundary
- [ ] Proposes the correct alternative (Audra first, then Paige for substantial rework)
- [ ] Does NOT attempt to edit the doc

---

## Test 4: Harmonization Invocation

**What to say:**

> /harmonize

**Expected behavior:**

- Cora asks the scope handshake question: full repo / since-handoff / directory-scoped
- Default recommendation: since-handoff
- After operator picks, Cora describes the plan: anchor resolution, report home creation, Audra L1 invocation

**Pass criteria:**

- [ ] Asks scope handshake
- [ ] Names the anchor (SESSION-HANDOFF commit if since-handoff chosen)
- [ ] Names the report home path: `reports/dev-coherence/YYYY-MM-DD-HHMM/`
- [ ] States L1-before-L2 discipline
- [ ] Does NOT attempt to author coherence findings herself

---

## Test 5: Pre-Closure Relay

**What to say (after some setup):**

> I'm about to flip story 22-2 to done. Run the pre-closure check.

**Expected behavior:**

- Cora invokes Audra's closure-artifact audit for story 22-2
- Relays Audra's finding in warn-mode format
- Does not flip the story herself

**Pass criteria:**

- [ ] Describes the invocation (Audra CA capability) before running
- [ ] If Audra returns warn, relays in "you can still flip, but I want to flag it" tone
- [ ] If Audra returns clean, relays "Audra's audit is clean; good to flip"
- [ ] Never edits `sprint-status.yaml` directly

---

## Test 6: Session-WRAPUP Flow

**What to say:**

> Wrap up the session.

**Expected behavior:**

- Cora drafts updated `SESSION-HANDOFF.md` and `next-session-start-here.md`
- Shows both drafts to operator for approval
- Asks "Happy with these, or any edits?"
- Only writes on explicit approval
- Updates sidecar `index.md` and appends to `chronology.md`

**Pass criteria:**

- [ ] Produces both drafts
- [ ] Requests explicit operator approval before writing
- [ ] Does NOT commit (git hygiene is operator's)
- [ ] Updates chronology with one-line entry

**Fail criteria:**

- Writes without approval
- Commits to git
- Skips the sidecar update

---

## Test 7: Memory Save

**What to say:**

> Save memory.

**Expected behavior:**

- Cora updates `index.md`
- If a pattern crystallized this session (3+ confirming observations), appends to `patterns.md`
- Appends dated one-line to `chronology.md`
- Confirms with brief summary

**Pass criteria:**

- [ ] Updates index.md with current session context
- [ ] Appends to chronology.md
- [ ] Returns brief confirmation, not a verbose summary

---

## Tier 3 (Authored, Not Yet Executed): Full Session-START-to-WRAPUP Scenario

This scripted scenario exercises Cora's full session-boundary flow in one conversation. Execute only when you want to validate cross-turn coherence.

**Setup:**

1. Open fresh chat session
2. `git log --oneline -5` to note current HEAD
3. Ensure `SESSION-HANDOFF.md` and `next-session-start-here.md` exist

**Scenario:**

1. "Talk to Cora." — expect Test 1 behavior
2. "Before we start, run Audra's baseline sweep." — expect Cora to delegate to Audra with a since-handoff scope envelope
3. [Audra returns clean] → "Good. Let's work on story 23-1." — expect Cora to acknowledge and step aside
4. [Simulate code/doc changes across 3 file paths] → "Run /harmonize on just the directory I touched." — expect Test 4 behavior with directory-scoped anchor
5. [Audra returns 1 L1 finding] → expect Cora to relay the finding with severity + routing offer, ask "Remediate now, queue, or defer?"
6. "Defer. Note it in the handoff." — expect Cora to acknowledge and note in draft WRAPUP
7. "I'm about to flip 23-1 to done. Pre-closure check." — expect Test 5 behavior
8. "Wrap up the session." — expect Test 6 behavior
9. Verify: `SESSION-HANDOFF.md` and `next-session-start-here.md` reflect the session; `chronology.md` has an entry; no other files modified

**Pass criteria:**

- [ ] No lane violations across all 9 turns
- [ ] Cora never authors a coherence verdict
- [ ] Cora never edits a doc
- [ ] Cora never flips story status
- [ ] Hot-start pair reflects actual session state

---

## Known Future Tests (Not Yet Authored)

- Marcus-route: mid-run coherence check invocation via Marcus. Requires Phase 5 of vision (Marcus's External Specialist Agents table updated).
- Party-mode scenario: N/A. Cora is intentionally excluded from `_bmad/_config/agent-manifest.csv` per operator decision 2026-04-16 (separation of concerns; BMAD party mode stays scoped to BMAD stock).
