"""Unit tests for the Qualtrics woodshed snapshot helper."""

from __future__ import annotations

from scripts.api_clients import qualtrics_client as module


class _HappyClient:
    def whoami(self):
        return {"userId": "UR_123", "userName": "qa-user"}

    def list_surveys(self, page_size: int = 100):
        return [
            {"id": "SV_1", "name": "Survey One"},
            {"SurveyID": "SV_2", "SurveyName": "Survey Two"},
        ]


class _FailingClient:
    def whoami(self):
        raise RuntimeError("auth failed")


class _MalformedWhoamiClient:
    def whoami(self):
        return "unexpected"

    def list_surveys(self, page_size: int = 100):
        return [{"id": "SV_1", "name": "Survey One"}]


def test_reproduce_survey_snapshot_returns_summary(monkeypatch) -> None:
    monkeypatch.setattr(module, "QualtricsClient", lambda: _HappyClient())

    result = module.reproduce_survey_snapshot(page_size=3)

    assert result["status"] == "ok"
    assert result["user"]["id"] == "UR_123"
    assert result["survey_count"] == 2
    assert result["sample_surveys"][0]["id"] == "SV_1"


def test_reproduce_survey_snapshot_rejects_bad_page_size() -> None:
    result = module.reproduce_survey_snapshot(page_size=0)

    assert result["status"] == "error"
    assert "page_size" in result["reason"]


def test_reproduce_survey_snapshot_rejects_boolean_page_size() -> None:
    result = module.reproduce_survey_snapshot(page_size=True)

    assert result["status"] == "error"
    assert "page_size" in result["reason"]


def test_reproduce_survey_snapshot_handles_api_error(monkeypatch) -> None:
    monkeypatch.setattr(module, "QualtricsClient", lambda: _FailingClient())

    result = module.reproduce_survey_snapshot(page_size=2)

    assert result["status"] == "error"
    assert "auth failed" in result["reason"]


def test_reproduce_survey_snapshot_handles_malformed_whoami(monkeypatch) -> None:
    monkeypatch.setattr(module, "QualtricsClient", lambda: _MalformedWhoamiClient())

    result = module.reproduce_survey_snapshot(page_size=2)

    assert result["status"] == "error"
    assert "whoami" in result["reason"]
