# Texas Wrangler Intake-Surface Gaps — Backlog Story Stub

**Opened:** 2026-04-17 (surfaced during APC C1-M1 Tejal trial preflight + dispatch)
**Status:** backlog
**Predecessor:** Epic 25 Story 25-1 (Texas runtime wrangling runner)
**Severity:** **High** (raised from Medium: DOCX is contract-vs-code drift, not just an architectural gap)

## Two Problems Surfaced (one preflight, one post-dispatch)

### Problem 1: Visual-source gap (preflight)

See original section below — images have no supported path, fall through to `read_text_file()` and fail with binary decode error.

### Problem 2: DOCX contract-vs-code drift (post-dispatch, trial run 2026-04-17)

**Texas's `transform-registry.md:19` advertises** `python-docx` as the default DOCX extractor with one documented known-loss (formatting / table flattening). **Texas's `run_wrangler.py:228-244` does not implement it.** The `local_file` provider handler has PDF-specific extraction branches but everything else — including `.docx` — falls through to `read_text_file()`, which performs a plain-text read against the DOCX ZIP-of-XML container and produces binary garbage.

**Evidence from trial run:**
- DOCX extraction reported 2,044 "words" and 1,522 "lines" but structural_fidelity: low, 0 headings.
- Cross-validation reported 2% key-term overlap — the "missing key terms" list contains literal unicode replacement characters and ZIP-compressed byte sequences (e.g., `]\u0307\uFFFD\\...`, `jvbtj\x1A?...`, `ezw`, `vni`, `bjh`), not actual vocabulary.
- The DOCX content is almost certainly fine; Texas just can't read it.

**Why this is higher severity than Problem 1:**
- Problem 1 (images) is a gap: registry and code both silent on images. Operator knows they're unsupported.
- Problem 2 (DOCX) is drift: registry actively lies about capability. Operator discovers the gap only after trusting it and getting a mysterious cross-val failure.
- Drift between documentation and code erodes trust in both. It also hides in the happy path (PDF works, so nobody notices DOCX was never wired in).

## Problem

Texas's current contract (`skills/bmad-agent-texas/scripts/run_wrangler.py`, provider enum at line 148) supports text-extraction providers only: `local_file`, `pdf`, `url`, `notion`, `playwright_html`. Transform-registry (`skills/bmad-agent-texas/references/transform-registry.md`) matches: PDF / DOCX / Markdown / Notion / HTML/URL. **Image formats (JPG, PNG) have no supported path.**

Consequences:
- A `.jpg`/`.png` dropped into a Texas directive with `provider: local_file` falls through to `read_text_file()` → binary decode error → FAILED manifest entry (confirmed at `run_wrangler.py:228-244`).
- The architecturally-clean escape hatch is `OPTIONAL_CONTEXT_ASSETS` in `run-constants.yaml` → Marcus's downstream context envelope → CD / Irene / Gary / sensory-bridges. This works for **context** but not for **source-of-truth visuals** (e.g., a roadmap image that IS the primary source for a learning-objective chain).

## Historical Context

Pre-Texas-runtime (pre-Story 25-1, landed 2026-04-17), the source-prompting step was ad-hoc LLM-driven inside Marcus. Images flowed as "asset reference" entries through the context envelope with no runner enforcing text-only. Operator confirms: "I used to provide the APC Course Map image during interview as a secondary source without issue, and it found its way downstream." Texas formalized extraction as a contract-gated runtime step and in doing so accidentally narrowed the input surface.

## Current Gap

No Texas-contract role exists for "this is a first-class visual source that should be registered, perceived (sensory-bridges), and contribute evidence to fidelity." Today:

- Extraction report does not acknowledge visual sources
- G0 fidelity checks cannot validate visual sources
- Perception cache does not cross-link to Texas's manifest
- Fidelity lineage chain (source → lesson plan → slides → narration) breaks at the visual-source boundary

## Options

### Option A: Extend Texas with an image provider

Add `provider: image` routed through `skills/sensory-bridges/scripts/pdf_to_agent.py` (or a new `image_to_agent.py`). Extraction report includes structured image-perception output alongside text.

**Requires:**
- New roles in contract (e.g., `visual-primary`, `visual-supplementary`)
- Perception cache integration at the wrangler layer
- New G0 fidelity criteria for visual sources (`visual_structural_fidelity`, `visual_completeness`)
- Transform-registry update with Image row + fallback strategy
- New golden fixtures for visual-wrangler tests

**Pros:** Single runner owns all source registration; fidelity chain unbroken.
**Cons:** Expands Texas's surface area meaningfully; touches perception + fidelity + contract schema.

### Option B: Sibling visual-wrangler runner

Leave Texas text-only; add `skills/bmad-agent-texas/scripts/run_visual_wrangler.py` with the same manifest/report schema, invoked by Marcus for visual sources.

**Requires:**
- New script + test suite
- Marcus delegation update for multi-runner orchestration
- Shared manifest format between text + visual runners
- G0 fidelity update for visual-sources block

**Pros:** Clean lane boundary; text vs visual stay separate.
**Cons:** More moving parts; Marcus orchestrates both instead of one.

### Option C: Explicit contract rejection + documented escape hatch

Do nothing to Texas's code. Update Texas's directive schema to **reject** image providers at directive-load time (exit with clear error: "images must route via OPTIONAL_CONTEXT_ASSETS in run-constants.yaml"). Document the context-envelope path as the canonical mechanism.

**Pros:** Minimal code change; honors current architectural separation.
**Cons:** Doesn't close the fidelity-lineage gap. Visual sources still invisible to Texas's manifest.

## Recommendation (for story discussion, not this backlog stub)

Probably a hybrid: **Option C now** (reject images with clean error, document escape hatch) + **Option A or B as Epic 25+ follow-on** (full visual-source first-class support). Party-mode consensus needed on A vs B + on fidelity-chain requirements.

## Operator Scope Direction (2026-04-17)

Juanl clarified Texas's identity and scope for this work:

> "Texas as a 'wrangler' must be savvy at finding and handling anything and everything that might be out there or be presented. But that doesn't mean there can't be very deliberate routing of one source type or another for efficient processing by Texas."

Translation for the story shape:

- **Texas owns the intake surface** — any source type, any format, any provider. The wrangler name is load-bearing. Operator should never get a "sorry, we don't do images" rejection from Texas; that would violate the persona and the lane.
- **Deliberate routing is allowed and encouraged.** Texas can internally dispatch to specialist extractors (sensory-bridges for images, pypdf for PDFs, python-docx for DOCX, notion_client for Notion, etc.) — the key is that Texas is the *single dispatcher*, not the *single extractor*. Option A (extend the runner) and Option B (sibling runner that Texas invokes) are both compatible with this — the difference is whether "extend" means "add an image extractor alongside existing ones" or "add a sibling runner that Texas orchestrates."
- **Option C is now off the table.** Rejecting images with "clean error path" would not align with the wrangler identity. Texas must accept and route.

## Revised Option Space (post operator guidance)

- **Option A (preferred shape):** Texas runner gains an image extractor path (via sensory-bridges) AND wires the `python-docx` extractor the registry already promises. Provider enum extends. Single manifest, single report, single dispatcher.
- **Option B (alternate shape):** Texas runner orchestrates a sibling `run_visual_wrangler.py` (and possibly a sibling `run_rich_text_wrangler.py` for DOCX / future PPTX-text). Still presents as one Texas dispatcher to the operator; internally routes by source type. Shared manifest schema.
- **Option C:** withdrawn.

Party-mode consensus for A vs B pre-implementation: Winston (runner architecture), Amelia (implementation cost), Murat (test boundary). **Include Paige on the agenda** — the transform-registry drift is a documentation-vs-code SSOT issue her lane covers.

## Scope Expansion (Problem 2 additions)

If Option A chosen:
- Wire `python-docx` into the `.docx` branch of `local_file` handler (the registry already promises this; implementation gap).
- Add DOCX-specific known-losses to extraction report evidence (table flattening, style loss — per registry).
- Transform registry becomes the contract: any format it advertises must have a working extractor OR be explicitly marked "planned / not yet shipped."
- Add a `format-capability-lockstep` check to Audra's L1 sweep — registry claims vs code reality. Would have caught this drift.

If Option B chosen:
- DOCX (and possibly PPTX-text) handled by the rich-text-wrangler sibling.
- Image handled by the visual-wrangler sibling.
- PDF + Markdown + URL + Notion remain in the core text-wrangler.
- Texas dispatcher routes by format; each wrangler has its own contract + extractor set.

## Not In Scope (Related but Separate)

- Sensory-bridges coverage expansion (already tracked separately)
- CD / Gary visual-reference intake (already supported via run-constants)
- OCR vs image-perception semantic debate (image-perception is the APP's established path via sensory-bridges; OCR adds no value beyond that)

## Acceptance Hint (Draft for Story Open)

- Texas either accepts visual sources (Option A/B) OR rejects with clear error path (Option C)
- Extraction report surface includes or explicitly excludes visual sources per chosen option
- G0 fidelity chain decision is documented: visual sources either IN scope (new criteria) or OUT of scope (documented carve-out)
- No surprise FAILED manifest entries for operator-declared visual sources
