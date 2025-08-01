# /tests/test_generate_manifest.py

import pytest
import sys
import yaml
from pathlib import Path
from scripts import generate_manifest

# This fixture sets up a file system with persona files for testing.
@pytest.fixture
def setup_manifest_fs(fs):
    generate_manifest.ROOT_DIR = Path("/app")
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
    def test_main_generates_correct_manifest(self, setup_manifest_fs, mocker):
        # Arrange
        # We only need to mock the find_all_personas function.
        # The main logic now takes its config as a direct argument.
        mock_paths = [
            Path("/app/projects/p1.persona.md"),
            Path("/app/projects/p2.persona.md"),
            Path("/app/projects/p3.persona.md"),
            Path("/app/projects/p4.persona.md"),
        ]
        mocker.patch('scripts.generate_manifest.find_all_personas', return_value=mock_paths)
        
        # Define the active stati to be passed into main()
        active_stati_for_test = ["active", "beta"]

        # Act
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