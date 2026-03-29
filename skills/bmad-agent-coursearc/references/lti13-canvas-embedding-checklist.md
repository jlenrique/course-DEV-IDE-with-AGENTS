# LTI 1.3 Canvas Embedding Checklist (CourseArc)

Reference documentation:

- Canvas LTI services: https://canvas.instructure.com/doc/api/lti_advantage_services.html
- IMS LTI 1.3 core spec: https://www.imsglobal.org/spec/lti/v1p3/

1. Confirm Canvas developer key and deployment records exist for LTI 1.3.
2. Confirm CourseArc tool configuration values (issuer, client ID, JWKS URL, launch URL, redirect URL).
3. Verify OIDC login initiation succeeds from Canvas test shell.
4. Validate deep-link content selection workflow for instructor role.
5. Validate learner launch path from module placement.
6. Verify role mapping for instructor, TA, and learner identities.
7. Confirm grade passback expectation (if enabled) and fallback behavior when unavailable.
8. Record placement strategy (module page link, assignment launch, or external tool menu).
9. Capture launch evidence: timestamp, test user role, result, and any remediation applied.
10. Record final launch URLs and handoff notes for production placement.

Companion guide:

- Use lti-role-mapping-and-grading.md for role-code mapping and grade passback decision logic.
