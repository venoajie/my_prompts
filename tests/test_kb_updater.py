# /tests/test_kb_updater.py

import pytest
import sys
import yaml
from pathlib import Path
from scripts import kb_updater

@pytest.fixture
def setup_kb_fs(fs):
    """Setup a fake file system for knowledge base updater tests."""
    root_dir = Path("/app")
    kb_updater.ROOT_DIR = root_dir
    
    # Create scan directories and some files
    fs.create_dir(root_dir / "scripts")
    fs.create_dir(root_dir / "projects/proj1")
    
    fs.create_file(root_dir / "scripts/main.py", contents="import os")
    fs.create_file(root_dir / "projects/proj1/setup.sh", contents="echo 'hello'")
    fs.create_file(root_dir / "projects/proj1/data.txt", contents="ignore me") # Wrong extension

    # Create a file that should be excluded
    fs.create_dir(root_dir / "scripts/.venv/lib")
    fs.create_file(root_dir / "scripts/.venv/lib/ignored.py", contents="ignore")
    
    return root_dir

class TestKbUpdater:
    def test_main_generates_inventory(self, setup_kb_fs, mocker):
        # Arrange
        root_dir = setup_kb_fs
        
        # Mock the LLM call function
        mock_gen_meta = mocker.patch(
            'scripts.kb_updater.generate_metadata_for_file',
            # Use a side effect to return different data based on input
            side_effect=lambda path, content: {"src": str(path.relative_to(root_dir)), "description": f"Desc for {path.name}"}
        )

        # Act
        kb_updater.main()

        # Assert
        output_file = root_dir / "knowledge_base_inventory.yml"
        assert output_file.exists()

        with open(output_file, 'r') as f:
            inventory = yaml.safe_load(f)

        source_files = inventory['source_files']
        assert len(source_files) == 2
        
        # Check sorting
        assert source_files[0]['src'] == 'projects/proj1/setup.sh'
        assert source_files[0]['description'] == 'Desc for setup.sh'
        
        assert source_files[1]['src'] == 'scripts/main.py'
        assert source_files[1]['description'] == 'Desc for main.py'

        # Verify mock calls
        assert mock_gen_meta.call_count == 2
        # Check that it wasn't called for the ignored file
        for call in mock_gen_meta.call_args_list:
            path_arg = call.args[0]
            assert ".venv" not in str(path_arg)