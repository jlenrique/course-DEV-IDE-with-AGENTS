---
name: quality-control
description: Automated quality validation scripts for accessibility, brand compliance, and audit logging. Use when Quinn-R or Marcus needs deterministic quality checks on production artifacts.
---

# Quality Control

## Overview

This skill provides automated, deterministic quality checking for production artifacts. It is the companion skill to Quinn-R (Quality Guardian agent), handling checks that have clear pass/fail criteria: WCAG 2.1 AA accessibility scanning, style bible brand compliance, and SQLite audit trail logging. Quinn-R handles judgment-based review; this skill handles the scriptable parts.

Scripts are invoked by Quinn-R during quality gate reviews or by Marcus for pre-checkpoint validation. All scripts accept artifact content as input and return structured JSON results.

## Scripts

| Script | Purpose | Invoked By |
|--------|---------|------------|
| `./scripts/accessibility_checker.py` | WCAG 2.1 AA scanning: reading level, heading hierarchy, alt text | Quinn-R (CC capability) |
| `./scripts/brand_validator.py` | Style bible compliance: color codes, typography, voice markers | Quinn-R (BV capability) |
| `./scripts/quality_logger.py` | Log quality review results to SQLite `quality_gates` table | Quinn-R (after review) |

## References

| Reference | Purpose |
|-----------|---------|
| `./references/quality-standards.md` | Review dimensions, severity levels, pass/fail thresholds |
| `./references/accessibility-standards.md` | WCAG 2.1 AA checklist for educational content |
| `./references/brand-validation.md` | Style bible compliance rules and marker extraction |
