#!/usr/bin/env python3
# scripts/validate_personas.py

import sys
from pathlib import Path
import yaml

def find_repo_root(start_path: Path) -> Path:
    """Finds the repository root by looking for the 'domains' directory."""
    current = start_path.resolve()
    while current != current.parent:
        if (current / "domains").is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find repository root ('domains/' directory).")

def validate_persona(file_path: Path) -> list:
    """
    Validates a single persona file against the PEL's architectural rules.
    Returns a list of error messages.
    """
    errors = []
    try:
        text = file_path.read_text(encoding='utf-8')
        if not text.startswith("---"):
            errors.append("File does not start with YAML frontmatter '---'.")
            return errors

        parts = text.split("---", 2)
        if len(parts) < 3:
            errors.append("Malformed frontmatter; missing closing '---'.")
            return errors

        metadata = yaml.safe_load(parts[1])
        if not isinstance(metadata, dict):
            errors.append("Frontmatter is not a valid key-value map.")
            return errors

        # Rule 1: Check for required keys
        required_keys = ['alias', 'title', 'version', 'status']
        for key in required_keys:
            if key not in metadata:
                errors.append(f"Missing required key: '{key}'.")

        # Rule 2: Validate 'status' value
        valid_statuses = ['active', 'deprecated', 'experimental']
        if 'status' in metadata and metadata['status'] not in valid_statuses:
            errors.append(f"Invalid 'status': '{metadata['status']}'. Must be one of {valid_statuses}.")

        # Rule 3: Validate 'expected_artifacts' if present
        if 'expected_artifacts' in metadata:
            artifacts = metadata['expected_artifacts']
            if not isinstance(artifacts, list):
                errors.append("'expected_artifacts' must be a list.")
            else:
                for i, artifact in enumerate(artifacts):
                    if not isinstance(artifact, dict):
                        errors.append(f"Artifact at index {i} is not a key-value map.")
                        continue
                    for key in ['id', 'type', 'description']:
                        if key not in artifact:
                            errors.append(f"Artifact at index {i} is missing required key: '{key}'.")
                    if 'description' in artifact and ("source file to be tested" in artifact['description'] and "ute-1" not in file_path.name):
                         errors.append(f"Artifact at index {i} has a generic description. It must be specific to the persona's function.")

    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {e}")
    except Exception as e:
        errors.append(f"An unexpected error occurred: {e}")

    return errors

def main():
    """
    Main function to find all persona files and validate them.
    """
    try:
        repo_root = find_repo_root(Path.cwd())
        domains_path = repo_root / "domains"
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    print("Starting PEL Persona Audit...")
    all_persona_files = list(domains_path.glob('**/*.persona.md'))
    total_errors = 0

    if not all_persona_files:
        print("Warning: No persona files found to validate.", file=sys.stderr)
        sys.exit(0)

    for persona_file in all_persona_files:
        relative_path = persona_file.relative_to(repo_root)
        errors = validate_persona(persona_file)
        if errors:
            print(f"\n--- [FAIL] {relative_path} ---")
            for error in errors:
                print(f"  - {error}")
            total_errors += len(errors)
        else:
            print(f"[PASS] {relative_path}")

    if total_errors > 0:
        print(f"\nAudit failed with {total_errors} error(s).")
        sys.exit(1)
    else:
        print("\nAudit complete. All personas are compliant.")
        sys.exit(0)

if __name__ == "__main__":
    main()