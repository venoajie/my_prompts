# /scripts/kb_updater.py
# Version 2.0 (YAML-based & Integrated)

import os
import sys
import yaml
from pathlib import Path
# Assuming you have a way to call an LLM API
# import llm_api 

# --- Configuration ---
ROOT_DIR = Path(__file__).parent.parent
# The persona used to generate the description
METADATA_GENERATOR_PERSONA = ROOT_DIR / "projects/prompt_engineering/personas/specialized/kb-metadata-generator.persona.md"
# The final output file
KB_INVENTORY_FILE = ROOT_DIR / "knowledge_base_inventory.yml"
# Directories to scan for source code
SCAN_DIRECTORIES = ["scripts", "projects"]
# File extensions to process
SOURCE_EXTENSIONS = [".py", ".sh", ".sql"]

def generate_metadata_for_file(file_path, file_content):
    """
    (Simulated LLM Call)
    Constructs a prompt and simulates a call to an LLM to get a description.
    In a real implementation, this would call an actual API.
    """
    print(f"  -> Generating metadata for {file_path.name}...")
    
    # --- This is where the actual LLM call would go ---
    # persona_prompt = METADATA_GENERATOR_PERSONA.read_text()
    # full_prompt = f"{persona_prompt}\n\n<file_path>{file_path}</file_path>\n<file_content>{file_content}</file_content>"
    # response_json = llm_api.generate(full_prompt)
    # metadata = json.loads(response_json)
    # return metadata
    # --- Simulation for this example ---
    file_id = file_path.name.upper().replace('.', '_') + "_SOURCE"
    return {
        "id": file_id,
        "src": str(file_path.relative_to(ROOT_DIR)),
        "description": f"A source file located at {file_path.relative_to(ROOT_DIR)} responsible for key system logic."
    }

def main():
    """Scans source directories, generates metadata, and writes the YAML inventory."""
    print(f"--- Starting Knowledge Base Inventory Update ---")
    
    all_metadata = []
    
    for directory in SCAN_DIRECTORIES:
        scan_path = ROOT_DIR / directory
        print(f"Scanning directory: {scan_path}")
        
        for extension in SOURCE_EXTENSIONS:
            for file_path in scan_path.rglob(f"**/*{extension}"):
                # Simple exclusion for safety
                if ".venv/" in str(file_path) or "build/" in str(file_path):
                    continue
                
                file_content = file_path.read_text(encoding='utf-8')
                metadata = generate_metadata_for_file(file_path, file_content)
                all_metadata.append(metadata)

    # Sort the final list alphabetically by source path for consistency
    all_metadata.sort(key=lambda x: x['src'])
    
    final_output = {
        "source_files": all_metadata
    }
    
    with open(KB_INVENTORY_FILE, 'w', encoding='utf-8') as f:
        yaml.dump(final_output, f, sort_keys=False, indent=2)
        
    print(f"\n✓ Knowledge base inventory successfully updated at: {KB_INVENTORY_FILE}")

if __name__ == "__main__":
    main()