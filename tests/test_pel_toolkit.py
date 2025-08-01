# /tests/test_pel_toolkit.py
# Version: 1.3 (Final API Compatibility Fix)

import pytest
import sys
import yaml
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Module under test
from scripts import pel_toolkit

# --- Test Setup & Fixtures ---

@pytest.fixture(autouse=True)
def setup_pel_toolkit_config(fs, mocker):
    """Set up a default mock environment for all tests."""
    fs.create_dir("/app")
    pel_toolkit.ROOT_DIR = Path("/app")
    pel_toolkit.CONFIG_FILE = pel_toolkit.ROOT_DIR / "pel.config.yml"
    pel_toolkit.PROJECTS_DIR_NAME = "projects"
    pel_toolkit.TEMPLATES_DIR_NAME = "templates"
    pel_toolkit.PERSONAS_DIR_NAME = "personas"
    pel_toolkit.META_FILENAME = ".domain_meta"

    pel_toolkit.GLOBAL_PERSONAS_PATH = pel_toolkit.ROOT_DIR / "projects/prompt_engineering/personas"
    fs.create_dir(pel_toolkit.GLOBAL_PERSONAS_PATH)

    config_data = {'resolution_paths': ['project', 'template']}
    fs.create_file(pel_toolkit.CONFIG_FILE, contents=yaml.dump(config_data))

    with open(pel_toolkit.CONFIG_FILE, 'r') as f:
        pel_toolkit.PEL_CONFIG = yaml.safe_load(f)

    mocker.patch.dict(sys.modules, {'validate_personas': mocker.MagicMock()})


# --- Test Cases ---

class TestFindProjectRoot:
    def test_find_project_root_success(self, fs):
        project_root = pel_toolkit.ROOT_DIR / "projects/my_proj"
        instance_path = project_root / "instances/test.md"
        fs.create_file(project_root / pel_toolkit.META_FILENAME)
        fs.create_file(instance_path)
        found_root = pel_toolkit.find_project_root(instance_path)
        assert found_root == project_root

    def test_find_project_root_not_found(self, fs):
        instance_path = pel_toolkit.ROOT_DIR / "projects/my_proj/instances/test.md"
        fs.create_file(instance_path)
        found_root = pel_toolkit.find_project_root(instance_path)
        assert found_root is None

class TestGetTemplatePath:
    def test_get_template_path_success(self, fs):
        project_root = pel_toolkit.ROOT_DIR / "projects/my_proj"
        meta_content = yaml.dump({'template': 'base_template'})
        fs.create_file(project_root / pel_toolkit.META_FILENAME, contents=meta_content)
        fs.create_dir(pel_toolkit.ROOT_DIR / "templates/base_template")
        template_path = pel_toolkit.get_template_path(project_root)
        expected_path = pel_toolkit.ROOT_DIR / "templates/base_template"
        assert template_path == expected_path

    def test_get_template_path_no_template_key(self, fs):
        project_root = pel_toolkit.ROOT_DIR / "projects/my_proj"
        fs.create_file(project_root / pel_toolkit.META_FILENAME, contents="some: data")
        template_path = pel_toolkit.get_template_path(project_root)
        assert template_path is None

class TestFindPersonaFile:
    @pytest.fixture
    def file_structure(self, fs):
        project_root = pel_toolkit.ROOT_DIR / "projects/proj_a"
        fs.create_dir(project_root / "personas")
        template_path = pel_toolkit.ROOT_DIR / "templates/template_a"
        fs.create_dir(template_path / "personas")
        return project_root, template_path

    def test_find_in_project_scope(self, fs, file_structure):
        project_root, template_path = file_structure
        fs.create_file(project_root / "personas" / "coder.persona.md")
        found = pel_toolkit.find_persona_file("coder", project_root, template_path)
        assert found == project_root / "personas" / "coder.persona.md"

class TestAssemblePersonaContent:
    @pytest.fixture
    def file_structure(self, fs):
        project_root = pel_toolkit.ROOT_DIR / "projects/proj_a"
        template_path = pel_toolkit.ROOT_DIR / "templates/template_a"
        fs.create_dir(project_root / "personas")
        fs.create_dir(template_path / "personas")
        return project_root, template_path

    def test_assemble_simple_persona(self, fs, file_structure):
        project_root, template_path = file_structure
        persona_path = project_root / "personas" / "simple.persona.md"
        fs.create_file(persona_path, contents="---\nkey: val\n---\nSimple content")
        content = pel_toolkit.assemble_persona_content(persona_path, project_root, template_path)
        assert content == "Simple content"

    def test_assemble_with_inheritance(self, fs, file_structure, mocker):
        project_root, template_path = file_structure
        child_path = project_root / "personas" / "child.persona.md"
        child_content = "---\ninherits_from: parent\n---\nChild body."
        fs.create_file(child_path, contents=child_content)
        parent_path = template_path / "personas" / "parent.persona.md"
        parent_content = "---\n---\nParent body."
        fs.create_file(parent_path, contents=parent_content)
        mocker.patch('scripts.pel_toolkit.find_persona_file', return_value=parent_path)
        content = pel_toolkit.assemble_persona_content(child_path, project_root, template_path)
        assert content == "Parent body.\nChild body."

class TestInjectFileContent:
    def test_inject_file_success(self, fs):
        injected_file = pel_toolkit.ROOT_DIR / "src/code.py"
        fs.create_file(injected_file, contents="def hello(): pass")
        mandate_body = 'Here is the code:\n<Inject src="src/code.py" />'
        result = pel_toolkit.inject_file_content(mandate_body)
        assert result == "Here is the code:\ndef hello(): pass"

class TestIsManifestStale:
    @pytest.fixture
    def setup_stale_check(self, fs):
        root_dir = pel_toolkit.ROOT_DIR
        manifest_path = root_dir / "persona_manifest.yml"
        persona_path = root_dir / "projects/prompt_engineering/personas/p1.persona.md"
        fs.create_file(persona_path)
        validate_personas_mock = sys.modules['validate_personas']
        validate_personas_mock.find_all_personas.return_value = [persona_path]
        now = datetime(2023, 10, 27, 12, 0, 0, tzinfo=timezone.utc)
        return manifest_path, persona_path, now

    def test_manifest_does_not_exist(self, fs, setup_stale_check):
        manifest_path, _, _ = setup_stale_check
        is_stale, reason = pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)
        assert is_stale
        assert reason == "Manifest file does not exist."

    def test_manifest_is_up_to_date(self, fs, setup_stale_check):
        manifest_path, persona_path, now = setup_stale_check
        manifest_time = now
        persona_mod_time = (now - timedelta(minutes=10)).timestamp()
        
        # **FIX**: Use the correct pyfakefs API to set file modification time.
        fs.get_object(persona_path).st_mtime = persona_mod_time

        manifest_content = yaml.dump({"generated_at_utc": manifest_time.isoformat()})
        fs.create_file(manifest_path, contents=manifest_content)
        is_stale, reason = pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)
        assert not is_stale
        assert reason == "Manifest is up-to-date."

    def test_manifest_is_stale(self, fs, setup_stale_check):
        manifest_path, persona_path, now = setup_stale_check
        manifest_time = now - timedelta(minutes=10)
        persona_mod_time = now.timestamp()
        
        # **FIX**: Use the correct pyfakefs API.
        fs.get_object(persona_path).st_mtime = persona_mod_time

        manifest_content = yaml.dump({"generated_at_utc": manifest_time.isoformat()})
        fs.create_file(manifest_path, contents=manifest_content)
        is_stale, reason = pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)
        assert is_stale
        assert "was modified after the manifest was generated" in reason

    def test_manifest_grace_period(self, fs, setup_stale_check):
        manifest_path, persona_path, now = setup_stale_check
        manifest_time = now
        persona_mod_time = (now + timedelta(seconds=1)).timestamp()

        # **FIX**: Use the correct pyfakefs API.
        fs.get_object(persona_path).st_mtime = persona_mod_time

        manifest_content = yaml.dump({"generated_at_utc": manifest_time.isoformat()})
        fs.create_file(manifest_path, contents=manifest_content)
        is_stale, _ = pel_toolkit.is_manifest_stale(manifest_path, pel_toolkit.ROOT_DIR)
        assert not is_stale

class TestMainFunction:
    @pytest.fixture
    def full_structure(self, fs):
        project_root = pel_toolkit.ROOT_DIR / "projects/proj_a"
        fs.create_file(
            project_root / pel_toolkit.META_FILENAME,
            contents=yaml.dump({'template': 'template_a'})
        )
        fs.create_file(
            project_root / "personas/coder.persona.md",
            contents="---\n---\nProject Coder Persona"
        )
        instance_path = project_root / "instances/my_task.md"
        instance_content = """---
persona_alias: coder
---
This is the mandate body.
"""
        fs.create_file(instance_path, contents=instance_content)
        return instance_path

    def test_main_success_flow(self, fs, full_structure, capsys):
        instance_path = full_structure
        pel_toolkit.main(str(instance_path))
        captured = capsys.readouterr()
        output = captured.out
        assert "<SystemPrompt>" in output
        assert "<PersonaLibrary>" in output
        assert "Project Coder Persona" in output
        assert captured.err == ""

    def test_main_stale_manifest_error(self, fs, full_structure, capsys, mocker):
        instance_path = full_structure
        mocker.patch('sys.exit', side_effect=SystemExit)
        mocker.patch('scripts.pel_toolkit.is_manifest_stale', return_value=(True, "Test Reason: Stale"))
        instance_content = """---
persona_alias: SI-1
---
Mandate body.
"""
        if fs.exists(instance_path):
            fs.remove(instance_path)
        fs.create_file(instance_path, contents=instance_content)
        with pytest.raises(SystemExit):
            pel_toolkit.main(str(instance_path))
        captured = capsys.readouterr()
        error_output = captured.err
        assert "FATAL ERROR: The persona_manifest.yml is stale." in error_output
        assert "Reason: Test Reason: Stale" in error_output

    def test_main_persona_not_found_error(self, fs, full_structure, capsys, mocker):
        instance_path = full_structure
        mock_exit = mocker.patch('sys.exit', side_effect=SystemExit(1))
        instance_content = """---
persona_alias: nonexistent
---
Mandate body.
"""
        if fs.exists(instance_path):
            fs.remove(instance_path)
        fs.create_file(instance_path, contents=instance_content)
        with pytest.raises(SystemExit) as excinfo:
            pel_toolkit.main(str(instance_path))
        assert excinfo.value.code == 1
        mock_exit.assert_called_once_with(1)
        captured = capsys.readouterr()
        assert "Error: Persona 'nonexistent' not found" in captured.err