# 11.1 Findings Matrix - C1-M1-PRES-ADHOC-20260330

Status: completed-for-story-11-1
Date: 2026-03-30
Owner: Epic 11 / Story 11.1
Approval: accepted for mitigation sequencing (11.2 -> 11.4)

## Purpose

Convert trial evidence into stable finding IDs that drive mitigation implementation in Stories 11.2-11.4 while preserving proven success behavior.

## Findings

| finding_id | type | severity | evidence_path | expected_behavior | actual_behavior | owner | linked_story | status |
|---|---|---|---|---|---|---|---|---|
| F11-001 | gap | critical | course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/irene-pass2-handoff-prompt.md | Pass 2 handoff includes perception artifacts as canonical grounding input | Handoff references gary_slide_output but not perception_artifacts | Marcus/Irene pipeline | 11.3 | mitigated-in-11.3 |
| F11-002 | gap | high | course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/gary-dispatch-result.json | Gary outbound result contains required contract metadata fields | quality_assessment/parameter_decisions/recommendations/flags absent | Gary pipeline | 11.2 | mitigated-in-11.2 |
| F11-003 | gap | medium | course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/gary-dispatch-result.json | visual_description fields contain resolved context values | visual_description contains pending export placeholders | Gary pipeline | 11.2 | mitigated-in-11.2 |
| F11-004 | gap | high | docs/trial-run-prompts-to-irene-pass2-v2.md | Theme and mapped parameter set are explicitly confirmed and logged pre-dispatch | Trial behavior previously allowed dispatch without explicit theme handshake | Marcus/Gary pipeline | 11.4 | mitigated-in-11.4 |
| F11-005 | gap | medium | state/ and skills/reports/ run-id scans | Run-specific formal quality/fidelity review artifact exists for run traceability | No run-specific artifact found for run ID in expected review locations | QA/Fidelity lane | 11.2 | mitigated-in-11.2 |
| S11-001 | strength | n/a | course-content/staging/ad-hoc/source-bundles/apc-c1m1-tejal-20260329/gary-dispatch-run-log.json | Mixed-fidelity generation and export succeed with mapped card sequence | Verified successful generation_ids, calls_made, and card coverage | preserve | 11.2,11.3,11.4 | preserve |

## Requirement Link Matrix

| requirement_id | requirement | source_findings | target_story | verification |
|---|---|---|---|---|
| R11-2-A | Enforce required Gary outbound fields with blocking validation | F11-002 | 11.2 | T11-2-01, T11-2-02 |
| R11-2-B | Improve descriptive field completeness and review trace output | F11-003, F11-005 | 11.2 | T11-2-03, T11-2-04 |
| R11-3-A | Require perception artifacts before Irene Pass 2 delegation | F11-001 | 11.3 | T11-3-01, T11-3-02 |
| R11-4-A | Enforce user-confirmed theme to parameter mapping gate | F11-004 | 11.4 | T11-4-01, T11-4-02, T11-4-03 |
| R11-P-A | Preserve mixed-fidelity success path and card mapping | S11-001 | 11.2,11.3,11.4 | T11-2-05, T11-3-04, T11-4-05 |

## Sign-Off

- Due-diligence sequencing gate: PASSED
- Finding-ID traceability gate: PASSED
- Ready to proceed to Story 11.2: YES
