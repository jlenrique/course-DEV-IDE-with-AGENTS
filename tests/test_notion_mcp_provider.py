"""Tests for the Notion MCP fetch-layer provider (Story 27-5).

Dependency injection: tests substitute a `FakeNotionMCPFetcher` for the
production fetcher. In live runs, Marcus resolves the Notion page via the
project-scope stdio Notion MCP server and injects a concrete fetcher.

Coverage (meets K>=12 target range 12-15 per green-light Amelia rider):
  1. Happy path — project-scope fetch returns (title, body, SourceRecord)
  2. Provenance — SourceRecord kind='notion_mcp_page' carries scope +
     last_edited_time + parent_path enrichment
  3. Scope mismatch — user-scope result with expected='project' raises
     NotionMCPAuthError (Amelia scope-binding rider)
  4. Permission-denied — NotionMCPPermissionError remediation text walks
     the operator through the Notion UI verbatim (Sally UX rider — the
     Tejal-trial 2026-04-17 blocker)
  5. Permission-denied — remediation names 'Connections' + 'Add connections'
     + 'Re-run' literally
  6. Not-found — NotionMCPNotFoundError surfaces typed
  7. Auth-failure — NotionMCPAuthError surfaces typed
  8. Page title surfaces from fetcher result unchanged (no transformation)
  9. Body markdown preserved verbatim (no mid-transform mutation)
 10. No-silent-empty-return: fetcher raising MUST propagate, NOT silently
     return '[]' or empty string (Murat rider — silent-degradation is the
     nightmare on MCP auth)
 11. AST portability guard — no marcus.orchestrator / marcus.dispatch
     imports in provider code
 12. Legacy 'notion' direct-api path still exists and is distinct (no
     import collision or code-reuse that would reintroduce NotionClient
     into the MCP path)
"""

from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent
_SWO_PATH = (
    _ROOT / "skills" / "bmad-agent-texas" / "scripts" / "source_wrangler_operations.py"
)
_spec = importlib.util.spec_from_file_location(
    "texas_source_wrangler_operations_notion_mcp_tests", _SWO_PATH
)
assert _spec is not None and _spec.loader is not None
sop = importlib.util.module_from_spec(_spec)
sys.modules["texas_source_wrangler_operations_notion_mcp_tests"] = sop
_spec.loader.exec_module(sop)


# ---------------------------------------------------------------------------
# Fake fetcher fixtures
# ---------------------------------------------------------------------------


class FakeNotionMCPFetcher(sop.NotionMCPFetcher):
    """Pre-scripted NotionMCPFetcher for unit tests."""

    def __init__(
        self,
        *,
        page_id: str = "abc123",
        page_title: str = "Test Page",
        markdown_body: str = "# Test Page\n\nBody content.\n",
        scope: str = "project",
        error: Exception | None = None,
    ) -> None:
        self.page_id = page_id
        self.page_title = page_title
        self.markdown_body = markdown_body
        self.scope = scope
        self.error = error
        self.last_called_with: str | None = None

    def fetch_page(self, page_locator: str) -> sop.NotionFetchResult:
        self.last_called_with = page_locator
        if self.error is not None:
            raise self.error
        return sop.NotionFetchResult(
            page_id=self.page_id,
            page_title=self.page_title,
            markdown_body=self.markdown_body,
            scope=self.scope,
            last_edited_time="2026-04-20T12:00:00Z",
            last_edited_by="sme@example.com",
            parent_path="/Cardiac Evaluation",
        )


# ---------------------------------------------------------------------------
# Happy-path + provenance tests
# ---------------------------------------------------------------------------


def test_notion_mcp_happy_path_returns_title_body_record() -> None:
    fetcher = FakeNotionMCPFetcher(
        page_title="Cardiac Evaluation",
        markdown_body="# Cardiac Evaluation\n\nStep 1: auscultation.\n",
    )

    title, body, rec = sop.wrangle_notion_mcp_page("abc123", fetcher=fetcher)

    assert title == "Cardiac Evaluation"
    assert "Step 1: auscultation" in body
    assert rec.kind == "notion_mcp_page"
    assert rec.ref == "notion_mcp://abc123"
    assert fetcher.last_called_with == "abc123"


def test_notion_mcp_provenance_carries_scope_and_metadata() -> None:
    fetcher = FakeNotionMCPFetcher(page_id="page-XYZ")

    _, _, rec = sop.wrangle_notion_mcp_page("page-XYZ", fetcher=fetcher)

    assert "page_id=page-XYZ" in rec.note
    assert "scope=project" in rec.note
    assert "last_edited_time=2026-04-20T12:00:00Z" in rec.note
    assert "last_edited_by=sme@example.com" in rec.note
    assert "parent_path=/Cardiac Evaluation" in rec.note


# ---------------------------------------------------------------------------
# Scope-binding (Amelia rider + user memory)
# ---------------------------------------------------------------------------


def test_notion_mcp_user_scope_rejected_when_project_expected() -> None:
    fetcher = FakeNotionMCPFetcher(scope="user")

    with pytest.raises(sop.NotionMCPAuthError) as exc_info:
        sop.wrangle_notion_mcp_page("abc", fetcher=fetcher)

    msg = str(exc_info.value)
    assert "scope mismatch" in msg
    assert "'project'" in msg
    assert "'user'" in msg
    assert "Texas-headless" in msg


def test_notion_mcp_user_scope_accepted_when_user_expected() -> None:
    """Scope binding honors caller intent — explicit expected_scope='user' is valid."""
    fetcher = FakeNotionMCPFetcher(scope="user")

    title, _, _ = sop.wrangle_notion_mcp_page(
        "abc", fetcher=fetcher, expected_scope="user"
    )
    assert title == "Test Page"


# ---------------------------------------------------------------------------
# Permission-denied remediation (Sally UX rider — the Tejal-trial case)
# ---------------------------------------------------------------------------


def test_notion_mcp_permission_remediation_walks_ui_steps_verbatim() -> None:
    """Sally non-negotiable: remediation text is the deliverable.

    We assert the exact strings the operator must see to recover from the
    Tejal-trial 2026-04-17 blocker. Any edit to the template must update
    this test — that is the whole point.
    """
    remediation = sop._notion_mcp_permission_remediation(
        page_title="Cardiac Evaluation", page_id="abc123"
    )
    # Operator-facing instructions — literal substrings
    assert "Cardiac Evaluation" in remediation
    assert "abc123" in remediation
    assert "project-scope Notion integration" in remediation
    assert "Texas-headless" in remediation
    assert "Connections" in remediation
    assert "Add connections" in remediation
    assert "Re-run" in remediation
    # The three-dots menu mention — any reasonable glyph acceptable
    assert "..." in remediation or "•••" in remediation
    # Disambiguation with user-scope (Tracy-IDE) path
    assert "Tracy-IDE" in remediation


def test_notion_mcp_permission_error_carries_remediation() -> None:
    remediation = sop._notion_mcp_permission_remediation("Page X", "id-X")
    err = sop.NotionMCPPermissionError(
        "page not shared", remediation=remediation
    )
    s = str(err)
    assert "page not shared" in s
    assert "Page X" in s
    assert "Connections" in s


def test_notion_mcp_permission_integration_name_defaults_are_substitutable() -> None:
    """Integration-name placeholder substitutes cleanly when provided."""
    remediation = sop._notion_mcp_permission_remediation(
        "Page Y",
        "id-Y",
        integration_name="Marcus-Texas-Integration",
    )
    assert "Marcus-Texas-Integration" in remediation
    # Default placeholder does NOT appear when explicit integration supplied
    assert "[your project-scope integration]" not in remediation


# ---------------------------------------------------------------------------
# Error-taxonomy tests (Murat rider — distinct error classes for diagnosability)
# ---------------------------------------------------------------------------


def test_notion_mcp_not_found_surfaces_typed() -> None:
    fetcher = FakeNotionMCPFetcher(
        error=sop.NotionMCPNotFoundError("page abc not found"),
    )
    with pytest.raises(sop.NotionMCPNotFoundError):
        sop.wrangle_notion_mcp_page("abc", fetcher=fetcher)


def test_notion_mcp_auth_failure_surfaces_typed() -> None:
    fetcher = FakeNotionMCPFetcher(
        error=sop.NotionMCPAuthError("MCP integration token missing"),
    )
    with pytest.raises(sop.NotionMCPAuthError):
        sop.wrangle_notion_mcp_page("abc", fetcher=fetcher)


def test_notion_mcp_fetcher_error_propagates_never_returns_empty() -> None:
    """Murat rider (non-negotiable): silent-degradation on MCP auth is the
    nightmare — downstream specialists plan against empty retrievals and
    nobody notices until production. A fetcher failure MUST propagate.
    """
    fetcher = FakeNotionMCPFetcher(
        error=sop.NotionMCPPermissionError(
            "integration not granted",
            remediation=sop._notion_mcp_permission_remediation("X", "id"),
        ),
    )
    with pytest.raises(sop.NotionMCPPermissionError):
        sop.wrangle_notion_mcp_page("id", fetcher=fetcher)
    # If we reached this point, the error propagated — not silently
    # returning an empty list or empty markdown body.


# ---------------------------------------------------------------------------
# Content preservation
# ---------------------------------------------------------------------------


def test_notion_mcp_body_markdown_preserved_verbatim() -> None:
    body = "# Heading\n\n- item 1\n- item 2\n\n**Bold** text.\n"
    fetcher = FakeNotionMCPFetcher(markdown_body=body)

    _, out_body, _ = sop.wrangle_notion_mcp_page("abc", fetcher=fetcher)

    assert out_body == body


# ---------------------------------------------------------------------------
# AST portability guard (Sprint 2 LangGraph rider)
# ---------------------------------------------------------------------------


def test_notion_mcp_provider_has_no_marcus_orchestrator_imports() -> None:
    """Provider code (source_wrangler_operations.py as host) must not
    import marcus.orchestrator.* or marcus.dispatch.* — leaf IO adapter
    discipline per Sprint 2 LangGraph-portability rulings.
    """
    src_path = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "bmad-agent-texas"
        / "scripts"
        / "source_wrangler_operations.py"
    )
    tree = ast.parse(src_path.read_text(encoding="utf-8"))
    forbidden_prefixes = ("marcus.orchestrator", "marcus.dispatch")
    offenders: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(alias.name.startswith(p) for p in forbidden_prefixes):
                    offenders.append(alias.name)
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if any(mod.startswith(p) for p in forbidden_prefixes):
                offenders.append(mod)
    assert not offenders, (
        f"source_wrangler_operations.py (host of notion_mcp provider) imports "
        f"forbidden orchestrator/dispatch modules: {offenders}. "
        f"Notion MCP provider must remain a leaf IO adapter."
    )


# ---------------------------------------------------------------------------
# Legacy vs MCP disjointness
# ---------------------------------------------------------------------------


def test_legacy_notion_and_notion_mcp_providers_are_disjoint() -> None:
    """Legacy `wrangle_notion_page` uses NotionClient (REST); new
    `wrangle_notion_mcp_page` does not. A regression where the MCP path
    accidentally imports NotionClient would reintroduce the coupling
    Story 27-5 is meant to avoid.
    """
    src_path = (
        Path(__file__).resolve().parent.parent
        / "skills"
        / "bmad-agent-texas"
        / "scripts"
        / "source_wrangler_operations.py"
    )
    src = src_path.read_text(encoding="utf-8")
    # NotionClient is legitimately imported at module top for the legacy
    # `wrangle_notion_page`. What we're regression-guarding is that the
    # MCP function body does not reference it.
    #
    # Find the span from 'def wrangle_notion_mcp_page' to the next top-level
    # 'def ' and assert NotionClient does not appear in that span.
    start = src.find("def wrangle_notion_mcp_page(")
    assert start != -1, "wrangle_notion_mcp_page function not found"
    # Next top-level def ('def ' at column 0)
    after = src[start + 1 :]
    next_def = after.find("\ndef ")
    end = start + 1 + next_def if next_def != -1 else len(src)
    mcp_fn_body = src[start:end]
    assert "NotionClient" not in mcp_fn_body, (
        "wrangle_notion_mcp_page body references NotionClient — that would "
        "couple the MCP path back to the legacy REST client. Keep them "
        "disjoint per Story 27-5."
    )
    # Sanity: the legacy function DOES reference NotionClient somewhere
    assert "NotionClient" in src
