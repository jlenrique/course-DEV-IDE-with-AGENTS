# Story 5.4: Remaining Tier 2 API Integrations (Botpress, Wondercraft)

Epic: 5 - Tool Capability Expansion
Status: done
Sprint key: 5-4-remaining-tier2-api-integrations
Completed: 2026-03-30

## Summary

Closed Story 5.4 by validating and hardening the Botpress and Wondercraft Tier 2 API clients, confirming integration-test connectivity gates, and extending unit coverage for core capability paths (conversation/NLU/deployment and podcast/scripted voice payload paths).

## Deliverables

- Existing API clients validated and hardened:
  - scripts/api_clients/botpress_client.py
  - scripts/api_clients/wondercraft_client.py
- Small hardening fix:
  - Wondercraft base URL normalization now guarantees /v1 suffix parity with Botpress behavior
- Unit tests expanded:
  - tests/test_botpress_client.py
  - tests/test_wondercraft_client.py
- Existing live integration coverage retained:
  - tests/test_integration_botpress.py
  - tests/test_integration_wondercraft.py
- Existing heartbeat verification path retained:
  - scripts/heartbeat_check.mjs

## Acceptance Criteria Trace

- AC1: Botpress client with conversation management, NLU, and deployment capabilities.
  - Satisfied by create_conversation(), send_message(), detect_intent(), and deploy_bot().
- AC2: Wondercraft client with podcast generation, voice synthesis, and episode management capabilities.
  - Satisfied by list_episodes(), create_podcast(), create_scripted_podcast(), create_conversation_podcast(), and async job polling.
- AC3: Both clients extend BaseAPIClient with retry/pagination/error handling.
  - Satisfied through BaseAPIClient inheritance and shared HTTP request pipeline.
- AC4: Integration tests verify API connectivity.
  - Satisfied by env-gated live tests for Botpress and Wondercraft connectivity checks.

## Validation

- pytest tests/test_botpress_client.py tests/test_wondercraft_client.py
  - Result: pass (11 tests total in combined targeted Story 5.4 + G.2 + 10.1 run)
- Existing live integration tests remain available and env-gated:
  - tests/test_integration_botpress.py
  - tests/test_integration_wondercraft.py

## Adversarial Review and Remediation

- Finding: Wondercraft client accepted custom base URLs without enforcing /v1 suffix, causing endpoint drift risk.
  - Remediation: normalized custom/default base URL to always end with /v1.
- Finding: Core payload contracts for Botpress send-message and intent-detection and Wondercraft scripted podcast paths lacked explicit unit assertions.
  - Remediation: added payload-contract tests for those paths.

## Completion Notes

Story 5.4 is complete. Epic 5 is now fully complete in sprint tracking.
