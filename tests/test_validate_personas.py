# /tests/test_validate_personas.py

import pytest
import sys
import yaml
from pathlib import Path
from scripts import validate_personas

# This is our mock configuration. We pass it directly to the functions.
# No file system or reloading is needed for these tests.
@pytest.fixture
def mock_config():
    return {
        "persona_types": {
            "specialized": {"required_keys": ["alias", "title", "status", "type", "expected_artifacts"]},
            "base": {"required_keys": ["alias", "title", "status", "type"]},
            "mixin": {"required_keys": ["status", "type"]}
        },
        "validation_rules": {
            "active_stati": ["active", "beta"]
        }
    }

class TestValidatePersonaFile:
    def test_valid_specialized_persona(self, mock_config):
        data = {
            "alias": "test-1", "title": "Test Persona", "status": "active", "type": "specialized",
            "expected_artifacts": [{"id": "out", "type": "code", "description": "A valid output file."}]
        }
        is_valid, msg = validate_personas.validate_persona_file(data, mock_config['persona_types'])
        assert is_valid
        assert "OK" in msg

    def test_missing_required_key(self, mock_config):
        data = {"alias": "test-1", "status": "active", "type": "base"} # Missing title
        is_valid, msg = validate_personas.validate_persona_file(data, mock_config['persona_types'])
        assert not is_valid
        assert "Missing required keys" in msg

    def test_invalid_type(self, mock_config):
        data = {"alias": "test-1", "status": "active", "type": "invalid_type"}
        is_valid, msg = validate_personas.validate_persona_file(data, mock_config['persona_types'])
        assert not is_valid
        assert "Invalid persona type" in msg

class TestMainValidation:
    @pytest.fixture
    def setup_fs_for_main(self, fs):
        # We still need a fake file system for the persona files themselves.
        validate_personas.ROOT_DIR = Path("/app")
        fs.create_file("/app/projects/p1.persona.md", contents="---\nalias: p1\ntitle: P1\nstatus: active\ntype: base\n---\ncontent")
        fs.create_file("/app/projects/p2.persona.md", contents="---\nalias: p2\ntitle: P2\nstatus: beta\ntype: base\n---\ncontent")
        fs.create_file("/app/projects/p3.persona.md", contents="---\nalias: p3\nstatus: active\ntype: base\n---\ncontent") # Invalid
        fs.create_file("/app/projects/p4.persona.md", contents="---\nalias: p4\ntitle: P4\nstatus: deprecated\ntype: base\n---\ncontent") # Skipped
        fs.create_file("/app/projects/p5.persona.md", contents="no frontmatter") # Invalid

    def test_main_summary(self, setup_fs_for_main, mock_config, capsys):
        error_count = validate_personas.main(mock_config)
        
        captured = capsys.readouterr()
        output = captured.out
        
        assert error_count == 2
        assert "2 passed" in output
        assert "2 failed" in output
        assert "1 skipped" in output

    def test_main_handles_no_personas_found(self, mock_config, capsys, mocker):
        mocker.patch('scripts.validate_personas.find_all_personas', return_value=[])
        error_count = validate_personas.main(mock_config)
        captured = capsys.readouterr()
        assert error_count == 0
        assert "No persona files found" in captured.out

# Tests for the config loader now test a small, isolated function
class TestConfigLoader:
    def test_load_config_success(self, fs):
        config_path = Path("/app/pel.config.yml")
        config_data = {"persona_types": {}, "validation_rules": {}}
        fs.create_file(config_path, contents=yaml.dump(config_data))
        
        loaded = validate_personas.load_config(config_path)
        assert loaded == config_data

    def test_load_config_file_not_found(self, capsys):
        with pytest.raises(SystemExit) as e:
            validate_personas.load_config(Path("/nonexistent/pel.config.yml"))
        
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "FATAL: Configuration file not found" in captured.err

    def test_load_config_bad_yaml(self, fs, capsys):
        config_path = Path("/app/pel.config.yml")
        fs.create_file(config_path, contents="key: 'unclosed")
        
        with pytest.raises(SystemExit) as e:
            validate_personas.load_config(config_path)
            
        assert e.value.code == 1
        captured = capsys.readouterr()
        assert "FATAL: Error parsing" in captured.err