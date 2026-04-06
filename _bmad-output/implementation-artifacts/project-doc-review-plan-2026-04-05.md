# Project Documentation Review Plan

Date: 2026-04-05

Purpose:
- record the consensus rules used for the Epic 12/13/14 documentation reconciliation
- define how future repo-wide doc reviews should distinguish active source-of-truth docs from historical evidence artifacts

## Consensus Decisions

1. Prompt packs are now a workflow family, not a single generic document.
   - Standard narrated workflow: `docs/workflow/production-prompt-pack-v4.1-narrated-deck-video-export.md`
   - Motion-enabled narrated workflow: `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`

2. `DOUBLE_DISPATCH` is a bounded branch inside either narrated workflow.
   - It does not justify a third prompt-pack family.
   - Winner authorization must collapse the deck before downstream motion or narration work.

3. Motion is materially different enough to warrant its own prompt-pack doc.
   - Gate 2M
   - motion generation/import
   - Motion Gate
   - motion-aware Irene Pass 2

4. Active source-of-truth docs must stay aligned with runtime behavior.
   - workflow docs
   - operator/startup/wrapup protocols
   - user/admin/dev guides
   - anti-drift docs
   - lane/fidelity matrices
   - architecture addenda
   - style guidance where workflow behavior affects content standards

5. Historical simulation artifacts are not auto-remediation targets unless still referenced as current guidance.
   - historical run logs and past fidelity walk reports remain chronology
   - current generated examples may be refreshed when they are used as active references

## Review Order

1. Workflow controls and anti-drift
   - session launcher/start/wrapup
   - prompt packs
   - operator card
   - HIL, checklists, contracts

2. User-facing guides
   - user guide
   - admin guide
   - developer guide

3. Governance and architecture
   - fidelity gate map
   - lane matrix
   - architecture addendum
   - project context

4. Standards and supporting references
   - style bible
   - token-efficiency review
   - other active operational references

## Drift Rules

- If runtime behavior changes, update the active prompt pack first.
- Then update the operator card and session protocols.
- Then update user/admin/dev guides.
- Then update anti-drift resources and architecture summaries.
- Only after that refresh generated example artifacts if they are still being cited.

## Validation Loop

- search for retired prompt-pack names and stale workflow claims
- rerun `python -m pytest tests/test_fidelity_walk.py -q`
- rerun `python -m scripts.utilities.fidelity_walk`
- inspect generated report for active anti-drift evidence paths

## Current Review Result

This review cycle updated the active documentation surface for:
- prompt-pack naming
- workflow-template selection
- double-dispatch winner authorization
- motion Gate 2M / Motion Gate ordering
- motion-aware operator, checklist, and contract language
- governance and architecture summaries

Remaining historical artifacts are treated as chronology unless elevated back into active guidance.
