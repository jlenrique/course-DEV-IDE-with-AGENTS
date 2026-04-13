---
title: Operator Script v4.2 - Irene A/B Tuning Loop
status: active
updated: 2026-04-12
---

# Operator Script v4.2 - Irene A/B Tuning Loop

Purpose: run controlled A/B Irene Pass 1 comparisons through Marcus, capture deterministic evidence, and feed findings into the next tuning iteration before Gary dispatch.

Scope:
- Uses prompt-pack naming conventions from `production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`.
- Inserts a repeatable A/B loop after Prompt 5/5B and before Prompt 6.
- A/B here means two Irene candidate runs (not Prompt 7B Gary variant A/B).

Interpreter rule:
- Use `.\.venv\Scripts\python.exe` for repo commands.

---

## Run Constants for Looping

Set once at loop start (in operator notes and/or `run-constants.yaml`):
- `RUN_ID`
- `BUNDLE_PATH`
- `LESSON_ID` (for evaluator, example `C1-M1`)
- `LOOP_ID` (example `L01`, then `L02`, `L03`)
- `PROFILE_A_ID` (example `baseline-ad-hoc` or `template-v1`)
- `PROFILE_B_ID` (example `template-v2`)
- `DELTA_HYPOTHESIS` (one sentence; what B should improve over A)
- `MAX_LOOPS` (recommended 3 before escalation)

Artifact naming convention for each loop:
- `ab-comparison/loop-[LOOP_ID]/A/`
- `ab-comparison/loop-[LOOP_ID]/B/`
- `ab-comparison/loop-[LOOP_ID]/comparative-eval.json`
- `ab-comparison/loop-[LOOP_ID]/feedback.md`

---

## Prompt 5C.0 - Loop Initialization + Lock

Operator to Marcus (copy/paste):

`Marcus, start Prompt 5C.0 for RUN_ID [RUN_ID], LOOP_ID [LOOP_ID]. Lock canonical inputs from [BUNDLE_PATH]: irene-packet.md, source bundle artifacts, operator-directives.md, and run-constants.yaml. Confirm both A and B will use identical locked inputs except approved tuning deltas for template selection and content-signal weighting. Write a loop-lock receipt to [BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/loop-lock-receipt.json including PROFILE_A_ID, PROFILE_B_ID, DELTA_HYPOTHESIS, MAX_LOOPS, and pass2_mode (set to "structural-coherence-check" until Epic 23 story 23-1 is implemented). Stop and wait for GO.`

Required write:
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/loop-lock-receipt.json`

Gate rule:
- Do not run A or B until lock receipt exists and operator says GO.

---

## Prompt 5C.1 - Candidate A Run (Pass 1)

Operator to Marcus (copy/paste):

`Marcus, run Prompt 5C.1 candidate A for LOOP_ID [LOOP_ID] using PROFILE_A_ID [PROFILE_A_ID]. Execute Irene Pass 1 from the locked bundle state, including cluster planning and template selection outputs. Run G1, G2, Quinn-R G2, and G1.5 (when clustering is enabled). Persist A artifacts under [BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/A including irene-pass1.md, cluster-plan-review.md, and a compact gate receipt.`

Required writes:
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/A/irene-pass1.md`
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/A/cluster-plan-review.md`
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/A/cluster-template-plan.json`
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/A/gate-receipt.json`

Gate rule:
- If G1/G2/Quinn-R/G1.5 has blocking failures, A is non-selectable until remediated.

---

## Prompt 5C.2 - Candidate B Run (Pass 1)

Operator to Marcus (copy/paste):

`Marcus, run Prompt 5C.2 candidate B for LOOP_ID [LOOP_ID] using PROFILE_B_ID [PROFILE_B_ID]. Use the same locked inputs as A, apply only approved B deltas, then run G1, G2, Quinn-R G2, and G1.5 (when clustering is enabled). Persist B artifacts under [BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/B with the same file set and a compact gate receipt.`

Required writes:
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/B/irene-pass1.md`
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/B/cluster-plan-review.md`
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/B/cluster-template-plan.json`
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/B/gate-receipt.json`

Gate rule:
- B must satisfy the same strict standards as A (no relaxed gates).

---

## Prompt 5C.3 - Comparative Evaluation (Pass 1 Focus)

Operator to Marcus (copy/paste):

`Marcus, compare A vs B for loop [LOOP_ID] and write a deterministic comparison report to [BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/comparative-eval.json with: selected_template_id by cluster, interstitial count by cluster, top template rationale signals, consecutive-template repetition risk, pacing-profile streak risk, gate outcomes (G1/G2/Quinn-R/G1.5), and regressions. Then write a decision memo at [BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/decision-memo.md recommending A, B, or no-go and wait for my approval.`

Required writes:
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/comparative-eval.json`
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/decision-memo.md`

Gate rule:
- No winner is promoted unless evaluator output exists and operator approves the decision memo.

---

## Prompt 5C.4 - HIL Judgment Pass (Pass 1 Quality + Intent)

> **HIL Reviewer Guidance (while pass2_mode = structural-coherence-check):**
> Your decision must be based on **Pass 1 evidence only**: template choices, cluster plan
> structure, narrative arc coherence, pacing rhythm, and gate receipts. If you have also
> run the optional Pass 2 confirmation, that output is **indicative, not evaluative** —
> do not let Pass 2 narration quality drive your PROMOTE/ITERATE decision. Pass 2 is
> currently cluster-blind for narration and will change substantially when Epic 23 ships.

Operator to Marcus (copy/paste):

`Marcus, present a side-by-side HIL review packet for loop [LOOP_ID] comparing A vs B on: pedagogical fit of template choices, selected_template_id continuity, variety and pacing rhythm, cluster narrative arc coherence, and operational clarity for downstream Prompt 6 dispatch. Write [BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/hil-review.md and wait for my final winner decision.`

Required write:
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/hil-review.md`

Gate rule:
- Operator final decision required (`A`, `B`, or `NO-GO`).
- Decision must cite Pass 1 structural evidence, not Pass 2 narration quality.

---

## Prompt 5C.5 - Feedback Capture + Next-Loop Directives

Operator to Marcus (copy/paste):

`Marcus, using comparative-eval.json, decision-memo.md, and hil-review.md for loop [LOOP_ID], produce feedback directives for Irene tuning. Include: (1) keep list, (2) fix list, (3) exact parameter or policy changes, (4) expected measurable impact for next loop, and (5) stop condition. Write [BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/feedback.md and also write the proposed next-loop directives file [BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/next-loop-directives.md.`

Required writes:
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/feedback.md`
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/next-loop-directives.md`

Gate rule:
- Next loop cannot start until directives are specific and testable (no vague wording).

---

## Prompt 5C.6 - Loop Progression Decision

Operator decision:
- If success criteria are met: promote winner and continue to Prompt 6.
- If partially met and under `MAX_LOOPS`: increment `LOOP_ID`, set new `DELTA_HYPOTHESIS`, return to Prompt 5C.0.
- If repeated no-go or max loops reached: pause and escalate for policy/weight redesign.

Operator to Marcus (copy/paste):

`Marcus, record loop closure for [LOOP_ID] with status [PROMOTE|ITERATE|ESCALATE], rationale, next action, and pass2_mode (from loop-lock receipt). Write [BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/loop-closure-receipt.json.`

Required write:
- `[BUNDLE_PATH]/ab-comparison/loop-[LOOP_ID]/loop-closure-receipt.json`

---

## Success Criteria by Major Step

- Initialization success:
  - lock receipt complete, delta hypothesis explicit, GO recorded.
- A/B execution success:
  - both candidates have full Pass 1 artifacts plus G1/G2/Quinn-R/G1.5 receipts.
- Comparison success:
  - deterministic evaluation JSON exists and Marcus decision memo is approved.
- Feedback success:
  - next-loop directives are concrete, bounded, and measurable.
- Loop success:
  - either promoted winner or controlled iterate decision with clear stop rule.

---

## Orientation Cues for the Operator

Use this quick self-check each loop:
1. Am I comparing only one meaningful change between A and B?
2. Did both sides run under identical locked inputs?
3. Do I have machine evidence (`comparative-eval.json`) and HIL evidence (`hil-review.md`)?
4. Are next-loop directives specific enough that someone else could run them without guessing?
5. Is this loop ending with a real decision (promote, iterate, or escalate)?

---

## Optional Pass 2 Structural-Coherence-Check (After Winner Promotion)

> **SCOPE LIMITATION (remove when Epic 23 story 23-1 ships):**
> Pass 2 operates in `structural-coherence-check` mode. Epic 23 cluster-aware narration
> (stories 23-1, 23-2, 23-3) is NOT yet implemented. Pass 2 is cluster-blind for narration
> generation. This means:
>
> - Pass 2 output is **indicative of structural integrity, not narration quality**.
> - **Do NOT let Pass 2 narration quality influence PROMOTE/ITERATE decisions** in the A/B loop.
>   The A/B winner must be selected on Pass 1 evidence only (template choices, cluster plans,
>   gate receipts, structural coherence).
> - Pass 2 quality metrics in the evaluator scoring must be **zeroed or excluded** until 23-1 is live.
> - All trial receipts (loop-lock, gate, closure) must include the field:
>   `pass2_mode: structural-coherence-check`
>   so these bounded-scope trials are distinguishable from future full-signal trials.

Run this only after winner promotion from Prompt 5C.6:
- Continue normal flow through Prompts 6-8 using the promoted Pass 1 output.
- Pass 2 confirmation checks structural coherence only: does the handoff succeed? Does the manifest parse? Are cluster fields populated?
- Do NOT evaluate narration word ranges, bridge cadence, or behavioral intent alignment — those checks require Epic 23.
- For structural checks, you may use `skills/bmad-agent-marcus/scripts/evaluate_cluster_template_selection.py` against prior baseline and current candidate bundles.
