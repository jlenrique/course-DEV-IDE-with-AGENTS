"""JSON-RPC response envelope builders for MCP client tests — AC-T.6.

Per Murat green-light strengthening: wrap mocked `responses` library calls
in these builders so tests assert against the JSON-RPC envelope shape, not
raw dict literals. Keeps test intent readable.
"""

from typing import Any


def jsonrpc_response(
    *, result: dict[str, Any], request_id: str = "test-req"
) -> dict[str, Any]:
    """Build a well-formed JSON-RPC 2.0 success envelope."""
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def jsonrpc_error(
    *,
    code: int,
    message: str,
    data: dict[str, Any] | None = None,
    request_id: str = "test-req",
) -> dict[str, Any]:
    """Build a well-formed JSON-RPC 2.0 error envelope."""
    err: dict[str, Any] = {"code": code, "message": message}
    if data is not None:
        err["data"] = data
    return {"jsonrpc": "2.0", "id": request_id, "error": err}


__all__ = ["jsonrpc_error", "jsonrpc_response"]
