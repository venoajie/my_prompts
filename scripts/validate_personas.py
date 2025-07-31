# /scripts/validate_personas.py
# Version: 2.0 (Architecture-Aware)

import os
import yaml
import sys
from pathlib import Path

# --- Configuration ---
PERSONA_FILENAME = "*.persona.md"
REQUIRED_KEYS = ['alias', 'version', 'title', 'status']
ROOT_DIR = Path(__file__).parent.parent

# ANSI Color Codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
NC = '\033[0m'

def find_all_personas(root_path):
    """Finds all persona files in templates and projects directories."""
    persona_files = []
    
    # Search in /templates
    templates_path = root_path / 'templates'
    if templates_path.exists():
        persona_files.extend(templates_path.rglob(PERSONA_FILENAME))
        
    # Search in /projects
    projects_path = root_path / 'projects'
    if projects_path.exists():
        persona_files.extend(projects_path.rglob(PERSONA_FILENAME))
        
    return persona_files

def validate_persona_file(file_path):
    """Validates a single persona file for YAML frontmatter and required keys."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        parts = content.split('---')
        if len(parts) < 3:
            return False, f"File does not contain valid YAML frontmatter. Path: {file_path}"

        frontmatter_str = parts[1]
        data = yaml.safe_load(frontmatter_str)

        if not isinstance(data, dict):
            return False, f"YAML frontmatter is not a valid dictionary. Path: {file_path}"

        missing_keys = [key for key in REQUIRED_KEYS if key not in data]
        if missing_keys:
            return False, f"Missing required keys: {', '.join(missing_keys)}. Path: {file_path}"

        return True, f"OK: {data.get('alias', 'N/A')}"

    except yaml.YAMLError as e:
        return False, f"YAML parsing error: {e}. Path: {file_path}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}. Path: {file_path}"

def main():
    """Main validation function."""
    print(f"{BLUE}--- Starting Persona Validation ---{NC}")
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