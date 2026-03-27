"""Unit tests for NotionClient (mocked HTTP)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from scripts.api_clients.notion_client import NotionClient, _block_to_lines


def test_block_to_lines_paragraph() -> None:
    block = {
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{"plain_text": "Hello", "type": "text"}],
        },
    }
    assert _block_to_lines(block) == ["Hello"]


def test_page_title_from_properties() -> None:
    client = NotionClient(api_key="secret_test")
    page = {
        "properties": {
            "Name": {
                "type": "title",
                "title": [{"plain_text": "My Page", "type": "text"}],
            }
        }
    }
    assert client.page_title(page) == "My Page"


@patch.object(NotionClient, "get")
def test_page_to_markdown(mock_get: MagicMock) -> None:
    client = NotionClient(api_key="secret_test")

    def get_side_effect(endpoint: str, **kwargs: object) -> dict:
        if endpoint.startswith("pages/"):
            return {
                "properties": {
                    "title": {
                        "type": "title",
                        "title": [{"plain_text": "T1", "type": "text"}],
                    }
                }
            }
        if endpoint.startswith("blocks/page-1/children"):
            return {
                "results": [
                    {
                        "id": "b1",
                        "type": "paragraph",
                        "has_children": False,
                        "paragraph": {
                            "rich_text": [{"plain_text": "Line", "type": "text"}],
                        },
                    }
                ],
                "has_more": False,
            }
        return {}

    mock_get.side_effect = get_side_effect
    title, body = client.page_to_markdown("page-1")
    assert title == "T1"
    assert "Line" in body
    assert "# T1" in body
