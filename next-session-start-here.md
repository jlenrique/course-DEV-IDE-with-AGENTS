# Next Session Start Here

## Immediate Next Action

**Implement Story 3.11: Mixed-Fidelity Gamma Generation System** — this is a critical blocker for Trial Run 2.

Story file: `_bmad-output/implementation-artifacts/3-11-mixed-fidelity-gamma-generation.md`
Status: `ready-for-dev`

Story 3.11 introduces a three-class fidelity system (`creative`, `literal-text`, `literal-visual`) that enables Gary to generate decks where some slides are creatively enhanced by Gamma and others preserve exact text or user-provided images. Irene classifies slides in the slide brief, Marcus handles fidelity discovery at run start and asset validation, Gary partitions API calls by fidelity class.

**Implementation order:**
1. Task 1: Irene's slide brief schema (fidelity fields)
2. Task 2: Gary's context envelope schema (fidelity, diagram_cards, provenance)
3. Task 3: Gary's two-call split generation logic in `gamma_operations.py`
4. Task 4: Marcus's fidelity discovery interview + delegation protocol
5. Task 5: Quality Reviewer fidelity-aware review criteria
6. Task 6: Memory hooks for fidelity learning
7. Task 7: Regression validation

**After 3.11 is complete:** Resume Trial Run 2 with corrected Slide 10 (knowledge check teaser with all 10 KC topics, generated in `preserve` mode).

---

**Trial Run 2 (Macro Trends & Case for Change) — HALTED pending Story 3.11:**

- Source bundle ready: `course-content/staging/ad-hoc/source-bundles/trial2-macro-trends/extracted.md`
- Lesson plan: `course-content/staging/ad-hoc/LP-C1M1-macro-trends-case-for-change.md`
- Slide brief: `course-content/staging/ad-hoc/SB-C1M1-macro-trends-case-for-change.md`
- Gamma generation (pre-halt): `https://gamma.app/docs/xhu9ykb264e87jf` (10 slides, slides 1-9 approved, slide 10 needs fidelity fix)
- PDF: `course-content/staging/ad-hoc/gamma-c1m1-macro-trends-trial2/The-Macro-Trends-and-The-Case-for-Change.pdf`
- Halt reason: Slide 10 content fidelity gap — Gamma's `generate` mode reframed/merged/embellished KC topic list
- Credits remaining: 7,290

**Trial Run 1 (Physician as Innovator) — Descript assembly still pending (Gate 5 / human task):**

Bundle: `course-content/staging/ad-hoc/c1m1-physician-innovator-pilot-pass2/`

---

## Critical Discovery This Session

**Gamma API `textMode` is deck-level, not per-card.** You cannot mix `generate` and `preserve` within a single API call. This is the root constraint driving Story 3.11's two-call architecture. Also confirmed:
- `additionalInstructions` is global (5000 chars, all cards)
- Reference image upload is UI-only (not in API as of 2026-03-28)
- Inline image URLs in `inputText` ARE supported — Gamma fetches and re-hosts on its CDN
- `imageOptions.source: noImages` prevents competing AI visuals when injecting user images
- Gamma UI supports copy-paste cards between documents (for manual merge if desired)
- Gamma Imagine (standalone image generation) is UI-only — no API surface

**Mixed-fidelity solution:** Two (or three) Gamma API calls per deck, partitioned by fidelity class. Each call produces a separate, complete, editable Gamma document with a formulaic name (e.g., `C1-M1-P2-Macro-Trends_creative_s01-s09`). PNGs from all calls merge into a single ordered set for the production pipeline.

---

**Branch**: **`dev/next-session`** (default working branch). **`master`** carries merged release history.

**Startup:** `git checkout dev/next-session` && `git pull origin dev/next-session`

## Current Status — STORIES 3.1–3.5, 3.9, 3.10 COMPLETE; 3.11 READY-FOR-DEV

- **Story 3.11 (Mixed-Fidelity Gamma Generation)**: READY-FOR-DEV — 32 ACs, 7 task groups
- **Stories 3.1–3.5, 3.9, 3.10**: DONE
- **Stories 3.6–3.8**: BACKLOG (Canvas, Qualtrics, Canva)
- **Epic 2**: COMPLETE (6/6 stories)
- **Epic 1**: COMPLETE (11/11 stories)

## Key File Paths for Story 3.11

| File | Role |
|---|---|
| `skills/bmad-agent-content-creator/references/template-slide-brief.md` | Add fidelity fields |
| `skills/bmad-agent-content-creator/references/delegation-protocol.md` | Fidelity classification heuristics |
| `skills/bmad-agent-gamma/references/context-envelope-schema.md` | Add fidelity, diagram_cards, provenance |
| `skills/gamma-api-mastery/scripts/gamma_operations.py` | Partition, reassemble, URL validation |
| `skills/bmad-agent-marcus/references/conversation-mgmt.md` | Fidelity discovery queries, Imagine handoff |
| `skills/bmad-agent-marcus/references/checkpoint-coord.md` | Visual asset delivery checkpoint |
| `skills/bmad-agent-quality-reviewer/references/review-protocol.md` | Fidelity-aware review criteria |

## Gotchas

- **Binary media in `course-content/`**: gitignored — files live on local disk only
- PowerShell doesn't support `&&` chaining
- `.venv` with Python 3.13
- GammaClient requires `dotenv.load_dotenv()` before instantiation in scripts
- `numCards` is ignored when `cardSplit: inputTextBreaks` — card count controlled by `---` separators
- Gamma credits: 7,290 remaining (90 used this session for Trial 2 creative generation)
