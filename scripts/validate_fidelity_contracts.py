"""Validate structural completeness of all fidelity contract YAML files.

Checks that every contract in state/config/fidelity-contracts/ conforms
to the schema defined in _schema.yaml.
"""

import sys
from pathlib import Path

import yaml


CONTRACTS_DIR = Path(__file__).resolve().parent.parent / "state" / "config" / "fidelity-contracts"

REQUIRED_TOP_LEVEL = {"gate", "gate_name", "producing_agent", "source_of_truth", "criteria"}

REQUIRED_SOURCE_OF_TRUTH = {"primary", "schema_ref"}

REQUIRED_CRITERION = {"id", "name", "description", "fidelity_class", "severity", "evaluation_type", "check", "requires_perception"}

VALID_SEVERITIES = {"critical", "high", "medium"}
VALID_EVAL_TYPES = {"deterministic", "agentic"}
VALID_FIDELITY_CLASSES = {"creative", "literal-text", "literal-visual"}
VALID_MODALITIES = {"image", "audio", "pdf", "video", None}


def validate_contract(filepath: Path) -> list[str]:
    """Validate a single contract file. Returns list of error messages."""
    errors: list[str] = []
    try:
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        return [f"Failed to parse YAML: {e}"]

    if not isinstance(data, dict):
        return ["Root element is not a mapping"]

    for field in REQUIRED_TOP_LEVEL:
        if field not in data:
            errors.append(f"Missing required top-level field: {field}")

    sot = data.get("source_of_truth", {})
    if isinstance(sot, dict):
        for field in REQUIRED_SOURCE_OF_TRUTH:
            if field not in sot:
                errors.append(f"source_of_truth missing field: {field}")
    elif "source_of_truth" in data:
        errors.append("source_of_truth must be a mapping")

    criteria = data.get("criteria", [])
    if not isinstance(criteria, list):
        errors.append("criteria must be a list")
        return errors

    if len(criteria) == 0:
        errors.append("criteria list is empty — at least one criterion required")

    seen_ids: set[str] = set()
    for i, criterion in enumerate(criteria):
        prefix = f"criteria[{i}]"
        if not isinstance(criterion, dict):
            errors.append(f"{prefix}: must be a mapping")
            continue

        for field in REQUIRED_CRITERION:
            if field not in criterion:
                errors.append(f"{prefix}: missing required field: {field}")

        cid = criterion.get("id", "")
        if cid in seen_ids:
            errors.append(f"{prefix}: duplicate id '{cid}'")
        seen_ids.add(cid)

        severity = criterion.get("severity")
        if severity and severity not in VALID_SEVERITIES:
            errors.append(f"{prefix}: invalid severity '{severity}' (must be one of {VALID_SEVERITIES})")

        eval_type = criterion.get("evaluation_type")
        if eval_type and eval_type not in VALID_EVAL_TYPES:
            errors.append(f"{prefix}: invalid evaluation_type '{eval_type}' (must be one of {VALID_EVAL_TYPES})")

        fc = criterion.get("fidelity_class", [])
        if isinstance(fc, list):
            for cls in fc:
                if cls not in VALID_FIDELITY_CLASSES:
                    errors.append(f"{prefix}: invalid fidelity_class '{cls}' (must be one of {VALID_FIDELITY_CLASSES})")
        else:
            errors.append(f"{prefix}: fidelity_class must be a list")

        if criterion.get("requires_perception") and criterion.get("perception_modality") not in VALID_MODALITIES:
            errors.append(f"{prefix}: requires_perception is true but perception_modality is missing or invalid")

    return errors


def main() -> int:
    contract_files = sorted(CONTRACTS_DIR.glob("g*.yaml"))
    if not contract_files:
        print(f"ERROR: No contract files found in {CONTRACTS_DIR}")
        return 1

    total_errors = 0
    total_criteria = 0

    print(f"Validating {len(contract_files)} fidelity contracts in {CONTRACTS_DIR}\n")

    for filepath in contract_files:
        errors = validate_contract(filepath)
        with open(filepath, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        n_criteria = len(data.get("criteria", [])) if isinstance(data, dict) else 0
        total_criteria += n_criteria

        if errors:
            print(f"FAIL  {filepath.name} ({n_criteria} criteria)")
            for e in errors:
                print(f"      - {e}")
            total_errors += len(errors)
        else:
            print(f"PASS  {filepath.name} ({n_criteria} criteria)")

    print(f"\n{'='*50}")
    print(f"Files: {len(contract_files)}  Criteria: {total_criteria}  Errors: {total_errors}")

    if total_errors > 0:
        print("VALIDATION FAILED")
        return 1

    print("ALL CONTRACTS VALID")
    return 0


if __name__ == "__main__":
    sys.exit(main())
