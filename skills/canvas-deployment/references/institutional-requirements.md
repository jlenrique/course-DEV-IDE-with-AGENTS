# Institutional Requirements — Canvas Deployment

## Policy Baseline

1. Accessibility compliance is required before publish.
2. Module structure must support predictable learner navigation.
3. Grading-critical assets must include verifiable points/submission metadata.
4. Deployment must produce confirmation URLs for instructor verification.
5. API token usage must remain within approved scope and tenancy.

## Compliance Enforcement Points

| Requirement | Enforcement Point | Failure Behavior |
|---|---|---|
| Accessibility pre-check | Before first Canvas write call | Block deployment (`status: blocked`) |
| Course targeting clarity | Course ID resolution step | Block deployment if unresolved |
| Module ordering integrity | Post-deployment structure verification | `status: warning` with missing/out-of-order modules |
| Grading metadata | Assignment validation before create | Block assignment creation for invalid graded payload |
| Token/policy hygiene | Credential load + self-check call | `status: failed` with auth/scope guidance |

## Recommended Operational Controls

- Maintain a dedicated Canvas sandbox course for rehearsal runs.
- Keep deployment manifests under version control with run IDs.
- Require human checkpoint on confirmation URLs before learner release.
- Record recurring failures in sidecar `patterns.md`.

## Escalation Triggers

Escalate to Marcus or LMS admin when:
- Authentication fails repeatedly (possible token revocation/scope drift).
- Accessibility checker blocks content repeatedly for the same pattern.
- Module verification reports missing structures after successful API responses.
- Rollback fails partially and leaves orphaned entities.
