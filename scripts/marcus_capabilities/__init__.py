"""Marcus production-readiness capabilities.

Four capability codes registered in Marcus's sanctum (see
``skills/bmad-agent-marcus/capabilities/``):

- **PR-PF** — Preflight (full): wraps ``app_session_readiness --with-preflight``
- **PR-RC** — Run-Constants author + validate (full): wraps ``run_constants``
- **PR-HC** — Health Check (stub): follow-up in story 26-10
- **PR-RS** — Run Selection (stub): follow-up in story 26-10

All four follow the pinned invocation + return envelope contracts from
Story 26-6 (see ``_bmad-output/implementation-artifacts/26-6-*.md`` AC-C.1/C.2).

Scripts are invoked via ``python -m scripts.marcus_capabilities.<code_slug>``.
The sanctum markdown files at ``skills/bmad-agent-marcus/capabilities/<slug>.md``
are authoritative for capability doctrine; the YAML registry is a fast
programmatic index and the schemas validate envelope args/results.
"""

from scripts.marcus_capabilities.registry import CAPABILITY_REGISTRY, UnknownCapability

__all__ = ["CAPABILITY_REGISTRY", "UnknownCapability"]
