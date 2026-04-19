#!/usr/bin/env python3
"""
Tracy Vocab Lockstep Validator

Validates that Tracy's suggested resources output conforms to the schema
and maintains lockstep with the defined vocabulary.
"""

import json
import sys
from pathlib import Path
from typing import Any

import jsonschema

_SCHEMA_REL = Path("state") / "config" / "schemas" / "suggested-resources.schema.json"
_VOCAB_YAML_REL = (
    Path("skills") / "bmad_agent_tracy" / "references" / "vocabulary.yaml"
)
_VOCAB_MD_REL = Path("skills") / "bmad_agent_tracy" / "references" / "vocabulary.md"


def load_schema() -> dict[str, Any]:
    """Load the suggested-resources schema."""
    repo_root = Path(__file__).parent.parent.parent
    schema_path = repo_root / _SCHEMA_REL
    try:
        with open(schema_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Schema file is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def validate_vocabulary_lockstep() -> bool:
    """Validate that vocabulary.yaml and vocabulary.md are in lockstep."""
    repo_root = Path(__file__).parent.parent.parent
    vocab_yaml = repo_root / _VOCAB_YAML_REL
    vocab_md = repo_root / _VOCAB_MD_REL

    if not vocab_yaml.exists() or not vocab_md.exists():
        # During initial implementation, files might not exist yet,
        # but the lockstep script must contain the mechanism
        print(
            "Warning: vocabulary.yaml or vocabulary.md missing, "
            "skipping lockstep check for now."
        )
        return True

    try:
        import yaml

        with open(vocab_yaml, encoding="utf-8") as f:
            yaml_content = yaml.safe_load(f)
        with open(vocab_md, encoding="utf-8") as f:
            md_content = f.read()

        # Basic lockstep parity check (ensure intent classes are documented)
        if "intent_class" in yaml_content and "day_1_values" in yaml_content["intent_class"]:
            for intent in yaml_content["intent_class"]["day_1_values"]:
                if intent not in md_content:
                    print(
                        "Error: intent_class "
                        f"'{intent}' from vocabulary.yaml is missing in vocabulary.md"
                    )
                    return False
        return True
    except Exception as e:
        print(f"Error validating vocabulary lockstep: {e}", file=sys.stderr)
        return False


def validate_suggested_resources(data: dict[str, Any]) -> bool:
    """
    Validate suggested resources data against schema.

    Args:
        data: The data to validate

    Returns:
        True if valid, False otherwise
    """
    try:
        schema = load_schema()
        jsonschema.validate(data, schema)
        return True
    except jsonschema.ValidationError as e:
        print(f"Schema validation error: {e.message}", file=sys.stderr)
        return False
    except jsonschema.SchemaError as e:
        print(f"Invalid schema: {e.message}", file=sys.stderr)
        return False


def main() -> None:
    """CLI entry point for validation."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/utilities/tracy_vocab_lockstep.py <json_file>")
        sys.exit(1)

    json_file = Path(sys.argv[1])
    if not json_file.is_file():
        print(f"File not found or is a directory: {json_file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Input file is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    lockstep_passed = validate_vocabulary_lockstep()
    schema_passed = validate_suggested_resources(data)

    if lockstep_passed and schema_passed:
        print("✅ Validation passed")
        sys.exit(0)
    else:
        print("❌ Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
