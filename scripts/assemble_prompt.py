#!/usr/bin/env python3
# assemble_prompt_v2.py

import argparse
import sys
from pathlib import Path
import yaml
from bs4 import BeautifulSoup

# --- Constants ---
# Using constants for directory names is good practice.
ENGINE_DIR_NAME = "engine"
DOMAINS_DIR_NAME = "domains"
PERSONAS_DIR_NAME = "personas"
KB_DIR_NAME = "knowledge_base"
INSTANCES_DIR_NAME = "instances"

# --- Core Logic ---

def find_repo_root(start_path: Path) -> Path:
    """Finds the repository root by looking for key directories."""
    current = start_path.resolve()
    while current != current.parent:
        if (current / ENGINE_DIR_NAME).is_dir() and (current / DOMAINS_DIR_NAME).is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find repository root. Ensure 'engine/' and 'domains/' directories exist.")

def load_artifact_with_frontmatter(path: Path) -> (dict, str):
    """Loads an artifact, parsing YAML frontmatter and returning metadata and content."""
    if not path.is_file():
        raise FileNotFoundError(f"Artifact not found at: {path}")

    text = path.read_text()
    if not text.startswith("---"):
        return {}, text  # No frontmatter found

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text  # Malformed frontmatter

    metadata = yaml.safe_load(parts[1])
    content = parts[2].strip()
    return metadata, content

def find_artifact(repo_root: Path, domain: str, artifact_type: str, alias: str) -> Path:
    """Finds an artifact file within a domain based on its alias and type."""
    # Example artifact filename: `sia-1.persona.md`
    # We will search for a file starting with the alias and containing the type.
    search_path = repo_root / DOMAINS_DIR_NAME / domain / artifact_type
    if not search_path.is_dir():
        raise FileNotFoundError(f"Artifact directory not found: {search_path}")
    
    matches = list(search_path.glob(f"**/{alias}.*.*")) # Use glob to find recursively
    if not matches:
        raise FileNotFoundError(f"Could not find {artifact_type} with alias '{alias}' in domain '{domain}'.")
    if len(matches) > 1:
        print(f"Warning: Found multiple artifacts for alias '{alias}'; using first one: {matches[0]}", file=sys.stderr)
    
    return matches[0]

def assemble_persona_content(repo_root: Path, domain: str, persona_alias: str) -> str:
    """
    Recursively assembles a persona's content by walking the 'inherits_from' chain.
    Child content is appended to parent content.
    """
    persona_path = find_artifact(repo_root, domain, PERSONAS_DIR_NAME, persona_alias)
    metadata, content = load_artifact_with_frontmatter(persona_path)

    parent_content = ""
    if "inherits_from" in metadata:
        parent_alias = metadata["inherits_from"]
        parent_content = assemble_persona_content(repo_root, domain, parent_alias)

    # Simple composition: parent directives first, then child's.
    return f"{parent_content}\n\n{content}"

def inject_knowledge_base(instance_content: str, kb_path: Path) -> str:
    """
    Injects knowledge base file content into the instance XML using a robust parser.
    Looks for tags like: <Inject src="path/to/file.py" />
    """
    if not kb_path.is_dir():
        print(f"Warning: Knowledge base directory not found at '{kb_path}'. No documents will be injected.", file=sys.stderr)
        return instance_content

    # Use BeautifulSoup for robust parsing, treating the content as XML
    soup = BeautifulSoup(instance_content, 'xml')
    for tag in soup.find_all('Inject'):
        src_file = tag.get('src')
        if not src_file:
            print(f"Warning: Found <Inject> tag without 'src' attribute. Skipping.", file=sys.stderr)
            continue

        doc_path = (kb_path / src_file).resolve()
        
        # Security check: ensure the path is within the knowledge base
        if kb_path.resolve() not in doc_path.parents:
             print(f"Error: Path traversal attempt blocked. '{src_file}' is outside the KB.", file=sys.stderr)
             tag.string = "<!-- INJECTION ERROR: PATH TRAVERSAL BLOCKED -->"
             continue

        if doc_path.is_file():
            file_content = doc_path.read_text()
            # Wrap content in CDATA to prevent XML parsing issues with the content itself
            tag.string = f"<![CDATA[\n{file_content}\n]]>"
        else:
            print(f"Warning: KB file '{src_file}' not found at '{doc_path}'. Tag will be empty.", file=sys.stderr)
            tag.string = "<!-- INJECTION ERROR: SOURCE FILE NOT FOUND -->"
    
    return str(soup)


def assemble_full_prompt(instance_path: Path) -> str:
    """Main assembly function."""
    repo_root = find_repo_root(instance_path)
    
    # 1. Load the instance file to get the mandate and persona metadata
    instance_meta, instance_mandate = load_artifact_with_frontmatter(instance_path)
    
    required_fields = ["domain", "persona_alias"]
    if not all(field in instance_meta for field in required_fields):
        raise ValueError(f"Instance file '{instance_path}' frontmatter is missing one of {required_fields}")

    domain = instance_meta["domain"]
    persona_alias = instance_meta["persona_alias"]
    
    # 2. Assemble the full persona by handling inheritance
    full_persona_content = assemble_persona_content(repo_root, domain, persona_alias)
    
    # Determine which engine to use from persona metadata (falls back to v1)
    persona_path = find_artifact(repo_root, domain, PERSONAS_DIR_NAME, persona_alias)
    persona_meta, _ = load_artifact_with_frontmatter(persona_path)
    engine_version = persona_meta.get("engine_version", "v1") # Default to v1
    
    # 3. Load the correct System Engine
    engine_path = repo_root / ENGINE_DIR_NAME / engine_version / "system_kernel.xml"
    engine_content = engine_path.read_text()

    # 4. Prepare the final instance block
    kb_path = repo_root / DOMAINS_DIR_NAME / domain / KB_DIR_NAME
    injected_mandate = inject_knowledge_base(instance_mandate, kb_path)
    
    final_instance_block = f"""
<Instance>
    <Runtime>
        <ActivatePersona alias="{persona_alias}"/>
        <Mandate>
            {injected_mandate}
        </Mandate>
    </Runtime>
</Instance>
"""
    # 5. Combine everything into the final prompt
    # The structure will be [SystemKernel][PersonaLibrary][Instance]
    return f"{engine_content}\n\n<PersonaLibrary>\n{full_persona_content}\n</PersonaLibrary>\n{final_instance_block}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Assemble a complete LLM prompt from the Prompt Engineering Library (V2).",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "instance_file",
        type=Path,
        help="Path to the instance file (e.g., 'domains/coding_trader_app/instances/my_task.instance.md')."
    )
    args = parser.parse_args()

    try:
        final_prompt = assemble_full_prompt(args.instance_file)
        print(final_prompt)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)