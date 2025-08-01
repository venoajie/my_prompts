# /scripts/generate_manifest.py
# Version: 3.2 (Absolute Imports)

import yaml
import sys
from datetime import datetime, timezone

# Import from the new shared utilities module using an absolute path
from scripts.pel_utils import load_config, find_all_personas, ROOT_DIR

# --- Main Logic ---
def main(active_stati):
    # (The rest of this file's content remains unchanged)
    print("--- Generating Persona Manifest ---")
    all_persona_paths = find_all_personas(ROOT_DIR)
    manifest = {
        "version": "1.1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "personas": []
    }
    print(f"Found {len(all_persona_paths)} total persona files. Filtering for active, specialized agents...")
    for persona_path in all_persona_paths:
        try:
            content = persona_path.read_text(encoding='utf-8')
            parts = content.split('---')
            if len(parts) < 3: continue
            data = yaml.safe_load(parts[1])
            if not isinstance(data, dict): continue
            if data.get('status') in active_stati and data.get('type') == 'specialized':
                body = "---".join(parts[2:])
                directive_start = body.find('<primary_directive>')
                directive_end = body.find('</primary_directive>')
                description = "No primary directive found."
                if directive_start != -1 and directive_end != -1:
                    description = body[directive_start + 19 : directive_end].strip().replace('\n', ' ').replace('  ', ' ')
                manifest["personas"].append({
                    "alias": data.get("alias"),
                    "title": data.get("title"),
                    "description": description
                })
        except Exception as e:
            print(f"Warning: Could not process file {persona_path}. Reason: {e}", file=sys.stderr)
            continue
    manifest["personas"].sort(key=lambda x: (x.get('alias') or ''))
    output_file = ROOT_DIR / "persona_manifest.yml"
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(manifest, f, sort_keys=False, indent=2)
    print(f"✓ Persona manifest with {len(manifest['personas'])} agents successfully generated at: {output_file}")
    return 0

if __name__ == "__main__":
    print("Loading configuration for command-line execution...")
    config = load_config(ROOT_DIR / "pel.config.yml")
    active_stati_from_config = config.get('validation_rules', {}).get('active_stati', ['active'])
    error_count = main(active_stati_from_config)
    sys.exit(error_count)