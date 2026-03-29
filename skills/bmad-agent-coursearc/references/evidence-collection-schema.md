# CourseArc Evidence Collection Schema

Use this schema to collect evidence before marking CourseArc tasks complete.

## Storage Convention

- Store evidence under `course-content/staging/{run_id}/coursearc-evidence/`.
- Include one evidence manifest file named `evidence-index.yaml`.

Run ID rules:

- Primary source: `run_id` from Marcus delegation envelope.
- Fallback when missing: `{course_code}-{module_id}-coursearc-{YYYYMMDD-HHMMSS}`.
- Record final run_id value in `evidence-index.yaml`.

## LTI Launch Evidence

Required fields:

- timestamp
- test_user_role
- launch_surface (module page, assignment, or external tool)
- launch_result (pass/fail)
- remediation_notes (if failed)

## SCORM Evidence

Required fields:

- import_timestamp
- package_name
- import_result (pass/fail)
- completion_behavior_verified (yes/no)
- score_behavior_documented (yes/no)

## WCAG Evidence

For each criterion row capture:

- criterion_code
- pass_fail
- evidence_path
- remediation_action

## Completion Rule

- Do not report `guidance-ready` completion unless all required evidence fields are present or blocked with explicit remediation items.

## evidence-index.yaml Template

```yaml
run_id: C1-M2-coursearc-20260329-153000
lti_evidence:
	timestamp: "2026-03-29T15:30:00Z"
	test_user_role: instructor
	launch_surface: module-page
	launch_result: pass
	remediation_notes: ""
scorm_evidence:
	import_timestamp: "2026-03-29T15:35:00Z"
	package_name: module2-interactive-v1
	import_result: pass
	completion_behavior_verified: yes
	score_behavior_documented: yes
wcag_evidence:
	- criterion_code: 2.1.1
		pass_fail: pass
		evidence_path: course-content/staging/C1-M2-coursearc-20260329-153000/coursearc-evidence/kbd-nav-check.png
		remediation_action: ""
```
