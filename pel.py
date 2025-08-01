# /pel.py
# Unified Command-Line Entry Point for the Prompt Engineering Library Toolkit

import sys
import argparse
from pathlib import Path

# --- 1. Environment Setup ---
# Add the 'scripts' directory to the Python path. This is the ONLY place
# in the entire system where sys.path is manipulated.
ROOT_DIR = Path(__file__).parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR.resolve()))

# --- 2. Import Tools ---
# These imports will now work reliably because the path is set.
from pel_utils import load_config
import validate_personas
import pel_toolkit
import generate_manifest

def main():
    """Parses command-line arguments and calls the appropriate tool."""
    parser = argparse.ArgumentParser(description="Prompt Engineering Library (PEL) Toolkit")
    subparsers = parser.add_subparsers(dest="command", required=True, help="The tool to run.")

    # --- 'validate' command ---
    validate_parser = subparsers.add_parser("validate", help="Validate all active personas in the library.")
    
    # --- 'assemble' command ---
    assemble_parser = subparsers.add_parser("assemble", help="Assemble a final prompt from an instance file.")
    assemble_parser.add_argument("instance_file", type=Path, help="Path to the instance file to assemble.")

    # --- 'generate-manifest' command ---
    manifest_parser = subparsers.add_parser("generate-manifest", help="Generate the persona_manifest.yml file.")

    args = parser.parse_args()

    # --- 3. Execute Command ---
    if args.command == "validate":
        config = load_config(ROOT_DIR / "pel.config.yml")
        exit_code = validate_personas.main(config)
        sys.exit(exit_code)

    elif args.command == "assemble":
        # pel_toolkit.main expects a string path
        pel_toolkit.main(str(args.instance_file))

    elif args.command == "generate-manifest":
        generate_manifest.main()

if __name__ == "__main__":
    main()