---
name: quality-control
description: Automated quality validation scripts for accessibility, brand compliance, and audit logging. Use when Quinn-R or Marcus needs deterministic quality checks on production artifacts.
---

# Quality Control

## Overview

This skill provides automated, deterministic quality checking for production artifacts. It is the companion skill to Quinn-R (Quality Guardian agent), handling checks that have clear pass/fail criteria: WCAG 2.1 AA accessibility scanning, style bible brand compliance, audio quality validation, composition integrity validation, and SQLite audit trail logging. Quinn-R handles judgment-based review; this skill handles the scriptable parts.

Scripts are invoked by Quinn-R during quality gate reviews or by Marcus for pre-checkpoint validation. All scripts accept artifact content as input and return structured JSON results. Scripts run in **two passes** matching Quinn-R's two-pass model.

## Scripts

| Script | Pass | Purpose | Invoked By |
|--------|------|---------|------------|
| `./scripts/accessibility_checker.py` | Post | WCAG 2.1 AA scanning: reading level, heading hierarchy, alt text, caption sync | Quinn-R (CC capability) |
| `./scripts/brand_validator.py` | Post | Style bible compliance: color codes, typography, voice markers | Quinn-R (BV capability) |
| `./scripts/visual_fill_validator.py` | Post | Literal-visual full-slide fill: edge-band sampling confirms image occupies entire slide with no empty borders | Quinn-R / Marcus (post-dispatch) |
| `./scripts/quality_logger.py` | Both | Log quality review results to SQLite `quality_gates` table | Quinn-R (after review) |

**Future scripts (planned for Story 3.4 ElevenLabs):**
| Script | Pass | Purpose |
|--------|------|---------|
| `audio_quality_checker.py` | Pre | WPM validation (130-170), VTT timestamp monotonicity, segment coverage >95% |
| `composition_validator.py` | Pre | Video duration vs narration duration (±0.5s), segment manifest completeness |

## References

| Reference | Purpose |
|-----------|---------|
| `./references/quality-standards.md` | Review dimensions (all 7), severity levels, pass/fail thresholds, two-pass model |
| `./references/accessibility-standards.md` | WCAG 2.1 AA checklist for educational content + caption sync requirements |
| `./references/brand-validation.md` | Style bible compliance rules and marker extraction |
