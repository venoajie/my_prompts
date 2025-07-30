#!/usr/bin/env python3
# pel_toolkit.py (v3.4)


import argparse
import sys
from pathlib import Path
from typing import Tuple, Optional, List, Dict
import json
import re
import subprocess

import yaml
from bs4 import BeautifulSoup, CData

# --- Constants --
ENGINE_DIR_NAME = "engine"
DOMAINS_DIR_NAME = "domains"
PERSONAS_DIR_NAME = "personas"
KB_DIR_NAME = "knowledge_base"
INSTANCES_DIR_NAME = "instances"
ALIGNMENT_CHECKER_ALIAS = "alignment-checker"
PROMPT_ENGINEERING_DOMAIN = "prompt_engineering"
SHARED_DOMAIN = "shared"
ARTIFACT_EXTENSIONS = [".persona.md", ".mixin.md"] 

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

    text = path.read_text(encoding='utf-8')
    if not text.startswith("---"):
        return {}, text

    try:
        parts = text.split("---", 2)
        if len(parts) < 3:
            return {}, text
        metadata = yaml.safe_load(parts[1]) or {}
        content = parts[2].strip()
        return metadata, content
    except Exception as e:
        print(f"Error parsing frontmatter in {path}: {e}", file=sys.stderr)
        return {}, text


def find_artifact(
    repo_root: Path,
    domain: str,
    artifact_type: str,
    alias: str,
) -> Optional[Path]:
    """
    Finds an artifact file by alias, checking primary domain then shared domain.
    This version is more specific about file extensions for robustness.
    """
    search_alias = alias.lower()

    def search_in_path(base_path: Path) -> Optional[Path]:
        if not base_path.is_dir():
            return None
        for ext in ARTIFACT_EXTENSIONS:
            # Match against the full filename (alias + extension)
            matches = list(base_path.glob(f"**/{search_alias}{ext}"))
            if matches:
                if len(matches) > 1:
                    print(f"Warning: Found multiple artifacts for alias '{alias}'; using first one: {matches[0]}", file=sys.stderr)
                return matches[0]
        return None

    # 1. Search in the primary domain
    primary_search_path = repo_root / DOMAINS_DIR_NAME / domain / artifact_type
    found_path = search_in_path(primary_search_path)
    if found_path:
        return found_path

    # 2. If not found, search in the shared domain
    if domain != SHARED_DOMAIN:
        shared_search_path = repo_root / DOMAINS_DIR_NAME / SHARED_DOMAIN / artifact_type
        found_path = search_in_path(shared_search_path)
        if found_path:
            return found_path

    return None # Return None instead of raising error here, let caller handle it.


def get_all_persona_metadata(
    repo_root: Path, 
    domain: str,
    ) -> List[Dict[str, str]]:
    
    """
    Scans a domain's persona directory and extracts key metadata for the alignment check.
    """
    personas_path = repo_root / DOMAINS_DIR_NAME / domain / PERSONAS_DIR_NAME
    if not personas_path.is_dir():
        return []

    metadata_list = []
    # Find all files ending in .persona.md, looking recursively in subdirectories
    for persona_file in personas_path.glob('**/*.persona.md'):
        metadata, content = load_artifact_with_frontmatter(persona_file)
        alias = metadata.get("alias")
        
        # Extract the primary directive directly from the content for robustness
        directive_match = re.search(r'<primary_directive>(.*?)</primary_directive>', content, re.DOTALL)
        primary_directive = directive_match.group(1).strip() if directive_match else ""

        if alias and primary_directive:
            metadata_list.append({
                "alias": alias,
                "primary_directive": primary_directive
            })
    return metadata_list


def perform_alignment_check(
    mandate_content: str, 
    all_personas_metadata: List[Dict[str, str]], 
    original_alias: str,
    ) -> Dict:
    
    """
    Constructs a prompt for the alignment checker, simulates an LLM call, and returns the result.
    """    # Load the ALIGNMENT-CHECKER persona's definition
    # Note: In a real system, you might not need to find the repo root again, but this is robust.
    # This assumes the alignment-checker persona is in the 'prompt_engineering' domain.
    try:
        repo_root = find_repo_root(Path.cwd())
        checker_persona_path = find_artifact(repo_root, PROMPT_ENGINEERING_DOMAIN, PERSONAS_DIR_NAME, ALIGNMENT_CHECKER_ALIAS)
        _, checker_prompt = load_artifact_with_frontmatter(checker_persona_path)
    except FileNotFoundError:
        print("Warning: ALIGNMENT-CHECKER persona not found. Skipping alignment check.", file=sys.stderr)
        return {"suggested_persona_alias": None}

    # Construct the prompt payload for the checker
    persona_list_json = json.dumps(all_personas_metadata, indent=2)
    alignment_prompt = f"""
{checker_prompt}

<PersonaList>
{persona_list_json}
</PersonaList>

<Mandate>
{mandate_content}
</Mandate>
"""
    # --- !!! LLM API INTEGRATION POINT !!! ---
    # In a real application, you would replace the following block
    # with a call to your LLM API (e.g., OpenAI, Anthropic, Google).
    #
    # Example:
    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model="gpt-4-turbo",
    #     messages=[{"role": "user", "content": alignment_prompt}],
    #     response_format={"type": "json_object"}
    # )
    # response_json_str = response.choices[0].message.content
    
    # For demonstration, we will print the prompt and return a simulated response.
    print("\n--- [INFO] SIMULATED ALIGNMENT CHECK PROMPT ---", file=sys.stderr)
    print(alignment_prompt, file=sys.stderr)
    print("--- [INFO] END OF SIMULATED PROMPT ---\n", file=sys.stderr)
    
    # Simulate a response. In a real scenario, this comes from the LLM.
    response_json_str = f'{{"suggested_persona_alias": "{original_alias}"}}'
    
    return json.loads(response_json_str)

def assemble_persona_content(
    repo_root: Path, 
    domain: str,
    persona_alias: str,
    ) -> str:
    
    """Recursively assembles a persona's content by walking the 'inherits_from' chain."""
    
    persona_path = find_artifact(
        repo_root, 
        domain, 
        PERSONAS_DIR_NAME, 
        persona_alias,
        )
    if not persona_path:
        raise FileNotFoundError(f"Could not find persona with alias '{persona_alias}' in domain '{domain}' or in the '{SHARED_DOMAIN}' domain.")
    metadata, content = load_artifact_with_frontmatter(persona_path)

    # Create the XML block for the CURRENT persona
    current_persona_xml = f"""
<persona>
    <meta>
        <alias>{metadata.get('alias', '')}</alias>
        <title>{metadata.get('title', '')}</title>
        <version>{metadata.get('version', '')}</version>
        <inherits_from>{metadata.get('inherits_from', '')}</inherits_from>
    </meta>
    {content}
</persona>"""

    parent_content_xml = ""
    if "inherits_from" in metadata and metadata["inherits_from"]:
        parent_alias = metadata["inherits_from"]
        # The recursive call now returns the fully formed XML for the parent(s)
        parent_content_xml = assemble_persona_content(
            repo_root, 
            domain, 
            parent_alias,
            )

    # The final library is the parent's XML followed by the current persona's XML
    return f"{parent_content_xml}\n{current_persona_xml}"

def inject_knowledge_base(
    instance_content: str,
    base_path: Path,
) -> str:
    """
    Injects file content into the instance XML by resolving <Inject> tags
    relative to a specified base path.
    """
    xml_fragment = f"<root>{instance_content}</root>"
    soup = BeautifulSoup(xml_fragment, 'xml')

    for tag in soup.find_all('Inject'):
        src_file = tag.get('src')
        if not src_file:
            print(f"Warning: Found <Inject> tag without 'src' attribute. Skipping.", file=sys.stderr)
            continue

        doc_path = (base_path / src_file).resolve()

        if not doc_path.is_relative_to(base_path.resolve()):
            print(f"Error: Path traversal attempt blocked. '{src_file}' is outside the repo.", file=sys.stderr)
            tag.string = "<!-- INJECTION ERROR: PATH TRAVERSAL BLOCKED -->"
            continue

        if doc_path.is_file():
            try:
                file_content = doc_path.read_text(encoding='utf-8')
                # Use the local base_path variable for relative path calculation ---
                new_tag = soup.new_tag("InjectedArtifact", src=str(doc_path.relative_to(base_path)))
                new_tag.append(CData(f"\n{file_content}\n"))
                tag.replace_with(new_tag)
            except Exception as e:
                print(f"Error reading file '{src_file}': {e}", file=sys.stderr)
                tag.string = f"<!-- INJECTION ERROR: COULD NOT READ FILE: {src_file} -->"
        else:
            print(f"Warning: File '{src_file}' not found. Tag will be replaced with an error.", file=sys.stderr)
            tag.string = f"<!-- INJECTION ERROR: SOURCE FILE NOT FOUND: {src_file} -->"

    return "".join(str(c) for c in soup.root.contents)


def _get_system_context(repo_root: Path) -> str:
    """
    Gathers system-level context and formats it as an XML block.
    Currently captures the Git commit hash.
    """
    context_blocks = []
    # Capture Git commit hash
    try:
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=repo_root,
            text=True
        ).strip()
        context_blocks.append(f"<CommitHash>{commit_hash}</CommitHash>")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: Could not determine git commit hash. It will not be included in the context.", file=sys.stderr)

    if not context_blocks:
        return ""

    return f"<SystemContext>{''.join(context_blocks)}</SystemContext>\n"



def assemble_full_prompt(
    instance_path: Path,
    chosen_alias: str,
) -> str:

    """Main assembly function, now aware of target_repo_path."""
    repo_root = find_repo_root(instance_path)
    instance_meta, instance_content_block = load_artifact_with_frontmatter(instance_path)
    domain = instance_meta["domain"]

    system_context = _get_system_context(repo_root)
    instance_content_block = system_context + instance_content_block
    
    target_repo_rel_path = instance_meta.get("target_repo_path")
    if target_repo_rel_path:
        injection_base_path = (repo_root / target_repo_rel_path).resolve()
        if not injection_base_path.is_dir():
            raise FileNotFoundError(f"Target repository path does not exist: {injection_base_path}")
    else:
        injection_base_path = repo_root

    # Pass the correct base path to the injection function ---
    injected_instance_block = inject_knowledge_base(instance_content_block, injection_base_path)

    full_persona_content = assemble_persona_content(repo_root, domain, chosen_alias)

    persona_path = find_artifact(repo_root, domain, PERSONAS_DIR_NAME, chosen_alias)
    persona_meta, _ = load_artifact_with_frontmatter(persona_path)
    engine_version = persona_meta.get("engine_version", "v1")

    engine_path = repo_root / ENGINE_DIR_NAME / engine_version / "system_kernel.xml"
    engine_content = engine_path.read_text()

    final_instance_block = f"""
<Instance>
    <Runtime>
        <ActivatePersona alias="{chosen_alias}"/>
        {injected_instance_block}
    </Runtime>
</Instance>
"""
    return f"{engine_content}\n\n<PersonaLibrary>\n{full_persona_content}\n</PersonaLibrary>\n{final_instance_block}"


def generate_agent_manifest(repo_root: Path):
    """
    Scans all domains, parses persona metadata, and generates a markdown manifest.
    This replaces the complex Makefile target.
    """
    print("# PEL Agent Manifest\n")
    print("This file describes the specialized AI agents available in this Prompt Engineering Library.\n")
    all_personas_paths = (repo_root / DOMAINS_DIR_NAME).glob('**/*.persona.md')

    for persona_file in all_personas_paths:
        # Exclude deprecated personas from the manifest
        if 'deprecated' in str(persona_file):
            continue

        metadata, content = load_artifact_with_frontmatter(persona_file)
        
        alias = metadata.get("alias")
        title = metadata.get("title")
        
        if not alias or not title:
            continue

        # Extract primary directive and function from content
        directive_match = re.search(r'<primary_directive>(.*?)</primary_directive>', content, re.DOTALL)
        primary_directive = directive_match.group(1).strip() if directive_match else "N/A"

        print(f"## Agent: {title} ({alias})")
        print(f"-   **Function:** {primary_directive}")
                
        # Extract and format expected_artifacts
        expected_artifacts = metadata.get("expected_artifacts")
        if isinstance(expected_artifacts, list) and expected_artifacts:
            print("-   **Expected Inputs:**")
            for artifact in expected_artifacts:
                if isinstance(artifact, dict):
                    artifact_id = artifact.get('id', 'N/A')
                    artifact_type = artifact.get('type', 'N/A')
                    artifact_desc = artifact.get('description', 'No description.')
                    print(f"    -   `{artifact_id}` ({artifact_type}): {artifact_desc}")
        # --- ENHANCEMENT END ---
            
        print("---\n")


if __name__ == "__main__":


    parser = argparse.ArgumentParser(
        description="PEL Toolkit: Assemble prompts and manage library artifacts.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # Main command is the default
    parser.add_argument(
        "instance_file",
        nargs='?', # Make it optional
        type=Path,
        help="Path to the instance file to assemble a prompt."
    )
    # New flag for the manifest generator
    parser.add_argument(
        "--generate-manifest",
        action="store_true",
        help="Scan the library and generate the PEL_AGENTS.md manifest to stdout."
    )
    
    args = parser.parse_args()
    
    try:
        # --- STAGE 1: ALIGNMENT CHECK ---
        
        # Define repo_root at the beginning of the block
        repo_root = find_repo_root(Path.cwd())
        
        if args.generate_manifest:
            generate_agent_manifest(repo_root)
            sys.exit(0)

        if not args.instance_file:
            parser.error("The 'instance_file' argument is required unless using --generate-manifest.")
        
        instance_path = args.instance_file
        instance_meta, instance_mandate = load_artifact_with_frontmatter(instance_path)
        original_alias = instance_meta["persona_alias"]
        domain = instance_meta["domain"]

        all_personas_metadata = get_all_persona_metadata(repo_root, domain)
        
        # Only perform check if there are personas to check against
        suggested_alias = original_alias
        if all_personas_metadata:
            alignment_result = perform_alignment_check(instance_mandate, all_personas_metadata, original_alias)
            suggested_alias = alignment_result.get("suggested_persona_alias", original_alias)
            
        chosen_alias = original_alias
        if suggested_alias and suggested_alias.lower() != original_alias.lower():
            print(f"[ALIGNMENT_WARNING] The requested persona '{original_alias}' may not be the best fit.", file=sys.stderr)
            print(f"The persona '{suggested_alias}' appears to be a much stronger match.", file=sys.stderr)
            
            user_choice = input("Proceed with original, or switch? (original/switch): ").lower().strip()
            if user_choice == "switch":
                chosen_alias = suggested_alias
                print(f"Switching to persona '{chosen_alias}'.", file=sys.stderr)

        # --- STAGE 2: FINAL ASSEMBLY ---
        
        # The assemble_full_prompt function needs the instance path AND the chosen alias
        final_prompt = assemble_full_prompt(
            args.instance_file, 
            chosen_alias,
            )
        print(final_prompt)
        
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)