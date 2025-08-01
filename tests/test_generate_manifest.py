# /tests/test_generate_manifest.py

import pytest
import sys
import yaml
from pathlib import Path
from scripts import generate_manifest

@pytest.fixture
def setup_manifest_fs(fs):
    """Setup a fake file system with persona files for testing."""
    # This test no longer needs to manipulate the module-level ROOT_DIR
    # because the code under test is now pure.
    fs.create_file(
        "/app/projects/p1.persona.md",
        contents="---\nalias: p1\ntitle: Persona One\nstatus: active\ntype: specialized\n---\n<primary_directive>This is the main goal.</primary_directive>"
    )
    fs.create_file(
        "/app/projects/p2.persona.md",
        contents="---\nalias: p2\ntitle: Persona Two\nstatus: active\ntype: base\n---\ncontent"
    )
    fs.create_file(
        "/app/projects/p3.persona.md",
        contents="---\nalias: p3\ntitle: Persona Three\nstatus: deprecated\ntype: specialized\n---\ncontent"
    )
    fs.create_file(
        "/app/projects/p4.persona.md",
        contents="---\nalias: p4\ntitle: Persona Four\nstatus: active\ntype: specialized\n---\n<primary_directive>Another goal.</primary_directive>"
    )

class TestGenerateManifest:
    def test_main_generates_correct_manifest(self, setup_manifest_fs, mocker, fs):
        # Arrange
        # We need to set the ROOT_DIR for the find_all_personas mock and output file path
        generate_manifest.ROOT_DIR = Path("/app")
        
        mock_paths = [
            Path("/app/projects/p1.persona.md"),
            Path("/app/projects/p2.persona.md"),
            Path("/app/projects/p3.persona.md"),
            Path("/app/projects/p4.persona.md"),
        ]
        # **FIX**: Mock the function in its new, correct location in pel_utils
        mocker.patch('scripts.pel_utils.find_all_personas', return_value=mock_paths)
        
        # Define the active stati to be passed into main()
        active_stati_for_test = ["active", "beta"]

        # Act
        # **FIX**: Pass the required `active_stati` argument to the main function.
        generate_manifest.main(active_stati=active_stati_for_test)

        # Assert
        output_file = Path("/app/persona_manifest.yml")
        assert output_file.exists()

        with open(output_file, 'r') as f:
            manifest = yaml.safe_load(f)

        assert manifest['version'] == "1.1"
        personas = manifest['personas']
        assert len(personas) == 2

        assert personas[0]['alias'] == 'p1'
        assert personas[1]['alias'] == 'p4'