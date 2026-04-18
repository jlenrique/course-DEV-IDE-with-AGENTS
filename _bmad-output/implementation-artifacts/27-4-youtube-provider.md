# Story 27-4: YouTube Provider (Video + Audio + Transcript)

**Epic:** 27 — Texas Intake Surface Expansion
**Status:** ratified-stub
**Sprint key:** `27-4-youtube-provider`
**Added:** 2026-04-17
**Points:** 5
**Depends on:** 27-2 (atomic-write + lockstep patterns).
**Blocks:** nothing in Epic 27; enables YouTube as a future Tracy provider target post-pilot.

## Story

As the Texas wrangler,
I want to accept a public YouTube URL via `provider: youtube` and emit three correlated asset rows — video file, audio track, and timed transcript,
So that a single operator-named or Tracy-suggested YouTube source flows through the pipeline as first-class material for downstream video/audio/narration consumers.

## Background

YouTube is the only provider in Epic 27 that produces a **three-asset manifest row** from a single URL. This makes it the most complex of the batch and justifies its 5-point estimate. Downstream agents will consume the assets differently: Kira may composite the video, ElevenLabs may reference the audio track for voice-match tuning, narration pipelines cite the transcript.

Transcript retrieval via YouTube Data API (caption track) or fallback to whisper-based local transcription if captions are absent or machine-generated and low-quality. Video/audio download via `yt-dlp` (the maintained successor to `youtube-dl`).

## Acceptance Criteria (Stub Level)

- **AC-1:** `provider: youtube` registered in `transform-registry.md` and dispatched in `run_wrangler.py`.
- **AC-2:** Directive schema accepts YouTube URL with optional `assets` filter (subset of `[video, audio, transcript]`); default is all three.
- **AC-3:** Per-asset row in `extraction-report.yaml` with asset-specific metadata (video codec + resolution; audio bitrate; transcript language + source).
- **AC-4:** Transcript extraction tier hierarchy: (1) human-authored captions from YouTube, (2) YouTube auto-captions with quality flag, (3) local whisper transcription as last resort.
- **AC-5:** Video/audio downloaded to bundle dir with sanitized filenames; size checks prevent runaway downloads (configurable cap, default 500MB per asset).
- **AC-6:** Rights/license surfaced from YouTube metadata (standard license / Creative Commons) in `provider_metadata.youtube`.
- **AC-7:** Cassette-backed tests for metadata + transcript API calls; skipped-by-default large-download live test.
- **AC-8:** Lockstep check passes. Epic 27 spine satisfied.
- **AC-9:** No pytest regressions.

## File Impact (Preliminary)

- `skills/bmad-agent-texas/scripts/providers/youtube_provider.py` — new
- `skills/bmad-agent-texas/scripts/run_wrangler.py` — youtube branch
- `skills/bmad-agent-texas/references/transform-registry.md` — add youtube row
- `tests/test_youtube_provider.py` — new
- `tests/cassettes/texas/youtube/*.yaml` — cassette library
- `requirements.txt` — `yt-dlp`, possibly `whisper` (or optional extras)

## Notes for Create-Story

- Three-asset shape may motivate its own AC decomposition at story-open (video AC, audio AC, transcript AC).
- Whisper fallback is the biggest scope variable — may be pulled into 27-4-follow-up story if scope creeps.
- Respect YouTube ToS: this is for operator-authorized educational use; add a README note about acceptable use.

## Party Input Captured
- **Amelia (Dev, Round 3):** 5 points; three-asset output surface.
- **John (PM, Round 3):** grouped originally with Notion/Box as "read-providers batch" but the three-asset complexity justifies standalone treatment.
