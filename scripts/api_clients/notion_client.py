"""Notion REST API client for Source Wrangler (Story 3.9).

Retrieves page metadata, walks block trees, exports simplified markdown,
and appends feedback blocks. Uses Notion-Version 2022-06-28.
"""

from __future__ import annotations

import os
from typing import Any

from scripts.api_clients.base_client import BaseAPIClient

NOTION_VERSION = "2022-06-28"


def _rich_text(block_type: str, block: dict[str, Any]) -> str:
    inner = block.get(block_type)
    if not isinstance(inner, dict):
        return ""
    parts: list[str] = []
    for seg in inner.get("rich_text", []) or []:
        parts.append(seg.get("plain_text", ""))
    return "".join(parts).strip()


def _block_to_lines(block: dict[str, Any]) -> list[str]:
    btype = block.get("type")
    if not btype:
        return []
    lines: list[str] = []
    text = _rich_text(btype, block)
    if btype == "paragraph":
        if text:
            lines.append(text)
    elif btype == "heading_1":
        lines.append(f"# {text}")
    elif btype == "heading_2":
        lines.append(f"## {text}")
    elif btype == "heading_3":
        lines.append(f"### {text}")
    elif btype in ("bulleted_list_item", "numbered_list_item", "to_do"):
        prefix = "- " if btype == "bulleted_list_item" else "1. "
        if text:
            lines.append(f"{prefix}{text}")
    elif btype == "quote":
        if text:
            lines.append(f"> {text}")
    elif btype == "code":
        lang = block.get("code", {}).get("language", "")
        if text:
            lines.append(f"```{lang}\n{text}\n```")
    elif btype == "divider":
        lines.append("---")
    elif btype == "callout" and text:
        lines.append(f"**Callout:** {text}")
    return lines


class NotionClient(BaseAPIClient):
    """Authenticated client for Notion API v1."""

    def __init__(
        self,
        api_key: str | None = None,
        timeout: int = 60,
        max_retries: int = 3,
    ) -> None:
        key = api_key or os.environ.get("NOTION_API_KEY", "")
        super().__init__(
            base_url="https://api.notion.com/v1",
            auth_header="Authorization",
            auth_prefix="Bearer",
            api_key=key or None,
            timeout=timeout,
            max_retries=max_retries,
            default_headers={"Notion-Version": NOTION_VERSION},
        )

    def retrieve_page(self, page_id: str) -> dict[str, Any]:
        """GET /pages/{page_id}."""
        return self.get(f"pages/{page_id.strip()}")

    def search_pages(self, query: str, page_size: int = 10) -> list[dict[str, Any]]:
        """POST /search for pages matching query text."""
        body: dict[str, Any] = {
            "query": query,
            "page_size": min(page_size, 100),
            "filter": {"property": "object", "value": "page"},
        }
        data = self.post("search", json=body)
        return list(data.get("results", []))

    def list_block_children_page(
        self, block_id: str, page_size: int = 100, start_cursor: str | None = None
    ) -> dict[str, Any]:
        """GET /blocks/{id}/children (one page)."""
        params: dict[str, Any] = {"page_size": page_size}
        if start_cursor:
            params["start_cursor"] = start_cursor
        return self.get(f"blocks/{block_id.strip()}/children", params=params)

    def iter_block_children(self, block_id: str) -> Any:
        """Yield all direct children of a block (paginated)."""
        cursor: str | None = None
        while True:
            data = self.list_block_children_page(block_id, start_cursor=cursor)
            yield from data.get("results", [])
            if not data.get("has_more"):
                break
            cursor = data.get("next_cursor")
            if not cursor:
                break

    def walk_blocks_depth_first(self, root_block_id: str) -> Any:
        """Depth-first traversal including nested children."""

        def walk(bid: str) -> Any:
            for block in self.iter_block_children(bid):
                yield block
                if block.get("has_children"):
                    yield from walk(block["id"])

        yield from walk(root_block_id)

    def page_title(self, page: dict[str, Any]) -> str:
        """Best-effort title from page properties (title property)."""
        props = page.get("properties", {})
        for _key, val in props.items():
            if val.get("type") == "title":
                title_parts: list[str] = []
                for seg in val.get("title", []) or []:
                    title_parts.append(seg.get("plain_text", ""))
                t = "".join(title_parts).strip()
                if t:
                    return t
        return "Untitled"

    def page_to_markdown(self, page_id: str) -> tuple[str, str]:
        """Return (title, markdown_body) for page content (block tree)."""
        page = self.retrieve_page(page_id)
        title = self.page_title(page)
        lines: list[str] = [f"# {title}", ""]
        for block in self.walk_blocks_depth_first(page_id.strip()):
            lines.extend(_block_to_lines(block))
        body = "\n".join(lines).strip() + "\n"
        return title, body

    def append_paragraphs(self, block_id: str, paragraphs: list[str]) -> dict[str, Any]:
        """Append child blocks (paragraphs) to a page or block."""
        children: list[dict[str, Any]] = []
        for para in paragraphs:
            if not para.strip():
                continue
            children.append(
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": para[:2000]},
                            }
                        ]
                    },
                }
            )
        if not children:
            return {}
        return self.patch(
            f"blocks/{block_id.strip()}/children",
            json={"children": children[:100]},
        )
