# Next Session Start Here

## Immediate Next Action

**Trial Run 2 is queued.** Marcus is activated and waiting on source material confirmation.

Target: **Part 2: The Macro Trends & The Case for Change** (C1-M1)

Pipeline entry point: `source-wrangler` → Irene P1 → Gate 1 → Gary → Gate 2 → Irene P2 → Gate 3 → ElevenLabs → Compositor → Gate 4 → Descript

**Before invoking Marcus:** Confirm whether source material comes from the existing SME PDF (`course-content/courses/TEJAL_Course 01 Mod 01 Notes 2026-03-16.pdf`) or a separate document. Marcus will route source-wrangler accordingly.

**Style preset for Trial 2:** `hil-2026-apc-nejal-A` (Approach A — Nano Banana 2 Mini, illustration stylePreset, generate/detailed, 10 cards). Confirmed canonical.

**Audio briefing for Irene:** Vary narration segment LENGTH deliberately — heavier conceptual slides get more text/time, lighter transitional slides get less. Trial 1 audio was "very good" but too uniform in duration.

---

**Trial Run 1 (Physician as Innovator) — Descript assembly still pending (Gate 5 / human task):**

Bundle: `course-content/staging/ad-hoc/c1m1-physician-innovator-pilot-pass2/`
- `visuals/` — 10 PNGs (local disk, gitignored)
- `audio/` — 10 MP3s (local disk, gitignored)
- `captions/` — 10 VTTs ✅ tracked
- `DESCRIPT-ASSEMBLY-GUIDE.md` ✅ tracked
- `manifest.yaml` ✅ tracked

Assembly guide is complete. Follow it in Descript to produce the final video.

**Before Descript (automation):** `.venv\Scripts\python.exe skills/compositor/scripts/compositor_operations.py sync-visuals <manifest.yaml>` then `guide <manifest.yaml> <DESCRIPT-ASSEMBLY-GUIDE.md>` after any new bundle is finalized.

---

**Branch**: **`dev/next-session`** (default working branch). **`master`** carries merged release history.

**Startup:** `git checkout dev/next-session` && `git pull origin dev/next-session`

## Current Status — STORIES 3.1–3.5, 3.9, 3.10 COMPLETE

- **Story 3.1 (Gary)**: DONE - 10+6 files, 29 tests
- **Story 3.2 (Irene + Quinn-R)**: DONE - 12+6+10 files, 28 tests
- **Story 3.3 (Kira)**: DONE - API client, Kira agent, kling-video skill, comparison video set
- **Story 3.3.1 (Composition Harmonization + Gary Deck)**: DONE
- **Story 3.4 (Voice Director / ElevenLabs)**: DONE
- **Story 3.5 (Compositor + Intent Contract)**: DONE
- **Story 3.9 (Source Wrangler)**: DONE — PDF extraction, Gamma URL guard, local preflight added
- **Story 3.10 (Tech Spec Wrangler)**: DONE
- **Epic 2**: COMPLETE (6/6 stories, 55 tests)
- **Epic 1**: COMPLETE (11/11 stories, 117 tests)
- **Total tests**: 76 passing (gamma-api-mastery + source-wrangler)

## Gary Style Preset System (added this session)

`state/config/gamma-style-presets.yaml` — two presets for HIL 2026 APC:

| Preset | Approach | Model | StylePreset | Status |
|--------|----------|-------|-------------|--------|
| `hil-2026-apc-nejal-A` | A (named tile, proven) | `nano-banana-2-mini` | `illustration` | **Default — use this** |
| `hil-2026-apc-nejal-B` | B (custom + text, experimental) | `flux-kontext-pro` | `custom` | Experimental |

**Key facts:**
- `imageOptions.stylePreset` is a real API field (added Feb 27, 2026). Named values: `illustration`, `lineArt`, `photorealistic`, `abstract`, `3D`, `custom`.
- When `stylePreset` is named (not `custom`), `imageOptions.style` is IGNORED by the API.
- `additionalInstructions` CONCATENATES across cascade layers (preset base + content-type + envelope).
- Reference image upload (Gamma UI "Add style references") is UI-only — not in API yet. `referenceImagePath` in Approach B is a design-intent field for Marcus/Gary to study.
- Full model list (20+ models) now in `skills/gamma-api-mastery/references/parameter-catalog.md`.

## Git & Content Storage (clarified this session)

**Binary media is NOT tracked in git.** `.gitignore` now excludes `course-content/**/*.{pdf,pptx,docx,jpg,jpeg,png,mp3,wav,zip,gif,webp}`.

**What git tracks:** agent skills, scripts, configs, `.md`/`.yaml`/`.json`/`.vtt` text artifacts.

**What lives on disk (Box Drive):** all binary media — slides, audio, PDFs, source documents.

## Composition Architecture (Resolved 2026-03-27)

### Pipeline
```
Marcus → Irene P1 → Marcus/[Gate 1] → Gary → Marcus/[Gate 2] →
Irene P2 → Marcus/[Gate 3] → ElevenLabs → Marcus → Kira →
Marcus → Quinn-R pre-comp → Compositor → Descript →
Quinn-R post-comp → Marcus/[Gate 4] → Canvas
```

### Key Design Decisions
- **Silent video always** from Kling (`sound-off`)
- **ElevenLabs owns all audio** (narration, SFX, music)
- **Segment manifest** (YAML) = single source of truth
- **Descript** = sole composition platform (manual-tool pattern)
- **Four HIL gates**: lesson plan → slides → script+manifest → final video
- **VO variation**: Irene writes varied-length segments (not uniform duration) — brief for transitional slides, longer for conceptual-heavy slides

## Gamma API — New Knowledge (2026-03-28)

- `imageOptions.stylePreset` confirmed in API (Feb 27, 2026 changelog)
- `imageOptions.style` only respected when `stylePreset: custom`
- Reference image upload = UI-only (not in API as of 2026-03-28)
- `stylePreset: custom` + `flux-kontext-pro` = Approach B for style-reference matching
- `ideogram-v3` = best for text accuracy in AI images (medical diagrams, text-bearing slides)
- Gamma Imagine = UI-only canvas, no API surface

## Gotchas
- **Binary media in `course-content/`**: gitignored — files live on local disk only. Source-wrangler reads from local paths.
- **Compositor:** `sync-visuals` copies approved PNGs into `<manifest_folder>/visuals/` and patches manifest paths in place; regenerate assembly guide after.
- **Style preset flatten**: Approach A keywords → `_keywordsHint` (not sent to API). Approach B keywords → appended to `style` string.
- PowerShell doesn't support `&&` chaining
- `.venv` with Python 3.13
- Kling API credits are SEPARATE from consumer credits
- Kling status endpoint is type-specific: `/v1/videos/text2video/{id}`
- Kling text rendering produces garbled characters — use Gary for text-bearing visuals
- `pyjwt` in requirements.txt for Kling JWT auth
- Cross-skill Python imports use `importlib.util` loader pattern
- GammaClient.list_themes() requires dotenv load in Python scripts
