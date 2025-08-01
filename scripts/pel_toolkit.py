# /scripts/pel_toolkit.py
# Version: 3.2

import os
import sys
import yaml
from pathlib import Path
import re
from datetime import datetime, timedelta

# --- Configuration (Loaded from pel.config.yml) ---

ROOT_DIR = Path(__file__).parent.parent
CONFIG_FILE = ROOT_DIR / "pel.config.yml"
PROJECTS_DIR_NAME = "projects"
META_FILENAME = ".domain_meta"

try:
    with open(CONFIG_FILE, 'r') as f:
        PEL_CONFIG = yaml.safe_load(f)
    RESOLUTION_PATHS = PEL_CONFIG.get('resolution_paths', ['project', 'template'])
except FileNotFoundError:
    print(f"FATAL: Configuration file not found at {CONFIG_FILE}", file=sys.stderr)
    sys.exit(1)
except yaml.YAMLError as e:
    print(f"FATAL: Error parsing {CONFIG_FILE}: {e}", file=sys.stderr)
    sys.exit(1)

def is_manifest_stale(manifest_path, root_dir):
    """
    Checks if the manifest is older than any recently modified persona file,
    with a grace period to prevent race conditions.
    """
    if not manifest_path.exists():
        return True, "Manifest file does not exist."

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_data = yaml.safe_load(f)
    
    generated_at_str = manifest_data.get("generated_at_utc")
    if not generated_at_str:
        return True, "Manifest is missing the 'generated_at_utc' timestamp."
        
    if generated_at_str.endswith('Z'):
        generated_at_str = generated_at_str[:-1]
    
    manifest_time = datetime.fromisoformat(generated_at_str)
    # Add a 2-second grace period to the manifest time for comparison
    manifest_time_with_grace = manifest_time + timedelta(seconds=2)

    sys.path.append(str(root_dir / "scripts"))
    from validate_personas import find_all_personas
    all_personas = find_all_personas(root_dir)
    
    for persona_path in all_personas:
        persona_mtime = datetime.fromtimestamp(persona_path.stat().st_mtime)
        if persona_mtime > manifest_time_with_grace:
            return True, f"Persona '{persona_path.name}' was modified after the manifest was generated."
            
    return False, "Manifest is up-to-date."


def find_project_root(instance_path):
    """
    Traverses up from the instance file to find the project root directory,
    defined as the directory containing the '.domain_meta' file.
    """
    current_path = Path(instance_path).resolve().parent
    while current_path != current_path.parent: # Stop at filesystem root
        if (current_path / META_FILENAME).exists():
            return current_path
        current_path = current_path.parent
    return None # Project root not found
def get_template_path(project_root):
    # ...
    pass
def find_persona_file(persona_alias, project_root, template_path):
    # ...
    pass
def assemble_persona_content(persona_path, project_root, template_path):
    # ...
    pass
def inject_file_content(mandate_body):
    # ...
    pass

def main(instance_file_path):
    """Main assembly function."""
    instance_path = Path(instance_file_path)
    
    if not instance_path.exists():
        print(f"Error: Instance file not found at {instance_path}", file=sys.stderr)
        sys.exit(1)

    with open(instance_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = content.split('---')
    if len(parts) < 3:
        print("Error: Instance file is missing YAML frontmatter.", file=sys.stderr)
        sys.exit(1)

    frontmatter_str = parts[1]
    mandate_body = "---".join(parts[2:])
    
    instance_data = yaml.safe_load(frontmatter_str)
    persona_alias = instance_data.get('persona_alias')

    if not persona_alias:
        print("Error: 'persona_alias' not defined in instance frontmatter.", file=sys.stderr)
        sys.exit(1)

    # --- STALENESS CHECK GUARDRAIL ---
    if persona_alias == "SI-1":
        manifest_path = ROOT_DIR / "persona_manifest.yml"
        stale, reason = is_manifest_stale(manifest_path, ROOT_DIR)
        if stale:
            print(f"FATAL ERROR: The persona_manifest.yml is stale.", file=sys.stderr)
            print(f"Reason: {reason}", file=sys.stderr)
            print(f"Please run 'make generate-manifest' from the root directory to update it.", file=sys.stderr)
            sys.exit(1)

    try:
        # Pass the absolute path to the root finder
        project_root = find_project_root(instance_path.resolve())
        if not project_root:
            # Use .resolve() only for the error message for clarity
            print(f"Error: Could not determine project root for instance file: {instance_path.resolve()}", file=sys.stderr)
            sys.exit(1)
            
        template_path = get_template_path(project_root)
        
        persona_path = find_persona_file(persona_alias, project_root, template_path)
        if not persona_path:
            print(f"Error: Persona '{persona_alias}' not found in project '{project_root.name}' or its template.", file=sys.stderr)
            sys.exit(1)
            
        full_persona_content = assemble_persona_content(persona_path, project_root, template_path)

        final_mandate = inject_file_content(mandate_body)

        final_prompt = f"""<SystemPrompt>
    <PersonaLibrary>
{full_persona_content}
    </PersonaLibrary>
</SystemPrompt>

<Instance>
{final_mandate}
</Instance>
"""
        print(final_prompt)
    except (FileNotFoundError, FileExistsError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pel_toolkit.py <path_to_instance_file.md>", file=sys.stderr)
        sys.exit(1)
    main(sys.argv[1])