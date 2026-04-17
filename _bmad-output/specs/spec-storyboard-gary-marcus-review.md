---
title: 'Storyboard review and authorized slide snapshot after Gary Gamma output'
type: feature
created: '2026-03-31'
status: done
baseline_commit: b8e86ac3ea06f2871ba11e696cbaa7729e9489f2
context:
  - docs/workflow/production-session-launcher.md
  - docs/project-context.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** After Gary’s Gamma generation, creative, literal-text, and literal-visual slides/PNGs exist as structured output but there is no single, easy “see everything at once” artifact for the operator to review with Marcus before Irene Pass 2. Without a clear authorization step, downstream steps risk using the wrong ordering or an informal “latest file wins” assumption.

**Approach:** Add a generator that turns an existing Gary dispatch payload (`gary_slide_output` and related paths) into a **view-only** static storyboard (**HTML table** for at-a-glance review + **`storyboard.json`** manifest as the single source of truth for ordering and metadata). Marcus obtains **conversational approval**: he prints a **short summary derived only from the manifest**, the human confirms, then Marcus persists an **immutable authorized snapshot** for the current production run. No approval buttons in HTML for v1.

## Boundaries & Constraints

**Always:** Manifest JSON and HTML must be generated from the **same ordered list** (no hand-edited drift). Summary text Marcus reads to the human must be **computed from that manifest**, not free-form recall. Static bundle is **read-only** in the browser; authorization is **only** via explicit human confirmation in chat after the summary. Preserve existing `validate_outbound_contract` / dispatch shapes in `gamma_operations`—extend via new artifacts, do not weaken required fields.

**Ask First:** Exact filesystem layout for “bundle directory” vs run root if multiple conventions exist in live sessions. Whether authorized snapshot filename is run-global or nested under an existing session folder pattern. When to enforce “authorized snapshot must exist” in `validate-irene-pass2-handoff.py` (feature flag vs always-on).

**Never:** Build interactive approve/reject UI in HTML for v1. Re-sort or rename PNGs on disk to impose order—**order lives in data**. Scope **Irene script-in-notes** layout and ElevenLabs-prep columns into a later story (not this spec). Change Gamma API calls or Gary’s generation logic except where a thin hook is required to pass `run_id`/paths into the generator.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|---------------------------|----------------|
| HAPPY_PATH | Valid Gary dispatch payload JSON/YAML with `gary_slide_output[]` (each with `slide_id`, `fidelity`, resolvable image path or URL field per contract) | `storyboard/storyboard.json` + `storyboard/index.html` with one row per slide, sequence column, fidelity class, thumbnail/link, title/id | Exit 0; log path to index |
| MIXED_FIDELITY_ORDER | Slides include creative + literal-text + literal-visual | Rows appear in **canonical run order** matching manifest array order | N/A |
| MISSING_ASSET | Entry references missing file | HTML shows row with visible **MISSING** state; manifest still lists entry with `asset_status: missing` (or equivalent) | Non-zero optional flag in CLI; document in Marcus runbook |
| APPROVAL_RECORD | Human confirms after Marcus summary | New YAML or JSON **authorized snapshot** written with run id, timestamp, ordered `slide_id[]`, optional hashes if cheap | Refuse write if manifest path missing or summary mismatch |

</frozen-after-approval>

## Code Map

- `skills/gamma-api-mastery/scripts/gamma_operations.py` — `gary_slide_output` schema, `validate_outbound_contract`, `validate_dispatch_ready`; authoritative slide field expectations.
- `skills/bmad-agent-marcus/scripts/validate-gary-dispatch-ready.py` — HIL Gate 2 pre–Irene; natural place to **invoke** or **document** storyboard generation timing.
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py` — future enforcement point for “only authorized slides” (optional task behind Ask First).
- `skills/bmad-agent-marcus/SKILL.md` — add operator protocol: when to generate bundle, summary wording, confirmation phrase, snapshot path.
- `state/config/fidelity-contracts/g4-narration-script.yaml` — Irene references Gary slides; alignment note only (no mandatory edit in v1).

## Tasks & Acceptance

**Execution:**

- [x] `skills/bmad-agent-marcus/scripts/generate-storyboard.py` — CLI: load Gary dispatch payload (JSON/YAML), emit `storyboard/storyboard.json` + `storyboard/index.html` under a user-supplied output directory; table columns: sequence, `slide_id`, `fidelity`, thumbnail/link, optional title; embed or sidecar relative asset paths — rationale: single implementation surface callable by Marcus.
- [x] `skills/bmad-agent-marcus/scripts/write-authorized-storyboard.py` (or merged into above with subcommand) — given manifest path + run metadata, write **authorized snapshot** file only after CLI validates manifest exists and is readable — rationale: separates generation from authorization persistence.
- [x] `skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py` — fixture payload covering mixed fidelity and one missing asset row — rationale: regression guard for ordering and HTML/Manifest parity.
- [x] `skills/bmad-agent-marcus/SKILL.md` — document conversational flow: generate → open `index.html` → Marcus prints manifest-derived summary → human confirms → write snapshot — rationale: operator contract without new UI.

**Acceptance Criteria:**

- Given a valid Gary dispatch payload file, when the operator runs the generator, then `storyboard.json` and `index.html` exist and the **number and order** of slides match `gary_slide_output` exactly.
- Given the generated manifest, when Marcus (or CLI helper) produces the pre-approval summary, then it includes **total count**, **first and last `slide_id`**, and **counts per `fidelity` value** present.
- Given explicit human approval in session, when the authorization step runs, then a new snapshot file records **run identifier**, **UTC timestamp**, and the **ordered list of `slide_id`**, and no prior snapshot is overwritten silently (append version suffix or fail — choose one and document).
- Given existing Gamma validation tests, when the change set is applied, then `pytest` for touched test modules passes with no changes to required outbound field definitions unless explicitly approved.

## Spec Change Log

- **2026-03-31 (review):** Consolidated adversarial pass in-session; one **patch** finding (Ruff E501 in HTML template) fixed. No intent_gap or bad_spec; no loopback to step 2.

## Design Notes

Use relative paths in HTML so opening `index.html` from disk resolves images when the bundle folder is moved with its assets. If PNGs live outside `storyboard/`, manifest stores path strings as emitted by Gary payload; HTML uses those paths for `src`/`href`.

## Verification

**Commands:**

- `python -m pytest skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py -q` -- expected: all pass
- `ruff check skills/bmad-agent-marcus/scripts/generate-storyboard.py` (and test file) -- expected: no new violations

**Manual checks:**

- Run generator on a real or redacted dispatch file; open `storyboard/index.html` in a browser; confirm one-screen scannability (table, all rows visible without extra navigation).

## Suggested Review Order

**Manifest and ordering**

- Canonical slide list, asset presence, and relative hrefs for static HTML.
  [`generate-storyboard.py:53`](../../skills/bmad-agent-marcus/scripts/generate-storyboard.py#L53)

- Operator-facing recap lines for conversational approval (count, endpoints, fidelity histogram).
  [`generate-storyboard.py:119`](../../skills/bmad-agent-marcus/scripts/generate-storyboard.py#L119)

**View-only HTML**

- Table layout, MISSING marker, remote URL handling without forms.
  [`generate-storyboard.py:148`](../../skills/bmad-agent-marcus/scripts/generate-storyboard.py#L148)

**CLI surface**

- `generate` / `summarize` subcommands, `--strict` exit code on missing assets.
  [`generate-storyboard.py:274`](../../skills/bmad-agent-marcus/scripts/generate-storyboard.py#L274)

**Authorization snapshot**

- Fail closed on overwrite; ordered `slide_ids` from manifest only.
  [`write-authorized-storyboard.py:43`](../../skills/bmad-agent-marcus/scripts/write-authorized-storyboard.py#L43)

**Regression tests**

- Mixed fidelity fixture, strict CLI, authorize idempotency refusal, summarize subcommand.
  [`test_generate_storyboard.py:52`](../../skills/bmad-agent-marcus/scripts/tests/test_generate_storyboard.py#L52)

**Operator contract**

- Marcus runbook: commands, order of operations, no in-page approval for v1.
  [`SKILL.md:109`](../../skills/bmad-agent-marcus/SKILL.md#L109)
