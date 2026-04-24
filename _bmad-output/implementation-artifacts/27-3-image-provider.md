# Story 27-3: Image Provider (Sensory-Bridges Integration)

**Epic:** 27 — Texas Intake Surface Expansion
**Status:** ready-for-dev  (Sprint 2 GREEN-LIT 2026-04-24; riders locked below)
**Sprint key:** `27-3-image-provider`
**Added:** 2026-04-17
**Expanded:** 2026-04-24
**Points:** 3
**Gate mode:** dual-gate
**K floor / target:** K≥14, target 15-18 (Amelia rider)
**Depends on:** 27-2 (atomic-write hygiene + transform-registry lockstep pattern); 27-6 (provider-template pattern established).
**Blocks:** nothing.
**DEV POSITION:** 3 (after 27-6 Box + 27-5 Notion MCP).

## Story

As the Texas wrangler,
I want to accept image source files (`.jpg`, `.jpeg`, `.png`, `.webp`) via a `provider: image` directive and route them through a sensory-bridges helper for perception-based extraction,
So that first-class visual sources (a roadmap image that IS the primary source for a learning-objective chain) flow through Texas's manifest + fidelity chain instead of being rejected with a binary-decode error.

## Background

Original defect from the 2026-04-17 Tejal trial preflight: a `.jpg`/`.png` dropped into a Texas directive with `provider: local_file` falls through to `read_text_file()` → binary decode error → FAILED manifest entry. The operator's workaround is `OPTIONAL_CONTEXT_ASSETS` in `run-constants.yaml`, which routes images via Marcus's context envelope — but that path is for **context**, not **source-of-truth visuals**.

Per operator direction (2026-04-17 backlog stub): Texas owns the intake surface; images must not be rejected; internal routing to a sensory-bridges helper is the architecture (Option A).

## Ratified rulings (Sprint 2 green-light 2026-04-24)

- **Architecture (Winston):** new sibling helper `skills/sensory-bridges/scripts/image_to_agent.py` — do **not** extend `pdf_to_agent.py`. The existing `png_to_agent.py` is a downstream slide-perception bridge used by other workflows; `image_to_agent.py` is a Texas-INTAKE helper producing `(title, body, SourceRecord)` in the wrangle_* contract.
- **Provenance (Winston):** provenance-preserving record carries source metadata (sha256, width×height, file size, mime type, bridge_version); `SourceRecord.kind="image_source"`, `ref="image://<sha256-prefix>"`.
- **Typed rejection (Winston):** typed `ImageError` taxonomy (`ImageError` base / `ImageFetchError` / `ImageDecodeError` / `ImageOCRFailureError` / `ImageVisionAPIError`). No silent empty returns. Unsupported suffixes raise `ImageFetchError` with remediation.
- **Dependency injection (Amelia):** `ImageAnalyzer` Protocol so unit tests inject a `FakeImageAnalyzer`. Production `VisionLLMAnalyzer` is a stub-with-remediation in v1 (live vision calls become a follow-on gated on key availability); the DI seam means image intake works end-to-end with caller-supplied pre-computed perception, and the provider itself does not require a vision API key to load.
- **G0 criteria (Amelia):** reuse existing `ExtractionReport.structural_fidelity` and `completeness_ratio` fields with image-specific assessment logic — **no schema bifurcation** (AC-4). Define explicit thresholds: `structural_fidelity` maps `high / medium / low / none` for images via (a) heading-count proxy from detected-text blocks, (b) visual-element count, (c) OCR confidence; `completeness_ratio` maps to `min(1.0, perceived_content_words / expected_image_floor)` with `_WORDS_PER_PAGE["image"] = 60` as the pdf-like floor. `source_type="image"` dispatch added to `_WORDS_PER_PAGE`.
- **Shape-pin tests (Amelia):** byte-stable assertions on `SourceRecord.kind`, `ref` prefix, `note` substrings, and `ExtractionReport.known_losses` ordering for each failure mode.
- **Negative fixtures (Murat):** one explicit negative fixture per failure mode (binary-decode, unsupported-suffix, OCR-empty, vision-API-missing, corrupt-header).
- **SCHEMA_CHANGELOG entry (Paige):** new patch entry documenting (a) `_WORDS_PER_PAGE` image key, (b) `image_source` `SourceRecord.kind`, (c) image-row in transform-registry with explicit `Known Limitations` semantics (the "known_losses column" clarification).
- **Rejection mode pinned (John):** image failures classify to `QualityTier.FAILED` ExtractionReport with structured `known_losses` — the runner continues and produces a report. No hard exit; consistent with DOCX-malformed pattern from 27-1. A hard reject would spam false-positives during trial-run iteration.
- **Contract roles (from stub AC-6):** `visual-primary` and `visual-supplementary` roles accepted by directive-schema validator (expanded `role` enum).
- **LangGraph portability guard:** AST-level assertion that `image_to_agent.py` and the `image` branch in `run_wrangler.py` do not import `marcus.orchestrator.*` or `marcus.dispatch.*`.

## Acceptance Criteria

- **AC-1:** `provider: image` registered in `_SUPPORTED_PROVIDERS` (run_wrangler.py) and dispatched in `_fetch_source`. `image` added to `_PROVIDER_SOURCE_TYPE` with value `"image"` and to `_EXTRACTOR_LABELS` with value `"sensory_bridges_image"`.
- **AC-2:** `skills/sensory-bridges/scripts/image_to_agent.py` exposes `wrangle_local_image(path, *, analyzer=None) -> tuple[str, str, SourceRecord]`. Accepts `.jpg`, `.jpeg`, `.png`, `.webp`. Unsupported suffix raises `ImageFetchError` with remediation naming allowed suffixes.
- **AC-3:** Extraction output body is a markdown-formatted document carrying:
  - H1 title (filename stem, underscores → spaces)
  - **Caption** section (single-paragraph description)
  - **Detected text (OCR)** section (multiline text extracted from the image)
  - **Visual elements** section (bulleted list of identified entities with type + description)
  - **Layout** section (layout description)
  - **Tier classification** footer line with `visual_structural_fidelity` + `visual_completeness` semantic labels, confidence, and bridge_version for provenance.
- **AC-4:** `ExtractionReport` for image sources uses the existing `structural_fidelity` + `completeness_ratio` fields with image-specific assessment logic — no schema bifurcation. `source_type: "image"` added to `_WORDS_PER_PAGE` in `extraction_validator.py` (value: `60`). The image-specific `assess_image_fidelity()` helper lives in `image_to_agent.py` and is called from the wrangle path before the runner's default validator runs.
- **AC-5:** Transform-registry row added for image sources with explicit `Known Limitations` narrative: OCR partial on stylized fonts, hand-drawn content requires vision-model pass, transparent-background PNGs may mis-crop, EXIF rotation not auto-applied, vision-API latency + cost are v1 follow-on concerns.
- **AC-6:** Directive-schema validator accepts new contract roles `visual-primary` and `visual-supplementary` in the `role` field.
- **AC-7:** Dependency-injected tests: `FakeImageAnalyzer` substitutes for production `VisionLLMAnalyzer` so the test suite does not require a vision API key or installed vision model.
- **AC-8:** Lockstep check passes. Epic 27 AC-S spine satisfied. Image row added to transform-registry lockstep test with `LOCKSTEP_EXEMPTIONS` entry analogous to Box (image is fetch+perception, not text-extractor).
- **AC-9:** No pytest regressions. Full regression floor ≥ baseline (1950 passed after 27-5; expected ≥1964 after this story with K=14-18 added).
- **AC-10:** SCHEMA_CHANGELOG patch entry landed alongside code.
- **AC-T.N (Murat):** five explicit negative fixtures (binary-decode, unsupported-suffix, OCR-empty, vision-API-missing, corrupt-header) — one test each.
- **AC-P (Portability):** AST guard passes — no `marcus.orchestrator.*` / `marcus.dispatch.*` imports in image intake surface.

## Test plan (K floor ≥14, target 15-18)

Happy paths (4):
1. JPEG happy path — pre-computed perception flows through to ExtractionReport (FULL_FIDELITY or ADEQUATE_WITH_GAPS).
2. PNG happy path — identical contract as JPEG.
3. WEBP happy path.
4. Uppercase/mixed-case suffix (`.JPG`) — normalized and accepted.

Negative paths (5 — Murat rider):
5. Unsupported suffix (`.bmp`) — `ImageFetchError` with remediation substrings.
6. OCR-empty image (no text detected) — ExtractionReport tier → DEGRADED or FAILED with known_losses entry.
7. Vision-API missing (production analyzer with no key) — `ImageVisionAPIError` with remediation.
8. Corrupt-header bytes — `ImageDecodeError`.
9. Non-file path — `ImageFetchError` FileNotFoundError semantics.

Structural/integration (3):
10. Provenance shape — sha256 prefix + bridge_version + size + dimensions in `SourceRecord.note`.
11. `source_type="image"` → `_WORDS_PER_PAGE` lookup returns 60; completeness ratio computed correctly.
12. Directive-schema validator accepts `visual-primary` / `visual-supplementary` roles.

Portability + registry + schema-changelog (2):
13. AST guard: no marcus.orchestrator/dispatch imports in image_to_agent.py.
14. Transform-registry lockstep — image row parses, exemption registered, test green.

Stretch (target 15-18 — Amelia rider):
15. Shape-pin on body markdown — canonical sections + ordering.
16. `run_wrangler._fetch_source('image', ...)` dispatches to `wrangle_local_image` end-to-end (runner-level smoke).
17. `FakeImageAnalyzer` with varied complexity → tier classification boundary transitions (high → medium → low).
18. Dual-gate second-gate smoke: `SchemaChangelog` file has new entry covering image row (string match).

## File Impact

- `skills/sensory-bridges/scripts/image_to_agent.py` — NEW. `wrangle_local_image`, `ImageAnalyzer` Protocol, `VisionLLMAnalyzer` stub, `FakeImageAnalyzer` (test fixture lives in tests but the Protocol is here), `ImageError` taxonomy, `assess_image_fidelity`.
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — add `image` branch in `_fetch_source`; register in `_SUPPORTED_PROVIDERS`, `_PROVIDER_SOURCE_TYPE`, `_EXTRACTOR_LABELS`, `_EXTRACTOR_LABELS_BY_KIND` (kind=`image_source`).
- `skills/bmad-agent-texas/scripts/extraction_validator.py` — add `"image": 60` entry in `_WORDS_PER_PAGE`.
- `skills/bmad-agent-texas/references/transform-registry.md` — add Image section with cross-reference footnote.
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` — new patch entry.
- `tests/test_image_provider.py` — NEW (≥14 tests, target 15-18).
- Directive-schema validator (if roles live in a JSON/YAML enum file): update role enum. Otherwise extend the inline role validator.

## Non-goals (deferred)

- Live vision-API integration (`VisionLLMAnalyzer` is a stub-with-remediation in v1).
- EXIF rotation normalization, transparent-background crop fix.
- Animated PNG / GIF multi-frame handling.
- Vision-API rate-limit + cost accounting (follow-on).

## Party Input Captured (sprint-level green-light 2026-04-24)
- **Operator (backlog stub 2026-04-17):** Option A (extend runner with image provider via sensory-bridges) adopted. Option C (reject images) withdrawn.
- **John (PM, Round 3):** rejection-mode pinned before dev — classify-as-FAILED (not hard-exit). 3 pts firm. Standalone (not bundled).
- **Winston (Architect):** sibling helper, not pdf_to_agent.py extension. Typed rejection taxonomy. Provenance-preserving record.
- **Amelia (Dev):** DI via ImageAnalyzer Protocol. Explicit G0 thresholds. K≥14 / 15-18.
- **Murat (TA):** explicit negative fixtures per failure mode. Structural-shape assertions, not log-string assertions. No flake-gate required (cassettes not used — DI substitutes).
- **Paige (TW):** SCHEMA_CHANGELOG entry is part of the landing deliverable.
- **Sally (UX):** remediation text for unsupported-suffix / vision-API-missing must name the fix steps.
