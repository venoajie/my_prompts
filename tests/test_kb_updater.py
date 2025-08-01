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
    
    fs.create_dir(root_dir / "scripts")
    fs.create_dir(root_dir / "projects/proj1")
    
    fs.create_file(root_dir / "scripts/main.py", contents="import os")
    fs.create_file(root_dir / "projects/proj1/setup.sh", contents="echo 'hello'")
    fs.create_file(root_dir / "projects/proj1/data.txt", contents="ignore me")

    fs.create_dir(root_dir / "scripts/.venv/lib")
    fs.create_file(root_dir / "scripts/.venv/lib/ignored.py", contents="ignore")
    
    return root_dir

class TestKbUpdater:
    def test_main_generates_inventory(self, setup_kb_fs, mocker):
        # Arrange
        root_dir = setup_kb_fs
        
        # **FIX**: In addition to setting ROOT_DIR, we must also patch the
        # module-level constant KB_INVENTORY_FILE which was defined at import time.
        fake_inventory_path = root_dir / "knowledge_base_inventory.yml"
        mocker.patch('scripts.kb_updater.KB_INVENTORY_FILE', fake_inventory_path)
        
        mock_gen_meta = mocker.patch(
            'scripts.kb_updater.generate_metadata_for_file',
            side_effect=lambda path, content: {"src": str(path.relative_to(root_dir)), "description": f"Desc for {path.name}"}
        )

        # Act
        kb_updater.main()

        # Assert
        assert fake_inventory_path.exists()

        with open(fake_inventory_path, 'r') as f:
            inventory = yaml.safe_load(f)

        source_files = inventory['source_files']
        assert len(source_files) == 2
        
        assert source_files[0]['src'] == 'projects/proj1/setup.sh'
        assert source_files[1]['src'] == 'scripts/main.py'

        assert mock_gen_meta.call_count == 2