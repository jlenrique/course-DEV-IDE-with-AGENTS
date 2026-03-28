# Story 3.11: Mixed-Fidelity Gamma Generation System

Status: ready-for-dev

## Story

As a course content producer,
I want the production pipeline to handle slides with different fidelity requirements within a single deck — creative enhancement for most slides, literal text preservation for assessment-linked slides, and faithful reproduction of SME-provided technical visuals,
So that every slide gets the right treatment and learners never see content that misrepresents what they'll be tested on or misrepresents technical diagrams provided by subject matter experts.

## Background & Motivation

**Trial Run 2 (2026-03-28)** exposed a critical content fidelity gap. Gamma's `textMode` parameter is deck-level — it cannot be set per-card. When the deck was generated in `generate` mode, Gamma reframed, merged, and embellished a knowledge check teaser slide that needed to list exact assessment topics. Fidelity audit: 5/10 KC topics well-represented, 2 misframed, 3 missing. Two root causes:

1. **Upstream editorial gap** — 3 KC topics omitted from inputText (Irene's responsibility to fix via better source analysis)
2. **Gamma's `generate` mode structurally rewrites content** — no per-card control exists in the API

A second fidelity dimension was identified: **SME-provided technical images** (clinical flowcharts, data visualizations, framework diagrams) that must be preserved or faithfully rebranded, not creatively reinterpreted by Gamma's AI image generation.

**Party Mode consensus (2026-03-28):** Irene, Gary, Winston, Caravaggio, and a parallel research team all converged on the same architecture. This story implements it.

## Fidelity Classification System

Three fidelity classes, owned by Irene, consumed by Gary:

| Class | What's Protected | Gamma Treatment | Image Source |
|---|---|---|---|
| `creative` (default) | Nothing — Gamma enhances freely | `textMode: generate`, full AI images | Gamma AI |
| `literal-text` | Exact text/data must appear as written | `textMode: preserve` + strict constraints | `noImages` or `themeAccent` |
| `literal-visual` | SME-provided image must be faithfully included | `textMode: preserve` + inline image URL | User-provided via Gamma Imagine → hosted URL |

## Acceptance Criteria

### Irene (Content Creator) — Slide Brief Schema

1. Slide brief template (`skills/bmad-agent-content-creator/references/template-slide-brief.md`) includes a `fidelity` field per slide with values: `creative` (default), `literal-text`, `literal-visual`
2. `literal-text` and `literal-visual` slides require a `fidelity_rationale` field explaining why literal treatment is needed
3. `literal-visual` slides include a `source_image` field pointing to the SME source material location and a `visual_treatment` field with value `user-rebranded`
4. Irene's delegation protocol (`skills/bmad-agent-content-creator/references/delegation-protocol.md`) documents when to apply each fidelity class, with examples:
   - `literal-text`: assessment teasers, citation slides, slides with testable statistics
   - `literal-visual`: SME-provided diagrams, clinical flowcharts, framework models, data visualizations with specific labeled data series
5. Default fidelity is `creative` — Irene must not over-apply literal tagging
6. Irene's lesson plan template (`skills/bmad-agent-content-creator/references/template-lesson-plan.md`) references fidelity classification in the content block schema

### Marcus (Orchestrator) — Fidelity Discovery, Delegation & Checkpoints

**Fidelity discovery at production run start:**

7. Marcus's production run interview (CM capability, `conversation-mgmt.md`) includes two new standard queries before delegating to Irene for Pass 1:
   - **Visual fidelity query:** "Are there any visuals in the source material — diagrams, charts, flowcharts, framework models — that need to be faithfully reproduced rather than creatively illustrated? If so, please process them in Gamma Imagine and drop the rebranded PNGs into `course-content/staging/ad-hoc/rebranded-assets/` (ad-hoc mode) or `course-content/staging/rebranded-assets/` (default mode)."
   - **Textual fidelity query:** "Are there any text elements that must appear literally on slides — assessment topics, specific statistics that will be tested, exact terminology from accreditation standards? If so, point me to the source documents or sections, or just describe what needs literal treatment."
8. User responses to the fidelity queries are captured and passed to Irene as part of the context envelope under a `fidelity_guidance` block:
   ```yaml
   fidelity_guidance:
     literal_visuals:
       - description: "Dual-axis chart from page 7 of Tejal's notes"
         source_ref: "TEJAL_Course 01 Mod 01 Notes 2026-03-16.pdf#page7"
         rebranded_asset_path: "course-content/staging/ad-hoc/rebranded-assets/slide-03-dual-axis-chart.png"
     literal_text:
       - description: "Knowledge check teaser — must list exact 10 KC topics from Chapters 2 & 3"
         source_ref: "course-content/staging/ad-hoc/source-bundles/trial2-macro-trends/extracted.md#Chapter 2 Knowledge Check"
   ```
9. Irene uses `fidelity_guidance` from the user (via Marcus) as primary input when tagging slides in the slide brief. Irene may also independently identify additional fidelity needs from her own pedagogical analysis of the source material — user guidance supplements, not replaces, Irene's judgment.

**Delegation and checkpoints:**

10. Marcus's context envelope to Gary includes a `diagram_cards` structured block for `literal-visual` slides:
    ```yaml
    diagram_cards:
      - card_number: 3
        image_url: "https://..."
        placement_note: "Primary visual, full-width"
        required: true
    ```
11. After Irene returns the slide brief with fidelity tags, Marcus surfaces `literal-visual` slides to the user as a checkpoint before Gary runs: "Irene flagged slides N and M as needing rebranded visuals. Source images are from [source]. Are the rebranded PNGs ready in the assets folder, and do you have hosted URLs?"
12. Marcus validates that all `diagram_cards[].image_url` values are populated and HTTPS-accessible before unblocking Gary
13. Marcus's conversation management reference (`skills/bmad-agent-marcus/references/conversation-mgmt.md`) documents the fidelity discovery queries, the Imagine handoff workflow, and the asset delivery protocol
14. Imagine handoff instructions include: export at highest resolution, 16:9 aspect ratio, PNG format

### Gary (Gamma Specialist) — Two-Call Split Generation

15. Gary's context envelope schema (`skills/bmad-agent-gamma/references/context-envelope-schema.md`) includes `fidelity` per slide, `diagram_cards` structured block, and `fidelity_guidance` from user
16. Gary partitions slides by fidelity class from the slide brief: creative slides in one group, literal slides (both text and visual) in another
17. Gary runs **two separate Gamma API calls** per deck when mixed fidelity is present:
    - **Call 1 (creative):** `textMode: generate`, full preset, standard `imageOptions`
    - **Call 2 (literal):** `textMode: preserve`, same theme/preset, `additionalInstructions: "Output ONLY the provided text. Do not add content, steps, or diagrams beyond what is given."`, `imageOptions.source: noImages` (or `themeAccent` if no user-provided images)
18. For `literal-visual` slides in Call 2: Gary embeds the `diagram_cards[].image_url` inline in the card's `inputText` block
19. Gary downloads PNGs from both calls and reassembles with sequential numbering matching original slide order
20. Gary produces a **provenance manifest** in the return envelope:
    ```yaml
    provenance:
      - card_number: 1
        source_call: creative
        generation_id: "abc123"
        fidelity: creative
      - card_number: 10
        source_call: literal
        generation_id: "def456"
        fidelity: literal-text
    ```
21. Gary's `gary_slide_output` array is a unified set — downstream consumers (Irene Pass 2, ElevenLabs, Compositor) see no difference from a single-call generation

### Gamma Document Naming & Archival Integrity

22. Each Gamma API call produces a separate document on gamma.app. Gary applies a **formulaic naming convention** so split documents are clearly related and individually editable:
    - Pattern: `{module-lesson-part}_{fidelity-class}_{slide-range}`
    - Examples: `C1-M1-P2-Macro-Trends_creative_s01-s09`, `C1-M1-P2-Macro-Trends_literal_s10`
    - For three-way splits: `..._literal-text_s10`, `..._literal-visual_s03-s07`
23. Gary passes the naming convention to Gamma via the document title in `inputText` (first line before the first `---` break) so the Gamma doc on gamma.app has the formulaic name
24. Each Gamma document is a complete, self-contained, editable artifact — no merge step is required. The naming convention makes the relationship between documents clear for archiving and future editing.

### Graceful Degradation

25. When ALL slides are tagged `creative` (the default case), Gary runs exactly one Gamma API call — behavior is identical to pre-story pipeline. No regression. Standard naming (no fidelity suffix needed).
26. When ALL slides are tagged literal, Gary runs one call in `preserve` mode — no split needed
27. Gary handles the edge case where `diagram_cards` references a URL that is unreachable: reports failure to Marcus with the specific card number and URL, does NOT proceed with generation

### Quality & Verification

28. Quality Reviewer (Quinn-R) can distinguish fidelity classes in the provenance manifest and applies appropriate review criteria:
    - `creative` slides: standard visual quality + pedagogical alignment
    - `literal-text` slides: exact text match against slide brief input
    - `literal-visual` slides: image presence verification + text match

### Fidelity Learning & Memory (Default Mode)

29. Gary's memory sidecar (`_bmad/memory/gamma-specialist-sidecar/patterns.md`) captures fidelity-specific learnings after each production run (default mode only):
    - **Constraint effectiveness:** Which `additionalInstructions` phrasings produce the best text fidelity in `preserve` mode (e.g., "Output ONLY..." vs "Do not modify..."), scored by observed fidelity in QA
    - **Image placement results:** Which `placement_note` instructions produce good layouts for inline image URLs, which produce drift — with Gamma model and card count context
    - **Visual consistency observations:** Degree of stylistic drift between creative and literal calls using the same theme/preset — noting model, card count, and mitigation effectiveness
    - **Edge cases encountered:** Gamma quirks discovered during literal generation (structural headings added in preserve mode, image resizing behavior, accent images appearing despite `noImages`, etc.) with workarounds that resolved them
30. Irene's memory sidecar (`_bmad/memory/content-creator-sidecar/patterns.md`) captures fidelity classification learnings:
    - **Classification patterns:** Which content types consistently need `literal-text` or `literal-visual` treatment — building a growing heuristic library beyond the initial examples in the delegation protocol
    - **User correction patterns:** When the user overrides Irene's fidelity classification (either upgrading to literal or downgrading to creative), capture the rationale to refine future tagging
    - **Source material signals:** Observable indicators in SME notes that predict literal fidelity needs (e.g., "Knowledge Check" headings, labeled diagrams, specific data citations)
31. Marcus's memory sidecar (`_bmad/memory/bmad-agent-marcus-sidecar/patterns.md`) captures production workflow learnings:
    - **User fidelity preferences:** Common responses to the fidelity discovery interview — does this user typically have literal visual needs? How do they prefer to describe literal text requirements?
    - **Checkpoint patterns:** How many literal slides per deck is typical? Do certain content types (e.g., Part summaries, assessment previews) consistently trigger fidelity flags?
    - **Hosting workflow notes:** What hosting approach (G3/G4/G2) the user prefers, URL durability observations, Imagine export settings that produce best results
32. All three agents' memory writes for fidelity learning follow existing memory-system rules: write-through for critical learnings (constraint phrasings that work), checkpoint for accumulated observations, append-only to `patterns.md`, condensed periodically. Ad-hoc mode suppresses memory writes per standard access boundaries.

## Tasks / Subtasks

- [ ] Task 1: Update Irene's slide brief schema (AC: #1, #2, #3, #5, #6)
  - [ ] 1.1 Add `fidelity`, `fidelity_rationale`, `source_image`, `visual_treatment` fields to `template-slide-brief.md`
  - [ ] 1.2 Add fidelity classification guidance to `template-lesson-plan.md` content block schema
  - [ ] 1.3 Document fidelity decision heuristics in `delegation-protocol.md` with examples

- [ ] Task 2: Update Gary's context envelope schema (AC: #15, #16)
  - [ ] 2.1 Add `fidelity` per-slide field to `context-envelope-schema.md` inbound schema
  - [ ] 2.2 Add `diagram_cards` structured block to inbound schema
  - [ ] 2.3 Add `fidelity_guidance` block to inbound schema (passed through from Marcus)
  - [ ] 2.4 Add `provenance` array to outbound return schema
  - [ ] 2.5 Document merge/partition rules in schema comments

- [ ] Task 3: Implement Gary's two-call split generation (AC: #17, #18, #19, #20, #21, #22, #23, #24, #25, #26, #27)
  - [ ] 3.1 Add `partition_by_fidelity()` function to `gamma_operations.py` — takes slide brief + fidelity tags, returns two inputText blocks with card metadata
  - [ ] 3.2 Add `reassemble_slide_output()` function — takes PNGs from both calls, reassembles in original order with provenance manifest
  - [ ] 3.3 Update `generate_slide()` or add `generate_deck_mixed_fidelity()` — orchestrates the two-call flow
  - [ ] 3.4 Implement formulaic Gamma document naming: `{module-lesson-part}_{fidelity-class}_{slide-range}` — injected as first line of inputText (AC: #22, #23, #24)
  - [ ] 3.5 Implement URL validation for `diagram_cards` — HTTPS check, HEAD request to verify accessibility (AC: #27)
  - [ ] 3.6 Handle single-fidelity edge cases: all-creative = one `generate` call (no fidelity suffix), all-literal = one `preserve` call (AC: #25, #26)
  - [ ] 3.7 Write tests: `test_partition_by_fidelity.py`, `test_reassemble_slide_output.py`, `test_url_validation.py`, `test_doc_naming.py`

- [ ] Task 4: Update Marcus's fidelity discovery and delegation protocol (AC: #7, #8, #9, #10, #11, #12, #13, #14)
  - [ ] 4.1 Add fidelity discovery queries to Marcus's production run interview in `conversation-mgmt.md` — two standard questions: visual fidelity (rebranded assets) and textual fidelity (literal content sources)
  - [ ] 4.2 Define `fidelity_guidance` block structure in Marcus's context envelope to Irene — captures user responses with source refs and asset paths
  - [ ] 4.3 Define designated asset drop locations: `course-content/staging/ad-hoc/rebranded-assets/` (ad-hoc) and `course-content/staging/rebranded-assets/` (default)
  - [ ] 4.4 Add `diagram_cards` construction to Marcus's context envelope building in `conversation-mgmt.md` — populated after Irene returns tagged slide brief
  - [ ] 4.5 Document Imagine handoff checkpoint in `checkpoint-coord.md` — Marcus surfaces tagged slides, confirms assets are ready, validates URLs
  - [ ] 4.6 Add pre-flight URL validation step before Gary delegation
  - [ ] 4.7 Document asset delivery protocol: user processes in Imagine → drops PNGs to designated location → provides hosted URLs (Phase 1: Gamma workspace upload = G3)

- [ ] Task 5: Update Quality Reviewer protocol (AC: #28)
  - [ ] 5.1 Update `skills/bmad-agent-quality-reviewer/references/review-protocol.md` to document fidelity-aware review criteria
  - [ ] 5.2 Add provenance manifest consumption to Quinn-R's pre-composition review pass

- [ ] Task 6: Fidelity learning and memory integration (AC: #29, #30, #31, #32)
  - [ ] 6.1 Add fidelity-specific pattern categories to Gary's `memory-system.md` — constraint effectiveness, image placement, visual consistency, edge cases
  - [ ] 6.2 Add fidelity classification pattern categories to Irene's `memory-system.md` — classification patterns, user correction patterns, source material signals
  - [ ] 6.3 Add fidelity workflow pattern categories to Marcus's `memory-system.md` — user preferences, checkpoint patterns, hosting workflow notes
  - [ ] 6.4 Add memory write hooks to Gary's generation flow: after QA assessment, capture fidelity-relevant observations to `patterns.md` (default mode only)
  - [ ] 6.5 Add memory write hooks to Irene's Pass 1 flow: after user reviews fidelity tags, capture corrections to `patterns.md` (default mode only)
  - [ ] 6.6 Add memory write hooks to Marcus's delegation flow: after production run, capture fidelity discovery insights to `patterns.md` (default mode only)

- [ ] Task 7: Regression validation (AC: #25)
  - [ ] 6.1 Generate a test deck with all-creative slides — verify output is identical to pre-story behavior
  - [ ] 6.2 Generate a test deck with mixed fidelity — verify two-call split produces correct unified output
  - [ ] 6.3 Generate a test deck with a `literal-visual` slide containing an inline image URL — verify image appears on the themed card

## Dev Notes

### Agent Architecture Pattern

This story follows the established three-layer architecture: **Agent** (judgment/decisions) → **Skill** (tool expertise) → **API Client** (connectivity). Changes are in the agent and skill layers only — `gamma_client.py` requires NO modifications. The API client already supports all required parameters.

### Key Constraint: Gamma API Limitations

- `textMode` is **deck-level**, not per-card — this is the root constraint driving the two-call architecture
- `additionalInstructions` is **global** (5000 chars, all cards) — cannot target individual slides
- Reference image upload is **UI-only** — not exposed in the API as of 2026-03-28
- Inline image URLs in `inputText` are the only API mechanism for injecting specific images
- Image URLs must be HTTPS, publicly accessible, with recognized image extension (.png, .jpg, etc.)

### Visual Consistency Concern (Caravaggio)

Two separate Gamma generation calls with the same theme/preset may produce **stylistic drift** in AI-generated illustrations. Mitigation: literal slides default to `imageOptions.source: noImages` or `themeAccent` — they don't carry AI illustrations. Creative slides carry the visual storytelling. Different jobs, different tools.

### Image Hosting for Phase 1 (G3 — Gamma Workspace Upload)

The user processes SME images in Gamma Imagine (UI), exports as high-res 16:9 PNG, uploads to their Gamma workspace (drag-and-drop), and provides the Gamma-hosted URL. Gamma re-hosts on its CDN, so URLs are durable. No external hosting infrastructure needed for Phase 1.

### Phase 2 (Future — Not In Scope)

- **Option D / Pattern B:** Gamma template-based generation for recurring literal slide types (KC teasers, title cards, summary cards). Create templates in UI, invoke via `from-template` API.
- **Automated image hosting (G2):** S3/CDN upload script in `gamma_operations.py` for production-scale asset management.
- **Box Drive links (G4):** Test whether Box shared links resolve to raw images Gamma can fetch. Zero-cost experiment.

### Existing Files to Modify

| File | Change |
|---|---|
| `skills/bmad-agent-content-creator/references/template-slide-brief.md` | Add fidelity fields |
| `skills/bmad-agent-content-creator/references/template-lesson-plan.md` | Add fidelity to content block schema |
| `skills/bmad-agent-content-creator/references/delegation-protocol.md` | Add fidelity classification heuristics |
| `skills/bmad-agent-gamma/references/context-envelope-schema.md` | Add fidelity, diagram_cards, provenance |
| `skills/gamma-api-mastery/scripts/gamma_operations.py` | Add partition, reassemble, URL validation functions |
| `skills/bmad-agent-marcus/references/conversation-mgmt.md` | Add Imagine handoff, diagram_cards construction |
| `skills/bmad-agent-marcus/references/checkpoint-coord.md` | Add visual asset delivery checkpoint |
| `skills/bmad-agent-quality-reviewer/references/review-protocol.md` | Add fidelity-aware review criteria |

### New Files to Create

| File | Purpose |
|---|---|
| `skills/gamma-api-mastery/scripts/tests/test_partition_fidelity.py` | Tests for partition and reassembly logic |

### References

- [Trial 2 fidelity audit: Marcus memory sidecar `_bmad/memory/bmad-agent-marcus-sidecar/index.md` — 2026-03-28 entries]
- [Gamma API parameter catalog: `skills/gamma-api-mastery/references/parameter-catalog.md`]
- [Gamma developer docs: `https://developers.gamma.app/guides/generate-api-parameters-explained`]
- [Gamma image URL best practices: `https://developers.gamma.app/guides/image-url-best-practices`]
- [Context envelope schema: `skills/bmad-agent-gamma/references/context-envelope-schema.md`]
- [Style preset library: `state/config/gamma-style-presets.yaml`]
- [Party Mode session transcript: 2026-03-28, this conversation]

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List
