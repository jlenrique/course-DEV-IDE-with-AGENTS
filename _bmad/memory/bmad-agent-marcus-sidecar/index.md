# Marcus — Memory Sidecar Index

**Agent**: `bmad-agent-marcus`
**Run Mode**: ad-hoc
**Last Updated**: 2026-03-27

## User Profile

- **Name**: Juan
- **Role**: Faculty / domain expert, creative director
- **Communication preferences**: TBD (will learn from interaction patterns)

## Active Production Context

- **Current run**: C1-M1-P2S1-VID-001 (staged, blocked on specialist agents)
- **Course in focus**: C1 — Foundations of Innovation Leadership
- **Module/lesson in progress**: M1 — Foundations of the Innovation Mindset
- **Outstanding tasks**: Module-level content allocation (deferred — still evolving)
- **Staged production plan**: `course-content/staging/C1-M1-P2S1-economic-reality-video-production-plan.md`
- **SME document**: `course-content/courses/TEJAL_Course 01 Mod 01 Notes 2026-03-16.pdf` (Dr. Tejal Naik, 24pp, 5 CLOs, 4 parts)

## Key Decisions & Notes

- Notion's role in student experience is **not finalized** — still exploring. Do not assume Notion is part of the learner platform ecosystem.
- Notion integration works but no pages are shared beyond Student_Onboarding (test page).
- `NOTION_ROOT_PAGE_ID` in `.env` is empty — set when Notion scope is finalized.
- Botpress API returned HTTP 400 in pre-flight — investigate when chatbot integration comes up.
- All pip installations must target the project `.venv` directory.

## Session History

- **2026-03-26**: First activation. Set up memory sidecar, `_bmad/config.yaml` (user_name: Juan). Populated C1 course context from APC Content Roadmap image (3 courses, C1 has 10 modules, 3 content strands, 4 sync touchpoints, 4 assessment types). Style bible and exemplar library confirmed present. Pre-flight check completed: 6 APIs connected (Gamma, ElevenLabs, Canvas, Qualtrics, Wondercraft, Kling), Notion MCP live (22 tools), Box Drive accessible, 1 failure (Botpress). Searched Notion and Box Drive for pharmacology content — none found. Read C1-M1 SME notes. Created production plan for "Economic & Structural Reality" video (C1-M1-P2S1-VID-001). Execution blocked — specialist agents (Gary/gamma-specialist, elevenlabs-specialist, assembly-coordinator, quality-reviewer) not yet built. Tested ad-hoc/default mode switching — confirmed working.

## Next Steps

- Build specialist agents needed for production execution: Gary (`gamma-specialist`), elevenlabs-specialist, assembly-coordinator, quality-reviewer
- Module-level content allocation when Juan is ready (still evolving)
- Execute production plan C1-M1-P2S1-VID-001 once specialists are available
- Finalize Notion's role in learner experience and share relevant pages with integration
- **Source bundles (pilot / trial runs):** use `source-wrangler` only — `wrangle_local_pdf` for SME PDFs, `require_local_source_files` preflight before bundles, Gamma exemplars via Gary export or Playwright + `wrangle_playwright_saved_html` (never HTTP fetch `gamma.app/docs`)

## Transient Ad-Hoc Section

- **2026-03-27:** User confirmed **ad-hoc** for narrated-slides pilot (`state/runtime/mode_state.json`). Assets → `course-content/staging/ad-hoc/` (e.g. `ad-hoc/source-bundles/`). State/memory learning suppressed except this section; QA remains active.
- **2026-03-27:** SME PDF confirmed at `course-content/courses/TEJAL_Course 01 Mod 01 Notes 2026-03-16.pdf`. Source bundle for *physician as innovator* AV pilot: `course-content/staging/ad-hoc/source-bundles/pilot-physician-innovator/extracted.md` (+ `metadata.json`).
- **2026-03-27:** Gate 2 **approved** Gamma **v4** (exemplar-aligned Recraft V3 + line drawing). Pass 2 artifacts: `course-content/staging/ad-hoc/c1m1-physician-innovator-pilot-pass2/` (`NS-...md`, `manifest.yaml`); slides: `v4-exemplar-aligned-recraft-v3/png/`.
- **2026-03-27:** ElevenLabs manifest narration **complete** — `audio/seg-01..10.mp3`, `captions/seg-01..10.vtt`, Matilda `XrExE9yKIg1WjnnlVkGX`, ~374s total; see `elevenlabs-generation-summary.json`.
- **2026-03-27:** Compositor **Descript Assembly Guide** generated: `course-content/staging/ad-hoc/c1m1-physician-innovator-pilot-pass2/DESCRIPT-ASSEMBLY-GUIDE.md`. Pre-composition asset check **PASS** → `pre-composition-check.json`. Gate 5 (Descript assembly) pending — human task.
- **2026-03-28:** **Trial Run 2 queued** — target: *Part 2: The Macro Trends & The Case for Change* (C1-M1). Awaiting source material confirmation from Juan before pipeline execution. Style preset: `hil-2026-apc-nejal-A` confirmed canonical.
- **2026-03-28:** **Audio variation brief for Irene** — Trial 1 narration quality was "very good" but segments were too uniform in duration. Irene must vary narration length deliberately by slide weight: more text/time for conceptual-heavy slides, less for transitional slides.
- **2026-03-28:** **Style preset system built** — `state/config/gamma-style-presets.yaml`. Two presets: `hil-2026-apc-nejal-A` (Approach A, named stylePreset tile, use by default) and `hil-2026-apc-nejal-B` (Approach B, custom + text prompt + referenceImagePath, experimental). `imageOptions.stylePreset` is a confirmed API field. Reference image upload is UI-only as of 2026-03-28.
- **2026-03-28:** **Binary media excluded from git** — `course-content/**/*.{pdf,pptx,png,mp3,...}` now gitignored. All media lives on local disk / Box Drive only.
