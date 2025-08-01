# /scripts/pel_toolkit.py
# Version: 4.1 (UTE Fixes)

import os
import sys
import yaml
from pathlib import Path
import re
from datetime import datetime, timedelta, timezone

# --- Configuration ---
ROOT_DIR = Path(__file__).parent.parent
CONFIG_FILE = ROOT_DIR / "pel.config.yml"
GLOBAL_PERSONAS_PATH = ROOT_DIR / "projects/prompt_engineering/personas"
PROJECTS_DIR_NAME = "projects"
META_FILENAME = ".domain_meta"
TEMPLATES_DIR_NAME = "templates"
PERSONAS_DIR_NAME = "personas"

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
    """Checks if the manifest is older than any recently modified persona file."""
    if not manifest_path.exists():
        return True, "Manifest file does not exist."

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_data = yaml.safe_load(f)
    
    generated_at_str = manifest_data.get("generated_at_utc")
    if not generated_at_str:
        return True, "Manifest is missing the 'generated_at_utc' timestamp."
        
    manifest_time = datetime.fromisoformat(generated_at_str)
    manifest_time_with_grace = manifest_time + timedelta(seconds=2)

    # **MODIFICATION**: The sys.path manipulation is removed from here for better testability.
    # It is assumed the calling environment (like the Makefile) sets the path correctly.
    from validate_personas import find_all_personas
    all_personas = find_all_personas(root_dir)
    
    for persona_path in all_personas:
        persona_mtime_utc = datetime.fromtimestamp(persona_path.stat().st_mtime, tz=timezone.utc)
        if persona_mtime_utc > manifest_time_with_grace:
            return True, f"Persona '{persona_path.name}' was modified after the manifest was generated."
            
    return False, "Manifest is up-to-date."

def find_project_root(instance_path):
    """Traverses up from the instance file to find the project root directory."""
    current_path = Path(instance_path).resolve().parent
    while current_path != current_path.parent:
        if (current_path / META_FILENAME).exists():
            return current_path
        current_path = current_path.parent
    return None

def get_template_path(project_root):
    meta_file = project_root / META_FILENAME
    if not meta_file.exists(): return None
    with open(meta_file, 'r') as f:
        meta_data = yaml.safe_load(f)
    template_name = meta_data.get('template')
    if not template_name: return None
    return ROOT_DIR / TEMPLATES_DIR_NAME / template_name


def find_persona_file(persona_alias, project_root, template_path):
    """
    Searches for a persona file using a three-tiered inheritance model.
    """
    search_alias = persona_alias.lower()
    
    search_paths = []
    if project_root:
        search_paths.append(project_root / "personas")
    if template_path:
        search_paths.append(template_path / "personas")
    search_paths.append(GLOBAL_PERSONAS_PATH)

    for scope_path in search_paths:
        if scope_path and scope_path.exists():
            found_files = list(scope_path.rglob(f"**/{search_alias}.persona.md")) + \
                          list(scope_path.rglob(f"**/{search_alias}.mixin.md"))
            
            if len(found_files) > 1:
                raise FileExistsError(f"Ambiguity Error: Found multiple personas with alias '{search_alias}' in scope '{scope_path}'.")
            
            if found_files:
                return found_files[0]
                
    return None

def assemble_persona_content(persona_path, project_root, template_path):
    with open(persona_path, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = content.split('---')
    if len(parts) < 3: return content
    frontmatter_str, body = parts[1], "---".join(parts[2:])
    data = yaml.safe_load(frontmatter_str)
    
    # **MODIFICATION**: Make the function robust against empty frontmatter.
    if data is None:
        data = {}

    inherits_from = data.get('inherits_from')
    if inherits_from:
        parent_path = find_persona_file(inherits_from, project_root, template_path)
        if not parent_path:
            raise FileNotFoundError(f"Inherited persona '{inherits_from}' not found for '{persona_path.name}'.")
        parent_content = assemble_persona_content(parent_path, project_root, template_path)
        return parent_content + "\n" + body.strip()
    return body.strip()

def inject_file_content(mandate_body):
    inject_pattern = re.compile(r'<Inject\s+src="([^"]+)"\s*/>')
    def replacer(match):
        file_path = ROOT_DIR / match.group(1)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return f"[ERROR: Injected file not found at '{match.group(1)}']"
    return inject_pattern.sub(replacer, mandate_body)

def main(instance_file_path):
    # This function now assumes sys.path is correctly configured by the caller
    # to find `validate_personas`.
    instance_path = Path(instance_file_path)
    with open(instance_path, 'r', encoding='utf-8') as f:
        content = f.read()
    parts = content.split('---')
    if len(parts) < 3:
        print("Error: Instance file is missing YAML frontmatter.", file=sys.stderr)
        sys.exit(1)
    instance_data = yaml.safe_load(parts[1])
    persona_alias = instance_data.get('persona_alias')
    if not persona_alias:
        print("Error: 'persona_alias' not defined in instance frontmatter.", file=sys.stderr)
        sys.exit(1)

    if persona_alias == "SI-1":
        manifest_path = ROOT_DIR / "persona_manifest.yml"
        stale, reason = is_manifest_stale(manifest_path, ROOT_DIR)
        if stale:
            print(f"FATAL ERROR: The persona_manifest.yml is stale.", file=sys.stderr)
            print(f"Reason: {reason}", file=sys.stderr)
            print(f"Please run 'make generate-manifest' from the root directory to update it.", file=sys.stderr)
            sys.exit(1)

    try:
        project_root = find_project_root(instance_path)
        if not project_root:
            print(f"Error: Could not determine project root for instance file: {instance_path.resolve()}", file=sys.stderr)
            sys.exit(1)
        template_path = get_template_path(project_root)
        persona_path = find_persona_file(persona_alias, project_root, template_path)
        if not persona_path:
            print(f"Error: Persona '{persona_alias}' not found in project '{project_root.name}' or its template.", file=sys.stderr)
            sys.exit(1)
        full_persona_content = assemble_persona_content(persona_path, project_root, template_path)
        final_mandate = inject_file_content("---".join(parts[2:]))
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
    except (FileNotFoundError, FileExistsError, Exception) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pel_toolkit.py <path_to_instance_file.md>", file=sys.stderr)
        sys.exit(1)
    
    # Add scripts directory to path for command-line execution
    sys.path.append(str(Path(__file__).parent.resolve()))
    main(sys.argv[1])