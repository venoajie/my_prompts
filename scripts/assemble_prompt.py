#!/usr/bin/env python3
# assemble_prompt_v2.1.py

import argparse
import sys
from pathlib import Path
from typing import Tuple 

import yaml
from bs4 import BeautifulSoup

# --- Constants ---
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

def load_artifact_with_frontmatter(path: Path) -> Tuple[dict, str]:
    """Loads an artifact, parsing YAML frontmatter and returning metadata and content."""
    if not path.is_file():
        raise FileNotFoundError(f"Artifact not found at: {path}")

    text = path.read_text()
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text

    metadata = yaml.safe_load(parts[1])
    content = parts[2].strip()
    return metadata, content

def find_artifact(repo_root: Path, domain: str, artifact_type: str, alias: str) -> Path:
    """Finds an artifact file within a domain based on its alias and type."""
    search_path = repo_root / DOMAINS_DIR_NAME / domain / artifact_type
    if not search_path.is_dir():
        raise FileNotFoundError(f"Artifact directory not found: {search_path}")
    
    matches = list(search_path.glob(f"**/{alias}.*.*"))
    if not matches:
        raise FileNotFoundError(f"Could not find {artifact_type} with alias '{alias}' in domain '{domain}'.")
    if len(matches) > 1:
        print(f"Warning: Found multiple artifacts for alias '{alias}'; using first one: {matches[0]}", file=sys.stderr)
    
    return matches[0]

def assemble_persona_content(repo_root: Path, domain: str, persona_alias: str) -> str:
    """Recursively assembles a persona's content by walking the 'inherits_from' chain."""
    persona_path = find_artifact(repo_root, domain, PERSONAS_DIR_NAME, persona_alias)
    metadata, content = load_artifact_with_frontmatter(persona_path)

    parent_content = ""
    if "inherits_from" in metadata and metadata["inherits_from"]:
        parent_alias = metadata["inherits_from"]
        parent_content = assemble_persona_content(repo_root, domain, parent_alias)

    return f"{parent_content}\n\n{content}"

def inject_knowledge_base(instance_content: str, repo_root: Path, domain: str) -> str:
    """Injects file content into the instance XML by resolving paths from the repo root."""

    kb_path = repo_root / DOMAINS_DIR_NAME / domain / KB_DIR_NAME

    if not kb_path.is_dir():
        print(f"Warning: Knowledge base directory for domain '{domain}' not found at '{kb_path}'. Only repo-root paths will be resolved.", file=sys.stderr)

    soup = BeautifulSoup(instance_content, 'xml')
    for tag in soup.find_all('Inject'):
        src_file = tag.get('src')
        if not src_file:
            print(f"Warning: Found <Inject> tag without 'src' attribute. Skipping.", file=sys.stderr)
            continue

        doc_path = (repo_root / src_file).resolve()
        
        if not doc_path.is_relative_to(repo_root.resolve()):
             print(f"Error: Path traversal attempt blocked. '{src_file}' is outside the repo.", file=sys.stderr)
             tag.string = "<!-- INJECTION ERROR: PATH TRAVERSAL BLOCKED -->"
             continue

        if doc_path.is_file():
            file_content = doc_path.read_text()
            tag.string = f"<![CDATA[\n{file_content}\n]]>"
        else:
            # Fallback for non-code artifacts like ARCHITECTURE_BLUEPRINT.md
            fallback_path = (kb_path / src_file).resolve()
            if fallback_path.is_file():
                 file_content = fallback_path.read_text()
                 tag.string = f"<![CDATA[\n{file_content}\n]]>"
            else:
                print(f"Warning: File '{src_file}' not found at repo root or in KB. Tag will be empty.", file=sys.stderr)
                tag.string = "<!-- INJECTION ERROR: SOURCE FILE NOT FOUND -->"
    
    return str(soup)

def assemble_full_prompt(instance_path: Path) -> str:
    """Main assembly function."""
    repo_root = find_repo_root(instance_path)
    instance_meta, instance_mandate = load_artifact_with_frontmatter(instance_path)
    
    required_fields = ["domain", "persona_alias"]
    if not all(field in instance_meta for field in required_fields):
        raise ValueError(f"Instance file '{instance_path}' frontmatter is missing one of {required_fields}")

    domain = instance_meta["domain"]
    persona_alias = instance_meta["persona_alias"]
    
    full_persona_content = assemble_persona_content(repo_root, domain, persona_alias)
    
    persona_path = find_artifact(repo_root, domain, PERSONAS_DIR_NAME, persona_alias)
    persona_meta, _ = load_artifact_with_frontmatter(persona_path)
    engine_version = persona_meta.get("engine_version", "v1")
    
    engine_path = repo_root / ENGINE_DIR_NAME / engine_version / "system_kernel.xml"
    engine_content = engine_path.read_text()

    injected_mandate = inject_knowledge_base(instance_mandate, repo_root, domain)
    
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