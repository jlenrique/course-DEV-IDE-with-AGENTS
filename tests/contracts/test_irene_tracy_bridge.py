import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

sys.path.insert(0, ".")

tracy_scripts_path = Path(__file__).parent.parent.parent / "skills" / "bmad_agent_tracy" / "scripts"
if str(tracy_scripts_path) not in sys.path:
    sys.path.insert(0, str(tracy_scripts_path))

from irene_bridge import IreneTracyBridge  # noqa: E402


class TestIreneTracyBridge:
    @pytest.fixture
    def mock_dispatcher(self):
        dispatcher = Mock()
        dispatcher.select_posture.return_value = {"status": "success"}
        return dispatcher

    @pytest.fixture
    def bridge(self, mock_dispatcher):
        return IreneTracyBridge(mock_dispatcher)

    def test_process_plan_locked_auto_dispatches_in_scope_gaps(self, bridge, mock_dispatcher):
        lesson_plan = {
            "units": [
                {
                    "id": "unit_1",
                    "scope_decision": "in-scope",
                    "identified_gaps": [{"type": "enrichment", "description": "Need examples"}],
                }
            ]
        }
        results = bridge.process_plan_locked(lesson_plan)
        assert len(results) == 1
        assert results[0] == {"status": "success"}
        mock_dispatcher.select_posture.assert_called_once()
        brief = mock_dispatcher.select_posture.call_args[0][0]
        assert brief["gap_type"] == "enrichment"
        assert brief["scope_decision"] == "in-scope"
        assert brief["target_element"] == "unit_1"
        assert brief["evidence_bolster"] is False

    def test_process_plan_locked_propagates_evidence_bolster_flag(self, bridge, mock_dispatcher):
        lesson_plan = {
            "evidence_bolster": True,
            "units": [
                {
                    "id": "unit_1",
                    "scope_decision": "in-scope",
                    "identified_gaps": [{"type": "evidence", "description": "Need source check"}],
                }
            ],
        }

        results = bridge.process_plan_locked(lesson_plan)

        assert len(results) == 1
        brief = mock_dispatcher.select_posture.call_args[0][0]
        assert brief["evidence_bolster"] is True

    def test_process_plan_locked_skips_out_of_scope_units(self, bridge, mock_dispatcher):
        lesson_plan = {
            "units": [
                {
                    "id": "unit_1",
                    "scope_decision": "out-of-scope",
                    "identified_gaps": [{"type": "enrichment", "description": "Need examples"}],
                }
            ]
        }
        results = bridge.process_plan_locked(lesson_plan)
        assert len(results) == 0
        mock_dispatcher.select_posture.assert_not_called()

    def test_process_plan_locked_handles_empty_plan(self, bridge, mock_dispatcher):
        lesson_plan = {}
        results = bridge.process_plan_locked(lesson_plan)
        assert len(results) == 0
        mock_dispatcher.select_posture.assert_not_called()

    def test_process_plan_locked_handles_multiple_gaps(self, bridge, mock_dispatcher):
        lesson_plan = {
            "units": [
                {
                    "id": "unit_1",
                    "scope_decision": "in-scope",
                    "identified_gaps": [{"type": "enrichment"}, {"type": "evidence"}],
                }
            ]
        }
        results = bridge.process_plan_locked(lesson_plan)
        assert len(results) == 2
        assert mock_dispatcher.select_posture.call_count == 2

    def test_process_dials_dispatches_endorsed(self, bridge, mock_dispatcher):
        plan_unit = {
            "id": "unit_2",
            "scope_decision": "in-scope",
            "dials": {
                "enrich": {"endorsed": True},
                "corroborate": {"endorsed": False},
                "gap_fill": {},
            },
        }
        results = bridge.process_dials(plan_unit)
        assert len(results) == 1
        mock_dispatcher.select_posture.assert_called_once()
        brief = mock_dispatcher.select_posture.call_args[0][0]
        assert brief["dial"] == "enrich"

    def test_process_dials_skips_unendorsed(self, bridge, mock_dispatcher):
        plan_unit = {"dials": {"enrich": {"endorsed": False}}}
        results = bridge.process_dials(plan_unit)
        assert len(results) == 0
        mock_dispatcher.select_posture.assert_not_called()

    def test_process_dials_catches_dispatcher_error(self, bridge, mock_dispatcher):
        mock_dispatcher.select_posture.side_effect = ValueError("Mock failure")
        plan_unit = {"dials": {"corroborate": {"endorsed": True}}}
        results = bridge.process_dials(plan_unit)
        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert results[0]["reason"] == "Mock failure"
        assert results[0]["dial"] == "corroborate"

    def test_process_plan_locked_catches_dispatcher_error(self, bridge, mock_dispatcher):
        mock_dispatcher.select_posture.side_effect = Exception("General failure")
        lesson_plan = {
            "units": [
                {
                    "id": "unit_1",
                    "scope_decision": "in-scope",
                    "identified_gaps": [{"type": "enrichment"}],
                }
            ]
        }
        results = bridge.process_plan_locked(lesson_plan)
        assert len(results) == 1
        assert results[0]["status"] == "failed"
        assert results[0]["reason"] == "General failure"
        assert "gap" in results[0]
