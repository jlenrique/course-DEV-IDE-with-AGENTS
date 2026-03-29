---
name: canvas-deployment
description: Canvas deployment orchestration and verification layer. Use when the user asks to publish to Canvas, verify module structure, or run accessibility-gated LMS deployment.
---

# Canvas Deployment

## Purpose

Provides deterministic Canvas deployment operations for the Canvas specialist (Deployment Director). This skill orchestrates the shared `CanvasClient` from the repository API client module `scripts.api_clients.canvas_client`, performs accessibility pre-checks, executes module/content publishing, verifies structure, and returns confirmation URLs.

## Key Paths

| Path | Purpose |
|---|---|
| `./references/deployment-workflows.md` | Content-type workflow patterns for pages, quizzes, discussions, assignments, and modules |
| `./references/institutional-requirements.md` | Compliance and policy requirements for Canvas deployment |
| `./references/token-management.md` | Credential and token-scope handling guidance |
| `./scripts/canvas_operations.py` | Deployment engine: validate -> accessibility gate -> publish -> verify -> rollback |

## Script Index

| Script | Purpose | Invoked By |
|---|---|---|
| `canvas_operations.py` | Manifest validation, accessibility pre-check, Canvas creation calls, module verification, rollback, confirmation URL output | `skills/bmad-agent-marcus/references/specialist-registry.yaml` entry `canvas-specialist` |

## Deployment Output Contract

`canvas_operations.py` returns structured JSON with:
- `status`: `deployed | warning | blocked | failed | dry-run`
- `course_id`
- `accessibility`
- `module_structure_verification`
- `confirmation_urls`
- `created`
- `warnings`
- `errors`

## Accessibility Gate

All publish operations run a pre-deployment accessibility scan over content bodies (pages, assignment descriptions, discussion prompts). If any critical findings are detected, status is `blocked` and no publish calls execute.

## Verification

Post-deployment verification confirms expected module names exist in Canvas and reports missing or out-of-order structures. Confirmation URLs are always returned for instructor review.
