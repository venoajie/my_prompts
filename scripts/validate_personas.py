# /scripts/validate_personas.py
# Version: 5.2 (Absolute Imports)

import os
import yaml
import sys
from pathlib import Path

# Import from the new shared utilities module using an absolute path
from scripts.pel_utils import load_config, find_all_personas, ROOT_DIR

# --- Constants ---
# (The rest of this file's content remains unchanged)
CONFIG_FILE = ROOT_DIR / "pel.config.yml"
ARTIFACT_REQUIRED_KEYS = ['id', 'type', 'description']
GENERIC_DESCRIPTIONS_BLACKLIST = [
    "a file", "some code", "input data", "a document", "user input"
]
GREEN, YELLOW, RED, BLUE, NC, GRAY = '\033[92m', '\033[93m', '\033[91m', '\033[94m', '\033[0m', '\033[90m'

def _validate_expected_artifacts(artifacts):
    if not isinstance(artifacts, list):
        return False, "'expected_artifacts' must be a list."
    for i, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            return False, f"Artifact at index {i} is not a dictionary."
        if not all(key in artifact for key in ARTIFACT_REQUIRED_KEYS):
            return False, f"Artifact at index {i} is missing required keys."
        if any(phrase in artifact.get('description', '').lower() for phrase in GENERIC_DESCRIPTIONS_BLACKLIST):
            return False, f"Artifact '{artifact.get('id')}' has a generic description."
    return True, ""

def validate_persona_file(data, persona_type_rules):
    persona_type = data.get('type')
    if not persona_type:
        return False, "Frontmatter is missing required 'type' key."
    if persona_type not in persona_type_rules:
        return False, f"Invalid persona type '{persona_type}'."
    rules = persona_type_rules[persona_type]
    required_keys = rules.get('required_keys', [])
    if not all(key in data for key in required_keys):
        return False, f"Missing required keys for '{persona_type}' persona."
    if persona_type == "specialized":
        is_valid, msg = _validate_expected_artifacts(data.get('expected_artifacts', []))
        if not is_valid: return False, msg
    return True, f"OK: {data.get('alias', 'N/A')} ({persona_type})"

def main(config):
    active_stati = config.get('validation_rules', {}).get('active_stati', ['active'])
    persona_type_rules = config.get('persona_types', {})
    print(f"{BLUE}--- Starting Persona Validation (v5.2) ---{NC}")
    print(f"Validating only personas with status in: {active_stati}\n")
    all_persona_paths = find_all_personas(ROOT_DIR)
    if not all_persona_paths:
        print(f"{YELLOW}No persona files found. Validation skipped.{NC}")
        return 0
    error_count, success_count, skipped_count = 0, 0, 0
    for persona_path in all_persona_paths:
        relative_path = persona_path.relative_to(ROOT_DIR)
        try:
            content = persona_path.read_text(encoding='utf-8')
            parts = content.split('---')
            if len(parts) < 3: raise ValueError("File does not contain valid YAML frontmatter.")
            data = yaml.safe_load(parts[1])
            if not isinstance(data, dict): raise ValueError("YAML frontmatter is not a valid dictionary.")
            if data.get('status') not in active_stati:
                print(f"{GRAY}[SKIP]{NC} {relative_path} (status: '{data.get('status')}')")
                skipped_count += 1
                continue
            is_valid, message = validate_persona_file(data, persona_type_rules)
            if is_valid:
                print(f"{GREEN}[PASS]{NC} {relative_path}")
                success_count += 1
            else:
                raise ValueError(message)
        except (ValueError, yaml.YAMLError) as e:
            print(f"{RED}[FAIL]{NC} {relative_path}\n     └─ {YELLOW}Reason: {e}{NC}")
            error_count += 1
    print(f"\nValidation Summary: {GREEN}{success_count} passed, {RED}{error_count} failed, {GRAY}{skipped_count} skipped.{NC}")
    return error_count

if __name__ == "__main__":
    loaded_config = load_config(CONFIG_FILE)
    final_error_count = main(loaded_config)
    sys.exit(1 if final_error_count > 0 else 0)