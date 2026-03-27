# Quality Standards

Review dimensions, severity levels, and pass/fail thresholds for all production artifacts.

## Dimensions

| Dimension | Default Severity | Pass Threshold | Automated Script |
|-----------|-----------------|----------------|-----------------|
| Brand Consistency | High | 0.7 | `brand_validator.py` |
| Accessibility (WCAG 2.1 AA) | Critical | 1.0 (zero critical) | `accessibility_checker.py` |
| Learning Objective Alignment | High | 0.8 | None (judgment) |
| Instructional Soundness | Medium-High | 0.7 | None (judgment) |
| Content Accuracy | Critical-escalation | N/A (human) | None (escalation) |

## Severity Levels

| Severity | Impact | Action |
|----------|--------|--------|
| Critical | Blocks publication | Must fix before any review |
| High | Significant gap | Should fix before human review |
| Medium | Improvement opportunity | Recommended, not blocking |
| Low | Minor polish | Optional |
| Critical-escalation | Requires human judgment | Route through Marcus |

## Score Calculation

Start at 1.0 per dimension. Deductions: critical -0.3, high -0.15, medium -0.05, low -0.02. Floor at 0.0.

## Overall Verdict

- **PASS**: all dimensions meet threshold
- **PASS WITH NOTES**: all pass but medium/low findings exist
- **FAIL**: any dimension below threshold
- **PARTIAL REVIEW**: dimension(s) skipped due to missing references
