# /tests/test_generate_manifest.py

import pytest
import sys
import yaml
from pathlib import Path
from scripts import generate_manifest

@pytest.fixture(autouse=True)
def setup_manifest_env(fs, mocker):
    """Setup a fake file system and mock dependencies."""
    fs.create_dir("/app")
    generate_manifest.ROOT_DIR = Path("/app")
    mocker.patch.dict(sys.modules, {'validate_personas': mocker.MagicMock()})

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
    def test_main_generates_correct_manifest(self, fs, mocker):
        # Arrange
        # **FIX**: Patch the name 'find_all_personas' directly in the namespace
        # of the module under test. This is the correct way to mock an import.
        mock_paths = [
            Path("/app/projects/p1.persona.md"),
            Path("/app/projects/p2.persona.md"),
            Path("/app/projects/p3.persona.md"),
            Path("/app/projects/p4.persona.md"),
        ]
        mock_find_personas = mocker.patch(
            'scripts.generate_manifest.find_all_personas',
            return_value=mock_paths
        )

        # Act
        generate_manifest.main()

        # Assert
        output_file = Path("/app/persona_manifest.yml")
        assert output_file.exists()

        with open(output_file, 'r') as f:
            manifest = yaml.safe_load(f)

        assert manifest['version'] == "1.1"
        assert "generated_at_utc" in manifest
        
        personas = manifest['personas']
        assert len(personas) == 2

        assert personas[0]['alias'] == 'p1'
        assert personas[1]['alias'] == 'p4'

        # Verify the mock was called
        mock_find_personas.assert_called_once_with(Path("/app"))