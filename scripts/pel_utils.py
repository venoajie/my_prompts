# /scripts/pel_utils.py

import yaml
import sys
from pathlib import Path

# --- Constants ---
ROOT_DIR = Path(__file__).parent.parent
PERSONA_FILENAME_PATTERNS = ["*.persona.md", "*.mixin.md"]

def load_config(config_path):
    """Loads and validates the configuration from a given path."""
    if not config_path.exists():
        print(f"FATAL: Configuration file not found at {config_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        if 'persona_types' not in config or 'validation_rules' not in config:
             raise KeyError("Config must contain 'persona_types' and 'validation_rules' sections.")
        return config
    except (yaml.YAMLError, KeyError) as e:
        print(f"FATAL: Error parsing or validating {config_path}: {e}", file=sys.stderr)
        sys.exit(1)

def find_all_personas(root_path):
    """Finds all persona and mixin files in templates and projects directories."""
    persona_files = []
    search_paths = [root_path / 'templates', root_path / 'projects']
    for path in search_paths:
        if path.exists():
            for pattern in PERSONA_FILENAME_PATTERNS:
                persona_files.extend(path.rglob(pattern))
    return persona_files