# Accessibility Standards — WCAG 2.1 AA for Educational Content

Checklist for automated and judgment-based accessibility review of medical education artifacts.

## Automated Checks (accessibility_checker.py)

### Reading Level
- Target: Grade 12 or below for resident/student audiences; Grade 14 acceptable for attending physician content (calibratable)
- Metric: Flesch-Kincaid Grade Level
- Finding severity: Medium (above target by 1-2 grades), High (above by 3+)

### Heading Hierarchy
- Rule: H1 → H2 → H3 → H4, no level skips (H2 → H4 without H3 = violation)
- Finding severity: Critical (heading skip creates navigation barrier)

### Alt Text
- Rule: Every image placeholder or visual reference must have descriptive alt text
- Check: Scan for image references without `alt=` or `[alt:` annotations
- Finding severity: Critical (missing alt text is WCAG Level A violation)

### Text Length / Density
- Rule: No single content block exceeds cognitive load guidelines (>200 words without a break)
- Finding severity: Medium

## Judgment-Based Checks (Quinn-R)

### Color Contrast
- WCAG 2.1 AA requires 4.5:1 contrast ratio for normal text, 3:1 for large text
- Agent reviews color references in slide briefs against style bible palette
- Finding severity: Critical

### Language Clarity
- Plain language principles for target audience
- Medical jargon appropriate for audience level (physicians vs. students)
- Finding severity: Medium

### Navigability
- Logical content flow supports assistive technology navigation
- Table of contents / section structure present in long-form artifacts
- Finding severity: High
