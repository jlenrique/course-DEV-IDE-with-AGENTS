# CourseArc SCORM Packaging Specs

Reference documentation:

- SCORM technical reference: https://scorm.com/scorm-explained/technical-scorm-standard/
- ADL resources: https://adlnet.gov/projects/scorm/

- Target version: SCORM 2004 4th Edition unless institution requires SCORM 1.2.
- Package includes launchable index and valid imsmanifest.xml.
- imsmanifest.xml includes organization/item/resource mappings and schema metadata.
- Manifest namespaces are valid and aligned with target SCORM version.
- Package naming convention includes course/module/version.
- Media assets are compressed without breaking accessibility alternatives.
- Include completion and score behavior notes in deployment handoff.
- Validate import in Canvas test shell before production deployment.

Completion and score expectations:

- Document expected cmi.completion_status transitions.
- Document score behavior and pass threshold when scoring is enabled.

Required verification evidence:

- Import result screenshot or log from Canvas test shell.
- Completion tracking behavior observed (complete/incomplete transitions).
- Score behavior notes (if scoring is enabled).
- List of known limitations or remediation items before production release.
