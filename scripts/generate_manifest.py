# /scripts/generate_manifest.py
# This script scans all active personas and creates a machine-readable manifest.

import yaml
from pathlib import Path
import sys
from datetime import datetime

# --- Configuration ---
ROOT_DIR = Path(__file__).parent.parent
# We need to import find_all_personas and ACTIVE_STATI from our validator
# to ensure we use the exact same logic for discovering active personas.
sys.path.append(str(ROOT_DIR / "scripts"))
try:
    from validate_personas import find_all_personas, ACTIVE_STATI
except ImportError:
    print("FATAL: Could not import from 'validate_personas.py'. Ensure the file exists in the 'scripts' directory.", file=sys.stderr)
    sys.exit(1)

def main():
    """Scans all active personas and generates a YAML manifest."""
    print("--- Generating Persona Manifest ---")
    all_persona_paths = find_all_personas(ROOT_DIR)
    
    manifest = {
        "version": "1.1",
        "generated_at_utc": datetime.utcnow().isoformat() + "Z",
        "personas": []
    }
    
    print(f"Found {len(all_persona_paths)} total persona files. Filtering for active, specialized agents...")
    
    for persona_path in all_persona_paths:
        try:
            with open(persona_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parts = content.split('---')
            if len(parts) < 3: continue
            
            data = yaml.safe_load(parts[1])
            if not isinstance(data, dict): continue
            
            # The manifest should only list runnable, specialist agents.
            # Base, mixin, and utility types are not user-selectable tasks.
            if data.get('status') in ACTIVE_STATI and data.get('type') == 'specialized':
                # Extract the primary directive, which describes the persona's function.
                body = "---".join(parts[2:])
                directive_start = body.find('<primary_directive>')
                directive_end = body.find('</primary_directive>')
                
                description = "No primary directive found."
                if directive_start != -1 and directive_end != -1:
                    # Clean up the extracted text
                    description = body[directive_start + 19 : directive_end].strip().replace('\n', ' ').replace('  ', ' ')

                manifest["personas"].append({
                    "alias": data.get("alias"),
                    "title": data.get("title"),
                    "description": description
                })
        except Exception as e:
            print(f"Warning: Could not process file {persona_path}. Reason: {e}", file=sys.stderr)
            continue
            
    # Sort the final list alphabetically by alias for consistent output
    manifest["personas"].sort(key=lambda x: x['alias'])
    
    output_file = ROOT_DIR / "persona_manifest.yml"
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(manifest, f, sort_keys=False, indent=2)
        
    print(f"✓ Persona manifest with {len(manifest['personas'])} agents successfully generated at: {output_file}")

if __name__ == "__main__":
    main()