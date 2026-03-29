# SCORM Export Review Checklist

- Publish target selected (SCORM 1.2 or SCORM 2004 3rd/4th Edition as required).
- Completion tracking mode defined and tested (`passed/failed` versus `completed/incomplete`).
- `imsmanifest.xml` contains correct organization and resource mappings.
- Launch file path resolved from manifest and validated after zip/unzip.
- Suspend/resume flow verified for at least one partial-attempt learner path.
- Score and status reporting verified in LMS staging gradebook.
- Package tested in LMS staging before production upload with learner and instructor roles.
- Accessibility checks completed for keyboard navigation and transcripts.
- WCAG 2.1 AA checks verified using `wcag-2-1-aa-interactive-checklist.md`.

## Required Evidence Payload

- package_name and version
- publish target and tracking mode
- launch path validation result
- staging LMS test run references
- known limitations and remediation owner
