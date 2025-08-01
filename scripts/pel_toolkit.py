# /scripts/pel_toolkit.py
# Version: 3.0 (Config-Driven & Hardened)

import os
import sys
import yaml
from pathlib import Path
import re

# --- Configuration (Loaded from pel.config.yml) ---
ROOT_DIR = Path(__file__).parent.parent
CONFIG_FILE = ROOT_DIR / "pel.config.yml"
TEMPLATES_DIR_NAME = "templates"
PROJECTS_DIR_NAME = "projects"
PERSONAS_DIR_NAME = "personas"
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

def find_project_root(instance_path):
    """Traverses up from the instance file to find the project root directory."""
    current_path = Path(instance_path).parent
    while current_path != ROOT_DIR and not (current_path.parent.name == PROJECTS_DIR_NAME):
        current_path = current_path.parent
        if current_path == current_path.parent:
            return None
    return current_path if (current_path.parent.name == PROJECTS_DIR_NAME) else None

def get_template_path(project_root):
    """Reads the .domain_meta file to find the associated template directory."""
    meta_file = project_root / META_FILENAME
    if not meta_file.exists():
        return None
    
    with open(meta_file, 'r') as f:
        meta_data = yaml.safe_load(f)
    
    template_name = meta_data.get('template')
    if not template_name:
        return None
        
    return ROOT_DIR / TEMPLATES_DIR_NAME / template_name

def find_persona_file(persona_alias, project_root, template_path):
    """
    Searches for a persona or mixin file in a deterministic order defined by pel.config.yml.
    Halts with an error if duplicate aliases are found within the same scope.
    """
    search_alias = persona_alias.lower()
    
    # Build the search path order based on the config file
    potential_search_dirs = {
        "project": project_root / PERSONAS_DIR_NAME if project_root else None,
        "template": template_path / PERSONAS_DIR_NAME if template_path else None
    }
    
    search_paths = [potential_search_dirs[p] for p in RESOLUTION_PATHS if potential_search_dirs.get(p)]

    for path in search_paths:
        if path and path.exists():
            # Search for both .persona.md and .mixin.md files.
            found_files = list(path.rglob(f"**/{search_alias}.persona.md")) + \
                          list(path.rglob(f"**/{search_alias}.mixin.md"))
            
            if len(found_files) > 1:
                # CRITICAL: Found duplicate aliases in the same scope (e.g., within the same project)
                paths_str = "\n - ".join(map(str, found_files))
                raise FileExistsError(
                    f"Ambiguity Error: Found multiple personas with alias '{search_alias}' within the search scope '{path}'.\n - {paths_str}"
                )
            
            if found_files:
                return found_files[0] # Return the single, unambiguous match
    return None

def assemble_persona_content(persona_path, project_root, template_path):
    """Recursively assembles persona content, handling inheritance."""
    with open(persona_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = content.split('---')
    if len(parts) < 3:
        return content # Not a valid frontmatter file, return as is

    frontmatter_str = parts[1]
    body = "---".join(parts[2:])
    
    data = yaml.safe_load(frontmatter_str)
    
    inherits_from = data.get('inherits_from')
    
    if inherits_from:
        parent_persona_path = find_persona_file(inherits_from, project_root, template_path)
        if not parent_persona_path:
            raise FileNotFoundError(f"Inherited persona '{inherits_from}' not found for '{persona_path.name}'.")
        
        parent_content = assemble_persona_content(parent_persona_path, project_root, template_path)
        return parent_content + "\n" + body.strip()
    
    return body.strip()

def inject_file_content(mandate_body):
    """Finds <Inject> tags and replaces them with file content."""
    inject_pattern = re.compile(r'<Inject\s+src="([^"]+)"\s*/>')
    
    def replacer(match):
        file_path_str = match.group(1)
        file_path = ROOT_DIR / file_path_str
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return f"[ERROR: Injected file not found at '{file_path_str}']"

    return inject_pattern.sub(replacer, mandate_body)

def main(instance_file_path):
    """Main assembly function."""
    instance_path = Path(instance_file_path).resolve()
    
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

    try:
        project_root = find_project_root(instance_path)
        if not project_root:
            print(f"Error: Could not determine project root for instance file: {instance_path}", file=sys.stderr)
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