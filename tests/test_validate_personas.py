# /tests/test_validate_personas.py

import pytest
import sys
import yaml
from pathlib import Path
from scripts import validate_personas

@pytest.fixture(autouse=True)
def setup_validation_config(fs):
    """Sets up a fake config file for all validation tests."""
    config_data = {
        "persona_types": {
            "specialized": {"required_keys": ["alias", "title", "status", "type", "expected_artifacts"]},
            "base": {"required_keys": ["alias", "title", "status", "type"]},
            "mixin": {"required_keys": ["status", "type"]}
        },
        "validation_rules": {
            "active_stati": ["active", "beta"]
        }
    }
    fs.create_file("/app/pel.config.yml", contents=yaml.dump(config_data))
    # Set the module-level variable to use the fake file system path
    validate_personas.ROOT_DIR = Path("/app")
    validate_personas.CONFIG_FILE = Path("/app/pel.config.yml")
    # Reload constants from the fake config
    validate_personas.PEL_CONFIG = config_data
    validate_personas.PERSONA_TYPE_RULES = config_data['persona_types']
    validate_personas.VALIDATION_RULES = config_data['validation_rules']
    validate_personas.ACTIVE_STATI = config_data['validation_rules']['active_stati']

class TestFindAllPersonas:
    def test_finds_all_persona_types(self, fs):
        fs.create_file("/app/projects/proj1/p1.persona.md")
        fs.create_file("/app/projects/proj1/m1.mixin.md")
        fs.create_file("/app/templates/temp1/p2.persona.md")
        fs.create_file("/app/templates/temp1/other.txt") # Should be ignored

        files = validate_personas.find_all_personas(Path("/app"))
        assert len(files) == 3
        paths = [str(f) for f in files]
        assert "/app/projects/proj1/p1.persona.md" in paths
        assert "/app/projects/proj1/m1.mixin.md" in paths
        assert "/app/templates/temp1/p2.persona.md" in paths

    def test_handles_missing_directories(self, fs):
        # Only create a projects dir, no templates dir
        fs.create_file("/app/projects/proj1/p1.persona.md")
        files = validate_personas.find_all_personas(Path("/app"))
        assert len(files) == 1


class TestValidatePersonaFile:
    def test_valid_specialized_persona(self):
        data = {
            "alias": "test-1",
            "title": "Test Persona",
            "status": "active",
            "type": "specialized",
            "expected_artifacts": [
                {"id": "out", "type": "code", "description": "A valid output file."}
            ]
        }
        is_valid, msg = validate_personas.validate_persona_file(data)
        assert is_valid
        assert "OK" in msg

    def test_missing_required_key(self):
        data = {"alias": "test-1", "status": "active", "type": "base"} # Missing title
        is_valid, msg = validate_personas.validate_persona_file(data)
        assert not is_valid
        assert "Missing required keys" in msg
        assert "title" in msg

    def test_invalid_type(self):
        data = {"alias": "test-1", "status": "active", "type": "invalid_type"}
        is_valid, msg = validate_personas.validate_persona_file(data)
        assert not is_valid
        assert "Invalid persona type" in msg

    def test_invalid_expected_artifacts(self):
        data = {
            "alias": "test-1", "title": "Test", "status": "active", "type": "specialized",
            "expected_artifacts": [{"id": "a", "type": "b", "description": "a file"}] # Generic description
        }
        is_valid, msg = validate_personas.validate_persona_file(data)
        assert not is_valid
        assert "has a generic description" in msg

class TestMainValidation:
    @pytest.fixture
    def setup_fs_for_main(self, fs):
        # Valid active persona
        fs.create_file("/app/projects/p1.persona.md", contents="---\nalias: p1\ntitle: P1\nstatus: active\ntype: base\n---\ncontent")
        # Valid beta persona
        fs.create_file("/app/projects/p2.persona.md", contents="---\nalias: p2\ntitle: P2\nstatus: beta\ntype: base\n---\ncontent")
        # Invalid persona (missing key)
        fs.create_file("/app/projects/p3.persona.md", contents="---\nalias: p3\nstatus: active\ntype: base\n---\ncontent")
        # Skipped persona
        fs.create_file("/app/projects/p4.persona.md", contents="---\nalias: p4\ntitle: P4\nstatus: deprecated\ntype: base\n---\ncontent")
        # File with no frontmatter
        fs.create_file("/app/projects/p5.persona.md", contents="no frontmatter")

    def test_main_success_and_failure_summary(self, setup_fs_for_main, capsys, mocker):
        mocker.patch('sys.exit')
        validate_personas.main()
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert "[PASS]" in output
        assert "[FAIL]" in output
        assert "[SKIP]" in output
        assert "Successful: 2" in output
        assert "Failed:     2" in output # p3 (missing key) + p5 (no frontmatter)
        assert "Skipped:    1" in output
        sys.exit.assert_called_once_with(1)

    def test_main_all_valid_exits_zero(self, fs, capsys, mocker):
        fs.create_file("/app/projects/p1.persona.md", contents="---\nalias: p1\ntitle: P1\nstatus: active\ntype: base\n---\ncontent")
        mocker.patch('sys.exit')

        validate_personas.main()
        
        captured = capsys.readouterr()
        assert "All active personas are valid." in captured.out
        sys.exit.assert_called_once_with(0)