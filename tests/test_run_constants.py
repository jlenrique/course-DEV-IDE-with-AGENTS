"""Tests for frozen bundle run-constants.yaml loading (production wiring).

Marked ``trial_critical`` — on the pre-Prompt-1 trial path. Must pass before
firing any trial production run. See ``docs/dev-guide/testing.md``.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.utilities import run_constants as rc

pytestmark = pytest.mark.trial_critical


def _write_valid_constants(bundle: Path, root: Path, *, bundle_rel: str | None = None) -> None:
    rel = bundle_rel or str(bundle.relative_to(root)).replace("\\", "/")
    data = {
        "schema_version": 1,
        "frozen_at_utc": "2026-04-03T00:00:00Z",
        "run_id": "T-UNIT-001",
        "lesson_slug": "lesson-unit",
        "bundle_path": rel,
        "primary_source_file": str(root / "primary.pdf"),
        "optional_context_assets": [],
        "theme_selection": "theme-a",
        "theme_paramset_key": "preset-a",
        "execution_mode": "tracked/default",
        "quality_preset": "production",
        "double_dispatch": False,
        "motion_enabled": False,
        "motion_budget": {"max_credits": 24, "model_preference": "std"},
        "slide_mode_proportions": {
            "literal-text": 0.25,
            "literal-visual": 0.35,
            "creative": 0.40,
        },
    }
    (bundle / "run-constants.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False),
        encoding="utf-8",
    )


def test_load_run_constants_happy_path(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    bundle = root / "bundles" / "lesson-unit-001"
    bundle.mkdir(parents=True)
    (root / "primary.pdf").write_text("x", encoding="utf-8")
    _write_valid_constants(bundle, root)

    loaded = rc.load_run_constants(bundle, root=root)
    assert loaded.run_id == "T-UNIT-001"
    assert loaded.execution_mode == "tracked/default"
    assert loaded.optional_context_assets == ()
    assert loaded.double_dispatch is False
    assert loaded.motion_enabled is False
    assert loaded.motion_budget is not None
    assert loaded.motion_budget.max_credits == 24
    assert loaded.motion_budget.model_preference == "std"
    assert loaded.slide_mode_proportions == {
        "literal-text": 0.25,
        "literal-visual": 0.35,
        "creative": 0.40,
    }


def test_bundle_path_must_match_directory(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    bundle = root / "bundles" / "lesson-unit-001"
    bundle.mkdir(parents=True)
    (root / "primary.pdf").write_text("x", encoding="utf-8")
    _write_valid_constants(bundle, root, bundle_rel="bundles/wrong-folder")

    with pytest.raises(rc.RunConstantsError, match="bundle_path"):
        rc.load_run_constants(bundle, root=root)


def test_verify_paths_requires_primary_file(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    bundle = root / "b" / "c"
    bundle.mkdir(parents=True)
    data = {
        "run_id": "X",
        "lesson_slug": "ls",
        "bundle_path": "b/c",
        "primary_source_file": str(root / "missing.pdf"),
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
    }
    (bundle / "run-constants.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(rc.RunConstantsError, match="primary_source_file"):
        rc.load_run_constants(bundle, root=root, verify_paths_exist=True)


def test_execution_mode_aliases(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    bundle = root / "b"
    bundle.mkdir(parents=True)
    (root / "p.pdf").write_text("1", encoding="utf-8")
    data = {
        "run_id": "X",
        "lesson_slug": "ls",
        "bundle_path": "b",
        "primary_source_file": str(root / "p.pdf"),
        "optional_context_assets": "none",
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked",
        "quality_preset": "draft",
    }
    (bundle / "run-constants.yaml").write_text(yaml.safe_dump(data), encoding="utf-8")
    loaded = rc.load_run_constants(bundle, root=root)
    assert loaded.execution_mode == "tracked/default"


def test_parse_invalid_quality_preset() -> None:
    raw = {
        "run_id": "a",
        "lesson_slug": "b",
        "bundle_path": "c",
        "primary_source_file": "d",
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "nope",
        "double_dispatch": False,
        "motion_enabled": False,
    }
    with pytest.raises(rc.RunConstantsError, match="quality_preset"):
        rc.parse_run_constants(raw)


def test_parse_invalid_double_dispatch_type() -> None:
    raw = {
        "run_id": "a",
        "lesson_slug": "b",
        "bundle_path": "c",
        "primary_source_file": "d",
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
        "double_dispatch": "yes",
    }
    with pytest.raises(rc.RunConstantsError, match="double_dispatch"):
        rc.parse_run_constants(raw)


def test_evidence_bolster_absent_defaults_to_false() -> None:
    parsed = rc.parse_run_constants(_MINIMAL_RAW)
    assert parsed.evidence_bolster is False


def test_evidence_bolster_true_parses() -> None:
    parsed = rc.parse_run_constants({**_MINIMAL_RAW, "evidence_bolster": True})
    assert parsed.evidence_bolster is True


def test_evidence_bolster_non_bool_raises() -> None:
    with pytest.raises(rc.RunConstantsError, match="evidence_bolster"):
        rc.parse_run_constants({**_MINIMAL_RAW, "evidence_bolster": "true"})


def test_parse_motion_budget_fields() -> None:
    raw = {
        "run_id": "a",
        "lesson_slug": "b",
        "bundle_path": "c",
        "primary_source_file": "d",
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
        "double_dispatch": False,
        "motion_enabled": True,
        "motion_budget": {
            "max_credits": 18,
            "model_preference": "pro",
        },
    }
    parsed = rc.parse_run_constants(raw)
    assert parsed.motion_enabled is True
    assert parsed.motion_budget is not None
    assert parsed.motion_budget.max_credits == 18
    assert parsed.motion_budget.model_preference == "pro"


def test_parse_invalid_motion_budget_model_preference() -> None:
    raw = {
        "run_id": "a",
        "lesson_slug": "b",
        "bundle_path": "c",
        "primary_source_file": "d",
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
        "motion_enabled": True,
        "motion_budget": {
            "max_credits": 18,
            "model_preference": "ultra",
        },
    }
    with pytest.raises(rc.RunConstantsError, match="model_preference"):
        rc.parse_run_constants(raw)


def test_parse_invalid_motion_enabled_type() -> None:
    raw = {
        "run_id": "a",
        "lesson_slug": "b",
        "bundle_path": "c",
        "primary_source_file": "d",
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
        "motion_enabled": "yes",
    }
    with pytest.raises(rc.RunConstantsError, match="motion_enabled"):
        rc.parse_run_constants(raw)


def test_motion_enabled_requires_explicit_budget() -> None:
    raw = {
        "run_id": "a",
        "lesson_slug": "b",
        "bundle_path": "c",
        "primary_source_file": "d",
        "optional_context_assets": [],
        "theme_selection": "t",
        "theme_paramset_key": "p",
        "execution_mode": "tracked/default",
        "quality_preset": "draft",
        "motion_enabled": True,
    }
    with pytest.raises(
        rc.RunConstantsError,
        match="motion_enabled requires an explicit motion_budget",
    ):
        rc.parse_run_constants(raw)


_MINIMAL_RAW: dict = {
    "run_id": "a",
    "lesson_slug": "b",
    "bundle_path": "c",
    "primary_source_file": "d",
    "optional_context_assets": [],
    "theme_selection": "t",
    "theme_paramset_key": "p",
    "execution_mode": "tracked/default",
    "quality_preset": "draft",
}


def test_cluster_density_absent_defaults_to_none() -> None:
    parsed = rc.parse_run_constants(_MINIMAL_RAW)
    assert parsed.cluster_density is None


def test_cluster_density_valid_values() -> None:
    for value in ("none", "sparse", "default", "rich"):
        raw = {**_MINIMAL_RAW, "cluster_density": value}
        parsed = rc.parse_run_constants(raw)
        assert parsed.cluster_density == value


def test_cluster_density_invalid_value_raises() -> None:
    raw = {**_MINIMAL_RAW, "cluster_density": "maximum"}
    with pytest.raises(rc.RunConstantsError, match="cluster_density"):
        rc.parse_run_constants(raw)


def test_cluster_density_non_string_raises() -> None:
    raw = {**_MINIMAL_RAW, "cluster_density": True}
    with pytest.raises(rc.RunConstantsError, match="cluster_density"):
        rc.parse_run_constants(raw)


def test_cluster_density_in_happy_path_load(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    bundle = root / "bundles" / "slug-001"
    bundle.mkdir(parents=True)
    (root / "primary.pdf").write_text("x", encoding="utf-8")
    data = {
        "run_id": "T-UNIT-001",
        "lesson_slug": "slug",
        "bundle_path": "bundles/slug-001",
        "primary_source_file": str(root / "primary.pdf"),
        "optional_context_assets": [],
        "theme_selection": "th",
        "theme_paramset_key": "pk",
        "execution_mode": "tracked/default",
        "quality_preset": "production",
        "cluster_density": "sparse",
    }
    (bundle / "run-constants.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
    )
    loaded = rc.load_run_constants(bundle, root=root)
    assert loaded.cluster_density == "sparse"


def test_slide_mode_proportions_valid_values_parse() -> None:
    raw = {
        **_MINIMAL_RAW,
        "slide_mode_proportions": {
            "literal-text": 0.2,
            "literal-visual": 0.4,
            "creative": 0.4,
        },
    }
    parsed = rc.parse_run_constants(raw)
    assert parsed.slide_mode_proportions == {
        "literal-text": 0.2,
        "literal-visual": 0.4,
        "creative": 0.4,
    }


def test_slide_mode_proportions_missing_key_raises() -> None:
    raw = {
        **_MINIMAL_RAW,
        "slide_mode_proportions": {
            "literal-text": 0.6,
            "creative": 0.4,
        },
    }
    with pytest.raises(rc.RunConstantsError, match="exactly"):
        rc.parse_run_constants(raw)


def test_slide_mode_proportions_extra_key_raises() -> None:
    raw = {
        **_MINIMAL_RAW,
        "slide_mode_proportions": {
            "literal-text": 0.3,
            "literal-visual": 0.3,
            "creative": 0.3,
            "experimental": 0.1,
        },
    }
    with pytest.raises(rc.RunConstantsError, match="unexpected keys"):
        rc.parse_run_constants(raw)


def test_slide_mode_proportions_non_numeric_raises() -> None:
    raw = {
        **_MINIMAL_RAW,
        "slide_mode_proportions": {
            "literal-text": "high",
            "literal-visual": 0.5,
            "creative": 0.5,
        },
    }
    with pytest.raises(rc.RunConstantsError, match="must be numeric"):
        rc.parse_run_constants(raw)


def test_slide_mode_proportions_bool_value_raises() -> None:
    raw = {
        **_MINIMAL_RAW,
        "slide_mode_proportions": {
            "literal-text": True,
            "literal-visual": 0.5,
            "creative": 0.5,
        },
    }
    with pytest.raises(rc.RunConstantsError, match="must be numeric"):
        rc.parse_run_constants(raw)


def test_slide_mode_proportions_out_of_range_raises() -> None:
    raw = {
        **_MINIMAL_RAW,
        "slide_mode_proportions": {
            "literal-text": -0.1,
            "literal-visual": 0.6,
            "creative": 0.5,
        },
    }
    with pytest.raises(rc.RunConstantsError, match="within \\[0, 1\\]"):
        rc.parse_run_constants(raw)


def test_slide_mode_proportions_sum_not_one_raises() -> None:
    raw = {
        **_MINIMAL_RAW,
        "slide_mode_proportions": {
            "literal-text": 0.2,
            "literal-visual": 0.2,
            "creative": 0.2,
        },
    }
    with pytest.raises(rc.RunConstantsError, match="must sum to 1.0"):
        rc.parse_run_constants(raw)


def _load_profile_targets() -> dict[str, dict]:
    data = yaml.safe_load(rc.EXPERIENCE_PROFILES_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    profiles = data.get("profiles")
    assert isinstance(profiles, dict)
    return profiles


def test_resolve_experience_profile_visual_led_matches_yaml() -> None:
    profiles = _load_profile_targets()
    resolved = rc.resolve_experience_profile("visual-led")
    assert resolved == {
        "cluster_density": profiles["visual-led"]["cluster_density"],
        "slide_mode_proportions": profiles["visual-led"]["slide_mode_proportions"],
        "narration_profile_controls": profiles["visual-led"]["narration_profile_controls"],
    }


def test_resolve_experience_profile_text_led_matches_yaml() -> None:
    profiles = _load_profile_targets()
    resolved = rc.resolve_experience_profile("text-led")
    assert resolved == {
        "cluster_density": profiles["text-led"]["cluster_density"],
        "slide_mode_proportions": profiles["text-led"]["slide_mode_proportions"],
        "narration_profile_controls": profiles["text-led"]["narration_profile_controls"],
    }


def test_resolve_experience_profile_unknown_profile_raises() -> None:
    with pytest.raises(rc.RunConstantsError, match="unknown experience profile"):
        rc.resolve_experience_profile("cinematic-led")


def test_resolve_experience_profile_matches_slide_mode_keys() -> None:
    resolved = rc.resolve_experience_profile("visual-led")
    assert tuple(resolved["slide_mode_proportions"].keys()) == rc.SLIDE_MODE_KEYS


def test_resolve_experience_profile_malformed_yaml_raises(tmp_path: Path) -> None:
    profiles_path = tmp_path / "experience-profiles.yaml"
    profiles_path.write_text("profiles: [unterminated", encoding="utf-8")

    with pytest.raises(rc.RunConstantsError, match="Invalid YAML"):
        rc.resolve_experience_profile("visual-led", profiles_path=profiles_path)


def test_resolve_experience_profile_requires_narration_controls_mapping(tmp_path: Path) -> None:
    profiles_path = tmp_path / "experience-profiles.yaml"
    profiles_path.write_text(
        yaml.safe_dump(
            {
                "profiles": {
                    "visual-led": {
                        "slide_mode_proportions": {
                            "literal-text": 0.15,
                            "literal-visual": 0.25,
                            "creative": 0.60,
                        },
                        "narration_profile_controls": "invalid",
                    }
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(rc.RunConstantsError, match="narration_profile_controls"):
        rc.resolve_experience_profile("visual-led", profiles_path=profiles_path)


def test_resolve_experience_profile_requires_cluster_density(tmp_path: Path) -> None:
    profiles_path = tmp_path / "experience-profiles.yaml"
    profiles_path.write_text(
        yaml.safe_dump(
            {
                "profiles": {
                    "visual-led": {
                        "slide_mode_proportions": {
                            "literal-text": 0.15,
                            "literal-visual": 0.25,
                            "creative": 0.60,
                        },
                        "narration_profile_controls": {
                            "narrator_source_authority": "source-grounded",
                            "slide_content_density": "adaptive",
                            "elaboration_budget": "medium",
                        },
                    }
                }
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(rc.RunConstantsError, match="cluster_density"):
        rc.resolve_experience_profile("visual-led", profiles_path=profiles_path)


def test_resolve_experience_profile_uses_repo_stable_default_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)
    resolved = rc.resolve_experience_profile("visual-led")
    assert resolved["cluster_density"] == "default"


def test_resolve_experience_profile_round_trips_through_parse_without_mutation() -> None:
    resolved = rc.resolve_experience_profile("visual-led")
    raw = {
        **_MINIMAL_RAW,
        "experience_profile": "visual-led",
        "slide_mode_proportions": resolved["slide_mode_proportions"],
    }

    parsed = rc.parse_run_constants(raw)

    assert parsed.experience_profile == "visual-led"
    assert parsed.cluster_density == resolved["cluster_density"]
    assert parsed.slide_mode_proportions == resolved["slide_mode_proportions"]


def test_experience_profile_absent_defaults_to_none() -> None:
    parsed = rc.parse_run_constants(_MINIMAL_RAW)
    assert parsed.experience_profile is None


def test_experience_profile_valid_value_populates_dataclass() -> None:
    parsed = rc.parse_run_constants({**_MINIMAL_RAW, "experience_profile": "visual-led"})
    assert parsed.experience_profile == "visual-led"
    assert parsed.cluster_density == "default"
    assert (
        parsed.slide_mode_proportions
        == rc.resolve_experience_profile("visual-led")["slide_mode_proportions"]
    )


def test_experience_profile_text_led_populates_rich_cluster_density() -> None:
    parsed = rc.parse_run_constants({**_MINIMAL_RAW, "experience_profile": "text-led"})
    assert parsed.experience_profile == "text-led"
    assert parsed.cluster_density == "rich"


def test_experience_profile_explicit_slide_mode_proportions_must_match_resolved_profile() -> None:
    with pytest.raises(rc.RunConstantsError, match="must match the resolved experience_profile"):
        rc.parse_run_constants(
            {
                **_MINIMAL_RAW,
                "experience_profile": "visual-led",
                "slide_mode_proportions": {
                    "literal-text": 0.60,
                    "literal-visual": 0.25,
                    "creative": 0.15,
                },
            }
        )


def test_experience_profile_explicit_cluster_density_must_match_resolved_profile() -> None:
    with pytest.raises(rc.RunConstantsError, match="must match the resolved experience_profile"):
        rc.parse_run_constants(
            {
                **_MINIMAL_RAW,
                "experience_profile": "visual-led",
                "cluster_density": "rich",
            }
        )


def test_experience_profile_unknown_value_raises() -> None:
    with pytest.raises(rc.RunConstantsError, match="unknown experience profile"):
        rc.parse_run_constants({**_MINIMAL_RAW, "experience_profile": "unknown"})


def test_main_json_exit_code(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    root = tmp_path / "r"
    bundle = root / "z"
    bundle.mkdir(parents=True)
    (root / "f.pdf").write_text("1", encoding="utf-8")
    _write_valid_constants(bundle, root, bundle_rel="z")

    code = rc.main(["--bundle-dir", str(bundle), "--root", str(root), "--json"])
    assert code == 0
    out = capsys.readouterr().out
    assert "T-UNIT-001" in out
    assert '"status": "pass"' in out
