"""Tests for narration config YAML schemas.

Validates narration-grounding-profiles.yaml and narration-script-parameters.yaml
for structural correctness, required fields, and cross-file consistency with the
G4 fidelity contract.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[4]
CONFIG_DIR = ROOT / "state" / "config"
PROFILES_PATH = CONFIG_DIR / "narration-grounding-profiles.yaml"
PARAMS_PATH = CONFIG_DIR / "narration-script-parameters.yaml"
G4_CONTRACT_PATH = CONFIG_DIR / "fidelity-contracts" / "g4-narration-script.yaml"

FIDELITY_CLASSES = {"creative", "literal-text", "literal-visual"}


# ---- Fixture: load YAML files ----

@pytest.fixture(scope="module")
def profiles() -> dict:
    assert PROFILES_PATH.exists(), f"Missing: {PROFILES_PATH}"
    return yaml.safe_load(PROFILES_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def params() -> dict:
    assert PARAMS_PATH.exists(), f"Missing: {PARAMS_PATH}"
    return yaml.safe_load(PARAMS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def g4_contract() -> dict:
    assert G4_CONTRACT_PATH.exists(), f"Missing: {G4_CONTRACT_PATH}"
    return yaml.safe_load(G4_CONTRACT_PATH.read_text(encoding="utf-8"))


# ---- Narration Grounding Profiles Tests ----

class TestNarrationGroundingProfiles:
    VALID_STANCES = {"explain-behind", "read-along", "guided-interpretation"}

    def test_schema_version_present(self, profiles: dict) -> None:
        assert "schema_version" in profiles

    def test_profiles_key_exists(self, profiles: dict) -> None:
        assert "profiles" in profiles
        assert isinstance(profiles["profiles"], dict)

    def test_all_fidelity_classes_have_profiles(self, profiles: dict) -> None:
        profile_keys = set(profiles["profiles"].keys())
        assert profile_keys == FIDELITY_CLASSES

    @pytest.mark.parametrize("fidelity_class", sorted(FIDELITY_CLASSES))
    def test_profile_has_required_fields(self, profiles: dict, fidelity_class: str) -> None:
        profile = profiles["profiles"][fidelity_class]
        required = {"slide_role", "source_role", "stance", "min_source_claims", "description"}
        missing = required - set(profile.keys())
        assert not missing, f"{fidelity_class} missing: {missing}"

    @pytest.mark.parametrize("fidelity_class", sorted(FIDELITY_CLASSES))
    def test_min_source_claims_is_non_negative_int(self, profiles: dict, fidelity_class: str) -> None:
        val = profiles["profiles"][fidelity_class]["min_source_claims"]
        assert isinstance(val, int) and val >= 0

    @pytest.mark.parametrize("fidelity_class", sorted(FIDELITY_CLASSES))
    def test_profile_stance_is_valid(self, profiles: dict, fidelity_class: str) -> None:
        stance = profiles["profiles"][fidelity_class]["stance"]
        assert stance in self.VALID_STANCES

    def test_creative_profile_demands_source_primary(self, profiles: dict) -> None:
        creative = profiles["profiles"]["creative"]
        assert creative["source_role"] == "primary"
        assert creative["min_source_claims"] >= 1


# ---- Narration Script Parameters Tests ----

class TestNarrationScriptParameters:
    def test_schema_version_present(self, params: dict) -> None:
        assert "schema_version" in params

    REQUIRED_TOP_LEVEL = [
        "narration_density",
        "slide_echo",
        "visual_narration",
        "terminology_treatment",
        "pedagogical_bridging",
        "engagement_stance",
        "source_depth",
        "pronunciation_sensitivity",
    ]

    @pytest.mark.parametrize("section", REQUIRED_TOP_LEVEL)
    def test_top_level_section_exists(self, params: dict, section: str) -> None:
        assert section in params, f"Missing top-level section: {section}"

    # -- narration_density --

    def test_density_target_wpm_in_range(self, params: dict) -> None:
        wpm = params["narration_density"]["target_wpm"]
        assert 100 <= wpm <= 200, f"target_wpm {wpm} outside plausible range"

    def test_density_min_lt_mean_lt_max(self, params: dict) -> None:
        d = params["narration_density"]
        assert d["min_words_per_slide"] < d["mean_words_per_slide"] < d["max_words_per_slide"]

    # -- slide_echo --

    VALID_ECHO_VALUES = {"verbatim", "paraphrase", "inspired"}

    def test_slide_echo_default_is_valid(self, params: dict) -> None:
        assert params["slide_echo"]["default"] in self.VALID_ECHO_VALUES

    def test_slide_echo_per_fidelity_covers_all_classes(self, params: dict) -> None:
        overrides = set(params["slide_echo"]["per_fidelity_override"].keys())
        assert overrides == FIDELITY_CLASSES

    @pytest.mark.parametrize("fidelity_class", sorted(FIDELITY_CLASSES))
    def test_slide_echo_override_values_valid(self, params: dict, fidelity_class: str) -> None:
        val = params["slide_echo"]["per_fidelity_override"][fidelity_class]
        assert val in self.VALID_ECHO_VALUES

    # -- visual_narration --

    def test_visual_narration_deictic_valid(self, params: dict) -> None:
        valid = {"none", "minimal", "moderate", "frequent"}
        assert params["visual_narration"]["deictic_references"] in valid

    def test_visual_narration_depth_valid(self, params: dict) -> None:
        valid = {"identify", "summarize", "detailed"}
        assert params["visual_narration"]["description_depth"] in valid

    def test_visual_narration_reference_function_valid(self, params: dict) -> None:
        valid = {"annotation", "audience_guidance"}
        assert params["visual_narration"]["reference_function"] in valid

    def test_visual_narration_orientation_policy_valid(self, params: dict) -> None:
        valid = {"brief_only", "allowed", "none"}
        assert params["visual_narration"]["orientation_cue_policy"] in valid

    def test_visual_narration_meta_language_policy_valid(self, params: dict) -> None:
        valid = {"allowed", "discouraged", "forbidden"}
        assert params["visual_narration"]["meta_slide_language"] in valid

    def test_visual_narration_forbidden_phrases_is_list(self, params: dict) -> None:
        phrases = params["visual_narration"]["forbidden_meta_phrases"]
        assert isinstance(phrases, list)
        assert phrases, "forbidden_meta_phrases should not be empty when policy is configured"

    # -- terminology_treatment --

    def test_terminology_strategy_valid(self, params: dict) -> None:
        valid = {"inline_appositive", "parenthetical_aside", "no_gloss"}
        assert params["terminology_treatment"]["gloss_strategy"] in valid

    def test_terminology_audience_valid(self, params: dict) -> None:
        valid = {"novice", "intermediate", "expert"}
        assert params["terminology_treatment"]["audience_assumption"] in valid

    def test_terminology_domain_filter_is_list(self, params: dict) -> None:
        assert isinstance(params["terminology_treatment"]["gloss_domain_filter"], list)

    # -- pedagogical_bridging --

    def test_bridging_transition_style_valid(self, params: dict) -> None:
        valid = {"conceptual", "sequential", "question_driven", "narrative_arc"}
        assert params["pedagogical_bridging"]["transition_style"] in valid

    # -- engagement_stance --

    def test_engagement_posture_valid(self, params: dict) -> None:
        valid = {"lecturer", "collegial_guide", "coach", "storyteller"}
        assert params["engagement_stance"]["posture"] in valid

    # -- source_depth --

    def test_source_depth_creative_valid(self, params: dict) -> None:
        valid = {"describe_visual", "teach_behind", "full_synthesis"}
        assert params["source_depth"]["creative_slides"] in valid

    def test_source_depth_literal_valid(self, params: dict) -> None:
        valid = {"confirm_visible", "light_enrich", "full_synthesis"}
        assert params["source_depth"]["literal_slides"] in valid

    # -- pronunciation_sensitivity --

    def test_pronunciation_auto_flag_is_bool(self, params: dict) -> None:
        assert isinstance(params["pronunciation_sensitivity"]["auto_flag"], bool)


# ---- Cross-file consistency tests ----

class TestCrossFileConsistency:
    def test_g4_gate_name_mentions_segment_manifest(self, g4_contract: dict) -> None:
        assert g4_contract["gate_name"] == "Narration Script + Segment Manifest"

    def test_g4_source_of_truth_references_segment_manifest_template(
        self, g4_contract: dict
    ) -> None:
        source_of_truth = g4_contract["source_of_truth"]
        assert source_of_truth["schema_ref"] == (
            "skills/bmad-agent-content-creator/references/template-narration-script.md"
        )
        assert source_of_truth["schema_ref_secondary"] == (
            "skills/bmad-agent-content-creator/references/template-segment-manifest.md"
        )

    def test_g4_07_references_config_files(self, g4_contract: dict) -> None:
        """G4-07 must reference both narration config files."""
        criteria = g4_contract["criteria"]
        g4_07 = next((c for c in criteria if c["id"] == "G4-07"), None)
        assert g4_07 is not None, "G4-07 criterion not found in contract"
        refs = g4_07.get("config_refs", [])
        assert any("narration-grounding-profiles" in r for r in refs)
        assert any("narration-script-parameters" in r for r in refs)

    def test_g4_07_requires_perception(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_07 = next((c for c in criteria if c["id"] == "G4-07"), None)
        assert g4_07 is not None
        assert g4_07["requires_perception"] is True

    def test_g4_09_references_config_files(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_09 = next((c for c in criteria if c["id"] == "G4-09"), None)
        assert g4_09 is not None, "G4-09 criterion not found in contract"
        refs = g4_09.get("config_refs", [])
        assert any("narration-grounding-profiles" in r for r in refs)
        assert any("narration-script-parameters" in r for r in refs)

    def test_g4_09_requires_perception(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_09 = next((c for c in criteria if c["id"] == "G4-09"), None)
        assert g4_09 is not None
        assert g4_09["requires_perception"] is True

    def test_g4_07_only_applies_to_creative(self, g4_contract: dict) -> None:
        criteria = g4_contract["criteria"]
        g4_07 = next((c for c in criteria if c["id"] == "G4-07"), None)
        assert g4_07 is not None
        assert g4_07["fidelity_class"] == ["creative"]

    def test_profiles_min_source_claims_aligns_with_g407_intent(
        self, profiles: dict, g4_contract: dict
    ) -> None:
        """Creative profile min_source_claims >= 1 matches G4-07's requirement."""
        creative_min = profiles["profiles"]["creative"]["min_source_claims"]
        assert creative_min >= 1

    def test_source_depth_creative_default_not_describe_visual(self, params: dict) -> None:
        """Creative slides should default to teach_behind or full_synthesis, not describe_visual."""
        val = params["source_depth"]["creative_slides"]
        assert val != "describe_visual", "Creative slides must go deeper than describe_visual"

    def test_g4_criterion_ids_sequential(self, g4_contract: dict) -> None:
        """All G4 criteria IDs must be sequential G4-01, G4-02, ..., G4-NN."""
        ids = [c["id"] for c in g4_contract["criteria"]]
        expected = [f"G4-{str(i).zfill(2)}" for i in range(1, len(ids) + 1)]
        assert ids == expected
