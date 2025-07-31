# /scripts/validate_personas.py
# Version: 3.1 (Refactored & Hardened)

import os
import yaml
import sys
from pathlib import Path

# --- Configuration ---
ROOT_DIR = Path(__file__).parent.parent
PERSONA_FILENAME_PATTERNS = ["*.persona.md", "*.mixin.md"]

# --- Persona Types & Validation Rules ---
PERSONA_TYPE_SPECIALIZED = 'specialized'
PERSONA_TYPE_BASE = 'base'
PERSONA_TYPE_MIXIN = 'mixin'

BASE_REQUIRED_KEYS = ['alias', 'version', 'title', 'status']
SPECIALIZED_REQUIRED_KEYS = BASE_REQUIRED_KEYS + ['inherits_from', 'expected_artifacts']
ARTIFACT_REQUIRED_KEYS = ['id', 'type', 'description']
GENERIC_DESCRIPTIONS_BLACKLIST = [
    "a file", "some code", "input data", "a document", "user input"
]

# --- ANSI Color Codes ---
GREEN, YELLOW, RED, BLUE, NC = '\033[92m', '\033[93m', '\033[91m', '\033[94m', '\033[0m'

def find_all_personas(root_path):
    """Finds all persona and mixin files in templates and projects directories."""
    persona_files = []
    search_paths = [root_path / 'templates', root_path / 'projects']
    for path in search_paths:
        if path.exists():
            for pattern in PERSONA_FILENAME_PATTERNS:
                persona_files.extend(path.rglob(pattern))
    return persona_files

def get_persona_type(file_path):
    """Determines if a persona is base, mixin, or specialized based on its directory."""
    path_parts = file_path.parts
    if PERSONA_TYPE_BASE in path_parts:
        return PERSONA_TYPE_BASE
    if PERSONA_TYPE_MIXIN in path_parts:
        return PERSONA_TYPE_MIXIN
    if PERSONA_TYPE_SPECIALIZED in path_parts:
        return PERSONA_TYPE_SPECIALIZED
    return None

def _validate_expected_artifacts(artifacts):
    """Helper function to validate the structure and content of the expected_artifacts block."""
    if not isinstance(artifacts, list):
        return False, "'expected_artifacts' must be a list."
    
    for i, artifact in enumerate(artifacts):
        if not isinstance(artifact, dict):
            return False, f"Artifact at index {i} is not a dictionary."
        
        missing_keys = [key for key in ARTIFACT_REQUIRED_KEYS if key not in artifact]
        if missing_keys:
            return False, f"Artifact at index {i} is missing keys: {', '.join(missing_keys)}."
        
        description = artifact.get('description', '').lower()
        if any(phrase in description for phrase in GENERIC_DESCRIPTIONS_BLACKLIST):
            return False, f"Artifact '{artifact.get('id')}' has a generic description: '{artifact.get('description')}'. Be more specific."
            
    return True, ""

def validate_persona_file(file_path):
    """Validates a single persona file based on its type."""
    persona_type = get_persona_type(file_path)
    if not persona_type:
        return False, "Could not determine persona type (base, mixin, specialized) from path."

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split('---')
        if len(parts) < 3:
            return False, "File does not contain valid YAML frontmatter."

        data = yaml.safe_load(parts[1])
        if not isinstance(data, dict):
            return False, "YAML frontmatter is not a valid dictionary."

        # --- Refactored Validation Logic ---
        required_keys_for_type = SPECIALIZED_REQUIRED_KEYS if persona_type == PERSONA_TYPE_SPECIALIZED else BASE_REQUIRED_KEYS
        
        missing_keys = [key for key in required_keys_for_type if key not in data]
        if missing_keys:
            return False, f"Missing required keys for {persona_type} persona: {', '.join(missing_keys)}."

        if persona_type == PERSONA_TYPE_SPECIALIZED:
            is_valid, msg = _validate_expected_artifacts(data.get('expected_artifacts', []))
            if not is_valid:
                return False, msg

        return True, f"OK: {data.get('alias', 'N/A')} ({persona_type})"

    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}."
    except Exception as e:
        return False, f"An unexpected error occurred: {e}."

def main():
    """Main validation function."""
    print(f"{BLUE}--- Starting Persona Validation (v3.1) ---{NC}")
    print(f"Searching for personas in: {ROOT_DIR / 'templates'} and {ROOT_DIR / 'projects'}")
    
    all_personas = find_all_personas(ROOT_DIR)
    
    if not all_personas:
        print(f"{YELLOW}No persona files found. Validation skipped.{NC}")
        sys.exit(0)

    print(f"Found {len(all_personas)} persona files to validate.\n")

    error_count = 0
    success_count = 0

    for persona_path in all_personas:
        is_valid, message = validate_persona_file(persona_path)
        relative_path = persona_path.relative_to(ROOT_DIR)
        if is_valid:
            print(f"{GREEN}[PASS]{NC} {relative_path}")
            success_count += 1
        else:
            print(f"{RED}[FAIL]{NC} {relative_path}\n     └─ {YELLOW}Reason: {message}{NC}")
            error_count += 1
    
    print("\n" + "="*30)
    print(f"{BLUE}Validation Summary:{NC}")
    print(f"  {GREEN}Successful: {success_count}{NC}")
    print(f"  {RED}Failed:     {error_count}{NC}")
    print("="*30 + "\n")

    if error_count > 0:
        sys.exit(1)
    else:
        print(f"{GREEN}All personas are valid.{NC}")
        sys.exit(0)

if __name__ == "__main__":
    main()