from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest
from pydantic import ValidationError

from marcus.irene.intake import (
    CONVERGENCE_NARRATION_PATTERNS,
    ConvergenceSignal,
    apply_corroborate_intake,
    parse_irene_retrieval_intake,
    resolve_convergence_narration,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SCHEMA_PATH = (
    _REPO_ROOT / "state" / "config" / "schemas" / "irene-retrieval-intake.schema.json"
)


def _valid_intake_payload() -> dict:
    return {
        "run_id": "RUN-INTAKE-001",
        "pass_2_cluster_id": "c-u01",
        "suggested_resources_ref": "run-records/RUN-INTAKE-001/suggested-resources.yaml",
        "extraction_report_ref": "run-records/RUN-INTAKE-001/extraction-report.yaml",
        "intake_mode": "corroborate",
        "evidence_bolster_active": True,
    }


def _corroborate_result() -> list[dict]:
    return [
        {
            "query_id": "q-1",
            "status": "success",
            "output": {
                "posture": "corroborate",
                "evidence_found": True,
                "sources": ["scite:support-101"],
            },
        }
    ]


def test_intake_payload_matches_schema_contract() -> None:
    schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
    payload = _valid_intake_payload()
    jsonschema.validate(payload, schema)

    intake = parse_irene_retrieval_intake(payload)
    assert intake.intake_mode == "corroborate"
    assert intake.evidence_bolster_active is True


def test_intake_model_is_frozen() -> None:
    intake = parse_irene_retrieval_intake(_valid_intake_payload())
    with pytest.raises(ValidationError):
        intake.run_id = "mutated"


@pytest.mark.parametrize(
    "signal,expected",
    [
        (
            ConvergenceSignal(
                providers_agreeing=["scite", "consensus"],
                providers_disagreeing=[],
                single_source_only=[],
            ),
            CONVERGENCE_NARRATION_PATTERNS["dual_scite_consensus"],
        ),
        (
            ConvergenceSignal(
                providers_agreeing=["scite"],
                providers_disagreeing=[],
                single_source_only=["scite"],
            ),
            CONVERGENCE_NARRATION_PATTERNS["single_scite"],
        ),
        (
            ConvergenceSignal(
                providers_agreeing=["consensus"],
                providers_disagreeing=[],
                single_source_only=["consensus"],
            ),
            CONVERGENCE_NARRATION_PATTERNS["single_consensus"],
        ),
        (None, CONVERGENCE_NARRATION_PATTERNS["fallback"]),
    ],
)
def test_convergence_mapping(signal, expected) -> None:
    phrase = resolve_convergence_narration(signal, evidence_bolster_active=True)
    assert phrase == expected


def test_convergence_mapping_unknown_partial_uses_fallback_when_bolster_inactive() -> None:
    signal = ConvergenceSignal(
        providers_agreeing=["scite"],
        providers_disagreeing=["consensus"],
        single_source_only=[],
    )

    phrase = resolve_convergence_narration(signal, evidence_bolster_active=False)
    assert phrase == CONVERGENCE_NARRATION_PATTERNS["single_scite"]


def test_convergence_mapping_dual_source_uses_single_source_when_bolster_inactive() -> None:
    signal = ConvergenceSignal(
        providers_agreeing=["scite", "consensus"],
        providers_disagreeing=[],
        single_source_only=[],
    )

    phrase = resolve_convergence_narration(signal, evidence_bolster_active=False)
    assert phrase == CONVERGENCE_NARRATION_PATTERNS["single_scite"]


def test_intake_rejects_windows_drive_relative_refs() -> None:
    payload = _valid_intake_payload()
    payload["suggested_resources_ref"] = "C:temp/suggested-resources.yaml"

    with pytest.raises(ValidationError):
        parse_irene_retrieval_intake(payload)


def test_corroborate_intake_uses_dual_source_language_when_available() -> None:
    intake = parse_irene_retrieval_intake(_valid_intake_payload())
    extraction_report = {
        "schema_version": "1.1",
        "sources": [
            {
                "source_id": "scite:support-101",
                "provider": "scite",
                "retrieval_intent": "sleep hygiene studies",
                "convergence_signal": {
                    "providers_agreeing": ["scite", "consensus"],
                    "providers_disagreeing": [],
                    "single_source_only": [],
                },
            }
        ],
    }

    decision = apply_corroborate_intake(
        intake,
        suggested_resources=_corroborate_result(),
        extraction_report=extraction_report,
    )

    assert decision.include_retrieval_segment is True
    assert decision.narration_attribution == CONVERGENCE_NARRATION_PATTERNS[
        "dual_scite_consensus"
    ]
    assert len(decision.retrieval_provenance) == 1
    assert decision.retrieval_provenance[0].source_id == "scite:support-101"


def test_corroborate_intake_degrades_gracefully_on_empty_retrieval() -> None:
    intake = parse_irene_retrieval_intake(_valid_intake_payload())
    decision = apply_corroborate_intake(
        intake,
        suggested_resources=_corroborate_result(),
        extraction_report={"schema_version": "1.1", "sources": []},
    )

    assert decision.include_retrieval_segment is False
    assert decision.narration_attribution is None
    assert decision.retrieval_provenance == ()
    assert decision.known_losses == ("retrieval_empty_for_cluster_c-u01",)


def test_corroborate_intake_degrades_when_no_corroborate_posture_exists() -> None:
    intake = parse_irene_retrieval_intake(_valid_intake_payload())
    decision = apply_corroborate_intake(
        intake,
        suggested_resources=[{"output": {"posture": "embellish", "evidence_found": True}}],
        extraction_report={
            "schema_version": "1.1",
            "sources": [
                {
                    "source_id": "scite:support-101",
                    "provider": "scite",
                }
            ],
        },
    )

    assert decision.include_retrieval_segment is False
    assert decision.known_losses == ("retrieval_empty_for_cluster_c-u01",)


def test_corroborate_intake_degrades_on_malformed_extraction_payload() -> None:
    intake = parse_irene_retrieval_intake(_valid_intake_payload())
    decision = apply_corroborate_intake(
        intake,
        suggested_resources=_corroborate_result(),
        extraction_report={"schema_version": "1.1", "sources": "malformed"},
    )

    assert decision.include_retrieval_segment is False
    assert decision.known_losses == ("retrieval_empty_for_cluster_c-u01",)


def test_corroborate_intake_degrades_on_timeout_style_error_rows() -> None:
    intake = parse_irene_retrieval_intake(_valid_intake_payload())
    decision = apply_corroborate_intake(
        intake,
        suggested_resources=_corroborate_result(),
        extraction_report={
            "schema_version": "1.1",
            "sources": [
                {
                    "ref_id": "src-retrieval-1",
                    "error_kind": "timeout",
                    "error_detail": "provider timed out",
                    "retrieval_intent": "sleep hygiene studies",
                }
            ],
        },
    )

    assert decision.include_retrieval_segment is False
    assert decision.known_losses == ("retrieval_empty_for_cluster_c-u01",)


def test_corroborate_intake_handles_malformed_convergence_payload_without_crash() -> None:
    intake = parse_irene_retrieval_intake(_valid_intake_payload())
    decision = apply_corroborate_intake(
        intake,
        suggested_resources=_corroborate_result(),
        extraction_report={
            "schema_version": "1.1",
            "sources": [
                {
                    "source_id": "scite:support-101",
                    "provider": "scite",
                    "convergence_signal": {
                        "providers_agreeing": "invalid",
                        "providers_disagreeing": [],
                        "single_source_only": [],
                    },
                }
            ],
        },
    )

    assert decision.include_retrieval_segment is True
    assert decision.narration_attribution == CONVERGENCE_NARRATION_PATTERNS["fallback"]
