"""Tests for validate-cluster-plan.py (G1.5 gate).

Covers:
- Happy path: valid clustered manifest passes all criteria
- G1.5-01: broken parent_slide_id reference
- G1.5-02: invalid interstitial_type vocabulary
- G1.5-03: empty isolation_target
- G1.5-04: invalid narration_burden value
- G1.5-05: missing narrative_arc on head
- G1.5-06: develop-position missing develop_type
- G1.5-07: redundant develop_type within a cluster
- G1.5-08: interstitial with double_dispatch_eligible == true
- G1.5-09: cluster_interstitial_count out of bounds
- G1.5-10: cluster count outside density target
- G1.5-11: head segment with non-establish cluster_position
- G1.5-12: non-clustered segment with cluster metadata leaked
- G1.5-13: clustered manifest with omitted cluster_density
- Regression: non-clustered manifest (cluster_density: none) passes cleanly
"""

from __future__ import annotations

import json
from importlib import util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "validate-cluster-plan.py"


def _load_module():
    spec = util.spec_from_file_location("validate_cluster_plan", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


mod = _load_module()
validate_cluster_plan = mod.validate_cluster_plan
ClusterPlanError = mod.ClusterPlanError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _head(
    slide_id: str,
    cluster_id: str,
    *,
    narrative_arc: str = "From confusion to clarity through progressive disclosure",
    master_behavioral_intent: str = "credible",
    cluster_interstitial_count: int = 2,
    double_dispatch_eligible: bool = True,
) -> dict:
    return {
        "slide_id": slide_id,
        "cluster_id": cluster_id,
        "cluster_role": "head",
        "cluster_position": "establish",
        "develop_type": None,
        "parent_slide_id": None,
        "interstitial_type": None,
        "isolation_target": None,
        "narration_burden": None,
        "narrative_arc": narrative_arc,
        "master_behavioral_intent": master_behavioral_intent,
        "cluster_interstitial_count": cluster_interstitial_count,
        "double_dispatch_eligible": double_dispatch_eligible,
    }


def _interstitial(
    slide_id: str,
    cluster_id: str,
    parent_slide_id: str,
    *,
    cluster_position: str = "develop",
    develop_type: str | None = "deepen",
    interstitial_type: str = "reveal",
    isolation_target: str = "the central diagram",
    narration_burden: str = "low",
    double_dispatch_eligible: bool = False,
) -> dict:
    return {
        "slide_id": slide_id,
        "cluster_id": cluster_id,
        "cluster_role": "interstitial",
        "cluster_position": cluster_position,
        "develop_type": develop_type,
        "parent_slide_id": parent_slide_id,
        "interstitial_type": interstitial_type,
        "isolation_target": isolation_target,
        "narration_burden": narration_burden,
        "narrative_arc": None,
        "master_behavioral_intent": None,
        "cluster_interstitial_count": None,
        "double_dispatch_eligible": double_dispatch_eligible,
    }


def _flat(slide_id: str) -> dict:
    """Non-clustered segment — all cluster fields null."""
    return {
        "slide_id": slide_id,
        "cluster_id": None,
        "cluster_role": None,
        "cluster_position": None,
        "develop_type": None,
        "parent_slide_id": None,
        "interstitial_type": None,
        "isolation_target": None,
        "narration_burden": None,
        "narrative_arc": None,
        "master_behavioral_intent": None,
        "cluster_interstitial_count": None,
        "double_dispatch_eligible": True,
    }


def _valid_manifest(cluster_density: str = "sparse") -> dict:
    """One cluster (head + 2 interstitials), one flat slide."""
    return {
        "cluster_density": cluster_density,
        "segments": [
            _head("s1", "c1", cluster_interstitial_count=2),
            _interstitial("s2", "c1", "s1", cluster_position="develop", develop_type="deepen"),
            _interstitial("s3", "c1", "s1", cluster_position="resolve", develop_type=None),
            _flat("s4"),
        ],
    }


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_manifest_passes() -> None:
    result = validate_cluster_plan(_valid_manifest())
    assert result["passed"] is True
    assert result["errors"] == []


def test_non_clustered_manifest_passes() -> None:
    manifest = {
        "cluster_density": "none",
        "segments": [_flat("s1"), _flat("s2"), _flat("s3")],
    }
    result = validate_cluster_plan(manifest)
    assert result["passed"] is True


# ---------------------------------------------------------------------------
# G1.5-01: broken parent_slide_id
# ---------------------------------------------------------------------------

def test_broken_parent_slide_id_fails() -> None:
    m = _valid_manifest()
    m["segments"][1]["parent_slide_id"] = "nonexistent"
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-01" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-02: invalid interstitial_type
# ---------------------------------------------------------------------------

def test_invalid_interstitial_type_fails() -> None:
    m = _valid_manifest()
    m["segments"][1]["interstitial_type"] = "isolate"  # old vocabulary
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-02" in e for e in result["errors"])


def test_valid_interstitial_types_pass() -> None:
    for itype in ("reveal", "emphasis-shift", "bridge-text", "simplification", "pace-reset"):
        m = _valid_manifest()
        m["segments"][1]["interstitial_type"] = itype
        result = validate_cluster_plan(m)
        assert result["passed"] is True, f"Expected pass for type={itype}, got errors: {result['errors']}"


# ---------------------------------------------------------------------------
# G1.5-03: empty isolation_target
# ---------------------------------------------------------------------------

def test_empty_isolation_target_fails() -> None:
    m = _valid_manifest()
    m["segments"][1]["isolation_target"] = ""
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-03" in e for e in result["errors"])


def test_null_isolation_target_fails() -> None:
    m = _valid_manifest()
    m["segments"][1]["isolation_target"] = None
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-03" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-04: invalid narration_burden
# ---------------------------------------------------------------------------

def test_invalid_narration_burden_fails() -> None:
    m = _valid_manifest()
    m["segments"][1]["narration_burden"] = "very-high"
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-04" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-05: missing narrative_arc on head
# ---------------------------------------------------------------------------

def test_missing_narrative_arc_on_head_fails() -> None:
    m = _valid_manifest()
    m["segments"][0]["narrative_arc"] = None
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-05" in e for e in result["errors"])


def test_empty_narrative_arc_on_head_fails() -> None:
    m = _valid_manifest()
    m["segments"][0]["narrative_arc"] = ""
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-05" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-06: develop-position missing develop_type
# ---------------------------------------------------------------------------

def test_develop_position_missing_develop_type_fails() -> None:
    m = _valid_manifest()
    m["segments"][1]["develop_type"] = None  # cluster_position is develop
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-06" in e for e in result["errors"])


def test_develop_type_invalid_value_fails() -> None:
    m = _valid_manifest()
    m["segments"][1]["develop_type"] = "expand"  # not a valid sub-type
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-06" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-07: redundant develop_type within a cluster
# ---------------------------------------------------------------------------

def test_redundant_develop_type_fails() -> None:
    m = {
        "cluster_density": "sparse",
        "segments": [
            _head("s1", "c1", cluster_interstitial_count=2),
            _interstitial("s2", "c1", "s1", cluster_position="develop", develop_type="deepen"),
            _interstitial("s3", "c1", "s1", cluster_position="develop", develop_type="deepen"),
        ],
    }
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-07" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-08: interstitial with double_dispatch_eligible == true
# ---------------------------------------------------------------------------

def test_interstitial_double_dispatch_true_fails() -> None:
    m = _valid_manifest()
    m["segments"][1]["double_dispatch_eligible"] = True
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-08" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-09: cluster_interstitial_count out of bounds
# ---------------------------------------------------------------------------

def test_cluster_interstitial_count_zero_fails() -> None:
    m = _valid_manifest()
    m["segments"][0]["cluster_interstitial_count"] = 0
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-09" in e for e in result["errors"])


def test_cluster_interstitial_count_four_fails() -> None:
    m = _valid_manifest()
    m["segments"][0]["cluster_interstitial_count"] = 4
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-09" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-10: cluster count outside density target
# ---------------------------------------------------------------------------

def test_cluster_count_exceeds_sparse_fails() -> None:
    # sparse = 1-2 clusters; give it 3
    m = {
        "cluster_density": "sparse",
        "segments": [
            _head("s1", "c1"), _interstitial("s2", "c1", "s1", cluster_position="resolve", develop_type=None),
            _head("s3", "c2"), _interstitial("s4", "c2", "s3", cluster_position="resolve", develop_type=None),
            _head("s5", "c3"), _interstitial("s6", "c3", "s5", cluster_position="resolve", develop_type=None),
        ],
    }
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-10" in e for e in result["errors"])


def test_cluster_count_zero_with_default_density_fails() -> None:
    # default = 3-5 clusters; give it 0
    m = {
        "cluster_density": "default",
        "segments": [_flat("s1"), _flat("s2")],
    }
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-10" in e for e in result["errors"])


def test_cluster_density_none_with_zero_clusters_passes() -> None:
    m = {
        "cluster_density": "none",
        "segments": [_flat("s1"), _flat("s2")],
    }
    result = validate_cluster_plan(m)
    assert result["passed"] is True


# ---------------------------------------------------------------------------
# G1.5-11: head segment with non-establish cluster_position
# ---------------------------------------------------------------------------

def test_head_with_non_establish_position_fails() -> None:
    m = _valid_manifest()
    m["segments"][0]["cluster_position"] = "develop"
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-11" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-12: non-clustered segment with cluster metadata leaked
# ---------------------------------------------------------------------------

def test_flat_segment_with_leaked_cluster_id_fails() -> None:
    m = _valid_manifest()
    m["segments"][3]["cluster_id"] = "c1"  # flat segment getting cluster_id
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-12" in e for e in result["errors"])


def test_flat_segment_with_leaked_narrative_arc_fails() -> None:
    m = _valid_manifest()
    m["segments"][3]["narrative_arc"] = "some arc"
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-12" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-13: master_behavioral_intent required on heads
# ---------------------------------------------------------------------------

def test_missing_master_behavioral_intent_fails() -> None:
    m = _valid_manifest()
    m["segments"][0]["master_behavioral_intent"] = None
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-14" in e for e in result["errors"])


def test_empty_master_behavioral_intent_fails() -> None:
    m = _valid_manifest()
    m["segments"][0]["master_behavioral_intent"] = ""
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-14" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-13: clustered manifest with omitted cluster_density
# ---------------------------------------------------------------------------

def test_clustered_manifest_with_omitted_cluster_density_fails() -> None:
    m = _valid_manifest()
    m["cluster_density"] = None  # omit cluster_density
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-13" in e for e in result["errors"])


# ---------------------------------------------------------------------------
# G1.5-09 hardened: actual interstitial count must match declared count
# ---------------------------------------------------------------------------

def test_actual_count_mismatch_fails() -> None:
    # Head declares cluster_interstitial_count=2 but only 1 interstitial in manifest
    m = {
        "cluster_density": "sparse",
        "segments": [
            _head("s1", "c1", cluster_interstitial_count=2),
            _interstitial("s2", "c1", "s1", cluster_position="resolve", develop_type=None),
        ],
    }
    result = validate_cluster_plan(m)
    assert result["passed"] is False
    assert any("G1.5-09" in e for e in result["errors"])
