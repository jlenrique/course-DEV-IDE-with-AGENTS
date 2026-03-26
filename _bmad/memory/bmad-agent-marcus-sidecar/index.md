# Marcus — Memory Sidecar Index

**Agent**: `bmad-agent-marcus`
**Run Mode**: default
**Last Updated**: 2026-03-26

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

- **2026-03-26**: First activation. Set up memory sidecar, `_bmad/config.yaml` (user_name: Juan). Populated C1 course context from APC Content Roadmap image (3 courses, C1 has 10 modules, 3 content strands, 4 sync touchpoints, 4 assessment types). Style bible and exemplar library confirmed present. Pre-flight check completed: 6 APIs connected (Gamma, ElevenLabs, Canvas, Qualtrics, Wondercraft, Kling), Notion MCP live (22 tools), Box Drive accessible, 1 failure (Botpress). Searched Notion and Box Drive for pharmacology content — none found. Read C1-M1 SME notes. Created production plan for "Economic & Structural Reality" video (C1-M1-P2S1-VID-001). Execution blocked — specialist agents (gamma-specialist, elevenlabs-specialist, assembly-coordinator, quality-reviewer) not yet built. Tested ad-hoc/default mode switching — confirmed working.

## Next Steps

- Build specialist agents needed for production execution (gamma-specialist, elevenlabs-specialist, assembly-coordinator, quality-reviewer)
- Module-level content allocation when Juan is ready (still evolving)
- Execute production plan C1-M1-P2S1-VID-001 once specialists are available
- Finalize Notion's role in learner experience and share relevant pages with integration

## Transient Ad-Hoc Section

_Empty — not currently in ad-hoc mode._
