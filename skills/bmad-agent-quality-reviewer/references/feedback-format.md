# Feedback Format

Structured quality report template for all review outputs.

## Report Structure

Every quality report follows this structure, organized by dimension (not severity):

```
## Quality Review Report

**Run ID:** {production_run_id}
**Artifact:** {artifact_path}
**Type:** {content_type}
**Producing Specialist:** {specialist_name}
**Review Date:** {date}
**Review Mode:** {default | ad-hoc}

### Verdict

**Overall:** {PASS | PASS WITH NOTES | FAIL | PARTIAL REVIEW}
**Confidence:** {0.0 - 1.0}

### Dimension Scores

| Dimension | Result | Score | Findings |
|-----------|--------|-------|----------|
| Brand Consistency | {PASS/FAIL} | {0.0-1.0} | {count} |
| Accessibility | {PASS/FAIL} | {0.0-1.0} | {count} |
| Learning Alignment | {PASS/FAIL} | {0.0-1.0} | {count} |
| Instructional Soundness | {PASS/FAIL} | {0.0-1.0} | {count} |
| Content Accuracy | {PASS/FLAGGED/N/A} | — | {count} |

### Critical Summary

{One-line descriptions of all critical and high findings for Marcus to relay to the user}

### Findings by Dimension

#### Brand Consistency
{findings list}

#### Accessibility
{findings list}

#### Learning Objective Alignment
{findings list}

#### Instructional Soundness
{findings list}

#### Content Accuracy Flags
{escalation items for human review}

### Calibration Notes
{Any severity adjustments made based on learned preferences}

### Pattern Alerts
{Recurring issues detected — for upstream improvement}
```

## Finding Format

Every individual finding follows this structure:

```
**[{SEVERITY}]** {one-line description}
- **Location:** {specific artifact location — file, slide, line, heading}
- **Dimension:** {brand | accessibility | alignment | soundness | accuracy}
- **Description:** {what is wrong and why it matters}
- **Fix Suggestion:** {specific, actionable fix the specialist can implement immediately}
- **Calibration:** {if severity was adjusted from default, note the adjustment and source}
```

## Severity Definitions

| Severity | Meaning | Action Required | Examples |
|----------|---------|----------------|----------|
| **Critical** | Blocks publication | Must fix before human review | WCAG violation, medical accuracy flag |
| **High** | Significant quality gap | Should fix before human review | Brand violation, learning objective misalignment |
| **Medium** | Improvement opportunity | Recommended fix, not blocking | Content density optimization, tone adjustment |
| **Low** | Minor polish | Optional fix | Typo, formatting inconsistency |
| **Critical-escalation** | Requires human judgment | Route through Marcus to human | Potential medical inaccuracy, clinical concern |

## Score Calculation

Dimension scores (0.0 - 1.0) are calculated as:
- Start at 1.0
- Each critical finding: -0.3
- Each high finding: -0.15
- Each medium finding: -0.05
- Each low finding: -0.02
- Floor at 0.0

**Pass threshold** (from `state/config/tool_policies.yaml` or defaults):
- Brand: 0.7
- Accessibility: 1.0 (zero critical findings required)
- Learning Alignment: 0.8
- Instructional Soundness: 0.7

**Overall verdict:**
- PASS: all dimensions pass
- PASS WITH NOTES: all dimensions pass but medium/low findings exist
- FAIL: any dimension below threshold
- PARTIAL REVIEW: one or more dimensions skipped due to missing references
