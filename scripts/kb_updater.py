# pseudocode
import os
from pathlib import Path
import llm_api # Your preferred LLM API library

# 1. Define the persona for the API call
METADATA_GENERATOR_PROMPT = Path("domains/prompt_engineering/personas/kb-metadata-generator.persona.md").read_text()

def update_knowledge_base(scan_directory: str):
    # 2. Scan the directory for source files
    for filepath in Path(scan_directory).rglob('*.py'):
        print(f"Processing {filepath}...")
        file_content = filepath.read_text()
        
        # 3. Construct the API request
        # The prompt will be a combination of the persona and the file content
        prompt = f"{METADATA_GENERATOR_PROMPT}\n\n<File path='{filepath}'>\n{file_content}\n</File>"
        
        # 4. Call the LLM API
        response_json_str = llm_api.generate(prompt)
        
        # 5. Parse the JSON response
        metadata = json.loads(response_json_str)
        
        # 6. Generate the XML tag from the structured JSON
        xml_tag = f'<Document id="{metadata["id"]}" src="{metadata["src"]}" version="1.0" description="{metadata["description"]}"/>'
        
        # 7. Update a central knowledge base file
        # This logic would find and replace the line for this ID or append it.
        update_kb_file("knowledge_base.xml", metadata["id"], xml_tag)

if __name__ == "__main__":
    update_knowledge_base("src/")