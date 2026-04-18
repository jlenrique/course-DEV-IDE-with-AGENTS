"""AC-T.6 — Python MCP client mocked-HTTP tests.

Uses `responses` library (dev-dep added in 27-0). Per Murat strengthening:
timeout test is mocked at the `requests` layer — no real short-timeout
sleeps, no CI-load flakiness. JSON-RPC envelopes built via helpers in
`tests._helpers.mcp_fixtures` so the envelope shape is asserted structurally.
"""

from __future__ import annotations

import pytest
import responses
from retrieval import (
    MCPAuthError,
    MCPClient,
    MCPFetchError,
    MCPProtocolError,
    MCPRateLimitError,
    MCPServerConfig,
)

from tests._helpers.mcp_fixtures import jsonrpc_error, jsonrpc_response

URL = "https://api.scite.ai/mcp"


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> MCPClient:
    monkeypatch.setenv("SCITE_USER_NAME", "alice")
    monkeypatch.setenv("SCITE_PASSWORD", "secret")
    return MCPClient(
        {
            "scite": MCPServerConfig(
                url=URL,
                auth_env=["SCITE_USER_NAME", "SCITE_PASSWORD"],
            )
        }
    )


def test_mcp_client_auth_header_construction(client: MCPClient) -> None:
    """AC-T.6: Authorization header is HTTP Basic from env vars."""
    with responses.RequestsMock() as rsps:
        rsps.post(URL, json=jsonrpc_response(result={"ok": True}))
        client.call_tool("scite", "any", {})
        assert len(rsps.calls) == 1
        auth = rsps.calls[0].request.headers.get("Authorization", "")
        assert auth.startswith("Basic "), f"Expected Basic auth header; got {auth!r}"


def test_mcp_client_jsonrpc_envelope_parse(client: MCPClient) -> None:
    """Happy path — result dict is returned verbatim."""
    with responses.RequestsMock() as rsps:
        rsps.post(URL, json=jsonrpc_response(result={"citation_count": 42}))
        result = client.call_tool("scite", "get_citations", {"doi": "10.1/x"})
        assert result == {"citation_count": 42}


def test_mcp_client_401_maps_to_mcp_auth_error(client: MCPClient) -> None:
    with responses.RequestsMock() as rsps:
        rsps.post(URL, status=401, body="unauthorized")
        with pytest.raises(MCPAuthError):
            client.call_tool("scite", "t", {})


def test_mcp_client_429_maps_to_mcp_rate_limit_error(client: MCPClient) -> None:
    with responses.RequestsMock() as rsps:
        rsps.post(URL, status=429, body="rate limited")
        with pytest.raises(MCPRateLimitError):
            client.call_tool("scite", "t", {})


def test_mcp_client_5xx_maps_to_mcp_fetch_error(client: MCPClient) -> None:
    with responses.RequestsMock() as rsps:
        rsps.post(URL, status=500, body="boom")
        with pytest.raises(MCPFetchError):
            client.call_tool("scite", "t", {})


def test_mcp_client_timeout_maps_to_mcp_fetch_error(client: MCPClient) -> None:
    """Mocked at the requests layer — no real timeout sleeps."""
    import requests as _r

    with responses.RequestsMock() as rsps:
        def _raise_timeout(request):
            raise _r.Timeout("simulated")

        rsps.add_callback(responses.POST, URL, callback=_raise_timeout)
        with pytest.raises(MCPFetchError, match="timed out"):
            client.call_tool("scite", "t", {})


def test_mcp_client_jsonrpc_error_envelope_maps_to_protocol_error(
    client: MCPClient,
) -> None:
    """JSON-RPC error envelope (not HTTP error) → MCPProtocolError."""
    with responses.RequestsMock() as rsps:
        rsps.post(URL, json=jsonrpc_error(code=-32602, message="invalid params"))
        with pytest.raises(MCPProtocolError, match="-32602"):
            client.call_tool("scite", "t", {})


def test_mcp_client_missing_credentials_raises_auth_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Missing env vars → MCPAuthError at lazy-resolve time (not at construction)."""
    monkeypatch.delenv("SCITE_USER_NAME", raising=False)
    monkeypatch.delenv("SCITE_PASSWORD", raising=False)
    client = MCPClient(
        {
            "scite": MCPServerConfig(
                url=URL, auth_env=["SCITE_USER_NAME", "SCITE_PASSWORD"]
            )
        }
    )
    with (
        responses.RequestsMock(assert_all_requests_are_fired=False),
        pytest.raises(MCPAuthError, match="unset"),
    ):
        client.call_tool("scite", "t", {})


def test_mcp_client_list_tools_returns_tools_array(client: MCPClient) -> None:
    with responses.RequestsMock() as rsps:
        rsps.post(
            URL,
            json=jsonrpc_response(
                result={"tools": [{"name": "search"}, {"name": "get_doi"}]}
            ),
        )
        tools = client.list_tools("scite")
        assert [t["name"] for t in tools] == ["search", "get_doi"]
