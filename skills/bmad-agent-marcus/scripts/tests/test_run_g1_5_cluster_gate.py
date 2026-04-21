"""Tests for run-g1.5-cluster-gate.py (G1.5 gate script).

Covers:
- Skip: cluster_density none/absent → no receipt, no review doc, exit 0
- Pass: valid manifest → receipt with status pass, review doc generated
- Fail: invalid manifest → receipt with status fail, errors present, exit 1
- Review doc: contains expected cluster/interstitial content
- Receipt: JSON with required fields
"""

from __future__ import annotations

import json
import subprocess
import sys
from importlib import util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[4]
SCRIPT_PATH = ROOT / "skills" / "bmad-agent-marcus" / "scripts" / "run-g1.5-cluster-gate.py"


def _load_module():
    import sys
    sys.path.insert(0, str(ROOT))
    spec = util.spec_from_file_location("run_g1_5_cluster_gate", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    mod = util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # Inject the imports that may not be available in the dynamic load
    from scripts.utilities.run_constants import RunConstantsError, load_run_constants
    mod.RunConstantsError = RunConstantsError
    mod.load_run_constants = load_run_constants
    return mod


mod = _load_module()
run_gate = mod.run_gate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_run_constants(bundle: Path, cluster_density: str | None = "sparse") -> None:
    data: dict = {
        "run_id": "T-GATE-001",
        "lesson_slug": "gate-test",
        "bundle_path": bundle.as_posix(),
        "primary_source_file": str(bundle / "source.pdf"),
        "optional_context_assets": [],
        "theme_selection": "theme-a",
        "theme_paramset_key": "preset-a",
        "execution_mode": "tracked/default",
        "quality_preset": "production",
    }
    if cluster_density is not None:
        data["cluster_density"] = cluster_density
    (bundle / "run-constants.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")


def _valid_manifest() -> dict:
    return {
        "cluster_density": "sparse",
        "segments": [
            {
                "slide_id": "s1",
                "cluster_id": "c1",
                "cluster_role": "head",
                "cluster_position": "establish",
                "develop_type": None,
                "parent_slide_id": None,
                "interstitial_type": None,
                "isolation_target": None,
                "narration_burden": None,
                "narrative_arc": "From confusion to clarity through progressive disclosure",
                "master_behavioral_intent": "credible",
                "cluster_interstitial_count": 1,
                "double_dispatch_eligible": True,
            },
            {
                "slide_id": "s2",
                "cluster_id": "c1",
                "cluster_role": "interstitial",
                "cluster_position": "resolve",
                "develop_type": None,
                "parent_slide_id": "s1",
                "interstitial_type": "reveal",
                "isolation_target": "the central workflow diagram",
                "narration_burden": "low",
                "narrative_arc": None,
                "master_behavioral_intent": None,
                "cluster_interstitial_count": None,
                "double_dispatch_eligible": False,
            },
        ],
    }


def _invalid_manifest() -> dict:
    m = _valid_manifest()
    m["segments"][1]["interstitial_type"] = "isolate"  # invalid vocab
    return m


# ---------------------------------------------------------------------------
# Skip: non-clustered run
# ---------------------------------------------------------------------------

def test_skip_when_cluster_density_none(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="none")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump({"cluster_density": "none", "segments": []}), encoding="utf-8"
    )

    result = run_gate(bundle_dir=bundle)
    assert result["skipped"] is True
    assert not (bundle / "g1.5-cluster-gate-receipt.json").exists()
    assert not (bundle / "cluster-plan-review.md").exists()


def test_skip_when_cluster_density_absent(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density=None)
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump({"segments": []}), encoding="utf-8"
    )

    result = run_gate(bundle_dir=bundle)
    assert result["skipped"] is True


# ---------------------------------------------------------------------------
# Pass: valid manifest
# ---------------------------------------------------------------------------

def test_pass_writes_receipt_with_status_pass(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump(_valid_manifest()), encoding="utf-8"
    )

    result = run_gate(bundle_dir=bundle)
    assert result["skipped"] is False
    assert result["passed"] is True
    assert result["errors"] == []

    receipt_path = bundle / "g1.5-cluster-gate-receipt.json"
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == "pass"
    assert receipt["cluster_count"] == 1
    assert receipt["errors"] == []
    assert "timestamp" in receipt


def test_pass_generates_review_doc(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump(_valid_manifest()), encoding="utf-8"
    )

    run_gate(bundle_dir=bundle)

    review_path = bundle / "cluster-plan-review.md"
    assert review_path.exists()
    content = review_path.read_text(encoding="utf-8")
    assert "Cluster Plan Review" in content
    assert "G1.5 Status" in content
    assert "c1" in content  # cluster ID present
    assert "From confusion to clarity" in content  # narrative arc
    assert "Operator Decision" in content


# ---------------------------------------------------------------------------
# Fail: invalid manifest
# ---------------------------------------------------------------------------

def test_fail_writes_receipt_with_status_fail(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump(_invalid_manifest()), encoding="utf-8"
    )

    result = run_gate(bundle_dir=bundle)
    assert result["skipped"] is False
    assert result["passed"] is False
    assert len(result["errors"]) > 0

    receipt_path = bundle / "g1.5-cluster-gate-receipt.json"
    assert receipt_path.exists()
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["status"] == "fail"
    assert len(receipt["errors"]) > 0


def test_fail_does_not_generate_review_doc(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump(_invalid_manifest()), encoding="utf-8"
    )

    run_gate(bundle_dir=bundle)
    assert not (bundle / "cluster-plan-review.md").exists()


# ---------------------------------------------------------------------------
# CLI exit codes
# ---------------------------------------------------------------------------

def test_cli_exits_zero_on_pass(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump(_valid_manifest()), encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--bundle-dir", str(bundle)],
        capture_output=True,
    )
    assert result.returncode == 0


def test_cli_exits_nonzero_on_fail(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump(_invalid_manifest()), encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--bundle-dir", str(bundle)],
        capture_output=True,
    )
    assert result.returncode == 1


def test_cli_exits_zero_on_skip(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="none")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump({"cluster_density": "none", "segments": []}), encoding="utf-8"
    )

    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--bundle-dir", str(bundle)],
        capture_output=True,
    )
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# Backward compat: source_artifact in receipt
# ---------------------------------------------------------------------------

def test_source_artifact_in_receipt_segment_manifest(tmp_path: Path) -> None:
    """Existing segment-manifest path records source_artifact in receipt."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump(_valid_manifest()), encoding="utf-8"
    )

    run_gate(bundle_dir=bundle)

    receipt = json.loads((bundle / "g1.5-cluster-gate-receipt.json").read_text(encoding="utf-8"))
    assert receipt.get("source_artifact") == "segment-manifest.yaml"


# ---------------------------------------------------------------------------
# Mode A: cluster-plan.yaml present, no segment-manifest.yaml
# ---------------------------------------------------------------------------

def _minimal_cluster_plan(cluster_density: str = "sparse") -> dict:
    """Minimal cluster-plan.yaml — structural fields only, narration fields null."""
    return {
        "cluster_density": cluster_density,
        "segments": [
            {
                "slide_id": "s1",
                "cluster_id": "c1",
                "cluster_role": "head",
                "cluster_position": "establish",
                "parent_slide_id": None,
                "interstitial_type": None,
                "isolation_target": None,
                "narration_burden": None,
                "narrative_arc": "From confusion to clarity",
                "master_behavioral_intent": None,
                "develop_type": None,
                "cluster_interstitial_count": 1,
                "double_dispatch_eligible": True,
            },
            {
                "slide_id": "s2",
                "cluster_id": "c1",
                "cluster_role": "interstitial",
                "cluster_position": "resolve",
                "parent_slide_id": "s1",
                "interstitial_type": "reveal",
                "isolation_target": None,
                "narration_burden": None,
                "narrative_arc": None,
                "master_behavioral_intent": None,
                "develop_type": None,
                "cluster_interstitial_count": None,
                "double_dispatch_eligible": False,
            },
        ],
    }


def test_fallback_to_cluster_plan_when_manifest_absent(tmp_path: Path) -> None:
    """Mode A happy path: cluster-plan.yaml present, no segment-manifest.yaml → gate runs."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "cluster-plan.yaml").write_text(
        yaml.safe_dump(_minimal_cluster_plan()), encoding="utf-8"
    )

    result = run_gate(bundle_dir=bundle)
    assert result["skipped"] is False
    assert result["passed"] is True
    assert result["errors"] == []

    receipt = json.loads((bundle / "g1.5-cluster-gate-receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "pass"
    assert receipt["source_artifact"] == "cluster-plan.yaml"


def test_cluster_plan_invalid_structural_field_fails(tmp_path: Path) -> None:
    """Mode A failure: cluster-plan.yaml with invalid structural field → gate fails cleanly."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    plan = _minimal_cluster_plan()
    plan["segments"][1]["interstitial_type"] = "bad-type"  # invalid vocab
    (bundle / "cluster-plan.yaml").write_text(yaml.safe_dump(plan), encoding="utf-8")

    result = run_gate(bundle_dir=bundle)
    assert result["passed"] is False
    assert any("G1.5-02" in e for e in result["errors"])

    receipt = json.loads((bundle / "g1.5-cluster-gate-receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"] == "fail"
    assert receipt["source_artifact"] == "cluster-plan.yaml"


def test_cluster_plan_density_none_skips(tmp_path: Path) -> None:
    """Mode A skip: cluster-plan.yaml with cluster_density none → gate skips."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="none")
    (bundle / "cluster-plan.yaml").write_text(
        yaml.safe_dump({"cluster_density": "none", "segments": []}), encoding="utf-8"
    )

    result = run_gate(bundle_dir=bundle)
    assert result["skipped"] is True
    assert not (bundle / "g1.5-cluster-gate-receipt.json").exists()


def test_cluster_plan_narration_fields_null_do_not_fail(tmp_path: Path) -> None:
    """Mode A structural: null narration fields (isolation_target, narration_burden,
    master_behavioral_intent) do not produce errors in structural mode."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "cluster-plan.yaml").write_text(
        yaml.safe_dump(_minimal_cluster_plan()), encoding="utf-8"
    )

    result = run_gate(bundle_dir=bundle)
    assert result["passed"] is True
    # Confirm none of the narration-only criteria fired
    for err in result["errors"]:
        assert "G1.5-03" not in err
        assert "G1.5-04" not in err
        assert "G1.5-14" not in err


# ---------------------------------------------------------------------------
# Mode C: both files / neither file / malformed YAML
# ---------------------------------------------------------------------------

def test_both_files_present_cluster_plan_wins(tmp_path: Path) -> None:
    """Mode C priority: when both files exist, cluster-plan.yaml wins."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "cluster-plan.yaml").write_text(
        yaml.safe_dump(_minimal_cluster_plan()), encoding="utf-8"
    )
    (bundle / "segment-manifest.yaml").write_text(
        yaml.safe_dump(_valid_manifest()), encoding="utf-8"
    )

    result = run_gate(bundle_dir=bundle)
    receipt = json.loads((bundle / "g1.5-cluster-gate-receipt.json").read_text(encoding="utf-8"))
    assert receipt["source_artifact"] == "cluster-plan.yaml"
    assert result["passed"] is True


def test_neither_file_present_raises_with_both_names(tmp_path: Path) -> None:
    """Mode C error: neither file present → FileNotFoundError citing both filenames."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")

    with pytest.raises(FileNotFoundError) as exc_info:
        run_gate(bundle_dir=bundle)
    msg = str(exc_info.value)
    assert "segment-manifest.yaml" in msg
    assert "cluster-plan.yaml" in msg


def test_malformed_cluster_plan_yaml_raises(tmp_path: Path) -> None:
    """Mode C edge: malformed YAML in cluster-plan.yaml → yaml error, no partial receipt."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "cluster-plan.yaml").write_text("key: [unclosed", encoding="utf-8")

    with pytest.raises(yaml.YAMLError):
        run_gate(bundle_dir=bundle)
    assert not (bundle / "g1.5-cluster-gate-receipt.json").exists()


def test_review_doc_parseable_from_minimal_cluster_plan(tmp_path: Path) -> None:
    """AC-6: review doc is written and parseable (non-empty markdown) from cluster-plan.yaml."""
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    _write_run_constants(bundle, cluster_density="sparse")
    (bundle / "cluster-plan.yaml").write_text(
        yaml.safe_dump(_minimal_cluster_plan()), encoding="utf-8"
    )

    run_gate(bundle_dir=bundle)

    review_path = bundle / "cluster-plan-review.md"
    assert review_path.exists()
    content = review_path.read_text(encoding="utf-8")
    assert "Cluster Plan Review" in content
    assert "Operator Decision" in content
    assert len(content) > 100  # non-trivially non-empty
