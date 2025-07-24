
---

### **Artifact 2: `scripts/assemble_prompt.py`**

This Python script is the operational heart of your library. It requires no external libraries beyond the standard Python installation.

```python
#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
import re

# --- Configuration ---
# These constants define the structure of the repository.
SYSTEM_DIR_NAME = "system"
CORE_PROMPT_FILE = "PEL_SYSTEM_CORE_V1.0.prompt"
DOMAINS_DIR_NAME = "domains"
KB_DIR_NAME = "knowledge_base"

def find_repo_root(start_path: Path) -> Path:
    """Traverse up from the start_path to find the repository root."""
    current = start_path.resolve()
    while current != current.parent:
        if (current / SYSTEM_DIR_NAME).is_dir() and (current / DOMAINS_DIR_NAME).is_dir():
            return current
        current = current.parent
    raise FileNotFoundError("Could not find repository root. Ensure 'system/' and 'domains/' directories exist.")

def assemble_prompt(instance_path: Path) -> str:
    """
    Assembles a complete LLM prompt by combining the System Core, the instance
    prompt, and injecting content from the knowledge base.

    Args:
        instance_path: The path to the instance prompt file.

    Returns:
        A single string containing the fully assembled prompt.
    """
    if not instance_path.is_file():
        print(f"Error: Instance file not found at '{instance_path}'", file=sys.stderr)
        sys.exit(1)

    try:
        repo_root = find_repo_root(instance_path)
        
        # 1. Load the System Core
        core_path = repo_root / SYSTEM_DIR_NAME / CORE_PROMPT_FILE
        if not core_path.is_file():
            print(f"Error: System Core file not found at '{core_path}'", file=sys.stderr)
            sys.exit(1)
        core_content = core_path.read_text()

        # 2. Load the instance prompt content
        instance_content = instance_path.read_text()

        # 3. Find the domain's knowledge base directory
        # Assumes instance file is at .../domains/[domain_name]/instances/[file]
        domain_root = instance_path.parent.parent
        kb_path = domain_root / KB_DIR_NAME
        
        if not kb_path.is_dir():
            print(f"Warning: Knowledge base directory not found at '{kb_path}'. No documents will be injected.", file=sys.stderr)

        # 4. Inject documents from the knowledge base
        def inject_document(match):
            """Replacement function for re.sub to inject file content."""
            full_tag = match.group(0)
            src_file_name = match.group(2)
            
            # Reconstruct the opening tag without the self-closing part
            opening_tag = match.group(1).rstrip('/>') + '>'
            
            doc_path = kb_path / src_file_name
            if doc_path.is_file():
                doc_content = doc_path.read_text()
                # Escape XML special characters in the content to be safe
                # For this specific use case, we assume content is code in a markdown block,
                # which is generally safe. For true XML safety, a library would be better.
                return f"{opening_tag}\n```\n{doc_content}\n```\n</Document>"
            else:
                print(f"Warning: Knowledge base file '{src_file_name}' not found at '{doc_path}'. Tag will be left empty.", file=sys.stderr)
                return f"{opening_tag}</Document>"

        # Regex to find <Document ... src="..." /> tags
        # It captures the full opening tag (group 1) and the src value (group 2)
        doc_regex = re.compile(r'(<Document[^>]*?src="([^"]+)"[^>]*?/>)')
        processed_instance_content = doc_regex.sub(inject_document, instance_content)

        # 5. Combine and return
        return f"{core_content}\n\n{processed_instance_content}"

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Assemble a complete LLM prompt from the Prompt Engineering Library.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "instance_file",
        type=str,
        help="Path to the instance prompt file (e.g., 'domains/coding/instances/my_task.prompt')."
    )
    args = parser.parse_args()
    
    instance_path = Path(args.instance_file)
    
    final_prompt = assemble_prompt(instance_path)
    print(final_prompt)