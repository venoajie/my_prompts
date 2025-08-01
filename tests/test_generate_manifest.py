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
    
    # Mock the module-level dependency
    mocker.patch.dict(sys.modules, {'validate_personas': mocker.MagicMock()})

    # Persona Files
    fs.create_file(
        "/app/projects/p1.persona.md",
        contents="---\nalias: p1\ntitle: Persona One\nstatus: active\ntype: specialized\n---\n<primary_directive>This is the main goal.</primary_directive>"
    )
    fs.create_file(
        "/app/projects/p2.persona.md",
        contents="---\nalias: p2\ntitle: Persona Two\nstatus: active\ntype: base\n---\ncontent" # Not specialized, should be ignored
    )
    fs.create_file(
        "/app/projects/p3.persona.md",
        contents="---\nalias: p3\ntitle: Persona Three\nstatus: deprecated\ntype: specialized\n---\ncontent" # Not active, should be ignored
    )
    fs.create_file(
        "/app/projects/p4.persona.md",
        contents="---\nalias: p4\ntitle: Persona Four\nstatus: active\ntype: specialized\n---\n<primary_directive>Another goal.</primary_directive>"
    )

@pytest.fixture
def mock_find_all_personas(mocker):
    """Mocks the find_all_personas function to return a predictable list."""
    paths = [
        Path("/app/projects/p1.persona.md"),
        Path("/app/projects/p2.persona.md"),
        Path("/app/projects/p3.persona.md"),
        Path("/app/projects/p4.persona.md"),
    ]
    # Since we mocked the module, we configure the mock on the module object
    validate_personas_mock = sys.modules['validate_personas']
    validate_personas_mock.find_all_personas.return_value = paths
    return validate_personas_mock.find_all_personas

class TestGenerateManifest:
    def test_main_generates_correct_manifest(self, mock_find_all_personas, fs):
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

        # Check sorting and content
        assert personas[0]['alias'] == 'p1'
        assert personas[0]['title'] == 'Persona One'
        assert personas[0]['description'] == 'This is the main goal.'

        assert personas[1]['alias'] == 'p4'
        assert personas[1]['title'] == 'Persona Four'
        assert personas[1]['description'] == 'Another goal.'

        # Verify the mock was called
        mock_find_all_personas.assert_called_once_with(Path("/app"))