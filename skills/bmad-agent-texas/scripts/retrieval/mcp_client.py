"""Hand-rolled JSON-RPC-over-HTTP MCP client — Option Y (Story 27-0).

Green-light round 1 (2026-04-17) unanimous: avoid the pre-1.0 `mcp` PyPI
package. Use JSON-RPC 2.0 (frozen since 2010) directly over `requests`
(mature). Future Option-X migration is a single-file swap because this
module exposes a **library-agnostic public surface**:

    call_tool(server, tool, args) -> dict
    list_tools(server) -> list[dict]

No `requests.Response` leaks to callers. No `mcp` types on the API. This
keeps adapters (27-2 scite, 27-2.5 Consensus, future HTTP-MCP providers)
independent of the transport.

Auth is HTTP Basic by default (scite pattern: `SCITE_USER_NAME` +
`SCITE_PASSWORD` → base64 Authorization header). Per-server config
overrides the default.

Error taxonomy (AC-T.6):
  - 401 / 403 → `MCPAuthError`
  - 429 → `MCPRateLimitError`
  - 5xx / timeout / connection error → `MCPFetchError`
  - JSON-RPC error envelope (`result.error`) → `MCPProtocolError`
"""

import base64
import json
import os
import uuid
from dataclasses import dataclass, field
from typing import Any

import requests


class MCPClientError(RuntimeError):
    """Base for all MCP client errors."""


class MCPAuthError(MCPClientError):
    """401 / 403 from the MCP server."""


class MCPRateLimitError(MCPClientError):
    """429 from the MCP server."""


class MCPFetchError(MCPClientError):
    """5xx / timeout / connection / unparseable response."""


class MCPProtocolError(MCPClientError):
    """JSON-RPC envelope carried an `error` member."""


@dataclass(frozen=True)
class MCPServerConfig:
    """Per-server connection config.

    `url` is the remote MCP endpoint (full URL, including path). `auth_env`
    lists env var names this server's credentials live in. `auth_style`
    selects how we transform those env vars into the `Authorization` header
    — `"basic"` (default) expects a pair `[user_env, password_env]`;
    `"bearer"` expects a single `[token_env]`.
    """

    url: str
    auth_env: list[str] = field(default_factory=list)
    auth_style: str = "basic"
    timeout_seconds: float = 30.0
    headers: dict[str, str] = field(default_factory=dict)


class MCPClient:
    """Library-agnostic MCP client — the narrow surface future Option X replaces.

    Instances are stateless apart from the shared `requests.Session`; safe
    to reuse across dispatch cycles. Tests construct an instance with an
    explicit `MCPServerConfig` and mock `requests` via the `responses`
    library.
    """

    def __init__(self, servers: dict[str, MCPServerConfig] | None = None) -> None:
        self._servers: dict[str, MCPServerConfig] = dict(servers or {})
        self._session = requests.Session()

    def register_server(self, name: str, config: MCPServerConfig) -> None:
        self._servers[name] = config

    def call_tool(
        self, server: str, tool: str, args: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """JSON-RPC `tools/call` against `server`. Returns the `result` payload."""
        config = self._require_server(server)
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/call",
            "params": {"name": tool, "arguments": dict(args or {})},
        }
        return self._post(server, config, payload)

    def list_tools(self, server: str) -> list[dict[str, Any]]:
        """JSON-RPC `tools/list`. Returns the `tools` array from the result."""
        config = self._require_server(server)
        payload = {
            "jsonrpc": "2.0",
            "id": str(uuid.uuid4()),
            "method": "tools/list",
            "params": {},
        }
        result = self._post(server, config, payload)
        tools = result.get("tools")
        if not isinstance(tools, list):
            raise MCPFetchError(
                f"{server!r} tools/list returned non-list 'tools' field: "
                f"{type(tools).__name__}"
            )
        return tools

    def _require_server(self, server: str) -> MCPServerConfig:
        if server not in self._servers:
            raise MCPFetchError(
                f"No MCP server registered under name {server!r}. "
                f"Register via MCPClient.register_server or pass to constructor."
            )
        return self._servers[server]

    def _post(
        self,
        server: str,
        config: MCPServerConfig,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **config.headers,
        }
        auth_header = _build_auth_header(config)
        if auth_header is not None:
            headers["Authorization"] = auth_header

        try:
            response = self._session.post(
                config.url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                timeout=config.timeout_seconds,
            )
        except requests.Timeout as exc:
            raise MCPFetchError(
                f"{server!r} request timed out after {config.timeout_seconds}s"
            ) from exc
        except requests.ConnectionError as exc:
            raise MCPFetchError(
                f"{server!r} connection error: {exc}"
            ) from exc
        except requests.RequestException as exc:
            raise MCPFetchError(
                f"{server!r} request failed: {exc}"
            ) from exc

        status = response.status_code
        if status in (401, 403):
            raise MCPAuthError(
                f"{server!r} auth failed with HTTP {status}: {response.text[:200]}"
            )
        if status == 429:
            raise MCPRateLimitError(
                f"{server!r} rate-limited with HTTP 429: {response.text[:200]}"
            )
        if status >= 500:
            raise MCPFetchError(
                f"{server!r} server error HTTP {status}: {response.text[:200]}"
            )
        if status >= 400:
            raise MCPFetchError(
                f"{server!r} unexpected HTTP {status}: {response.text[:200]}"
            )

        try:
            envelope = response.json()
        except ValueError as exc:
            raise MCPFetchError(
                f"{server!r} response not valid JSON: {response.text[:200]}"
            ) from exc

        if not isinstance(envelope, dict):
            raise MCPFetchError(
                f"{server!r} JSON-RPC envelope is not a dict: "
                f"{type(envelope).__name__}"
            )

        if "error" in envelope:
            err = envelope["error"] or {}
            code = err.get("code", "unknown")
            message = err.get("message", "")
            raise MCPProtocolError(
                f"{server!r} JSON-RPC error {code}: {message}"
            )

        if "result" not in envelope:
            raise MCPFetchError(
                f"{server!r} JSON-RPC envelope missing 'result' field"
            )
        result = envelope["result"]
        if not isinstance(result, dict):
            raise MCPFetchError(
                f"{server!r} JSON-RPC result is not a dict: "
                f"{type(result).__name__}"
            )
        return result


def _build_auth_header(config: MCPServerConfig) -> str | None:
    """Resolve env var references lazily; return the Authorization header value."""
    if not config.auth_env:
        return None
    if config.auth_style == "basic":
        if len(config.auth_env) != 2:
            raise MCPFetchError(
                f"auth_style='basic' requires exactly 2 auth_env entries "
                f"(user, password); got {len(config.auth_env)}"
            )
        user_env, pass_env = config.auth_env
        user = os.environ.get(user_env)
        password = os.environ.get(pass_env)
        if not user or not password:
            raise MCPAuthError(
                f"HTTP Basic auth requires env vars {user_env} + {pass_env}; "
                f"one or both are unset"
            )
        token = base64.b64encode(f"{user}:{password}".encode()).decode()
        return f"Basic {token}"
    if config.auth_style == "bearer":
        if len(config.auth_env) != 1:
            raise MCPFetchError(
                f"auth_style='bearer' requires exactly 1 auth_env entry; "
                f"got {len(config.auth_env)}"
            )
        (token_env,) = config.auth_env
        token = os.environ.get(token_env)
        if not token:
            raise MCPAuthError(
                f"Bearer auth requires env var {token_env}; unset"
            )
        return f"Bearer {token}"
    raise MCPFetchError(f"Unknown auth_style: {config.auth_style!r}")


__all__ = [
    "MCPAuthError",
    "MCPClient",
    "MCPClientError",
    "MCPFetchError",
    "MCPProtocolError",
    "MCPRateLimitError",
    "MCPServerConfig",
]
