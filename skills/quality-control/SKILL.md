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
| `./scripts/precomposition_validator.py` | Pre | Pre-composition asset validation: WPM review, VTT monotonicity, segment coverage, motion-fit checks, advisory/runtime nuance | Quinn-R / Marcus |
| `./scripts/quality_logger.py` | Both | Log quality review results to SQLite `quality_gates` table | Quinn-R (after review) |

## References

| Reference | Purpose |
|-----------|---------|
| `./references/quality-standards.md` | Review dimensions (all 7), severity levels, pass/fail thresholds, two-pass model |
| `./references/accessibility-standards.md` | WCAG 2.1 AA checklist for educational content + caption sync requirements |
| `./references/brand-validation.md` | Style bible compliance rules and marker extraction |

Pre-composition policy note:
- blocking findings include missing assets, missing coverage, non-monotonic VTT, unreadable motion assets, and material motion mismatch
- advisory findings include script-implied pacing variance, runtime-band drift, weak timing rationale, and bridge-cadence gaps already surfaced upstream
